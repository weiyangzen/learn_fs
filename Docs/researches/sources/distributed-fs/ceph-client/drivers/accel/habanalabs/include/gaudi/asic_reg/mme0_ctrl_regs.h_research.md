# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_ctrl_regs.h

## Purpose
`mme0_ctrl_regs.h` is an auto-generated Gaudi register address map for the `MME0_CTRL` block, whose prototype is `MME`. It names the MMIO offsets for the first MME control block's architectural descriptor registers, command/status/control registers, power/rate/debug controls, and four shadow descriptor banks. The driver uses these symbols to inspect MME idle state, configure security/protection access, program debug infrastructure through block bases, and coordinate MME execution through QMAN-submitted descriptors.

## Important APIs, types, and functions
The header exports only `#define` register address symbols. The important groups are:
- `mmMME0_CTRL_ARCH_*`: live architectural descriptor registers for base addresses, tensor S/L/O valid elements, loop strides, ROI sizes, spatial strides, AGU local and remote offsets, sync-object addresses/data, performance events, padding, metadata, and rate-limiter saturation.
- `mmMME0_CTRL_CMD`, `STATUS1`, `RESET`, `QM_STALL`, `SYNC_OBJECT_FIFO_TH`, `INTR_CAUSE`, `INTR_MASK`, and `PROT`: operational control, interrupt, reset, stall, and protection controls.
- `mmMME0_CTRL_PCU_*`, `EU_POWER_SAVE_DISABLE`, `TE_CLOSE_CGATE`, `AGU_*_CNTR`, `EZSYNC_OUT_CREDIT`, and `QM_SLV_LBW_CLK_EN`: performance-control, power, clock-gate, AGU accounting, and sync-message controls.
- `mmMME0_CTRL_CS_DBG_*`: CoreSight/debug status drop controls.
- `mmMME0_CTRL_SHADOW_0_*` through `SHADOW_3_*`: four replicated descriptor snapshots with the same tensor/AGU/sync/perf/padding/metadata layout as the live `ARCH_*` region.

There are no C functions or structs in this file. The "API" is the stability of the macro names and addresses.

## Control flow
No control flow executes in this header. Runtime control flow appears in Gaudi driver code that includes it. During hardware initialization, the driver enables MME-related capabilities and writes related QMAN registers, while MME control registers are used for protection setup and status/idle checks. During security initialization, `gaudi_security.c` computes protection-bit addresses and masks from `mmMME0_CTRL_RESET`, `mmMME0_CTRL_QM_STALL`, interrupt, PCU, protection, debug, AGU, and shadow-bank symbols, then writes protection-bit registers to restrict or permit access. During idle checks, `gaudi.c` reads `mmMME0_CTRL_ARCH_STATUS + offset` for each MME engine and combines it with QMAN status for master MMEs.

Command execution itself is descriptor-driven: userspace or firmware queues work through QMAN command streams, and MME hardware consumes descriptor fields whose live and shadow register addresses are named here. The header therefore defines the observable register layout for that flow but does not implement descriptor submission.

## State and persistence behavior
The file owns no software state. The addresses name hardware state inside MME0. Architectural descriptor registers represent the active descriptor context; shadow banks preserve snapshots for multiple descriptor slots or debug/visibility; command/status/reset/stall registers affect current engine control; interrupt cause/mask registers persist until acknowledged or reset; protection and power/clock controls persist until security setup, reconfiguration, or hardware reset changes them.

Because the file is generated, its values are expected to be treated as immutable for a given ASIC revision. Persistent driver behavior such as idle reporting, protection setup, and debug register routing depends on the exact spacing between the live region, control region, and shadow regions.

## Dependencies and integration points
The header is included by `gaudi_regs.h`, which is then included by Gaudi implementation files. It integrates with:
- `gaudi.c`, which reads `mmMME0_CTRL_ARCH_STATUS` with per-engine offsets to report idle state and writes MME rollup counters.
- `gaudi_security.c`, which derives protection-bit block addresses and masks from MME0 control and shadow symbols.
- `gaudi_coresight.c`, indirectly through generated block-base headers, where MME control block debug bases are used for STM/ETF/BMON/SPMU.
- QMAN register headers, because MME execution is driven by MME QMANs while control/status is observed through this MME control block.

The file assumes common Gaudi address conventions: symbols are absolute config-space register addresses, and repeated MME engines are reached by adding the appropriate MME block offset in consumers.

## Risks and edge cases
- This is generated hardware data. Manual edits would likely desynchronize the driver from ASIC documentation and firmware assumptions.
- Consumers rely on repeated layout. `gaudi.c` adds per-MME offsets to `mmMME0_CTRL_ARCH_STATUS`; if MME1/MME2/MME3 spacing changes, idle checks can read the wrong engine.
- Protection-bit code computes bit positions from the low address bits of these constants. Any register move across protection-bit word boundaries must be reflected in security logic.
- Shadow-bank layout is very large and repetitive. A missing or reordered shadow register can break debug or security behavior while still compiling.
- Register names do not encode access permissions. Writing a status, shadow, or reserved register from a new path can have hardware-specific side effects.
- The live `ARCH_*` descriptor layout overlaps conceptually with firmware/userspace descriptor formats; mismatches can appear as incorrect MME computation rather than a simple driver failure.

## Test signals
Positive signals include Gaudi MME initialization completing, `HW_CAP_MME` being set, idle checks reporting sane `ARCH_STATUS` values, successful workload execution through MME queues, correct interrupt masking/causes, and no protection-bit faults when accessing allowed MME control registers. Security validation should confirm protected registers remain inaccessible when expected. Negative signals include stuck MME idle status, queue submission timeouts, unexpected MME interrupts, protection-bit violations around `MME0_CTRL_*`, or debug/trace output tied to the wrong MME control block.
