# Research: subset-b-000978

Grouped research for generated Gaudi2 ASIC register and mask headers under `sources/distributed-fs/ceph-client`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_regs.h

## Purpose
`arc_farm_arc0_dup_eng_regs.h` is the generated address map for the Gaudi2 `ARC_FARM_ARC0_DUP_ENG` duplicate-engine block, prototype `ARC_DUP_ENG`. It exposes 276 register address macros in the 0x4E89000-0x4E896B0 region that let ARC farm firmware or the driver duplicate/route engine transactions across TPC, MME, NIC, EDMA, PDMA, ROT, and reserved engine slots.

## Important APIs, types, and functions
This header exports `mmARC_FARM_ARC0_DUP_ENG_*` macros only. Major groups are per-engine duplicate address tables for 25 TPCs, 4 MMEs, 24 NICs, 8 EDMAs, 2 PDMAs, 2 ROTs, and 16 reserved slots; engine mask registers for TPC/MME/EDMA/PDMA/ROT/reserved/NIC groups; multiple `DUP_TRANS_DATA_Q_*_*` queues; `DUP_GENERAL_CFG`, `DUP_BP_CFG`, and 14 group address-offset registers; debug input/status/output counters; 64 ARC context-id registers; and 64 ARC context-id offset registers.

## Control flow
The file contains no executable control flow. Runtime code programs it as a routing table: configure duplicate target addresses and masks, optionally set grouped address offsets and backpressure behavior, then allow ARC firmware or command submission paths to emit duplicated engine transactions. Debug paths can read the group transaction and output request counters to understand whether duplicated traffic is entering and leaving the block.

## State and persistence behavior
All state is hardware-resident and persists until reset or reprogramming. The engine address, mask, queue, context-id, and context-offset registers define how ARC0 traffic is mapped to engine endpoints. Incorrect persisted values can make later command streams target the wrong engine or context even if the command stream itself is valid.

## Dependencies and integration points
The header integrates with generated Gaudi2 base maps, ARC firmware setup, engine discovery/topology code, and debug/recovery code that reasons about ARC farm routing. Consumers depend on the register order and engine counts matching Gaudi2 topology constants elsewhere in the driver.

## Risks and edge cases
The largest risk is topology drift: a count mismatch for TPC, NIC, EDMA, or context-id slots can map a command to the wrong target. Masks and address tables are separate, so enabling a mask before the matching address table is initialized can route traffic into stale or reserved addresses. Reserved-engine slots should remain treated as reserved unless the hardware spec says otherwise.

## Test signals
Test signals include successful ARC farm initialization, command execution across TPC/MME/NIC/EDMA endpoints, no duplicated traffic to disabled engines, expected debug counters during routed work, and reset tests proving duplicate address/mask tables are reinitialized before traffic resumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_masks.h

## Purpose
`arc_farm_kdma_ctx_axuser_masks.h` is the generated bitfield map for the `ARC_FARM_KDMA_CTX_AXUSER` AXUSER registers. It provides 74 shift/mask macros for encoding ASID, MMU bypass, ordering, snoop, reduction, atomic, QOS, reserved, coordinate, override, and LB lock/override fields for DMA context traffic.

## Important APIs, types, and functions
There are no functions or C types. Important fields are `HB_ASID_WR/RD`, `HB_MMU_BP_WR/RD`, `HB_STRONG_ORDER_WR/RD`, `HB_NO_SNOOP_WR/RD`, `HB_WR_REDUCTION` fields for indication, dtype, op, rounding, and max, `HB_RD_ATOMIC` indication/addition-size/MSB-mask fields, `HB_QOS_WR/RD`, HB reserved bits, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD_X/Y`, HB write/read override low/high values, and LB coordinate/lock/reserved/override values.

## Control flow
The header has no runtime logic. It is used during AXUSER setup before queue or DMA traffic is allowed to run. Callers compose values using these masks and write them to the companion AXUSER register addresses; later DMA commits and QMAN commands rely on these attributes being stable.

## State and persistence behavior
The masks describe persistent hardware configuration fields. ASID, MMU bypass, ordering, snoop, QOS, reduction, atomic, and override values remain in the register bank until reset or reprogramming and can affect every subsequent transaction from the associated context.

## Dependencies and integration points
This mask header integrates with `arc_farm_kdma_ctx_axuser_regs.h` and with common code that also programs EDMA/QMAN AXUSER blocks using the same `AXUSER` prototype. It must stay aligned with security/MMU initialization, ASID allocation, and bus-routing/e2e-coordinate setup.

## Risks and edge cases
Risks include stale ASID or bypass attributes crossing context boundaries, QOS or no-snoop settings reducing coherency/performance, incorrect reduction/atomic encodings changing memory semantics, and software writing reserved bits as if they were portable feature controls. Field-width drift versus the address header or hardware spec would produce silent transaction-attribute bugs.

## Test signals
Validation includes MMU-on and MMU-bypass traffic, ASID isolation tests, HB and LB transactions, atomic/reduction paths if exposed, cache/no-snoop behavior checks, and negative tests that should produce protection or RAZWI errors for invalid ASID/security combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_regs.h

## Purpose
`arc_farm_kdma_ctx_axuser_regs.h` is an auto-generated Gaudi2 register-address header for the `ARC_FARM_KDMA_CTX_AXUSER` AXUSER register bank. It exposes 19 `mm...` address macros in the `0x4E8B800-0x4E8B84C` region for programming AXI user attributes on high-bandwidth (HB) and low-bandwidth (LB) DMA or queue-manager traffic. This is the KDMA context AXUSER view in the ARC farm.

## Important APIs, types, and functions
The file exports preprocessor constants only; there are no C types or functions. The important register groups are `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, HB write/read override low/high pairs, and the LB `COORD`, `LOCK`, `RSVD`, and `OVRD` registers. These addresses pair with AXUSER mask headers that define write/read ASID fields, MMU-bypass bits, cache/snoop controls, reduction/atomic encodings, QOS, coordinate routing, and override payload masks.

## Control flow
The header has no runtime control flow. Its constants are consumed by Gaudi2 initialization, queue setup, DMA context programming, firmware bring-up, and debug/error paths that issue `WREG32`/`RREG32` accesses. Typical sequencing is to program ASID and MMU bypass attributes before enabling or committing DMA/QMAN work, then leave the values resident while the corresponding queue or DMA context issues AXI transactions.

## State and persistence behavior
State is purely hardware-resident. Values written through these macros persist in the AXUSER register bank until reset or reprogramming, and they affect subsequent bus transactions from the associated block. The split HB/LB and read/write override registers mean stale values can survive across contexts if reset/init code does not explicitly reinitialize the bank.

## Dependencies and integration points
This generated header integrates with `gaudi2/asic_reg/*_axuser_masks.h`, common HabanaLabs register accessors, and Gaudi2 queue/DMA initialization code. It has no include dependencies beyond its guard. Its address base must stay synchronized with generated block base maps and with any driver tables that select EDMA, KDMA, or QMAN AXUSER windows by engine id.

## Risks and edge cases
The main risk is programming the right field at the wrong engine's AXUSER base, which can silently change ASID, MMU bypass, snoop, QOS, or security attributes for unrelated traffic. Nonsecured QMAN banks are especially sensitive because their name encodes the security domain. Register layout drift between the address header and mask header can also produce correct-looking writes to semantically wrong fields.

## Test signals
Useful signals are successful Gaudi2 probe/reset with MMU enabled, DMA or QMAN traffic using expected ASIDs, no RAZWI/protection errors after AXUSER programming, and queue stress that exercises host, HBM, and LB paths. Negative signals include access faults, unexpected secure/nonsecure violations, bad QOS behavior, or device traffic observed with stale ASID/MMU-bypass attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_masks.h

## Purpose
`arc_farm_kdma_ctx_masks.h` is the generated bitfield map for the `ARC_FARM_KDMA_CTX` `DMA_CORE_CTX` register bank. It defines 126 shift/mask macros used to compose DMA context descriptors for rate limits, power-low behavior, tensor/linear dimensions, control flags, address offsets, base addresses, write completion, and commit selection.

## Important APIs, types, and functions
The macro namespace covers `RATE_LIM_TKN` read/write token fields, `PWRLP` data/enable, full-width tensor sizes and strides, context index and increment, `CTRL` bits for transpose, dtype, compression, decompression, and read-uncacheable mode, source/destination offset and base fields, write-completion address/data fields, destination size 0, and `COMMIT` bits that select which context components are latched, including variants that source offsets/strides from corresponding destination fields and the `LIN` linear-DMA selector.

