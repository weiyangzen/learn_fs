# subset-b-000976 research

Grouped research for Gaudi TPC4, TPC5, and TPC6 generated ASIC register headers. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_cfg_regs.h

## Purpose

This auto-generated GPL-2.0 header defines the Gaudi TPC4 configuration register offsets for direct MMIO access. It is included through `include/gaudi/asic_reg/gaudi_regs.h`, which lets Gaudi driver code use symbolic `mmTPC4_CFG_*` names instead of hard-coded offsets. The file contains 602 register macros from `mmTPC4_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xF06400` through `mmTPC4_CFG_QM_SRF_31` at `0xF06E3C`.

## Important APIs, types, and macros

The file exports only preprocessor macros; it declares no C functions, structs, enums, or storage. The major macro families are:

- `mmTPC4_CFG_KERNEL_TENSOR_0..15_*`: 16 tensor descriptor blocks, each with base address low/high, padding value, tensor configuration, and five dimension size/stride pairs.
- `mmTPC4_CFG_KERNEL_*`: kernel sync object, kernel code base, five TID base/size pairs, kernel configuration/id, and `KERNEL_SRF_0..31` scalar register fields.
- `mmTPC4_CFG_*` control/status registers: `ROUND_CSR`, `PROT`, `SEMAPHORE`, `VFLAGS`, `SFLAGS`, `LFSR_POLYNOM`, `STATUS`, base/subtract address controls, `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, icache base registers, read/write rate limits, interrupt cause/mask, ARUSER/AWUSER, LUT function base registers, TSB/debug-memory controls, WQ/TSB counters, and MBIST controls.
- `mmTPC4_CFG_QM_TENSOR_0..15_*` and `mmTPC4_CFG_QM_*`: a second tensor/kernel/SRF register image used by the queue-manager side of the TPC configuration aperture.

## Control flow and state behavior

There is no executable control flow in the header. Runtime behavior appears where driver code writes these offsets through register helpers such as `WREG32`. Observed integration includes `gaudi_tpc_stall()` writing `mmTPC4_CFG_TPC_STALL`, `gaudi_mmu_prepare_reg()` programming `mmTPC4_CFG_ARUSER_LO` and `mmTPC4_CFG_AWUSER_LO` with an ASID, and security setup deriving protection-bit masks from TPC4 CFG offsets. The registers represent hardware state, not kernel-owned persistent data; values survive according to device reset and power behavior, while the macros themselves are compile-time constants.

## Dependencies and integration points

The header is guarded by `ASIC_REG_TPC4_CFG_REGS_H_` and is pulled into the Gaudi register aggregate. It aligns with `gaudi_blocks.h`, where `mmTPC4_CFG_BASE` is `0x7FFCF06000ull` and the CFG sub-block bases start at the same low offsets represented here. Bitfield shifts and masks are not defined in this file; driver users combine these offsets with TPC0-compatible field definitions such as `TPC0_CFG_TPC_STALL_V_SHIFT`.

## Risks and test signals

Because the file is generated and hardware-facing, manual edits are high risk: a wrong address can stall, misconfigure, or expose the wrong TPC engine. Macro spelling quirks such as `ICACHE_BASE_ADDERESS_*` and `IRQ_OCCOUPY_CNTR` are part of the generated API and should not be "fixed" locally without regenerating all dependent headers. Useful validation signals are build coverage of Gaudi register users, static checks that TPC4/5/6 normalized CFG layouts remain identical except for base address, reset tests that stop/stall TPCs, MMU ASID programming tests, and security/protection-bit tests that depend on address-to-bit calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_qm_regs.h

## Purpose

This generated header defines the Gaudi TPC4 QMAN register offsets. It supplies symbolic `mmTPC4_QM_*` constants for queue-manager global control, producer/completion queues, command processors, arbitration, clock/rate limiting, indirect gateway, and error registers. It contains 406 macros from `mmTPC4_QM_GLBL_CFG0` at `0xF08000` through `mmTPC4_QM_GLBL_MEM_INIT_BUSY` at `0xF08D00`.

## Important APIs, types, and macros

The header exports compile-time register constants only. Key macro families are:

- `GLBL_*`: global config/protection/error config, secure and non-secure property registers, status registers, message enables, AXCACHE, global error address/write-data capture, and memory-init busy state.
- `PQ_*`: four producer queues with base low/high, size, producer index, consumer index, queue config, ARUSER, and status registers.
- `CQ_*`: five completion/command queues with config, ARUSER, status, pointer low/high, transfer size, control, latched pointer/size/control status, and input FIFO counters.
- `CP_*`: five command-processor lanes with message base address windows, LDMA offsets, fence read data and counters, processor status, current instruction address, barrier config, debug, and ARUSER/AWUSER properties.
- `ARB_*`: arbitration config, WRR weights, 32 master available-credit registers, 32 choice-push offsets, slave/master controls, message security properties, arbiter base, state/status, error cause/message enable/drop status, and 32 master credit status registers.
- `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, HBW/LBW rate-limit registers, and `IND_GW_APB_*` indirect gateway registers.

