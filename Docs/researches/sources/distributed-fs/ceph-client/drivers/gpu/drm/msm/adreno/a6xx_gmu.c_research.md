# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.c

## Purpose

`a6xx_gmu.c` implements the GMU side of the Adreno A6xx/A7xx/A8xx GPU driver: firmware loading, HFI startup, RPMh vote construction, runtime power transitions, OOB handshakes, GMU memory allocation, IRQ handling, and GMU device binding. The GMU owns most GPU power-management decisions on full-GMU targets; wrapper/RGMU targets use a reduced path where Linux still maps GMU registers and power domains but skips firmware/HFI allocation.

## Important APIs, Types, And Functions

- `a6xx_gmu_resume()` and `a6xx_gmu_stop()` are the runtime PM entry points used by `a6xx_gpu.c`.
- `a6xx_gmu_set_freq()` translates GPU OPPs into GMU performance and bandwidth indices, sends either HFI frequency messages or legacy DCVS OOB requests, and updates `gmu->freq` plus `current_perf_index`.
- `a6xx_gmu_set_oob()` and `a6xx_gmu_clear_oob()` perform the CPU-to-GMU out-of-band handshake for boot/slumber, GPU critical sections, DCVS, and perfcounter/sysprof blocking.
- `a6xx_gmu_fw_start()` is the boot sequence coordinator. It starts RPMh, loads firmware on cold boot, programs HFI queue base, AHB fence ranges, chip id/log buffer registers, CX GBIF settings, idle policy, CM3 startup, legacy GX rail, SPTPRAC, and HFI queue control.
- `a6xx_gmu_init()` and `a6xx_gmu_wrapper_init()` bind the GMU platform device, configure DMA, map registers, attach power domains, allocate GMU buffers, install IRQs, probe OPP/RPMh votes, and initialize HFI queues.
- `a6xx_gmu_memory_alloc()` creates WC GEM BOs in the GMU VM, optionally at fixed IOVAs for firmware cache/dummy/debug regions.
- `a6xx_gmu_rpmh_votes_init()`, `a6xx_gmu_rpmh_arc_votes_init()`, `a6xx_gmu_rpmh_bw_votes_init()`, and `a6xx_gmu_pwrlevels_probe()` derive GMU/GX/CX ARC votes and DDR BCM votes from OPP tables and command-db data.
- `a6xx_gmu_fault()`, `a6xx_gmu_irq()`, and `a6xx_hfi_irq()` convert GMU watchdog, firmware fault, AHB bus, and fence errors into normal GPU recovery work.

## Control Flow

Initialization starts from `a6xx_gmu_init()`. The function finds the GMU platform device from the DT phandle, enables runtime PM, probes GMU clocks, creates a GMU-only `drm_gpuvm`, allocates fixed and dynamic BOs for dummy pages, debug memory, icache/dcache, log, and HFI queues, maps GMU MMIO and RSCC, requests disabled-by-default IRQs, attaches CX/GX power domains, obtains optional QMP/AOSS, builds OPP and RPMh vote tables, probes ACD, initializes HFI queue descriptors, initializes PDC/RSCC sleep sequences, and marks the GMU initialized. `a6xx_gmu_wrapper_init()` takes a shorter path for GMU wrapper/RGMU devices: map registers, attach domains, fetch clocks, mark legacy for manual SPTPRAC, and skip HFI/firmware memory.

Resume is serialized by `gmu->lock` in `a6xx_gpu.c`. `a6xx_gmu_resume()` powers the GMU device and GX domain, sets conservative GMU/hub clock rates, enables clocks, performs secure-world initialization for newer parts, reads A8xx slice info, applies initial bandwidth, unmasks/enables GMU IRQ, decides warm versus cold boot from retention state, calls `a6xx_gmu_fw_start()`, starts HFI, enables firmware fault IRQ, and finally applies the current GPU frequency. If any boot stage fails, it disables IRQs/clocks and releases runtime PM refs.

