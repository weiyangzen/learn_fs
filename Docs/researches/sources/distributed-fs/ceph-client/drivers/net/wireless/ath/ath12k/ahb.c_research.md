# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.c

## Purpose
`ath12k/ahb.c` implements the AHB platform-bus backend for ath12k. It provides HIF operations for MMIO access, CE and DP interrupt control, remoteproc/rootPD and userPD firmware boot, reserved-memory firmware loading, QMI CE configuration, resource mapping, probe/remove orchestration, and registration of family-specific AHB platform drivers.

## Important APIs, Types, And Functions
- `ath12k_ahb_hif_ops` supplies `.start`, `.stop`, `.read32`, `.write32`, `.irq_enable`, `.irq_disable`, `.map_service_to_pipe`, `.power_up`, and `.power_down` to the ath12k core HIF layer.
- MMIO helpers `ath12k_ahb_read32()` and `ath12k_ahb_write32()` choose normal register space or remapped CE space based on `ab->ce_remap` and `ab->cmem_offset`.
- Interrupt setup includes `ath12k_ahb_config_irq()`, `ath12k_ahb_config_ext_irq()`, CE IRQ handlers/workqueues, external IRQ group handlers, and NAPI poll through `ath12k_dp_service_srng()`.
- Remoteproc/firmware boot is handled by `ath12k_ahb_configure_rproc()`, `ath12k_ahb_boot_root_pd()`, `ath12k_ahb_config_rproc_irq()`, `ath12k_ahb_power_up()`, and `ath12k_ahb_power_down()`.
- Resource lifecycle functions include `ath12k_ahb_resource_init()`, `ath12k_ahb_resource_deinit()`, `ath12k_ahb_probe()`, `ath12k_ahb_remove()`, `ath12k_ahb_free_resources()`, `ath12k_ahb_register_driver()`, and `ath12k_ahb_unregister_driver()`.

## Control Flow And State Behavior
Probe allocates `ath12k_base` with `struct ath12k_ahb` private data, selects the registered device-family driver by OF match table, runs family probe, records fixed reserved-memory availability, pre-initializes core state, maps MMIO/CE resources, enables the XO clock, initializes HAL SRNGs, allocates CE pipes, initializes QMI CE mapping, configures remoteproc and userPD IRQs, requests CE/DP interrupts, runs family `arch_init`, and finally calls `ath12k_core_init()`.

Power-up maps reserved memory, requests `q6_fw<userpd>.mbn` and `iu_fw.mbn`, loads MDT segments with SCM authentication when enabled, optionally authenticates/resets PAS, toggles SMEM spawn state, waits for userPD spawned/ready completions, and clears spawn state. Power-down toggles stop state, waits for stop-ack, clears state, and shuts down PAS when SCM authentication was used.

Runtime interrupt state is split between CE interrupts serviced by bottom-half workqueues and external DP ring interrupts serviced through NAPI groups. Stop disables CE interrupts unless crash flush is active, synchronizes IRQs, cancels CE work, deletes RX replenish retry timer, and cleans CE pipes. Remove waits for recovery if needed, marks unregistering, cancels restart/QMI work, performs core cleanup/deinit, and frees resources.

## Dependencies And Integration Points
The file depends on platform devices, device tree matching, DMA mask setup, remoteproc, Qualcomm SSR notifier, SMEM state, SCM/PAS, MDT firmware loader, reserved memory, clocks, Kbuild `CONFIG_ATH12K_AHB`, ath12k core/HIF/HAL/CE/DP/QMI, and family-specific AHB drivers. It exports registration helpers so chipset-specific code can register an OF table plus architecture hooks.

## Risks And Edge Cases
- Probe has many ordered resources; unwind paths must mirror allocation or leaks/active remoteproc notifiers can remain.
- Firmware filenames and reserved-memory setup must match device tree and firmware packaging.
- UserPD/rootPD completions are timeout-based; missing IRQ wiring or SMEM bits causes boot failure.
- External IRQ mapping derives interrupt names from ring masks and ring indexes; wrong mapping can starve TX/RX completions.
- CE remap changes register address selection and must align with hardware `ce_remap` parameters.
- The family driver registry is global and rejects duplicate registrations; module init/exit ordering matters.

## Test Signals
Validate AHB probe/remove on supported IPQ-class hardware, deferred remoteproc probe, fixed reserved-memory device tree, SCM-authenticated and non-authenticated firmware load, missing firmware error paths, userPD spawn/ready/stop timeouts, CE interrupt servicing, DP NAPI ring servicing, crash-flush stop behavior, recovery wait, resource unwind by injected failures at each probe step, and family register/unregister duplicate/invalid argument paths.