## Control flow
The header is not executable. Software uses these masks while building context writes before the final commit register access. The control-flow dependency is important: fields named in `COMMIT` determine which earlier context registers are consumed, so programming code must update all selected registers first and then write a commit value assembled with these masks.

## State and persistence behavior
No software state is stored here. The masks define hardware state layout for the DMA context registers. Context state can persist across operations, and selective commit semantics mean a new descriptor can inherit fields from previous state if the commit mask omits them or if software fails to initialize them.

## Dependencies and integration points
This header is coupled to the matching `*_CTX_REGS_H_` file, the `DMA_CORE` status/error bank, AXUSER attributes, and any descriptor-generation code in the Gaudi2 driver or firmware. It is also tied to hardware packet formats when queue commands write context registers indirectly.

## Risks and edge cases
The main risks are data corruption from size/stride/address-field mismatch, accidental carryover of stale context fields, using compression/decompression/dtype combinations unsupported by the current engine mode, and writing high/low address halves with values beyond hardware-accepted address width. Since all masks are numeric constants, compile success does not prove semantic correctness.

## Test signals
Tests should exercise full context programming for linear and tensor DMA, partial commit behavior, boundary sizes and strides, 64-bit addresses, compression/decompression controls, and reset paths that guarantee context fields start from expected defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_regs.h

## Purpose
`arc_farm_kdma_ctx_regs.h` is the generated address map for the `ARC_FARM_KDMA_CTX` DMA context register bank in the `0x4E8B860-0x4E8B8EC` range. It defines 36 context registers for rate limiting, power behavior, tensor/linear DMA dimensions, strides, source/destination bases and offsets, write-completion metadata, and the final context commit trigger.

## Important APIs, types, and functions
The file exports `mm...` constants only. Key programming registers are `RATE_LIM_TKN`, `PWRLP`, `TE_NUMROWS`, `IDX`, `IDX_INC`, `CTRL`, source `TSIZE` and `STRIDE` registers for dimensions 0-4, destination `TSIZE` and `STRIDE` registers, `WR_COMP_ADDR_HI/LO`, `WR_COMP_WDATA`, `SRC_OFFSET`, `DST_OFFSET`, `SRC_BASE`, `DST_BASE`, `DST_TSIZE_0`, and `COMMIT`. These addresses pair with the corresponding `*_CTX_MASKS_H_` header, where `CTRL` selects transpose, dtype, compression/decompression, and read-uncacheable behavior and `COMMIT` selects which context fields are latched.

## Control flow
There is no executable code. Driver or firmware code writes a context in dependency order: set rate/power and index controls, program tensor sizes and strides, install source and destination address components, optionally configure write-completion data, and finally write `COMMIT` to latch the descriptor into the DMA engine. Status/error observation happens through the sibling DMA core register bank rather than this context map.

## State and persistence behavior
The programmed context is hardware state. It persists until overwritten, reset, or superseded by a later commit. Because the commit register can selectively source stride/offset/base values, partial context updates can intentionally reuse earlier fields; the same behavior is risky if software assumes a clean context after reset without actually initializing every relevant field.

## Dependencies and integration points
This header integrates with the matching DMA context mask header, the associated DMA core address/mask headers, Gaudi2 queue command generation, and firmware routines that prepare DMA descriptors. The register sequence also depends on AXUSER context programming when ASID, MMU bypass, or snoop attributes must match the programmed source and destination ranges.

## Risks and edge cases
The high-risk cases are stale context fields, high/low address halves programmed in the wrong order, tensor stride/size mismatches, and writing `COMMIT` before all selected fields are valid. Compression/decompression, transpose, and dtype bits are compactly encoded and can corrupt data if masks are mismatched or if callers treat this generated file as self-describing behavior rather than address data.

## Test signals
Validation should include linear and tensor DMA copies, 64-bit source/destination addresses, compression and decompression paths when supported, write-completion generation, reset/reinitialize cycles, and error injection for invalid size/stride combinations. Useful debug evidence is matching DMA core status context ids, idle/busy transitions, and no HB/LB read/write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_kdma_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_kdma_cgm_regs.h

## Purpose
`arc_farm_kdma_kdma_cgm_regs.h` is the generated address map for the ARC farm KDMA clock-gating manager (`ARC_FARM_KDMA_KDMA_CGM`), prototype `QMAN_CGM`. It defines the three register addresses `CFG`, `STS`, and `CFG1` in the 0x4E8BE00-0x4E8BE08 range.

## Important APIs, types, and functions
The only API is three `mmARC_FARM_KDMA_KDMA_CGM_*` constants. `CFG` and `CFG1` are configuration entry points for clock-gating behavior; `STS` is the matching status readback register. Field definitions are not present in this file, so users must rely on the generated mask/spec companion or existing hardware programming sequences.

## Control flow
There is no software control flow. Initialization or power-management code writes clock-gating configuration, then may read `STS` to confirm the manager accepted or reflected the requested state. Reset paths should return these registers to the expected default before KDMA/QMAN work starts.

## State and persistence behavior
Clock-gating configuration is persistent hardware state until reset or reprogramming. A stale or invalid setting can make a block appear idle, gated, or unresponsive even if queue/DMA context registers are otherwise correctly programmed.

## Dependencies and integration points
This header integrates with KDMA/QMAN power-management setup and any common `QMAN_CGM` helper used across Gaudi2 blocks. It is adjacent to the ARC farm KDMA core and context banks and should be programmed in a sequence compatible with those blocks' enable/halt state.

## Risks and edge cases
The risk is low at compile time but high at runtime: there are only addresses, no field masks, so callers can write magic values with little local type safety. Bad clock-gating values can create intermittent hangs that look like queue or DMA bugs.

## Test signals
Test signals include KDMA initialization after cold boot and reset, clock-gating status readback, sustained DMA traffic with clock gating enabled, and no timeout when transitioning the block between idle and active states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_kdma_cgm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_masks.h

## Purpose
`arc_farm_kdma_masks.h` is the generated bitfield companion for the `ARC_FARM_KDMA` `DMA_CORE` register bank. It provides 258 shift/mask macros that describe how to build and decode configuration, traffic-limit, cache, error, status, debug, local-to-host, idle, and APB-control register values.

## Important APIs, types, and functions
The exported API is the macro namespace. Important fields include `CFG_0_EN`, `CFG_1_HALT/FLUSH`, protection value/error bits, clock-gating bits for HBW/LBW/TE paths, `RD_GLBL` force-miss and LB-via-HB controls, HB/LB read outstanding and size fields, HB/LB write outstanding and AWID fields, rate-limit timeout/saturation/enable fields, write-completion limits and AWUSER value, `ERR_CFG` error-message and stop-on-error bits, detailed `ERR_CAUSE` flags, `STS0` request counts and busy bit, `STS1_IS_HALT`, context snapshot selectors, LB ready/valid status bits, power/debug status fields, APB enabler disable, L2H compare/mask values, and `IDLE_IND_MASK`.

## Control flow
There is no code path inside the header. It is used anywhere software composes a DMA core register value or decodes a status/error read. Typical control flow is read-modify-write: mask out a field, shift a new value into place, and write through the matching address macro. Recovery code decodes `ERR_CAUSE`, status bits, and idle indications to decide whether to stop, flush, reset, or report an engine fault.

## State and persistence behavior
The macros describe persistent hardware configuration fields and transient status fields. Configuration writes survive until reset or explicit change; status, request counters, inflight counts, and debug fields evolve with DMA traffic. Because mask names encode semantics, they are part of the implicit ABI between generated register files and driver code even though no data is stored in the header.

## Dependencies and integration points
This header must match the sibling DMA core register-address header and the generated hardware specification for the same ASIC revision. It integrates with initialization code, error interrupt handling, reset flows, and any common helper that abstracts the `DMA_CORE` prototype across KDMA and EDMA instances.

## Risks and edge cases
Mismatched masks can be worse than missing definitions: a write may hit a valid register but set the wrong field. Other risks are unbounded field values being shifted without prior range checks, accidentally clearing adjacent status bits during read-modify-write, and using status masks on write-only or write-one-to-clear registers. Reserved fields should not be used as feature hooks without hardware confirmation.

## Test signals
Good test coverage includes static build coverage of all macro users, register write/readback smoke tests where hardware permits, DMA enable/halt/flush exercises, error injection for every named `ERR_CAUSE` bit, and debug reads showing expected busy/idle and context snapshot fields during active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_regs.h

## Purpose
`arc_farm_kdma_regs.h` is the generated address map for the `ARC_FARM_KDMA` DMA core control/status block in the `0x4E8B000-0x4E8BE34` range. It exposes 67 `mm...` constants for enabling, halting, flushing, protection, clock gating, HB/LB read and write limits, AXI cache attributes, inflight counters, error reporting, context status snapshots, debug counters, local-to-host filtering, idle indications, and APB enable controls.

