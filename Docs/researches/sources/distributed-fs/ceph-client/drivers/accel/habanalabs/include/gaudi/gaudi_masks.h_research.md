## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_masks.h

### Purpose
`gaudi_masks.h` collects hand-authored and generated composite bit masks for Gaudi register programming. It turns low-level register field masks from `asic_reg/gaudi_regs.h` into reusable queue-manager enable/protection/error configurations, reset masks, idle predicates, RAZWI initiator decoding helpers, CPU reset values, and selected per-register field masks.

### Important APIs, Types, And Functions
The file exports 252 defines plus `enum axi_id`. Major definitions include QMAN enable masks for PCI DMA, HBM DMA, MME, TPC, and NIC; trusted/protection masks; QMAN error message and stop-on-error masks; clock-gating masks; low/high reset masks and shifts; CPU reset field masks and `CPU_RESET_*` values; idle masks and predicates `IS_QM_IDLE`, `IS_DMA_IDLE`, `IS_TPC_IDLE`, and `IS_MME_IDLE`; RAZWI initiator encoding macros; PSOC ETR AXI control masks; MMU error-capture masks; sync-manager monitor masks; and TPC CP fence status masks.

### Control Flow
The header has no executable statements, but its predicate macros are used as inline control-flow decisions in reset and idle polling paths. Queue setup code writes the composite QMAN masks, reset code assembles unit reset words, RAZWI reporting decodes initiator coordinates and AXI IDs, and coresight/debug code uses selected PSOC masks.

### State, Persistence, And Dependencies
The state affected by these masks is hardware register state: queue enable bits, protection bits, error reporting latches, reset state, idle state, MMU capture fields, and debug/trace settings. The header depends heavily on generated register masks from `asic_reg/gaudi_regs.h` and Linux bitfield helpers such as `FIELD_PREP`, `BIT_MASK`, and `GENMASK`.

### Integration Points
`gaudi.c` uses these masks for queue-manager enablement, engine reset, idle checks, MMU fault reporting, and RAZWI source identification. `gaudi_coresight.c` uses the coresight-related masks and aliases. The masks bridge generated per-register definitions with higher-level Gaudi control flows.

### Risks
Composite masks can hide hardware-field changes. If a generated field mask changes but a composite constant is not audited, the driver can enable the wrong queues, miss errors, or report false idle. The idle predicates are safety gates before reset/power operations, so false positives can reset active engines. RAZWI coordinate and AXI-ID decoding must match hardware encoding or diagnostics will point to the wrong initiator.

### Test Signals
Test queue enablement and stop-on-error configuration for DMA, TPC, MME, and NIC QMs; reset masks for all unit groups; idle polling under active and idle engines; MMU error capture decoding; RAZWI initiator decoding across representative DMA/TPC/MME/NIC/PCI/CPU/PSOC sources; and debug/coresight ETR setup.
