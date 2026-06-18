# Research: subset-b-000959

Grouped research for Gaudi2 private driver definitions, CoreSight programming, CoreSight register offsets, and register-mask helpers. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2P.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2P.h

## Purpose
This private Gaudi2 header centralizes ASIC-specific constants, resource counts, hardware capability masks, engine and interrupt identifiers, private driver state, and local function declarations used by the HabanaLabs Gaudi2 driver. It is the shared contract between Gaudi2 implementation files, including the CoreSight path, queue setup, memory mapping, security, block initialization, and event handling.

## Important APIs, types, and functions
- Firmware and timeout constants name the Linux and boot FIT images and define CPU, preboot, boot FIT, and CoreSight wait durations.
- Queue counts derive `NUMBER_OF_HW_QUEUES` and `NUMBER_OF_QUEUES` from PDMA, EDMA, MME, TPC, NIC, ROT, CPU, and `NUM_OF_PQ_PER_QMAN`.
- User mapping constants derive the size and index layout of `mapped_blocks`, including ARC, ACP, NIC UMR, decoder, and exposed sync-manager blocks.
- Memory-map constants describe firmware image, page-table, EDMA scratchpad, host VA, HBM VA, and internal CB sizing.
- Hardware capability masks encode initialized or available engines: PLL, DRAM, PMMU, CPU, MSI-X, CPU queue, clock gate, KDMA, DMMU bits, PDMA, EDMA, MME, ROT, HBM scrambler, decoder, TPC, NIC, and combined MMU masks.
- `enum gaudi2_reserved_sob_id`, `enum gaudi2_reserved_mon_id`, and `enum gaudi2_reserved_cq_id` reserve sync objects, monitors, and completion queues for CS completion, KDMA completion, and decoder normal/abnormal completion handling.
- Engine identity enums define DMA cores, rotators, MMEs, TPCs, decoders, HBMs, and EDMAs in driver-facing order.
- `enum gaudi2_irq_num` maps event queue, decoder interrupts, completion, NIC port interrupts, TPC assert, EQ error, user interrupts, reserved interrupts, unexpected error, and the final MSI-X index.
- `struct dup_block_ctx` carries a repeated-block initialization callback and addressing stride data.
- `struct gaudi2_queues_test_info` holds DMA and kernel addresses for queue self-test messages.
- `struct gaudi2_device` is the private per-device state extension hung off `hdev->asic_specific`.
- Function declarations expose Gaudi2 helpers including TPC iteration, CoreSight init/debug/halt, duplicated-block init, HMMU enable checks, range-register writes, security setup/error handling, and device activity reporting.

## Control flow
The header has no executable control flow, but many macros determine runtime control flow in implementation files. Queue and reserved-resource counts size loops and arrays; hardware capability masks gate initialization and error paths; IRQ enum ordering drives MSI-X allocation and event dispatch; `GAUDI2_ENG_ID_TO_STR` and `GAUDI2_QUEUE_ID_TO_STR` convert hardware identifiers defensively by returning `"not found"` when indexes exceed the known enum ranges. The `static_assert` after the IRQ enum ensures user interrupt numbering starts after the shared decoder interrupt range.

## State and persistence behavior
`struct gaudi2_device` defines the major persistent in-kernel state for the ASIC instance. It stores the CPU-CP information callback, user-mappable block table, MME random seeds, hardware queue lock, scratchpad memory, virtual MSI-X doorbell page, current DRAM BAR address, initialized hardware-capability bitmaps, active ARC bitmaps, per-engine decoder/TPC/NIC capability bitmaps, hardware event validity and histogram arrays, and queue-test buffers. These fields survive across normal driver operations and are reset or cleared by implementation code during engine reset, capability discovery, event processing, or teardown.