## Important APIs, types, and functions
The header has no functions or types. Major register groups are `CFG_0/1`, `PROT`, `CKG`, `RD_GLBL`, HB/LB read max outstanding/size/arcache/inflight/rate-limit registers, HB/LB write max outstanding/AWID/AWCACHE/inflight/rate-limit registers, write-completion controls, `ERR_CFG`, `ERR_CAUSE`, error-message address/data registers, `STS0/STS1`, read/write context status selectors and snapshots, `PWRLP_*`, `DBG_*`, APB base/enabler registers, `E2E_CRED_ASYNC_CFG`, L2H compare/mask pairs, and `IDLE_IND_MASK`.

## Control flow
The file only defines addresses. Runtime code typically enables the core via `CFG_0`, tunes outstanding/rate/cache limits, programs error handling, submits contexts through the sibling context bank, polls `STS0.BUSY` and `STS1.IS_HALT`, and uses `CFG_1` halt/flush bits during teardown or reset. Debug flows read descriptor counts, buffer status, descriptor ids, and context snapshot registers selected by `STS_RD_CTX_SEL` or `STS_WR_CTX_SEL`.

## State and persistence behavior
All state is in the DMA hardware block. Configuration and error-message routing persist until reset or reprogramming; status and inflight counters change as DMA traffic progresses. `ERR_CAUSE` and debug/status registers provide latched or sampled state used by recovery paths, while halt/flush bits can block forward progress if left asserted.

## Dependencies and integration points
This address map integrates with the matching DMA core mask header, the context register bank for descriptor details, AXUSER programming, QMAN command submission, reset/recovery code, and device error interrupt handlers. It is one generated instance of the common `DMA_CORE` prototype, so consumers often share code across KDMA and EDMA blocks while substituting the base macro namespace.

## Risks and edge cases
Subtle bugs come from treating KDMA and EDMA instances as interchangeable while using the wrong base address, leaving halt/flush asserted, masking `ERR_CAUSE` bits unintentionally, or setting HB/LB outstanding and rate limits outside hardware expectations. The L2H compare/mask and APB enabler registers can affect address filtering and debug access, so stale values can create hard-to-debug traffic drops.

## Test signals
Test signals include successful engine enable/disable, DMA traffic under HB and LB paths, correct busy-to-idle transitions, recovery after halt/flush, populated debug descriptor counters during load, and expected interrupt/error-message behavior when HB/LB read/write faults or descriptor overflow are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/cpu_if_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/cpu_if_regs.h

## Purpose
`cpu_if_regs.h` is the generated Gaudi2 CPU interface register map, prototype `CPU_IF`. It exposes 377 `mmCPU_IF_*` address macros in the 0x4CC1104-0x4CC19D8 range for CPU-originated AXI attribute overrides, host/firmware queues, address MSB configuration, interrupt aggregation, ECC/error reporting, SPI/SEI/MSI-X routing, counters, and low-bandwidth termination diagnostics.

## Important APIs, types, and functions
The file exports constants only. Important groups include CPU AXUSER/AWCACHE/LOCK/PROT override and override-enable registers; max outstanding, early response, and force-response controls; CPU SEI status/clear/mask; write/read total and inflight counters; SRAM/CFG/HBM/PCIe MSB address registers; KMD dirty status; master-interface E2E controls; LBW terminate address/response diagnostics; PF persistent/completion/event queue base/length/init registers; per-engine SERR/DERR/SEI/SPI status-clear-mask sets for TPC, MME, HDMA, PDMA, SRAM, HBM, HMMU, DEC, NIC, sync manager, HIF, XBAR, PLL, and PCIe; and MSI-X busy/generation registers.

## Control flow
There is no executable code. Device initialization programs address-extension registers and queue base/length pairs, initializes CPU-visible queues with `QUEUE_INIT`, unmasks the interrupt classes it expects to handle, and configures AXI overrides if needed. Interrupt handling reads status registers, writes clear registers, and uses masks to suppress or enable classes. Recovery code reads termination/error address registers, dirty status, counters, and inflight counts to decide whether firmware, queues, or the whole device must be reset.

## State and persistence behavior
The CPU interface is a central persistent hardware state bank. Queue bases and lengths persist while firmware and kernel queues are active. Interrupt masks persist until explicitly changed, while status/clear registers expose latched event state. Address MSB and AXI override registers affect subsequent CPU interface transactions, so stale values can corrupt address interpretation or transaction security/cache attributes.

## Dependencies and integration points
This header integrates with Gaudi2 firmware boot, CPU-CP queue setup, interrupt controller programming, MSI-X generation, ECC/SPI/SEI error handling, and low-level register access code. Consumers also depend on queue layout definitions and device address-map constants outside this generated header.

## Risks and edge cases
The highest risks are interrupt status/clear/mask triplet drift, programming queue base high/low words inconsistently, leaving interrupt masks wrong after reset, and misconfiguring address-extension registers for SRAM/CFG/HBM/PCIe windows. Because many status sets are replicated by engine family and index, a table off-by-one can acknowledge or mask the wrong hardware source.

## Test signals
Validation should include firmware queue initialization, event queue delivery, MSI-X generation, ECC/SPI/SEI interrupt injection for multiple engine families, reset with mask restoration, queue base/length boundary tests, and diagnostics showing read/write inflight counters return to zero during idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/cpu_if_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_masks.h

## Purpose
`dcore0_dec0_cmd_masks.h` is the generated bitfield map for the DCORE0 decoder 0 command register bank, prototype `VSI_CMD`. It defines 144 shift/mask macros for software-visible decoder command/status registers `SWREG0` through `SWREG26` plus dummy registers `SWREG64` through `SWREG67`.

## Important APIs, types, and functions
The macro API covers version/id/builddate fields, normal and abnormal external interrupt source/gate fields, command-buffer execution count and address fields, AXI read/write total counters, work-state and AXI handshake status bits, start/reset/abort/clock-gate controls, IRQ cause and IRQ enable bits for end-command, bus error, timeout, command error, abort, and jump, timeout cycle/enable fields, command-buffer executable address/length/id fields, AXI read/write id and max burst controls, command swap bits, ready command-buffer count, and dummy scratch-style full-width fields.

## Control flow
This header has no logic. Decoder command code composes writes to the control and command-buffer registers, triggers execution with `SW_START_TRIGGER`, then polls or handles interrupts signaled through the IRQ and work-state fields. Reset and abort flows use the `SW_RESET_*` and `SW_ABORT_MODE` masks. Debug and performance paths decode AXI counters and handshake bits from the status registers.

## State and persistence behavior
The masks describe hardware registers whose values persist until cleared, overwritten, or reset. IRQ cause bits are latched hardware state, command-buffer address/length/id are active execution state, and AXI counters/handshake bits reflect live decoder traffic. Timeout and IRQ-enable settings persist across commands unless reprogrammed.

## Dependencies and integration points
This file is tied to `dcore0_dec0_cmd_regs.h`, decoder firmware/driver command submission, interrupt handling, and any video/scaler decoder command-buffer ABI used by the Gaudi2 stack. It is generated from the same `VSI_CMD` prototype used for similar decoder command blocks.

## Risks and edge cases
Risks include write-one-to-clear or latched IRQ fields being manipulated with ordinary read-modify-write code, command-buffer high/low address or length mismatch, starting execution before AXI ids/burst/swap fields are valid, and treating dummy/reserved fields as portable configuration.

## Test signals
Test signals include decoder command execution, end-command interrupt delivery, timeout/bus-error/command-error injection, reset and abort behavior, AXI counter movement during command execution, and no stuck work-state after repeated command buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_regs.h

## Purpose
`dcore0_dec0_cmd_regs.h` is the generated address map for DCORE0 decoder 0 command registers, prototype `VSI_CMD`. It defines 31 `mmDCORE0_DEC0_CMD_SWREG*` addresses in the 0x41E0000-0x41E010C range for command submission, status, interrupt, timeout, AXI accounting, and dummy/scratch registers.

## Important APIs, types, and functions
There are no functions or types. The address constants cover contiguous `SWREG0` through `SWREG26` at 4-byte spacing and a second group `SWREG64` through `SWREG67`. Semantics are supplied by `dcore0_dec0_cmd_masks.h`: version/id, build date, interrupt sources, command execution address/length/id, command counters, AXI counters and handshakes, start/reset/abort controls, IRQ causes/enables, timeout, AXI id/burst/swap, and dummy fields.