## Control flow and state behavior

The file has no functions or branches. Driver control flow uses these constants in register writes and address calculations. Observed users stop TPC4 command processors by writing `mmTPC4_QM_GLBL_CFG1`, map queue IDs `GAUDI_QUEUE_ID_TPC_4_0..3` to `mmTPC4_QM_PQ_PI_0..3` doorbells, prepare non-secure property registers for MMU ASID handling, and construct protection masks from TPC4 QMAN offsets. Queue state lives in device registers and in DMA-visible queue memory addressed by these registers; persistence is hardware-reset scoped.

## Dependencies and integration points

The header is included by `include/gaudi/asic_reg/gaudi_regs.h`; block-level base constants live in `gaudi_blocks.h`, where `mmTPC4_QM_BASE` is `0x7FFCF08000ull`. Higher-level queue identity is connected to Gaudi queue IDs and async events such as `GAUDI_EVENT_TPC4_QM`. Field definitions are shared with peer QMANs, for example TPC0 QMAN bit shifts used when writing equivalent TPC4 registers.

## Risks and test signals

The risk is address fidelity. `PQ_PI_*` offsets are doorbells, so a wrong mapping can submit work to the wrong queue or fail to wake hardware. Security-sensitive global property and ARUSER/AWUSER registers participate in ASID and protection-bit setup. Test signals include successful Gaudi compilation, queue submission tests covering TPC4 lanes, reset/shutdown paths that stop TPC QMAN CPs, MMU context-switch tests, and security tests that verify protected QMAN register windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_cfg_regs.h

## Purpose

This auto-generated header is the TPC5 instance of the Gaudi TPC configuration register map. It has the same normalized macro layout as the TPC4 and TPC6 CFG headers, but all exported names use the `mmTPC5_CFG_*` prefix and addresses are in the TPC5 CFG aperture. The file contains 602 macros from `mmTPC5_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xF46400` through `mmTPC5_CFG_QM_SRF_31` at `0xF46E3C`.

## Important APIs, types, and macros

No functions, types, or variables are defined; the public surface is register macros. The important groups are the 16 `KERNEL_TENSOR_*` descriptors, kernel sync/code/TID/config/id/SRF registers, central TPC CFG control and status registers, ARUSER/AWUSER registers, LUT and debug-memory controls, WQ/TSB counters, MBIST controls, and the mirrored `QM_TENSOR_*` plus `QM_*` tensor/kernel/SRF image.

## Control flow and state behavior