## Dependencies and integration points
The file depends on Linux/HabanaLabs UAPI and internal generated Gaudi2 headers: DRM accel UAPI, common driver definitions, boot interface, Gaudi2 registers, packet formats, firmware interface, and async events. It is included by Gaudi2 implementation files that need common ASIC sizing and private state. `gaudi2_coresight_regs.h` includes this header for `CORESIGHT_TIMEOUT_USEC`, `HW_CAP_PMMU`, `MMUBP_ASID_MASK` through the masks dependency chain, and `struct gaudi2_device` used by CoreSight address validation.

## Risks and edge cases
- Many constants derive from generated register symbols; a generated header mismatch can silently corrupt resource counts, register spacing assumptions, or reserved object ranges.
- `NUM_USER_MAPPED_BLOCKS` and related start indexes must stay aligned with code that fills `mapped_blocks`; changing NIC, decoder, ARC, or sync-manager counts can break user mappings.
- Hardware capability masks use fixed bit positions, so firmware and diagnostic code must agree on bit layout.
- `HW_CAP_RESERVED` uses `BIT(43)` instead of `BIT_ULL(43)`, which is suspicious for a bit above 31 unless `BIT` is widened in this build context.
- `enum substitude_tpc` keeps a misspelled name and comments documenting replacement TPC behavior; renaming would affect all users.
- `struct gaudi2_device` is broad shared state, so additions require careful reset, teardown, and concurrency treatment.

## Test signals
Useful validation signals include successful Gaudi2 probe, queue count and MSI-X allocation consistency, no compile-time assertion failure for interrupt ordering, correct user block mmap behavior, hardware capability masks matching discovered engines, successful CoreSight init with expected masks, queue self-tests using `queues_test_info`, and reset paths clearing initialized and active capability bits without losing persistent event statistics unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2P.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight.c

## Purpose
This file implements Gaudi2 CoreSight debug support. It maps user-visible debug component IDs to hardware base addresses, configures STM, ETF, ETR, funnel, bus monitor, and SPMU blocks, halts trace collection, and masks out CoreSight components for binned or disabled hardware units at initialization.

## Important APIs, types, and functions
- `debug_stm_regs`, `debug_etf_regs`, `debug_funnel_regs`, `debug_bmon_regs`, and `debug_spmu_regs` are static ID-to-base-address tables indexed by Gaudi2 CoreSight enums from the public Gaudi2 CoreSight include.
- `struct component_config_offsets` describes which funnel, ETF, STM, SPMU, and BMON IDs belong to one logical unit.
- Binning tables cover XBAR edge, HMMU, HBM MC0/MC1, decoders, EDMA, and TPC units. They let init-time code zero all CoreSight base-table entries associated with disabled hardware instances.
- `gaudi2_coresight_timeout` polls a register bit until it becomes set or clear, using an extended timeout under PLDM.
- `gaudi2_unlock_coresight_unit` writes the CoreSight unlock value and waits for the lock-status bit to clear.
- `gaudi2_config_stm`, `gaudi2_config_etf`, `gaudi2_config_etr`, `gaudi2_config_funnel`, `gaudi2_config_bmon`, and `gaudi2_config_spmu` implement individual debug operations.
- `gaudi2_debug_coresight` dispatches `HL_DEBUG_OP_*` requests to those configuration helpers.
- `gaudi2_halt_coresight` disables ETFs and ETR for context teardown or debug stop.
- `gaudi2_coresight_set_disabled_components` mutates static base-address tables to zero out disabled units.
- `gaudi2_coresight_init` applies binning masks from `hdev->asic_prop`.

## Control flow
User debug requests enter through `gaudi2_debug_coresight`, which interprets `struct hl_debug_params::op`. For component-local operations, helpers validate `reg_idx` against the corresponding static table, fetch the base address, treat base address zero as a successful no-op, and, for PLDM, read an identifying/status register to skip stubbed components. STM, ETF, ETR, and funnel paths unlock CoreSight before programming. Missing input payloads for enable operations return `-EINVAL`; unlock or hardware timeout failures return `-EIO` or the poll error.