## Control flow
Runtime code writes command-buffer address and control registers, starts execution through `SWREG16`, then waits by polling work/IRQ state or by handling interrupt status in `SWREG17`. Reset and abort paths also target this register window. The header itself only supplies the physical offsets used by those flows.

## State and persistence behavior
State is in the decoder command hardware. Command setup registers persist between commands, IRQ/status fields reflect latched or live decoder state, and dummy registers may persist as hardware scratch if used. Correct reset/init code should not assume power-on defaults after a soft reset unless the decoder block was actually reset.

## Dependencies and integration points
This file integrates directly with `dcore0_dec0_cmd_masks.h`, decoder command-buffer generation, interrupt handling, reset/recovery code, and any debug tooling that reads decoder command status.

## Risks and edge cases
Address mistakes in this header would redirect decoder control to unrelated DCORE registers. More realistically, callers can pair these addresses with stale or mismatched masks, write start/reset bits in the wrong order, or forget to clear/mask IRQ sources before submitting a new command.

## Test signals
Useful validation includes command-buffer execution, repeated start/reset cycles, interrupt status/clear behavior, timeout programming, AXI counter sanity under load, and register dump comparison against expected DCORE0 decoder address ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_ctx_axuser_regs.h

## Purpose
`dcore0_edma0_core_ctx_axuser_regs.h` is an auto-generated Gaudi2 register-address header for the `DCORE0_EDMA0_CORE_CTX_AXUSER` AXUSER register bank. It exposes 19 `mm...` address macros in the `0x41CB800-0x41CB84C` region for programming AXI user attributes on high-bandwidth (HB) and low-bandwidth (LB) DMA or queue-manager traffic. This is the EDMA0 core context AXUSER bank for DCORE0.

