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