STM enable programs trace control, hardware event masks, stimulus port masks, ATB ID, timestamp frequency, synchronization, and final enable bits. Disable clears event/stimulus/timestamp registers, waits for the busy bit to clear, and leaves the block in a minimal disabled control state. ETF and ETR share a flush-and-wait sequence: assert FFCR bits, wait for flush completion and empty status, disable CTL, then either program sink mode/buffer settings and re-enable or clear settings. Funnel simply writes all input enables (`0xFFF`) or zero to the funnel control base.

BMON enable resets the monitor, programs up to four address windows, clears ID filters, programs bandwidth/window capture/reduction/STM trace ID settings, and writes the caller-supplied control word. Disable clears address windows and programs a disabled/reset trace state. SPMU enable validates at most six event types, resets PMCR, writes event selectors and trace controls, enables the cycle counter plus selected events, and starts collection. Disable stops PMCR, optionally copies event counters, overflow, and cycle counter into the caller output buffer, clears overflow state, and resets PMTRC.

Initialization calls `gaudi2_coresight_set_disabled_components` once per binned family. That helper computes `disabled_mask = ~enabled_mask & full_mask`, walks each disabled component, and writes `0x0` into every associated global CoreSight base-address table entry. Later configuration requests to those IDs become no-ops.

## State and persistence behavior
The file has no heap-backed private state, but it maintains process-global static base-address tables. `gaudi2_coresight_init` permanently mutates those tables for the lifetime of the loaded driver image by setting disabled component entries to zero. That design makes per-device binning state global to the module, which is acceptable only if all active devices share compatible masks or initialization ordering is constrained elsewhere. Runtime configuration writes directly to device registers and leaves hardware state in trace-enabled or trace-disabled mode until a matching disable, halt, reset, or device teardown path runs. ETR disable can persist the final trace write pointer to `params->output`.

## Dependencies and integration points
The implementation depends on `gaudi2_coresight_regs.h` for register offsets, `gaudi2_masks.h` for MMU/ASID masks, Gaudi2 generated register bases, UAPI debug operation and payload structs, common register access macros (`RREG32`, `WREG32`, `RMWREG32`), `hl_poll_timeout`, `hl_mem_area_inside_range`, and `hdev->asic_prop` masks and address ranges. It integrates with the user debug ioctl path through `gaudi2_debug_coresight`, with context memory ownership through ETR ASID programming, with PLDM by detecting stub components and stretching timeouts, and with ASIC initialization through `gaudi2_coresight_init`.

## Risks and edge cases
- Static table mutation during binning is global, so mixed devices or re-probe sequences with different masks could inherit zeros from an earlier device.
- Zero base addresses serve both as unsupported component sentinels and binned/stub markers; callers receive success instead of an explicit "unavailable" result.
- ETR address validation returns `int` but uses boolean semantics and has an overflow check `addr > addr + size`; edge cases around zero size and wraparound rely on the prior size check in `gaudi2_config_etr`.
- SPMU disable computes `events_num = output_arr_len - 2` before checking `output_arr_len > 2`; unsigned underflow is harmless because it is only used under the guarded branch, but the pattern is fragile.
- ETR programming writes trace AWUSER/ARUSER from `ctx->asid`; incorrect context or stale ASID would route trace writes into the wrong address space.
- PLDM stub detection depends on specific registers returning zero; a real component returning zero during reset could be skipped.
- Many magic register values encode hardware programming sequences without named bitfields, making regressions hard to review.

## Test signals
Signals include successful debug ioctl enable/disable for all operation types, invalid `reg_idx` returning `-EINVAL`, enable without input returning `-EINVAL`, timeouts producing device errors, PLDM stubs being skipped without crashes, binned component requests becoming no-ops, ETR rejecting buffers outside allowed SRAM/DRAM/MMU ranges, ETR output pointer matching hardware write pointer after disable, SPMU counter output length validation, and full reset/halt paths leaving ETF/ETR disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight_regs.h