Control flow is entirely in consumers. `gaudi_tpc_stall()` writes `mmTPC5_CFG_TPC_STALL`; MMU setup prepares `mmTPC5_CFG_ARUSER_LO` and `mmTPC5_CFG_AWUSER_LO`; security code computes protection-bit masks from TPC5 CFG register offsets. The constants describe MMIO state for one TPC engine. The kernel does not persist anything in this header; register contents are device state and are reset/reinitialized by Gaudi bring-up and reset paths.

## Dependencies and integration points

The header is included by `gaudi_regs.h` and corresponds to `mmTPC5_CFG_BASE` in `gaudi_blocks.h` (`0x7FFCF46000ull`). Its layout matched the TPC4/TPC6 CFG normalized macro sequence during review, which allows common driver routines to use TPC0-compatible bitfield definitions against per-instance addresses.

## Risks and test signals

Generated-address drift is the main risk. TPC5 offsets are separated from TPC4 and TPC6 by aperture placement, not by semantic layout, so any hand edit can silently desynchronize multi-TPC reset, MMU, or security logic. Tests should build Gaudi register consumers, exercise TPC5 stall/reset and queue launch paths, verify MMU ASID propagation to CFG ARUSER/AWUSER, and compare normalized TPC4/TPC5/TPC6 CFG macro order and count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_qm_regs.h

## Purpose

This generated header defines the TPC5 queue-manager register offsets for Gaudi. It is the TPC5-specific instance of the QMAN map used for queue control, producer/completion queues, command processors, arbitration, rate limiting, indirect APB gateway access, and error reporting. It contains 406 macros from `mmTPC5_QM_GLBL_CFG0` at `0xF48000` through `mmTPC5_QM_GLBL_MEM_INIT_BUSY` at `0xF48D00`.

## Important APIs, types, and macros

The file exports only `#define` constants. The macro layout covers `GLBL_*` global/protection/security/status/error registers, four `PQ_*` producer queues, five `CQ_*` completion/command queues, five `CP_*` command processor lanes, the large `ARB_*` credit/choice/status/error region, `CGM_*` clock gating controls, local range and strict-priority settings, HBW/LBW rate-limit controls, `GLBL_AXCACHE`, and `IND_GW_APB_*` indirect gateway registers.

## Control flow and state behavior

Consumers perform the runtime work. Gaudi stop logic writes `mmTPC5_QM_GLBL_CFG1` to stop CPs, queue doorbell selection maps `GAUDI_QUEUE_ID_TPC_5_0..3` to `mmTPC5_QM_PQ_PI_0..3`, MMU setup writes non-secure property registers, and security code builds protection masks from TPC5 QMAN offsets. Queue indices, CP state, fence counts, arbiter credits, and error captures are hardware state.

## Dependencies and integration points

The header is aggregated by `gaudi_regs.h` and aligns with `mmTPC5_QM_BASE` in `gaudi_blocks.h` (`0x7FFCF48000ull`). It integrates with Gaudi queue IDs, async event `GAUDI_EVENT_TPC5_QM`, register access helpers such as `WREG32`, and shared TPC0 QMAN field definitions used for equivalent bit positions.

## Risks and test signals

Risks concentrate around queue doorbells, security properties, and arbitration state: an incorrect offset may submit to a wrong queue, leave CPs running during reset, or misprogram protection windows. Good signals are compile coverage, TPC5 queue submission/doorbell tests, reset tests that stop TPC QMANs, MMU ASID tests, and structural checks proving the TPC4/TPC5/TPC6 QMAN macro sets remain normalized-identical aside from prefix and base address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_cfg_regs.h

## Purpose

This generated header defines the Gaudi TPC6 configuration register offsets. It mirrors the TPC4/TPC5 CFG layout for the TPC6 address aperture and gives driver code symbolic `mmTPC6_CFG_*` names for tensor descriptors, kernel launch fields, execution controls, debug/MBIST controls, and the queue-manager-visible TPC configuration image. It contains 602 macros from `mmTPC6_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xF86400` through `mmTPC6_CFG_QM_SRF_31` at `0xF86E3C`.

## Important APIs, types, and macros