Suspend goes through `a6xx_gmu_stop()`. If the GMU is responsive, `a6xx_gmu_shutdown()` performs any missing dummy GPU OOB handshake, releases perfcounter OOB, waits for the target idle level, halts the bus as needed, tells firmware to slumber, waits for GMU not busy, stops HFI, disables IRQs, and asks RPMh/RSCC to power off. If hung or timed out, `a6xx_gmu_force_off()` disables keepalive, flushes HFI, masks IRQs, disables SPTPRAC, asserts GEMNoC workaround, waits for outstanding RPMh TCS votes, opens the AHB fence, halts CM3, halts buses, asserts GPU SW reset, and runs the RPMh stop path.

## State And Persistence Behavior

Persistent GMU state lives in `struct a6xx_gmu`: MMIO/RSCC mappings, IRQ numbers, power domains, GMU VM, BOs for HFI/debug/icache/dcache/dummy/log, clock handles, OPP-derived frequency/bandwidth tables, ARC and BCM vote arrays, HFI queue descriptors, ACD table, QMP handle, current frequency/perf index, `idle_level`, and status bits. `GMU_STATUS_FW_START` and `GMU_STATUS_PDC_SLEEP` coordinate RSCC/PDC sleep transitions; `GMU_STATUS_OOB_PERF_SET` tracks sysprof's perfcounter OOB vote; `GMU_STATUS_SECURE_INIT` prevents repeated secure init.

Firmware persistence is split by target generation. Legacy GMUs load a flat image into ITCM and use OOB for boot/slumber and DCVS. Newer GMUs parse block headers from firmware and place blocks into ITCM, DTCM, icache, dcache, or dummy BOs. Warm boot only applies where retention state is known safe; newer A6xx forces cold boot because external cache regions must be restored.

## Dependencies And Integration Points

This file depends on DRM GEM and msm GEM/VM helpers, Adreno firmware arrays, HFI helpers from `a6xx_hfi.*`, register XML headers, Linux OPP/devfreq, runtime PM, generic power domains, Qualcomm SCM, QMP/AOSS, command-db, TCS/RPMh, clocks, IRQs, and platform resources named `gmu_pdc`, `gmu_pdc_seq`, `rscc`, and GMU core memory. It is consumed by `a6xx_gpu.c` through PM callbacks, frequency callbacks, hardware init OOB sections, sysprof setup, fault recovery, crash-state GMU snapshots, and `gx_is_on` tests.

## Risks And Edge Cases

- OOB requests require `gmu->lock`; callers that violate the lock contract risk racing firmware state or losing ack/clear ordering.
- Firmware block parsing trusts the firmware's block walk enough to iterate until image end; bad block sizes or addresses only log unmatched blocks, so malformed firmware can produce partial state.
- Runtime PM reference handling spans GMU device, GX domain, CX domain links, clocks, and OPPs. Error paths must remain balanced, especially around optional `gxpd`.
- Forced-off recovery writes registers while the hardware may be partially collapsed; barriers, fence allow mode, bus halt, and reset ordering are critical.
- RPMh/command-db data and OPP `level`/bandwidth properties must match DT. Missing levels fail probe or leave GMU unable to vote the intended corners.
- Sysprof uses `GMU_OOB_PERFCOUNTER_SET` to block IFPC while performance counter select registers are meaningful. Missed clear leaves extra power residency; missed set loses counters through IFPC.
- Generation conditionals are dense. A6xx legacy, A650/A660, A7xx, A8xx, wrapper, and RGMU paths use different registers and firmware assumptions.

## Test Signals

Useful validation signals include successful probe with GMU BO allocation names visible, boot logs showing GMU firmware version, runtime suspend/resume cycles without GMU watchdog or HFI fault IRQs, devfreq transitions changing `gmu->freq`, OPP/command-db failures absent, sysprof toggling perfcounter OOB without timeout, GPU hang recovery completing with CX collapse, and devcoredumps containing GMU log/HFI/debug buffers. Kernel logs to watch are "GMU firmware initialization timed out", "Unable to start the HFI queues", "Timeout waiting for GMU OOB set", "Unable to power off the GPU RSC", "GMU watchdog expired", and ACD/QMP errors.