## Important APIs, types, and functions
The file exports preprocessor constants only; there are no C types or functions. The important register groups are `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, HB write/read override low/high pairs, and the LB `COORD`, `LOCK`, `RSVD`, and `OVRD` registers. These addresses pair with AXUSER mask headers that define write/read ASID fields, MMU-bypass bits, cache/snoop controls, reduction/atomic encodings, QOS, coordinate routing, and override payload masks.

## Control flow
The header has no runtime control flow. Its constants are consumed by Gaudi2 initialization, queue setup, DMA context programming, firmware bring-up, and debug/error paths that issue `WREG32`/`RREG32` accesses. Typical sequencing is to program ASID and MMU bypass attributes before enabling or committing DMA/QMAN work, then leave the values resident while the corresponding queue or DMA context issues AXI transactions.

## State and persistence behavior
State is purely hardware-resident. Values written through these macros persist in the AXUSER register bank until reset or reprogramming, and they affect subsequent bus transactions from the associated block. The split HB/LB and read/write override registers mean stale values can survive across contexts if reset/init code does not explicitly reinitialize the bank.

## Dependencies and integration points
This generated header integrates with `gaudi2/asic_reg/*_axuser_masks.h`, common HabanaLabs register accessors, and Gaudi2 queue/DMA initialization code. It has no include dependencies beyond its guard. Its address base must stay synchronized with generated block base maps and with any driver tables that select EDMA, KDMA, or QMAN AXUSER windows by engine id.

## Risks and edge cases
The main risk is programming the right field at the wrong engine's AXUSER base, which can silently change ASID, MMU bypass, snoop, QOS, or security attributes for unrelated traffic. Nonsecured QMAN banks are especially sensitive because their name encodes the security domain. Register layout drift between the address header and mask header can also produce correct-looking writes to semantically wrong fields.

## Test signals
Useful signals are successful Gaudi2 probe/reset with MMU enabled, DMA or QMAN traffic using expected ASIDs, no RAZWI/protection errors after AXUSER programming, and queue stress that exercises host, HBM, and LB paths. Negative signals include access faults, unexpected secure/nonsecure violations, bad QOS behavior, or device traffic observed with stale ASID/MMU-bypass attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_ctx_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_ctx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_ctx_regs.h

## Purpose
`dcore0_edma0_core_ctx_regs.h` is the generated address map for the `DCORE0_EDMA0_CORE_CTX` DMA context register bank in the `0x41CB860-0x41CB8EC` range. It defines 36 context registers for rate limiting, power behavior, tensor/linear DMA dimensions, strides, source/destination bases and offsets, write-completion metadata, and the final context commit trigger.

## Important APIs, types, and functions
The file exports `mm...` constants only. Key programming registers are `RATE_LIM_TKN`, `PWRLP`, `TE_NUMROWS`, `IDX`, `IDX_INC`, `CTRL`, source `TSIZE` and `STRIDE` registers for dimensions 0-4, destination `TSIZE` and `STRIDE` registers, `WR_COMP_ADDR_HI/LO`, `WR_COMP_WDATA`, `SRC_OFFSET`, `DST_OFFSET`, `SRC_BASE`, `DST_BASE`, `DST_TSIZE_0`, and `COMMIT`. These addresses pair with the corresponding `*_CTX_MASKS_H_` header, where `CTRL` selects transpose, dtype, compression/decompression, and read-uncacheable behavior and `COMMIT` selects which context fields are latched.

## Control flow
There is no executable code. Driver or firmware code writes a context in dependency order: set rate/power and index controls, program tensor sizes and strides, install source and destination address components, optionally configure write-completion data, and finally write `COMMIT` to latch the descriptor into the DMA engine. Status/error observation happens through the sibling DMA core register bank rather than this context map.

## State and persistence behavior
The programmed context is hardware state. It persists until overwritten, reset, or superseded by a later commit. Because the commit register can selectively source stride/offset/base values, partial context updates can intentionally reuse earlier fields; the same behavior is risky if software assumes a clean context after reset without actually initializing every relevant field.

## Dependencies and integration points
This header integrates with the matching DMA context mask header, the associated DMA core address/mask headers, Gaudi2 queue command generation, and firmware routines that prepare DMA descriptors. The register sequence also depends on AXUSER context programming when ASID, MMU bypass, or snoop attributes must match the programmed source and destination ranges.

## Risks and edge cases
The high-risk cases are stale context fields, high/low address halves programmed in the wrong order, tensor stride/size mismatches, and writing `COMMIT` before all selected fields are valid. Compression/decompression, transpose, and dtype bits are compactly encoded and can corrupt data if masks are mismatched or if callers treat this generated file as self-describing behavior rather than address data.

## Test signals
Validation should include linear and tensor DMA copies, 64-bit source/destination addresses, compression and decompression paths when supported, write-completion generation, reset/reinitialize cycles, and error injection for invalid size/stride combinations. Useful debug evidence is matching DMA core status context ids, idle/busy transitions, and no HB/LB read/write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_ctx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_masks.h

## Purpose
`dcore0_edma0_core_masks.h` is the generated bitfield companion for the `DCORE0_EDMA0_CORE` `DMA_CORE` register bank. It provides 258 shift/mask macros that describe how to build and decode configuration, traffic-limit, cache, error, status, debug, local-to-host, idle, and APB-control register values.

## Important APIs, types, and functions
The exported API is the macro namespace. Important fields include `CFG_0_EN`, `CFG_1_HALT/FLUSH`, protection value/error bits, clock-gating bits for HBW/LBW/TE paths, `RD_GLBL` force-miss and LB-via-HB controls, HB/LB read outstanding and size fields, HB/LB write outstanding and AWID fields, rate-limit timeout/saturation/enable fields, write-completion limits and AWUSER value, `ERR_CFG` error-message and stop-on-error bits, detailed `ERR_CAUSE` flags, `STS0` request counts and busy bit, `STS1_IS_HALT`, context snapshot selectors, LB ready/valid status bits, power/debug status fields, APB enabler disable, L2H compare/mask values, and `IDLE_IND_MASK`.

## Control flow
There is no code path inside the header. It is used anywhere software composes a DMA core register value or decodes a status/error read. Typical control flow is read-modify-write: mask out a field, shift a new value into place, and write through the matching address macro. Recovery code decodes `ERR_CAUSE`, status bits, and idle indications to decide whether to stop, flush, reset, or report an engine fault.

## State and persistence behavior
The macros describe persistent hardware configuration fields and transient status fields. Configuration writes survive until reset or explicit change; status, request counters, inflight counts, and debug fields evolve with DMA traffic. Because mask names encode semantics, they are part of the implicit ABI between generated register files and driver code even though no data is stored in the header.

## Dependencies and integration points
This header must match the sibling DMA core register-address header and the generated hardware specification for the same ASIC revision. It integrates with initialization code, error interrupt handling, reset flows, and any common helper that abstracts the `DMA_CORE` prototype across KDMA and EDMA instances.

## Risks and edge cases
Mismatched masks can be worse than missing definitions: a write may hit a valid register but set the wrong field. Other risks are unbounded field values being shifted without prior range checks, accidentally clearing adjacent status bits during read-modify-write, and using status masks on write-only or write-one-to-clear registers. Reserved fields should not be used as feature hooks without hardware confirmation.

## Test signals
Good test coverage includes static build coverage of all macro users, register write/readback smoke tests where hardware permits, DMA enable/halt/flush exercises, error injection for every named `ERR_CAUSE` bit, and debug reads showing expected busy/idle and context snapshot fields during active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_regs.h

## Purpose
`dcore0_edma0_core_regs.h` is the generated address map for the `DCORE0_EDMA0_CORE` DMA core control/status block in the `0x41CB000-0x41CBE34` range. It exposes 67 `mm...` constants for enabling, halting, flushing, protection, clock gating, HB/LB read and write limits, AXI cache attributes, inflight counters, error reporting, context status snapshots, debug counters, local-to-host filtering, idle indications, and APB enable controls.

## Important APIs, types, and functions
The header has no functions or types. Major register groups are `CFG_0/1`, `PROT`, `CKG`, `RD_GLBL`, HB/LB read max outstanding/size/arcache/inflight/rate-limit registers, HB/LB write max outstanding/AWID/AWCACHE/inflight/rate-limit registers, write-completion controls, `ERR_CFG`, `ERR_CAUSE`, error-message address/data registers, `STS0/STS1`, read/write context status selectors and snapshots, `PWRLP_*`, `DBG_*`, APB base/enabler registers, `E2E_CRED_ASYNC_CFG`, L2H compare/mask pairs, and `IDLE_IND_MASK`.

## Control flow
The file only defines addresses. Runtime code typically enables the core via `CFG_0`, tunes outstanding/rate/cache limits, programs error handling, submits contexts through the sibling context bank, polls `STS0.BUSY` and `STS1.IS_HALT`, and uses `CFG_1` halt/flush bits during teardown or reset. Debug flows read descriptor counts, buffer status, descriptor ids, and context snapshot registers selected by `STS_RD_CTX_SEL` or `STS_WR_CTX_SEL`.

## State and persistence behavior
All state is in the DMA hardware block. Configuration and error-message routing persist until reset or reprogramming; status and inflight counters change as DMA traffic progresses. `ERR_CAUSE` and debug/status registers provide latched or sampled state used by recovery paths, while halt/flush bits can block forward progress if left asserted.

## Dependencies and integration points
This address map integrates with the matching DMA core mask header, the context register bank for descriptor details, AXUSER programming, QMAN command submission, reset/recovery code, and device error interrupt handlers. It is one generated instance of the common `DMA_CORE` prototype, so consumers often share code across KDMA and EDMA blocks while substituting the base macro namespace.

## Risks and edge cases
Subtle bugs come from treating KDMA and EDMA instances as interchangeable while using the wrong base address, leaving halt/flush asserted, masking `ERR_CAUSE` bits unintentionally, or setting HB/LB outstanding and rate limits outside hardware expectations. The L2H compare/mask and APB enabler registers can affect address filtering and debug access, so stale values can create hard-to-debug traffic drops.

## Test signals
Test signals include successful engine enable/disable, DMA traffic under HB and LB paths, correct busy-to-idle transitions, recovery after halt/flush, populated debug descriptor counters during load, and expected interrupt/error-message behavior when HB/LB read/write faults or descriptor overflow are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_arc_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_arc_aux_regs.h

## Purpose
`dcore0_edma0_qm_arc_aux_regs.h` is the generated address map for the DCORE0 EDMA0 QMAN ARC auxiliary block, prototype `QMAN_ARC_AUX`. It defines 284 register addresses in the 0x41C8100-0x41C8920 range for ARC run/halt/reset/debug control, address-window setup, context ids, software interrupts, SEI/REI/ECC reporting, termination diagnostics, scratchpads, traffic counters, AXI override attributes, ordering, and engine-access controls.

## Important APIs, types, and functions
The exported API is `mmDCORE0_EDMA0_QM_ARC_AUX_*` constants. Major groups include `RUN_HALT_REQ/ACK`, reset vector and debug mode, cluster/ARC ids, wake event, DCCM system base, CTI mux/status, ARC reset request/status, SRAM/PCIe/CFG/HBM base and offset registers, seven general-purpose base pairs, CBU/LBU cache override registers, 8 context ids and CID offsets, 16 software interrupt registers, IRQ interrupt masks, ARC SEI status/clear/mask/cause/halt masks, ARC REI status/clear/mask, DCCM/I-cache/D-cache ECC address/syndrome registers, LBW terminate diagnostics, scratchpads, CBU/LBU total and inflight counters, AR/AWUSER and cache/prot overrides, ordering masks/addresses, and upper DCCM enable.

## Control flow
This header is address data only. Bring-up code programs address windows and reset vectors, releases or halts the ARC, and configures interrupt masks. Firmware and driver-side debug can use software interrupts and scratchpads for handshakes. Error paths read SEI/REI/ECC and termination diagnostics, clear latched causes, and may halt ARC execution depending on halt-mask configuration.

## State and persistence behavior
The ARC auxiliary bank contains long-lived firmware execution state and debug/error state. Reset vector, base address windows, context ids, interrupt masks, cache/prot/user overrides, and ordering controls persist while the QMAN ARC runs. Scratchpads and counters persist as diagnostic state. ECC and interrupt status are latched until cleared.

## Dependencies and integration points
This register map integrates with EDMA0 QMAN firmware boot, ARC control paths, interrupt/error handling, Gaudi2 address-window setup, and queue-manager recovery. It also connects to CTI/CoreSight-style debug paths and to the main EDMA0 QMAN register block, which may report ARC-related queue errors.

## Risks and edge cases
High-risk areas are ARC halt/reset sequencing, wrong base MSB/LSB setup for SRAM/PCIe/CFG/HBM windows, stale context ids, interrupt-mask mistakes that hide ECC or exception causes, and clearing latched diagnostics before software captures them. Because this header has addresses only, field semantics must come from hardware docs or matching mask headers elsewhere.

## Test signals
Validation includes ARC firmware boot/halt/reset, software interrupt delivery, scratchpad handshake, ECC/SEI/REI injection, LBW termination diagnostics, address-window access tests, and counter behavior showing CBU/LBU traffic drains during idle/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_arc_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_axuser_nonsecured_regs.h

## Purpose
`dcore0_edma0_qm_axuser_nonsecured_regs.h` is an auto-generated Gaudi2 register-address header for the `DCORE0_EDMA0_QM_AXUSER_NONSECURED` AXUSER register bank. It exposes 19 `mm...` address macros in the `0x41CAB80-0x41CABCC` region for programming AXI user attributes on high-bandwidth (HB) and low-bandwidth (LB) DMA or queue-manager traffic. The `NONSECURED` namespace marks this as the non-secure AXUSER bank for EDMA0 QMAN traffic.

## Important APIs, types, and functions
The file exports preprocessor constants only; there are no C types or functions. The important register groups are `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, HB write/read override low/high pairs, and the LB `COORD`, `LOCK`, `RSVD`, and `OVRD` registers. These addresses pair with AXUSER mask headers that define write/read ASID fields, MMU-bypass bits, cache/snoop controls, reduction/atomic encodings, QOS, coordinate routing, and override payload masks.

## Control flow
The header has no runtime control flow. Its constants are consumed by Gaudi2 initialization, queue setup, DMA context programming, firmware bring-up, and debug/error paths that issue `WREG32`/`RREG32` accesses. Typical sequencing is to program ASID and MMU bypass attributes before enabling or committing DMA/QMAN work, then leave the values resident while the corresponding queue or DMA context issues AXI transactions.

## State and persistence behavior
State is purely hardware-resident. Values written through these macros persist in the AXUSER register bank until reset or reprogramming, and they affect subsequent bus transactions from the associated block. The split HB/LB and read/write override registers mean stale values can survive across contexts if reset/init code does not explicitly reinitialize the bank.

## Dependencies and integration points
This generated header integrates with `gaudi2/asic_reg/*_axuser_masks.h`, common HabanaLabs register accessors, and Gaudi2 queue/DMA initialization code. It has no include dependencies beyond its guard. Its address base must stay synchronized with generated block base maps and with any driver tables that select EDMA, KDMA, or QMAN AXUSER windows by engine id.

## Risks and edge cases
The main risk is programming the right field at the wrong engine's AXUSER base, which can silently change ASID, MMU bypass, snoop, QOS, or security attributes for unrelated traffic. Nonsecured QMAN banks are especially sensitive because their name encodes the security domain. Register layout drift between the address header and mask header can also produce correct-looking writes to semantically wrong fields.

## Test signals
Useful signals are successful Gaudi2 probe/reset with MMU enabled, DMA or QMAN traffic using expected ASIDs, no RAZWI/protection errors after AXUSER programming, and queue stress that exercises host, HBM, and LB paths. Negative signals include access faults, unexpected secure/nonsecure violations, bad QOS behavior, or device traffic observed with stale ASID/MMU-bypass attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_cgm_regs.h

## Purpose
`dcore0_edma0_qm_cgm_regs.h` is the generated address map for the DCORE0 EDMA0 QMAN clock-gating manager, prototype `QMAN_CGM`. It defines `CFG`, `STS`, and `CFG1` register addresses in the 0x41CAD80-0x41CAD88 range.

## Important APIs, types, and functions
The file exports only `mmDCORE0_EDMA0_QM_CGM_CFG`, `mmDCORE0_EDMA0_QM_CGM_STS`, and `mmDCORE0_EDMA0_QM_CGM_CFG1`. These are the QMAN clock-gating control and status entry points; field masks are not present in this file.

## Control flow
Initialization or power-management code writes configuration before or after QMAN enable according to the hardware sequence and can read `STS` for state. Recovery code should return the CGM state to known defaults before restarting the EDMA0 QMAN.

## State and persistence behavior
The registers hold persistent clock/power configuration and live status. Bad state can manifest as QMAN idleness, missed progress, or reset timeouts rather than obvious register-access failure.

## Dependencies and integration points
This file integrates with the EDMA0 QMAN register block, ARC auxiliary block, and any common Gaudi2 `QMAN_CGM` programming helper. Its address base must remain aligned with generated DCORE0 EDMA0 block placement.

## Risks and edge cases
The primary risk is writing undocumented magic values or sequencing clock gating while queue pipes are active. Since the header lacks masks, consumers need external field definitions and must avoid assuming KDMA and EDMA CGM values are always interchangeable.

## Test signals
Tests should cover boot, reset, idle-to-active transitions, queue traffic with clock gating enabled, and status readbacks during power-management transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_cgm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_masks.h

## Purpose
`dcore0_edma0_qm_masks.h` is the generated bitfield map for the DCORE0 EDMA0 queue manager, prototype `QMAN`. It defines 766 shift/mask macros for global queue enable/stop/flush, error reporting, AXI attributes, PQ/CQ/CP programming, completion queues, fences, arbiters, ARC completion queue, address overrides, secure push controls, SEI, local-to-host filtering, rate limiting, indirect APB access, and performance counters.

## Important APIs, types, and functions
The macro surface covers global `PQF`, `CQF`, `CP`, and `ARC_CQF` enable/stop/flush fields; error config/status/message-enable fields including CP undefined command, stop-op, message write, WREG, fence overflow/underflow, CPDMA overflow, CQ CI errors, ARC CQ errors, ARC AXI error, and CP switch watchdog; protection and AXCACHE fields; PQ and CQ base/size/producer/consumer fields; CP message bases, fence controls/counts/data, barrier and LDMA offsets, status/current instruction/predicate/debug/credit/input data fields; PQC HBW/LBW bases, size, PI, config, secure push, and status; arbiter masks, weights, master credits, choice push offsets, slave enables, watchdog/id/quiet/max-inflight/base/state/error fields; ARC CQ config/pointers/status/message bases; CQ CI registers; CP config/switch watchdog; engine/QM/ARC base/range registers; SEI status/mask; global error address/data; L2H compare/mask; local range; rate limit; indirect gateway; and free/idle performance counter fields.

## Control flow
This header has no executable control flow, but it describes the control surface for EDMA0 queue execution. Initialization composes global enable values, programs queue bases/sizes/PIs, configures CP and arbiter policy, enables error reporting, sets AXI/cache/protection attributes, and then permits packet submission. Runtime submission updates producer indexes and relies on CP/CQ/fence machinery. Recovery paths stop/flush PQF/CQF/CP/ARC_CQF, decode error/status fields, drain arbiters, and reset or reinitialize affected queues.

## State and persistence behavior
The QMAN holds extensive persistent hardware state: queue bases and sizes, producer/consumer indices, fence counters, arbiter credits and policy, ARC CQ pointers, CP current instruction/predicate state, secure-push controls, error masks, and performance counter configuration. Status and counters evolve with traffic. Partial reset or incomplete teardown can leave stale queue pointers or credits that corrupt later submissions.

## Dependencies and integration points
This mask header is coupled to `dcore0_edma0_qm_regs.h`, EDMA0 QMAN firmware/driver setup, packet submission, interrupt/error handling, ARC auxiliary control, AXUSER programming, and completion queue handling. It represents one generated `QMAN` prototype instance, so common QMAN code may reuse logic across engines with different macro prefixes.

## Risks and edge cases
Risks include off-by-one queue index handling across 4 PQF, 5 CQF/CP-style lanes, and the ARC CQ path; using read/clear/status masks on wrong register variants; masking serious CP or ARC errors; programming queue base high/low words inconsistently; secure-push misconfiguration; and treating arbiter credit state as stateless after reset. Because many fields repeat by lane, copy/paste mistakes are likely.

## Test signals
Strong validation includes queue bring-up, packet submission/completion, CP fence overflow/underflow injection, CP undefined-command handling, CQ CI error handling, ARC CQ traffic, arbiter fairness/credit behavior, secure and nonsecure push cases, stop/flush recovery, SEI interrupt paths, and free/idle performance counters matching observed activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_regs.h

## Purpose
`dcore0_edma0_qm_regs.h` is the generated address map for the DCORE0 EDMA0 queue manager, prototype `QMAN`. It defines 517 register addresses in the 0x41CA000-0x41CAD70 range for global queue control, queue memory bases, CP/fence state, PQC, arbiters, ARC completion queues, completion queue CIs, address override/base windows, secure push, error routing, rate limits, indirect APB access, and performance counters.

## Important APIs, types, and functions
The file exports `mmDCORE0_EDMA0_QM_*` constants only. Register groups match the sibling mask header: `GLBL_*`, `PQ_BASE_*`, `PQ_SIZE`, `PQ_PI`, `CQ_*`, `CP_*`, `PQC_*`, `ARB_*`, `CSMR_STRICT_PRIO_CFG`, `ARC_CQ_*`, CQ IFIFO/CTL message bases and CI registers, `ADDR_OVRD`, `CP_CFG` and switch watchdogs, ARC and engine base/range registers, secure-push indicators, PQC status, SEI status/mask, global error address/data, L2H filters, local range, HBW/LBW rate-limit registers, indirect gateway APB registers, and free/idle performance counters.

## Control flow
The header supplies addresses for QMAN lifecycle code. Bring-up writes global config, queue base/size/PI registers, completion queue and CP parameters, arbiter policy, AXI/error settings, and base/range windows. Runtime command submission advances producer indices, while completion and interrupt paths read CQ/CP/fence/status registers. Recovery writes stop/flush bits, reads errors and current instruction state, drains arbiters, and reinitializes queues before re-enabling work.

## State and persistence behavior
Most registers represent persistent queue-manager state. Queue bases, indices, CP state, fence counters, arbiter credits, ARC CQ pointers, error configuration, and secure/local range settings can outlive a single command buffer and must be reset or rewritten during recovery. Some status/error registers are latched diagnostic state that should be captured before clearing.

## Dependencies and integration points
This file is inseparable from `dcore0_edma0_qm_masks.h`, EDMA0 queue setup, ARC auxiliary registers, EDMA0 core/context registers, AXUSER nonsecure attributes, and interrupt/error paths. Hardware register accessors use these absolute generated addresses to program the queue manager.

## Risks and edge cases
The biggest risks are lane count assumptions, stale queue pointers after reset, high/low base address mismatch, wrong pairing with mask macros, and failing to stop/flush all relevant PQF/CQF/CP/ARC_CQF components before reset. Arbiter credit and secure-push state are easy to miss in recovery.

## Test signals
Test signals include successful EDMA0 queue creation, command packet execution, completion delivery, fence operations, ARC CQ activity, arbiter fairness, secure push behavior, stop/flush/reset recovery, SEI/error interrupt injection, and performance counters that distinguish idle and active periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_core_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_core_ctx_axuser_regs.h

## Purpose
`dcore0_edma1_core_ctx_axuser_regs.h` is an auto-generated Gaudi2 register-address header for the `DCORE0_EDMA1_CORE_CTX_AXUSER` AXUSER register bank. It exposes 19 `mm...` address macros in the `0x41DB800-0x41DB84C` region for programming AXI user attributes on high-bandwidth (HB) and low-bandwidth (LB) DMA or queue-manager traffic. It is the same AXUSER prototype as EDMA0 core context but at the EDMA1 DCORE0 base.

## Important APIs, types, and functions
The file exports preprocessor constants only; there are no C types or functions. The important register groups are `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, HB write/read override low/high pairs, and the LB `COORD`, `LOCK`, `RSVD`, and `OVRD` registers. These addresses pair with AXUSER mask headers that define write/read ASID fields, MMU-bypass bits, cache/snoop controls, reduction/atomic encodings, QOS, coordinate routing, and override payload masks.

## Control flow
The header has no runtime control flow. Its constants are consumed by Gaudi2 initialization, queue setup, DMA context programming, firmware bring-up, and debug/error paths that issue `WREG32`/`RREG32` accesses. Typical sequencing is to program ASID and MMU bypass attributes before enabling or committing DMA/QMAN work, then leave the values resident while the corresponding queue or DMA context issues AXI transactions.

## State and persistence behavior
State is purely hardware-resident. Values written through these macros persist in the AXUSER register bank until reset or reprogramming, and they affect subsequent bus transactions from the associated block. The split HB/LB and read/write override registers mean stale values can survive across contexts if reset/init code does not explicitly reinitialize the bank.

## Dependencies and integration points
This generated header integrates with `gaudi2/asic_reg/*_axuser_masks.h`, common HabanaLabs register accessors, and Gaudi2 queue/DMA initialization code. It has no include dependencies beyond its guard. Its address base must stay synchronized with generated block base maps and with any driver tables that select EDMA, KDMA, or QMAN AXUSER windows by engine id.

## Risks and edge cases
The main risk is programming the right field at the wrong engine's AXUSER base, which can silently change ASID, MMU bypass, snoop, QOS, or security attributes for unrelated traffic. Nonsecured QMAN banks are especially sensitive because their name encodes the security domain. Register layout drift between the address header and mask header can also produce correct-looking writes to semantically wrong fields.

## Test signals
Useful signals are successful Gaudi2 probe/reset with MMU enabled, DMA or QMAN traffic using expected ASIDs, no RAZWI/protection errors after AXUSER programming, and queue stress that exercises host, HBM, and LB paths. Negative signals include access faults, unexpected secure/nonsecure violations, bad QOS behavior, or device traffic observed with stale ASID/MMU-bypass attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_core_ctx_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_qm_axuser_nonsecured_regs.h

## Purpose
`dcore0_edma1_qm_axuser_nonsecured_regs.h` is an auto-generated Gaudi2 register-address header for the `DCORE0_EDMA1_QM_AXUSER_NONSECURED` AXUSER register bank. It exposes 19 `mm...` address macros in the `0x41DAB80-0x41DABCC` region for programming AXI user attributes on high-bandwidth (HB) and low-bandwidth (LB) DMA or queue-manager traffic. This is the non-secure AXUSER bank for EDMA1 QMAN traffic.

## Important APIs, types, and functions
The file exports preprocessor constants only; there are no C types or functions. The important register groups are `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, HB write/read override low/high pairs, and the LB `COORD`, `LOCK`, `RSVD`, and `OVRD` registers. These addresses pair with AXUSER mask headers that define write/read ASID fields, MMU-bypass bits, cache/snoop controls, reduction/atomic encodings, QOS, coordinate routing, and override payload masks.

## Control flow
The header has no runtime control flow. Its constants are consumed by Gaudi2 initialization, queue setup, DMA context programming, firmware bring-up, and debug/error paths that issue `WREG32`/`RREG32` accesses. Typical sequencing is to program ASID and MMU bypass attributes before enabling or committing DMA/QMAN work, then leave the values resident while the corresponding queue or DMA context issues AXI transactions.

## State and persistence behavior
State is purely hardware-resident. Values written through these macros persist in the AXUSER register bank until reset or reprogramming, and they affect subsequent bus transactions from the associated block. The split HB/LB and read/write override registers mean stale values can survive across contexts if reset/init code does not explicitly reinitialize the bank.

## Dependencies and integration points
This generated header integrates with `gaudi2/asic_reg/*_axuser_masks.h`, common HabanaLabs register accessors, and Gaudi2 queue/DMA initialization code. It has no include dependencies beyond its guard. Its address base must stay synchronized with generated block base maps and with any driver tables that select EDMA, KDMA, or QMAN AXUSER windows by engine id.

## Risks and edge cases
The main risk is programming the right field at the wrong engine's AXUSER base, which can silently change ASID, MMU bypass, snoop, QOS, or security attributes for unrelated traffic. Nonsecured QMAN banks are especially sensitive because their name encodes the security domain. Register layout drift between the address header and mask header can also produce correct-looking writes to semantically wrong fields.

## Test signals
Useful signals are successful Gaudi2 probe/reset with MMU enabled, DMA or QMAN traffic using expected ASIDs, no RAZWI/protection errors after AXUSER programming, and queue stress that exercises host, HBM, and LB paths. Negative signals include access faults, unexpected secure/nonsecure violations, bad QOS behavior, or device traffic observed with stale ASID/MMU-bypass attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_masks.h

## Purpose
`dcore0_hmmu0_mmu_masks.h` is the generated bitfield map for the DCORE0 HMMU0 MMU register bank. It defines 164 shift/mask macros for enabling/bypassing the MMU, ordering, feature controls, address-range protection, page/access fault capture, interrupts, memory initialization, credits, static page-size configuration, illegal-address/RAZWI capture, and source id reporting.

## Important APIs, types, and functions
Important fields include `MMU_ENABLE`, weak-ordering control, feature enables for translation/page-fault/access-error behavior, VA ordering masks, DDR size, scrambler, memory-init busy bits, SPI/SEI cause and mask fields, page-error and access-error capture plus valid bits, interrupt clear/mask bits for page faults, access errors, multi-hit, security violations, and RAZWI, bypass control, static multi-page-size bits, core separate cache range/slice credits, page/access id low/high fields, DDR range enable, 8 secure min/max 64-bit range pairs, 8 privileged min/max 64-bit range pairs, illegal read/write address capture, RAZWI valid/id/address fields, and MMU source count.

## Control flow
The header is not executable. MMU initialization uses these masks to program translation enable, page-size/static features, ordering, DDR range protection, security/privilege ranges, and interrupt masks. Fault handling decodes capture and valid bits, reports page/access/RAZWI/security errors, clears interrupt/cause registers, and may trigger device reset depending on severity.

## State and persistence behavior
The macros describe persistent MMU configuration and latched fault state. Enable/bypass, feature, range, ordering, credit, and interrupt-mask fields persist across all translations until reset or reprogramming. Fault address/id/cause fields persist until cleared and are crucial for diagnosing illegal memory access.

## Dependencies and integration points
This file integrates with `dcore0_hmmu0_mmu_regs.h`, Gaudi2 MMU initialization, page-table setup, security/privilege range programming, fault interrupt handlers, and STLB/cache invalidation code. It must match the address header and the HMMU/STLB hardware spec for the same ASIC revision.

## Risks and edge cases
Risks include enabling translation before ranges and page tables are valid, clearing fault capture before logging it, programming secure/privileged range halves inconsistently, using bypass during user traffic, and misinterpreting RAZWI/access/page fault id widths. Range arrays are repeated and vulnerable to index drift.

## Test signals
Test signals include MMU enable/disable, mapped and unmapped memory access, secure and privileged range violations, page fault and access error injection, RAZWI capture, interrupt clear/mask behavior, and reset paths that restore all protection ranges and feature bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_regs.h

## Purpose
`dcore0_hmmu0_mmu_regs.h` is the generated address map for the DCORE0 HMMU0 MMU control bank. It defines 107 `mmDCORE0_HMMU0_MMU_*` addresses in the 0x408000C-0x4080324 range for MMU enable/features, ordering, fault capture, interrupts, bypass, page-size and credit setup, secure/privileged DDR ranges, illegal address capture, RAZWI capture, and source-count reporting.

## Important APIs, types, and functions
The file exports address constants only. Core registers include `MMU_ENABLE`, `FORCE_ORDERING`, `FEATURE_ENABLE`, VA ordering masks, `LOG2_DDR_SIZE`, `SCRAMBLER`, `MEM_INIT_BUSY`, `SPI_SEI_MASK/CAUSE`, page and access error capture/address/valid registers, interrupt clear/mask, debug memory wrap, SPI cause clear, pipe credit, bypass, static multi-page size, separate-cache controls, total slice credit, fault/access id registers, DDR range enable, 8 secure min/max 64-bit range pairs, 8 privileged min/max 64-bit range pairs, illegal read/write address pairs, RAZWI valid/id/address registers, and `MMU_SRC_NUM`.

## Control flow
There is no logic in the header. Initialization writes range and feature registers before enabling translation. Runtime fault handling reads capture/id/address registers, decodes them using the mask header, clears interrupts, and may reconfigure or reset the MMU. Debug and recovery code read busy, credit, and source-count registers to decide whether the MMU can be safely reprogrammed.

## State and persistence behavior
The MMU bank stores critical persistent translation and protection state. Translation enable, bypass, ranges, features, credits, and masks affect all downstream memory access until changed. Error captures are latched diagnostics that must be consumed before clear/reset.

## Dependencies and integration points
This address map integrates with `dcore0_hmmu0_mmu_masks.h`, STLB programming, page-table management, device memory allocation, security setup, and interrupt/error handling in the Gaudi2 driver.

## Risks and edge cases
The largest risks are using the wrong DCORE/HMMU instance address, enabling bypass accidentally, programming only one half of a 64-bit range/address, and clearing latched MMU faults before the driver records VA/source/id details. Generated address drift would break memory protection in ways that may surface as unrelated engine faults.

## Test signals
Validation should include MMU initialization, memory mapping/unmapping, page-fault injection, access violation capture, secure/privileged range checks, RAZWI logging, STLB invalidation coupling, and reset paths that prove translation/protection state is reloaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_masks.h

## Purpose
`dcore0_hmmu0_stlb_masks.h` is the generated bitfield map for the DCORE0 HMMU0 STLB register bank. It defines 192 shift/mask macros for STLB busy/ASID/root-hop setup, cache invalidation, feature and AXI-cache controls, hop configuration, invalidation status, SRAM init, memory-cache configuration, per-hop thresholds, multi-hit interrupts, range invalidation, and ASID scrambler polynomial matrix fields.

## Important APIs, types, and functions
Key fields include `BUSY`, `ASID`, `HOP0_PA43_12` and `HOP0_PA63_44`, cache invalidation producer/index/mask and base address fields, feature-enable bits for multi-page-size, lookup, bypass, bank stop, trace, follower, caching, and follower limits, STLB AXI cache attributes, hop configuration fields for first/last/follower/large-page behavior, lookup masks, invalidate-all start/set/page-size/consumer-index/hit-count/set fields, SRAM init busy bits, memory-cache invalidation done/idle, memory-cache base/config fields, threshold min/max/mask for hops 0-5, multi-hit interrupt mask, L0 cache config, memory read ARPROT, range invalidation enable/ASID/start/end fields, ASID scrambler enable, and H3 polynomial matrix rows 0-18.

## Control flow
The header is declarative. MMU/STLB initialization programs ASID and root-hop physical addresses, feature/hop/cache configuration, cache thresholds, scrambler fields, and interrupt masks. Invalidation flows write cache/range/all invalidation registers, poll busy/done/consumer/hit-count fields, and coordinate with MMU page-table updates.

## State and persistence behavior
STLB configuration is persistent translation-cache state. Root table address, ASID, feature, cache, hop, threshold, range invalidation, and scrambler values stay active until reset or reprogramming. Invalidation status and hit counts are transient but important for synchronization with page-table changes.

## Dependencies and integration points
This file integrates with `dcore0_hmmu0_stlb_regs.h`, HMMU MMU control, page-table management, TLB/cache invalidation code, ASID allocation, and memory fault handling. It shares address and ASID semantics with AXUSER/MMU programming elsewhere in Gaudi2.

## Risks and edge cases
Risks include stale translations after incomplete invalidation, wrong root-hop physical address halves, ASID mismatch with AXUSER traffic, bypass or bank-stop left enabled, threshold values that reduce cache correctness/performance, and scrambler matrix programming errors. Invalidation flows are synchronization-sensitive and should not ignore busy/done fields.

## Test signals
Test signals include STLB initialization, page-table walk success, range and full invalidations, ASID-specific invalidation, cache idle/done polling, multi-hit interrupt handling, page remap/unmap stress, and fault tests proving stale translations are not reused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_regs.h

## Purpose
`dcore0_hmmu0_stlb_regs.h` is the generated address map for the DCORE0 HMMU0 STLB bank, prototype `STLB`. It defines 59 register addresses in the 0x4081000-0x408114C range for STLB status, ASID/root page table setup, invalidation, feature/cache/hop configuration, thresholds, interrupts, range invalidation, and ASID scrambler polynomial rows.

## Important APIs, types, and functions
The exported constants include `BUSY`, `ASID`, root `HOP0` PA low/high registers, cache invalidation command and base registers, `STLB_FEATURE_EN`, `STLB_AXI_CACHE`, `HOP_CONFIGURATION`, lookup masks, invalidate-all/page-size/consumer/hit/set registers, SRAM init, memory cache invalidation/status/base/config, per-hop threshold registers, multi-hit interrupt clear/mask, L0 cache and ARPROT registers, range invalidation start/end controls, ASID scrambler control, and polynomial matrix registers 0-18.

## Control flow
There is no code in the file. MMU setup writes root table, ASID, feature, hop, cache, and scrambler registers. Page-table update paths use the invalidation and range invalidation addresses, then poll status/busy registers before allowing engines to rely on new translations. Fault/recovery code may read busy and cache status during MMU reset.

## State and persistence behavior
The STLB keeps persistent translation-cache configuration and live invalidation state. Root-hop addresses, ASID, feature bits, thresholds, cache config, and scrambler settings persist until reset/reprogramming. Invalidation status is transient but must be observed to avoid stale translations.

## Dependencies and integration points
This address map integrates with `dcore0_hmmu0_stlb_masks.h`, HMMU MMU registers, page-table allocation, ASID management, cache invalidation routines, and memory fault recovery.

## Risks and edge cases
Risks include using the wrong DCORE/HMMU STLB instance, writing invalidation ranges with mismatched MSB/LSB values, enabling lookup before root-hop setup, and failing to wait for invalidation completion. Address drift would cause memory-translation bugs that may first appear as engine DMA faults.

## Test signals
Tests should cover STLB enable and lookup, full/range/ASID invalidation, root table changes, page remap/unmap stress, busy/done polling, multi-hit interrupt behavior, and reset reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_acc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_acc_regs.h

## Purpose
`dcore0_mme_acc_regs.h` is the generated address map for the DCORE0 MME accumulator block, prototype `ACC`. It defines 25 `mmDCORE0_MME_ACC_*` registers in the 0x40F8000-0x40F8060 range for writeback-channel AXI/rate-limit controls, stall and cache/protection attributes, accumulator pseudo-random/LFSR controls, clock gating, inflight counters, E2E credits, interrupts, write AXI aggregation counters, BIST, and two-port BVALID aggregation status.

## Important APIs, types, and functions
The file exports address constants only. Key registers are `WBC0_AXI`, `WBC1_AXI`, `WBC0_RL`, `WBC1_RL`, `WBC_STALL`, `AWCACHE`, `AWPROT`, AP LFSR polynomial/seed select/write/read/clock-gate-delay registers, `WBC_SRC_BP`, `CLK_GATE_EN`, `WBC_INFLIGHTS`, `HBW_CLK_ENABLER_DIS`, `E2E_CRDT_TOP0/1`, `INTR_CAUSE`, `INTR_MASK`, `INTR_CLEAR`, write AXI aggregation counters, `BIST`, and `WR_AXI_AGG_2P_BVALID`.

## Control flow
The header contains no control flow. Initialization programs writeback channel policy, AXI attributes, clock gating, E2E credits, and interrupt masks before MME work is launched. Runtime/debug paths read inflight and aggregation counters, while interrupt handling reads cause, writes clear, and respects the mask register. BIST or LFSR seed controls are used by hardware test/diagnostic flows rather than normal command execution.

## State and persistence behavior
Accumulator configuration persists in hardware until reset or reprogramming. Inflight and aggregation counters reflect live MME writeback activity. Interrupt cause is latched until cleared, and clock-gating or HBW clock enabler state can affect whether the accumulator makes progress.

## Dependencies and integration points
This generated map integrates with MME initialization, command execution, writeback handling, interrupt processing, clock/power management, and BIST/diagnostic code. It is part of the broader DCORE0 MME register set and depends on generated block placement remaining stable.

## Risks and edge cases
Risks include stale writeback rate/AXI attribute state, masking accumulator interrupts, clearing causes before logging, using BIST/LFSR controls during active work, and leaving clock gating or source backpressure in a state that stalls MME completion.

## Test signals
Test signals include MME workloads with writeback, correct inflight counter drain at idle, interrupt cause/mask/clear behavior, rate-limit and stall recovery tests, BIST diagnostics where available, and reset cycles that restore writeback channel configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_acc_regs.h -->