## Purpose
This header defines per-component CoreSight register offsets for Gaudi2. It converts generated absolute register symbols for one representative instance into reusable offsets for all funnels, ETFs, STMs, SPMUs, and BMONs, allowing `gaudi2_coresight.c` to program any instance by adding a common offset to that instance's base address.

## Important APIs, types, and functions
- Includes `gaudi2_masks.h`, the public Gaudi2 CoreSight ID header, and `gaudi2P.h`.
- Funnel offsets cover control, priority, integration-test ATB registers, claim/lock/auth/status registers, device ID/type, peripheral IDs, and component IDs.
- ETF offsets cover size/status/read/write pointers, trigger/control/data, mode, buffer levels, watermark, formatter flush/status/control, prescaler, integration-test ATB registers, claim/lock/auth, device identity, peripheral IDs, and component IDs.
- STM offsets cover DMA registers, hardware-event enable/type/bank/mux/master/id registers, stimulus-port enable/trigger/scratch/override registers, trace control, timestamp frequency/stimulus/sync/aux registers, feature and integration-test registers, claim/lock/auth, device identity, peripheral IDs, and component IDs.
- SPMU offsets cover event counters, cycle counter low/high, trace controls, event type selectors, snapshot/status/overflow registers, counter enable/clear, interrupt enable/clear, PMCR, integration/claim/lock/auth, affinity, device identity, peripheral IDs, and component IDs.
- BMON offsets cover control/reset/interrupt, trigger thresholds, four address windows, reduction, ID filters, attribute/user filters, capture/release, bandwidth/window capture, match/cycle/latency/bandwidth/outstanding snapshots, STM trace/drop, identity, peripheral IDs, and component IDs.
- `mmCORESIGHT_UNLOCK_REGISTER_OFFSET` and `mmCORESIGHT_UNLOCK_STATUS_REGISTER_OFFSET` alias the STM lock access/status offsets for the common CoreSight unlock sequence.

## Control flow
The header has no runtime control flow. Its key design is compile-time offset derivation: each macro subtracts the representative component base, for example `mmDCORE0_TPC0_EML_*_BASE`, from the representative absolute register address. Runtime code then uses `base_reg + offset` for any instance of that component type. The grouping comments document that offsets are expected to be identical for all instances of each component class.

## State and persistence behavior
No state is stored or persisted. The header contributes constants only. Runtime state affected by these offsets lives in hardware registers programmed by `gaudi2_coresight.c`; incorrect offsets would write or read the wrong register fields on every instance using the shared formula.

## Dependencies and integration points
The file depends on generated Gaudi2 register definitions transitively through `gaudi2_masks.h`/`gaudi2P.h` and on public CoreSight ID definitions through `../include/gaudi2/gaudi2_coresight.h`. It is directly consumed by `gaudi2_coresight.c`. The common unlock aliases integrate all CoreSight component configuration paths with the same lock access/status sequence, even though the names use STM-derived representative offsets.

## Risks and edge cases
- The entire header assumes identical register layout across all instances of a component type; any hardware variant with a different layout would be misprogrammed.
- Offset derivation uses one DCORE0 TPC0 EML representative for many component classes. Generated register renames or base changes can break all offsets at compile time or, worse, silently shift values if generated addresses are wrong.
- There are many identity/integration-test offsets that are not currently used by `gaudi2_coresight.c`; future code may assume they are complete and correct without runtime validation.
- The common unlock aliases use STM lock offsets for all CoreSight units; this relies on ARM CoreSight lock register placement being common.
- The header includes broad private headers, so unrelated changes in private Gaudi2 definitions can affect compile dependencies for CoreSight code.

## Test signals
Validation signals include successful compile against generated register headers, `gaudi2_coresight.c` programming the expected hardware blocks, no MMIO faults during unlock/configure/halt, ETF/STM/SPMU/BMON values changing in the intended registers, PLDM stub checks reading the intended ID/status offsets, and hardware trace/counter output matching configured masks and buffer settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_coresight_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_masks.h