The public API is the macro list. Important groups are `KERNEL_TENSOR_0..15_*`, `KERNEL_SYNC_OBJECT_*`, `KERNEL_KERNEL_BASE_ADDRESS_*`, TID base/size registers for dimensions 0..4, `KERNEL_CONFIG`, `KERNEL_ID`, `KERNEL_SRF_0..31`, common CFG controls such as `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, interrupt and rate-limit registers, ARUSER/AWUSER controls, LUT base registers, TSB/debug-memory counters, MBIST registers, and the mirrored `QM_TENSOR_0..15_*` and `QM_SRF_0..31` family.

## Control flow and state behavior

There is no code path inside the header. Consumers use these offsets for MMIO. Observed flows include stalling TPC6 with `mmTPC6_CFG_TPC_STALL`, preparing ASID-related `mmTPC6_CFG_ARUSER_LO` and `mmTPC6_CFG_AWUSER_LO`, and building protection-bit masks for the TPC6 CFG register window. The state represented is hardware register state, not software persistence.

## Dependencies and integration points

The header is included by `gaudi_regs.h` and corresponds to `mmTPC6_CFG_BASE` in `gaudi_blocks.h` (`0x7FFCF86000ull`). It integrates with Gaudi reset, MMU, and security code and relies on common bitfield definitions from the equivalent TPC0 registers for shifts/masks.

## Risks and test signals

The file should be treated as generated source of truth. Incorrect offsets affect only TPC6 by name but can break common multi-TPC loops and protection calculations. Tests should include Gaudi build coverage, TPC6 stall/reset scenarios, MMU ASID propagation through CFG user attributes, security protection-window validation, and generated-layout comparisons across TPC4/TPC5/TPC6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_qm_regs.h

## Purpose

This auto-generated header defines the TPC6 QMAN register map for Gaudi. It provides symbolic offsets for queue-manager global control, producer queues, completion queues, command processors, arbitration, clock/rate controls, indirect gateway registers, and error capture. It contains 406 macros from `mmTPC6_QM_GLBL_CFG0` at `0xF88000` through `mmTPC6_QM_GLBL_MEM_INIT_BUSY` at `0xF88D00`.

## Important APIs, types, and macros

No executable API is declared. The exported register families are `GLBL_*`, `PQ_*` for four producer queues, `CQ_*` for five queues, `CP_*` for five command-processor lanes, `ARB_*` for scheduling/credits/errors, `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, HBW/LBW rate limits, `GLBL_AXCACHE`, `IND_GW_APB_*`, and global error/memory-init status registers.

## Control flow and state behavior

Driver users provide control flow. `gaudi_stop_tpc_qmans()` writes `mmTPC6_QM_GLBL_CFG1`; queue ID handling maps `GAUDI_QUEUE_ID_TPC_6_0..3` to `mmTPC6_QM_PQ_PI_0..3`; MMU setup prepares `mmTPC6_QM_GLBL_NON_SECURE_PROPS_0..4`; and security code derives protection masks from TPC6 QMAN offsets. Register contents are hardware queue-manager state and are not persisted by this header.

## Dependencies and integration points

The header is included by the Gaudi register aggregate and aligns with `mmTPC6_QM_BASE` in `gaudi_blocks.h` (`0x7FFCF88000ull`). It integrates with Gaudi queue IDs, async event `GAUDI_EVENT_TPC6_QM`, MMIO helpers, shared QMAN bitfield definitions, and security/protection-bit setup.

## Risks and test signals

The highest-risk offsets are `PQ_PI_*` doorbells, global stop/security registers, and arbiter credit/status regions. A mismatch can cause hangs, lost submissions, or incorrect isolation. Test signals include successful Gaudi builds, TPC6 queue submission tests, reset paths that stop CPs, MMU ASID and security-window validation, and structural diffing against TPC4/TPC5 QMAN maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_qm_regs.h -->