## Purpose
This private header collects Gaudi2 bit masks and composed register values used across the driver. It gives implementation files named masks for queue-manager error handling, protection, enable/idle/stop/flush bits, engine idle checks, PCIe and MME errors, sync-manager values, MMU/ASID protection bits, rotator halt bits, MSI-X address matching, and PCIe wrapper SEI interrupt fields.

## Important APIs, types, and functions
- Queue-manager masks compose error message enable, stop-on-error enable, protection/trust, normal enable, PDMA-specific enables, idle checks, ARC idle checks, stop bits, and flush bits.
- `MME_ARCH_IDLE_MASK`, `TPC_IDLE_MASK`, and `CGM_IDLE_MASK` group the architecture status bits needed to decide whether engines are idle.
- Arbiter and PCIe masks cover QM arbiter overflow/watchdog/LBW errors and PCIe FLR control interrupt masking.
- MME accumulator interrupt masks identify WBC response errors and arithmetic positive/negative infinity or NaN conditions.
- Sync-manager completion queue constants define high-to-low compare/mask values and low-bit extraction.
- `MMU_STATIC_MULTI_PAGE_SIZE_HOP4_PAGE_SIZE_MASK` and `STLB_HOP_CONFIGURATION_ONLY_LARGE_PAGE_MASK` wrap generated register field masks.
- `AXUSER_HB_SEC_ASID_MASK`, `AXUSER_HB_SEC_MMBP_MASK`, and `MMUBP_ASID_MASK` define the ASID/MMU-bypass bits used by CoreSight ETR trace AWUSER/ARUSER programming.
- Rotator MSS halt masks identify WBC, RSB, and MRSB halt bits.
- PCIe DBI MSI-X address-match masks and PCIe wrapper SEI interrupt indication/mask fields name low-level interrupt bits.

## Control flow
The header has no executable flow. It influences runtime flow by giving implementation files exact values to write to hardware registers or compare against hardware status. For example, queue setup can write `QMAN_ENABLE` or PDMA-specific enable masks, stop paths can use the `QM_GLBL_CFG*` stop/flush masks, idle polling can compare against `QM_IDLE_MASK` and `TPC_IDLE_MASK`, and CoreSight ETR can use `MMUBP_ASID_MASK` in `RMWREG32` calls to preserve unrelated AWUSER/ARUSER bits while updating the ASID/MMU-bypass field.

## State and persistence behavior
No state is stored in this file. The masks drive persistent hardware register state when used by implementation files. Because some macros are composed write values rather than pure field masks, confusing those categories could leave queues trusted, enabled, stopped, flushed, or error-reporting incorrectly until reset or reprogramming.

## Dependencies and integration points
The file depends on the generated Gaudi2 register header for shift and mask constants. It is included by `gaudi2_coresight_regs.h` and likely by other Gaudi2 implementation files that configure queues, engines, MMU, PCIe, rotator, and protection/error paths. Its `MMUBP_ASID_MASK` is directly integrated with CoreSight ETR address-space configuration in `gaudi2_coresight.c`.

## Risks and edge cases
- Several macros are full register write values while others are bit masks for read/modify/write; callers must use them in the correct mode.
- The typo `CHOISE` in QM arbiter masks is part of the public private-name surface and could propagate.
- Hard-coded literals such as `0x100`, `0x40`, CQ compare values, and AXUSER masks rely on generated headers and hardware documentation staying aligned.
- Shifted constants use plain `1` and small integer literals in many places; if a future field crosses 31 bits, callers may need widened literals.
- Error and idle masks are derived from representative DCORE0/PDMA0/TPC0 register definitions and assume identical bit layouts across duplicated engines.

## Test signals
Signals include successful queue enable/disable and idle polling, expected stop-on-error behavior, trusted/untrusted protection transitions, accurate MME/TPC idle detection, CoreSight ETR trace writes using the caller ASID, rotator halt paths affecting the intended sub-blocks, PCIe FLR/MSI-X masking behaving as expected, and interrupt/error handlers decoding the same bits that hardware reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_masks.h -->
