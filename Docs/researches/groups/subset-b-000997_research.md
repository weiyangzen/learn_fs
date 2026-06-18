# Research: subset-b-000997

Grouped research for Gaudi2 auto-generated ASIC register headers under `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg`. These files do not implement executable functions; they export memory-mapped register addresses and bit-field masks consumed by the Gaudi2 kernel driver through register access helpers such as `RREG32`, `WREG32`, `RMWREG32`, `FIELD_PREP`, and `FIELD_GET`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_masks.h

## Purpose
`pdma0_qm_masks.h` defines the bit positions and masks for the Gaudi2 PDMA0 queue manager register block. It is paired with `pdma0_qm_regs.h`: the register header supplies `mmPDMA0_QM_*` addresses and this mask header supplies the field encoding contract for those registers. The file is auto-generated, GPL-2.0 tagged, guarded by `ASIC_REG_PDMA0_QM_MASKS_H_`, and contains 767 `#define` macros.

## Important APIs, Types, And Functions
There are no C types or functions. The API surface is a macro namespace:

- Global queue-manager controls and status: `PDMA0_QM_GLBL_CFG*`, `PDMA0_QM_GLBL_ERR_CFG*`, `PDMA0_QM_GLBL_STS*`, `PDMA0_QM_GLBL_ERR_STS_*`, `PDMA0_QM_GLBL_ERR_MSG_EN_*`, and `PDMA0_QM_GLBL_PROT_*`.
- Producer queue fields for four queues: `PDMA0_QM_PQ_BASE_*`, `PDMA0_QM_PQ_SIZE_*`, `PDMA0_QM_PQ_PI_*`, `PDMA0_QM_PQ_CI_*`, `PDMA0_QM_PQ_CFG*`, and `PDMA0_QM_PQ_STS*`.
- Completion queue fields for five queues: `PDMA0_QM_CQ_CFG*`, `PDMA0_QM_CQ_STS*`, `PDMA0_QM_CQ_PTR_*`, `PDMA0_QM_CQ_TSIZE*`, `PDMA0_QM_CQ_CTL*`, and `PDMA0_QM_CQ_IFIFO*`.
- Command processor fields: `PDMA0_QM_CP_MSG_BASE*`, `PDMA0_QM_CP_FENCE*`, `PDMA0_QM_CP_PRED*`, `PDMA0_QM_CP_CURRENT_INST_*`, and `PDMA0_QM_CP_STS_*`.
- PQC, arbitration, indirect gateway, rate limiter, AXI/cache, local range, error, interrupt, and performance counter fields.

The macros follow the generated convention `<register>_<field>_SHIFT` plus `<register>_<field>_MASK`. Callers should combine these with kernel bitfield helpers rather than hard-coded shifts.

## Control Flow
The header contains no control flow. Runtime control flow occurs in driver code that writes queue bases, sizes, producer/consumer indices, command processor message windows, arbitration weights, and interrupt masks using the companion register addresses. A typical sequence is: program base/size fields, configure queue and command processor limits, enable error reporting and global queue manager behavior, then poll status/error fields during execution or reset.

## State And Persistence
The macros describe volatile hardware state, not software-owned persistent state. Fields such as queue producer and consumer indices, inflight/free/credit counts, fence counters, global idle/stop bits, and performance counters reflect device state in MMIO registers. Some values persist across driver calls until hardware reset or explicit reprogramming; the header itself stores no data.

## Dependencies
The file depends only on the C preprocessor and its include guard. Effective use depends on:

- `pdma0_qm_regs.h` for matching register addresses.
- Linux register helpers and bitfield helpers in the Gaudi2 driver.
- Hardware documentation/generator consistency for reserved bits, field widths, and queue counts.

## Integration Points
Gaudi2 security code references the PDMA0 QM address range and many PDMA0 QM registers when constructing allowed or protected register lists. Queue-manager setup and diagnostics in the Gaudi2 driver use the same macro namespace to configure command submission, completion queues, command processor fences, interrupts, and error handling. These masks are also part of ABI-adjacent behavior because incorrect queue programming can affect DMA execution visible to user workloads.

## Risks
The main risk is drift between generated masks and silicon/firmware expectations. A wrong mask can silently corrupt adjacent reserved fields, misprogram queue pointers, leave errors unmasked, or break security assumptions around protected queue-manager registers. Repeated queue families also create indexing risk: code that assumes strides or counts must match the generated layout, especially for four PQ instances, five CQ/CP instances, and 64 arbitration-credit entries.

## Test Signals
Useful signals include successful Gaudi2 boot and firmware load, command queue submission/completion under DMA workloads, no unexpected `GLBL_ERR_STS` bits, correct interrupt masking/unmasking, security-regression checks for protected PDMA0 QM ranges, reset/reinit tests that verify idle/stop status, and register smoke tests that compare generated masks against known hardware register specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_regs.h

## Purpose
`pdma0_qm_regs.h` is the Gaudi2 PDMA0 queue manager MMIO address map. It is auto-generated, guarded by `ASIC_REG_PDMA0_QM_REGS_H_`, and exports 518 `mmPDMA0_QM_*` address macros spanning `0x4C8A000` through `0x4C8AD70`. The block covers global queue-manager control, producer and completion queues, command processor state, indirect gateway, arbitration, error reporting, interrupts, ARC auxiliary windows, and performance counters.

## Important APIs, Types, And Functions
There are no functions or structs. The important API is the address macro namespace:

- Global registers: `mmPDMA0_QM_GLBL_CFG0`, `GLBL_CFG1`, `GLBL_CFG2`, error config/status/message-enable, `GLBL_AXCACHE`, `GLBL_PROT`, and global status.
- PQ registers for four queues: base low/high, size, producer index, consumer index, config, and status.
- CQ registers for five queues: config/status, pointer low/high, transfer size, control, control consumer index, and input FIFO state.
- CP registers for five command processors: message base windows, fence data/count registers, predicate state, current instruction, input data, debug and status.
- PQC and direct push registers, local range and L2H compare/mask registers, HBW/LBW rate limiters, arbitration config/credits/weights, indirect APB gateway, SEI status/mask, ARC AUX base address, and perf counters.

## Control Flow
The header does not execute. It drives register-access control flow in callers. Driver code programs queue memory windows, initializes producer/completion queues, sets command processor metadata, controls rate limiters and arbitration, then reads status/error registers while submitting and draining work. The companion mask file provides safe field encodings for these addresses.

## State And Persistence
All state is in hardware registers at the exported addresses. Queue pointer, size, status, fence, predicate, interrupt, error, and performance counter values are volatile MMIO values whose lifetime is defined by hardware reset, firmware sequencing, or explicit driver writes. The address macros are compile-time constants and carry no runtime persistence.

## Dependencies
This header depends only on the preprocessor. Runtime use depends on the Gaudi2 register access layer, `pdma0_qm_masks.h`, and generated base-range definitions used by security and reset code.

## Integration Points
`gaudi2_security.c` references `mmPDMA0_QM_BASE`, PDMA0 QM ARC AUX ranges, and many PDMA0 QM registers while defining security/protection behavior. Queue setup, reset handling, and debug flows in the Gaudi2 device code use this address map to communicate with the PDMA0 command submission engine.

## Risks
Address drift is high impact: an incorrect constant can target the wrong hardware register, corrupt queue-manager state, or weaken protected-register filtering. Large repeated families increase off-by-one and wrong-instance risk, especially around CQ/CP instance count and 64-entry arbitration tables. Generated files should not be manually edited because local fixes can diverge from the source hardware description.

## Test Signals
Relevant tests are register-map sanity checks, protected-range validation, DMA queue bring-up, command submission/completion stress, reset and reinitialization, interrupt/error injection where available, and comparison with hardware register XML or firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_core_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_core_ctx_axuser_regs.h

## Purpose
`pdma1_core_ctx_axuser_regs.h` defines the PDMA1 core-context AXUSER register addresses. It is an auto-generated address-only header with 20 macros in the `mmPDMA1_CORE_CTX_AXUSER_*` namespace, starting at `0x4C9B800`. These registers control or expose AXI user attributes for PDMA1 core context traffic.

## Important APIs, Types, And Functions
There are no functions or types. The exported macros cover HB attributes (`HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`), end-to-end coordination, read/write override low/high registers, and LB coordination/lock/reserved/override registers.

## Control Flow
The header does not implement logic. In runtime code, PDMA1 AXUSER setup writes ASID and MMU-bypass attributes before PDMA traffic uses the core context. `gaudi2.c` writes `mmPDMA1_CORE_CTX_AXUSER_HB_ASID` and clears `mmPDMA1_CORE_CTX_AXUSER_HB_MMU_BP` as part of ASID/MMU preparation for PDMA1.

## State And Persistence
The registers hold hardware AXUSER configuration. Values persist in the device register block until reset or reprogramming. The header only names addresses; it has no software state.

## Dependencies
The file depends on register access helpers in consumers. It shares the generated `AXUSER` prototype layout with `pdma1_qm_axuser_nonsecured_regs.h`, so driver code can configure similar fields in both the queue-manager and core-context paths.

## Integration Points
The key integration point is Gaudi2 memory-management setup, where PDMA1 traffic must carry the correct ASID and must not accidentally bypass the MMU. It also integrates with security/isolation assumptions because AXUSER values participate in transaction identity and routing.

## Risks
Misprogramming ASID or MMU-bypass registers can route DMA through the wrong address space or bypass translation. Address-only headers provide no mask guidance, so callers must know register semantics and full-register write safety. The gap between the QM nonsecured AXUSER block and core-context AXUSER block can lead to configuring one path but not the other.

## Test Signals
Signals include PDMA1 DMA correctness under multiple address spaces, IOMMU/MMU isolation tests, ASID switch tests, reset reinitialization, and checks that PDMA1 setup writes both QM and core-context AXUSER blocks consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_core_ctx_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_qm_axuser_nonsecured_regs.h

## Purpose
`pdma1_qm_axuser_nonsecured_regs.h` defines the PDMA1 queue-manager non-secured AXUSER register addresses. It is auto-generated, address-only, guarded by `ASIC_REG_PDMA1_QM_AXUSER_NONSECURED_REGS_H_`, and exports 20 macros starting at `0x4C9AB80`.

## Important APIs, Types, And Functions
The macro API mirrors the AXUSER prototype: HB ASID, MMU bypass, ordering, snoop, write reduction, read atomic, QoS, reserved, EMEM CPage, core, E2E coordination, write/read override low/high, and LB coordination/lock/reserved/override. No types or functions are declared.

## Control Flow
There is no in-header control flow. During device setup, driver code writes `mmPDMA1_QM_AXUSER_NONSECURED_HB_ASID` and `mmPDMA1_QM_AXUSER_NONSECURED_HB_MMU_BP` before using PDMA1 queue-manager traffic. This configures transaction identity for non-secured queue-manager accesses.

## State And Persistence
The state is hardware-resident AXUSER configuration. It persists until reset or explicit writes. Since these are full register addresses without masks, caller write ordering and values define all behavior.

## Dependencies
Consumers depend on Gaudi2 register access helpers and on shared AXUSER semantic definitions from hardware documentation. This file is commonly used alongside `pdma1_core_ctx_axuser_regs.h` to cover both queue-manager and core-context PDMA1 paths.

## Integration Points
Integration is with Gaudi2 MMU/ASID setup and PDMA queue-manager initialization. Correct values are needed for non-secured PDMA1 transactions to be translated and attributed properly.

## Risks
Incorrect ASID, bypass, override, or ordering attributes can break DMA isolation or cause hard-to-debug ordering/coherency failures. Because the header has no masks, broad writes can overwrite reserved or policy fields if callers do not use known-good values.

## Test Signals
Look for successful PDMA1 operation after MMU setup, multi-context ASID isolation, no unexpected RAZWI/security violations, and parity between configured QM AXUSER and core-context AXUSER registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_masks.h

## Purpose
`pmmu_hbw_stlb_masks.h` defines field masks and shifts for the high-bandwidth PMMU shared TLB block. It is paired with `pmmu_hbw_stlb_regs.h`, guarded by `ASIC_REG_PMMU_HBW_STLB_MASKS_H_`, and exports 193 macros covering STLB lookup, invalidation, cache configuration, page-table-hop configuration, thresholding, interrupts, range invalidation, and ASID scrambling.

## Important APIs, Types, And Functions
No functions or types are present. Key field groups include:

- `BUSY`, `ASID`, and HOP0 physical address fields.
- `CACHE_INV` producer index and index mask, plus invalidation base address fields.
- `STLB_FEATURE_EN` for multi-page-size mode, lookup enable, bypass, bank stop, trace, follower, caching, and follower limit.
- `STLB_AXI_CACHE` and `HOP_CONFIGURATION` fields used for memory access behavior and page-table walk topology.
- `INV_ALL_*`, `INV_PS`, consumer index, hit count, set selection, SRAM init busy flags.
- `MEM_CACHE_*`, `SET_THRESHOLD_HOP0..5`, multi-hit interrupt mask/clear, L0 cache config, ARPROT, range invalidation start/end/asid, and ASID scrambler polynomial matrix entries.

## Control Flow
The header itself is declarative. Driver MMU initialization composes `HOP_CONFIGURATION` with these shifts/masks, configures STLB features and memory cache behavior, and invalidates STLB/cache entries by programming invalidation registers then polling status. In `gaudi2.c`, HBW STLB cache invalidation writes and polls `MEM_CACHE_INVALIDATION` and `MEM_CACHE_INV_STATUS`, and STLB setup uses the HOP configuration field macros.

## State And Persistence
The fields describe MMU translation-cache state and configuration. Translation roots, cache enable/bypass state, invalidation indices, hit counters, thresholds, and ASID scrambling configuration persist in hardware until reset or reconfiguration. Invalidation status is transient and must be polled carefully.

## Dependencies
The masks depend on matching addresses in `pmmu_hbw_stlb_regs.h`, Gaudi2 MMU helper code, and kernel bitfield operations. Correctness also depends on page-table format and ASID allocation policy in the driver/firmware stack.

## Integration Points
The file integrates directly with Gaudi2 MMU initialization and invalidation paths. `gaudi2.c` uses `mmPMMU_HBW_STLB_BASE` and these masks to configure hop layout and invalidate HBW STLB caches. Security code includes the PMMU HBW STLB base region in protected-range handling.

## Risks
MMU mask errors are severe: wrong hop configuration can break address translation; wrong invalidation fields can leave stale translations; wrong ASID scrambling or range invalidation fields can cause cross-context leakage or spurious faults. Polling code must respect status bits and timeouts because invalidation is asynchronous.

## Test Signals
Signals include MMU initialization success, page-table walk correctness for small and large pages, range and full invalidation tests, stale-translation stress under map/unmap churn, ASID isolation, and absence of multi-hit interrupts or PMMU cache timeout errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_regs.h

## Purpose
`pmmu_hbw_stlb_regs.h` is the address map for the Gaudi2 high-bandwidth PMMU shared TLB. It is auto-generated, guarded by `ASIC_REG_PMMU_HBW_STLB_REGS_H_`, and exports 60 `mmPMMU_HBW_STLB_*` macros from `0x4D01000` to `0x4D0114C`.

## Important APIs, Types, And Functions
There are no C functions or types. Address groups include STLB busy/status and ASID, HOP0 physical address, cache invalidation base/control, feature enable, AXI cache attributes, hop configuration, lookup masks, all/set/page-size invalidation controls, SRAM init, memory-cache invalidation/status/base/config, per-hop thresholds, multi-hit interrupt controls, L0 cache config, read ARPROT, range invalidation start/end, and ASID scrambler control/polynomial matrix registers.

## Control Flow
The header is consumed by MMU setup and invalidation routines. Typical flow is: program translation root and hop configuration; enable or tune STLB/cache features; perform memory-cache or range invalidation; poll status; clear or mask interrupts as needed. `gaudi2.c` references `mmPMMU_HBW_STLB_MEM_CACHE_INVALIDATION`, `mmPMMU_HBW_STLB_MEM_CACHE_INV_STATUS`, and `mmPMMU_HBW_STLB_BASE` during invalidation and setup.

## State And Persistence
All values live in hardware MMIO registers. Configuration persists until reset or driver reprogramming; busy, hit count, invalidation status, and interrupt bits are transient hardware state.

## Dependencies
Runtime use depends on `pmmu_hbw_stlb_masks.h`, the Gaudi2 MMU code, register access helpers, and base-address definitions. It also depends on hardware page-table and cache-invalidation semantics.

## Integration Points
This header is central to Gaudi2 HBW memory translation. It integrates with map/unmap invalidation, device boot MMU setup, protected-register policy in security code, and diagnostics for PMMU/cache failures.

## Risks
Incorrect addresses can cause MMU programming to affect unrelated PMMU/PIF registers. Missing synchronization around invalidation status can leave stale translations. Since this block controls high-bandwidth memory access, errors can appear as data corruption, RAZWI faults, or device hangs rather than simple probe failures.

## Test Signals
Test with MMU enable/disable paths, full and range invalidation, multi-ASID workloads, memory pressure and map/unmap stress, reset/resume reinitialization, and checks for PMMU timeout or multi-hit interrupt status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_pif_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_pif_regs.h

## Purpose
`pmmu_pif_regs.h` defines the Gaudi2 PMMU PIF register address map. The PIF block appears to manage PMMU interface credits, rate limiting, arbitration, clock gating, interrupts, routing, debug counters, and base/mask windows for PMMU, PCI, TPC, and decoder paths. The header is auto-generated, guarded by `ASIC_REG_PMMU_PIF_REGS_H_`, and exports 57 macros from `0x4D03000` through `0x4D03324`.

## Important APIs, Types, And Functions
No functions or types are declared. Important address groups include core credit thresholds, core separation and E2E credit disable controls, rate limiter enable/token/saturation/timeout, arbitration type, clock gate config/active, SPI and SEI interrupt cause/mask/register/clear, debug buffer counters and full flags, E2E routing config, base address and mask pairs for PMMU/PCI/TPC/DEC windows, and debug base/mask pairs.

## Control Flow
This file has no logic. Driver or firmware setup code uses these addresses to tune traffic flow into or out of the PMMU: configure credits, optionally enable rate limiting, route E2E paths, set address decode windows, and handle SPI/SEI interrupts. Security code references `mmPMMU_PIF_BASE`, indicating this block participates in protected register range management.

## State And Persistence
The PIF registers hold hardware configuration and counters. Credit thresholds, routing, address masks, rate-limit parameters, and interrupt masks persist until reset or rewrite; debug counts and interrupt causes are transient.

## Dependencies
Consumers need Gaudi2 register helpers and the generated base definitions. There is no companion mask file in this work item, so callers either write whole-register values or obtain field definitions elsewhere.

## Integration Points
The PIF sits between PMMU and fabric/clients. It integrates with PMMU bring-up, performance tuning, debug/telemetry, interrupt handling, security register filtering, and address decode/routing policy for PCI, TPC, and decoder clients.

## Risks
Wrong PIF configuration can throttle or deadlock PMMU traffic, route requests incorrectly, mask important interrupts, or expose debug windows unexpectedly. Address mask/base pairs must be programmed consistently; mismatched PCI0/PCI1/PCI2 windows are particularly easy to confuse because the generated order has adjacent PCI base/mask entries.

## Test Signals
Signals include PMMU traffic under load, absence of PIF interrupt causes, expected debug buffer counts, stable performance with rate limiting enabled/disabled, correct address-window behavior, and protected-register checks around `mmPMMU_PIF_BASE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_pif_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_masks.h

## Purpose
`psoc_etr_masks.h` defines bit masks and shifts for the PSOC Embedded Trace Router/Trace Memory Controller style block. It pairs with `psoc_etr_regs.h`, is guarded by `ASIC_REG_PSOC_ETR_MASKS_H_`, and exports 197 macros for trace buffer sizing, status, pointers, AXI attributes, formatter/flush control, integration test signals, lock/access registers, authentication, and CoreSight identification registers.

## Important APIs, Types, And Functions
There are no functions or types. Important field groups include:

- Trace buffer controls: `RSZ`, `STS`, `RRD`, `RRP`, `RWP`, `TRG`, `CTL`, `RWD`, `MODE`, buffer levels, watermarks, and high pointer bytes.
- AXI data buffer setup: `AXICTL` protection/cache/scatter-gather/write-burst fields plus `DBALO` and `DBAHI`.
- Formatter/flush and prescaler: `FFSR`, `FFCR`, `PSCR`.
- Integration test and ATB signal registers: `ITMISCOP0`, `ITTRFLIN`, `ITATBDATA0`, `ITATBCTR*`, and `ITCTRL`.
- CoreSight management and ID: `CLAIMSET`, `CLAIMCLR`, `LAR`, `LSR`, `AUTHSTATUS`, `DEVID`, `DEVTYPE`, `PERIPHID*`, and `COMPID*`.

## Control Flow
The header is declarative. Gaudi2 CoreSight code unlocks the ETR, disables capture if active, configures trace buffer size/mode/base address/AXI attributes, sets formatter/prescaler, enables capture, later flushes and polls readiness, and reads write pointers. The masks support safe field extraction/preparation in those flows.

## State And Persistence
ETR state is hardware state: capture enable, buffer pointers, full/empty/triggered status, memory error status, formatter flush progress, lock state, and ID values. Configuration persists until reset or explicit reconfiguration; buffer pointers and levels change while tracing runs.

## Dependencies
The masks depend on `psoc_etr_regs.h`, Gaudi2 CoreSight driver code, kernel bitfield helpers, and PSOC global trace-address registers for the high address bits used by trace buffers.

## Integration Points
The file integrates with `gaudi2_coresight.c`, which programs trace capture for PSOC tracing. It also mirrors similar ETR mask usage in earlier Habana devices. PSOC global configuration provides trace ASID/AXUSER and address high bits that complement this ETR block.

## Risks
Trace capture is sensitive to ordering: enabling capture before programming buffer base/size or AXI attributes can write trace data to the wrong address. Incorrect masks for `FFCR`, `STS`, or pointer high bits can cause flush timeouts or corrupted trace dumps. AXI protection/cache fields must match MMU/security expectations.

## Test Signals
Signals include successful CoreSight enable/disable, flush completion without timeout, correct trace buffer contents and write pointer calculation, no `MEMERR`, stable lock/unlock behavior, and expected CoreSight ID register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_regs.h

## Purpose
`psoc_etr_regs.h` is the PSOC ETR address map for Gaudi2 tracing. It is auto-generated, guarded by `ASIC_REG_PSOC_ETR_REGS_H_`, and exports 47 `mmPSOC_ETR_*` register addresses from `0x6C44004` through `0x6C44FFC`.

## Important APIs, Types, And Functions
No functions or types are present. Address groups include trace RAM size/status/read/write pointers, trigger/control/read-write data/mode/buffer level/watermark, AXI control and data buffer base, formatter and flush status/control, prescaler, integration-test registers, claim/lock/authentication registers, and CoreSight device/peripheral/component ID registers.

## Control Flow
The file participates in CoreSight trace setup and teardown. Runtime code unlocks `LAR`, checks/disables `CTL`, manipulates `FFCR` to flush, waits on `STS`/`FFCR` readiness bits, programs buffer size/mode/base and AXI control, enables trace capture, and later reads `RWP`/`RWPHI` to locate captured data.

## State And Persistence
The ETR MMIO block stores trace capture configuration and live trace state. Capture state, buffer pointers, flush status, lock state, and ID registers are hardware-owned. Values persist until reset or reprogramming; pointer and level values evolve while tracing is active.

## Dependencies
Runtime use depends on `psoc_etr_masks.h`, the Gaudi2 CoreSight implementation, PSOC global trace address/AXUSER registers, and register helpers.

## Integration Points
`gaudi2_coresight.c` uses these addresses for PSOC trace sink operations. The block integrates with device debug flows and with memory-management setup for trace buffer writes.

## Risks
Incorrect addresses can make CoreSight control write into unrelated PSOC registers. Misordered ETR programming can corrupt host/device memory or hang while polling flush/readiness status. Because this is debug infrastructure, failures may only appear during diagnostics unless trace capture is part of test coverage.

## Test Signals
Run CoreSight capture tests, enable/disable cycles, flush timeout checks, trace buffer address validation, read-pointer validation, and ID-register sanity comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_masks.h

## Purpose
`psoc_global_conf_masks.h` defines field masks and shifts for the Gaudi2 PSOC global configuration block. It is paired with `psoc_global_conf_regs.h`, guarded by `ASIC_REG_PSOC_GLOBAL_CONF_MASKS_H_`, and exports 937 macros covering reset/boot sequencing, persistent flops, scratchpads, semaphores, trace configuration, interrupts, SPI/QSPI/BSAC controls, strap pins, isolation controls, ASIF request/response plumbing, pad configuration, scrambling, ADC, and DFT controls.

## Important APIs, Types, And Functions
There are no functions or types. Major field families include:

- Boot/reset: `BOOT_SEQ_RE_START`, `BTM_FSM`, `BOOT_SEQ_FSM`, timeout, reset indicators, reset source, reset masks, boot state, and boot-loader image/status fields.
- Firmware communication and persistence: `NON_RST_FLOPS`, `COLD_RST_FLOPS`, `SCRATCHPAD`, `SEMAPHORE`, `CPU_BOOT_STATUS`, and `KMD_MSG_TO_CPU`.
- Error/interrupt: RAZWI interrupt and mask info, timeout/peripheral/AXI/watchdog interrupts, PCIe PSOC DERR controls, SMB alert, SPI write-without-order interrupts, and ASIF functional/error interrupt fields.
- Trace/MMU identity: `TRACE_ADDR_MSB`, `TRACE_AXPROT`, `TRACE_AWUSER`, `TRACE_ARUSER`, scrambling controls and polynomial fields.
- Boot media and low-speed IO: SPI/QSPI selection, SPI DMA, direct write/read, BSAC, boot strap pins, I2C debug/slave, EMMC voltage, ADC configuration and data.
- Fabric/pad/isolation: ARC LBU AXI split controls, master interface controls, target ID, pad 1.8V/3.3V/default/select arrays, TPC/VDEC/NIC/MME/EDMA/HBM/XBAR/HIF-HMMU isolation, and ASIF master/core request/response/status/debug fields.

## Control Flow
The header is declarative. Runtime control flow in Gaudi2 code reads boot status, sends KMD messages to firmware, restarts boot sequencing, checks BTM FSM state, configures trace AXUSER/ARUSER/AWUSER and trace address fields, decodes RAZWI mask info, and controls reset-related fields. The masks are also used with `FIELD_GET` to format diagnostic information from RAZWI and boot/reset registers.

## State And Persistence
This block contains both volatile status and reset-persistent state. Non-reset flops and scratchpads intentionally survive some reset classes and may communicate boot/firmware state. Cold reset flops, reset-source indicators, boot FSMs, interrupt causes, semaphores, trace address and AXUSER settings, pad configuration, and isolation controls are hardware state with lifetimes defined by reset domain and firmware/driver ownership.

## Dependencies
Consumers need `psoc_global_conf_regs.h`, Gaudi2 boot/reset/CoreSight/security code, Linux bitfield helpers, and firmware protocols that assign meaning to scratchpad and message registers. Some fields are shared by firmware and kernel driver, so semantic compatibility matters beyond compile-time correctness.

## Integration Points
Gaudi2 device code uses these masks for boot status, firmware load handoff, reset sequencing, BTM FSM checks, RAZWI diagnostics, and trace/MMU setup. CoreSight uses trace address and AXUSER fields. Security code treats PSOC global configuration ranges specially, including scratchpad access checks.

## Risks
This is a high-blast-radius register block. Incorrect masks can break boot, reset, firmware communication, trace capture, interrupt reporting, isolation, or pad configuration. Reset-persistent registers are especially risky because stale or misdecoded bits can survive across flows. Shared firmware/KMD fields must not be repurposed without protocol coordination.

## Test Signals
Signals include successful cold/warm boot, firmware-load and KMD message exchange, reset/restart sequencing, accurate boot/reset-source reporting, RAZWI diagnostic correctness, CoreSight trace setup, scratchpad/security access validation, interrupt mask/clear behavior, and regression checks against generated hardware specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_regs.h

## Purpose
`psoc_global_conf_regs.h` is the Gaudi2 PSOC global configuration address map. It is auto-generated, guarded by `ASIC_REG_PSOC_GLOBAL_CONF_REGS_H_`, and exports 658 `mmPSOC_GLOBAL_CONF_*` addresses from `0x4C4B000` through `0x4C4BE70`. The block covers boot/reset control, firmware communication, scratchpads, semaphores, trace identity, interrupts, boot media, pad controls, isolation controls, ASIF plumbing, ADC, scrambling, and DFT.

## Important APIs, Types, And Functions
No executable APIs are declared. Important address groups include:

- `NON_RST_FLOPS_*`, `COLD_RST_FLOPS_*`, `SCRATCHPAD_0..31`, and `SEMAPHORE_0..31`.
- Boot/reset/FSM registers such as `PCI_FW_FSM`, `BOOT_SEQ_RE_START`, `BTM_FSM`, `SW_BTM_FSM`, `BOOT_SEQ_FSM`, timeouts, reset delays, reset source/state/masks, and boot image/status registers.
- Firmware and trace registers: `CPU_BOOT_STATUS`, `KMD_MSG_TO_CPU`, `TRACE_ADDR`, `TRACE_AXPROT`, `TRACE_AWUSER`, and `TRACE_ARUSER`.
- Error/interrupt/status registers: RAZWI, timeout/peripheral/AXI/watchdog, SMB alert, PCIe PSOC DERR, SPI write-without-order, ASIF function/error, and ASIF master status/error.
- IO/fabric families: I2C, SPI/QSPI/SPI DMA/BSAC, boot straps, pad 1.8V/3.3V/default/select arrays, isolation controls, ASIF request/response queues, ADC arrays, scrambling polynomial registers, and DFT control.

## Control Flow
The header itself has no logic. Gaudi2 runtime code reads and writes these addresses during firmware load, boot-status polling, reset/restart, CoreSight trace setup, RAZWI handling, and security checks. For example, `gaudi2.c` records `mmPSOC_GLOBAL_CONF_CPU_BOOT_STATUS` and `mmPSOC_GLOBAL_CONF_KMD_MSG_TO_CPU` for firmware interfaces, reads `BTM_FSM`, configures trace address/AXUSER registers through CoreSight paths, and reads RAZWI interrupt/mask info for diagnostics.

## State And Persistence
The register block mixes volatile status with reset-domain persistence. Scratchpads and non-reset flops can retain values across some reset paths and are used for firmware/driver handoff. Boot FSM, reset source, interrupt causes, pad configuration, isolation, ASIF queues, and trace settings are hardware state and may be firmware-owned, driver-owned, or shared depending on lifecycle phase.

## Dependencies
Runtime consumers depend on `psoc_global_conf_masks.h`, Gaudi2 boot/reset/security/CoreSight code, firmware protocols, and generated base range definitions. Address correctness is also security-sensitive because PSOC global config contains scratchpads and control registers used during privileged flows.

## Integration Points
This header integrates with Gaudi2 firmware loading, static loader metadata, pre-firmware boot status polling, reset machinery, CoreSight ETR buffer addressing and AXUSER setup, RAZWI diagnostics, and security register-range validation.

## Risks
Wrong addresses can break boot or reset, write firmware messages to the wrong register, misreport errors, or corrupt pad/isolation controls. The repeated pad/default/scrambling/ADC arrays are vulnerable to stride/count assumptions. Shared scratchpad and persistent registers require careful ownership because writes can affect firmware state beyond the current driver call.

## Test Signals
Signals include boot and firmware-load success, reset-source correctness, BTM/boot FSM expected states, KMD-to-CPU messaging, CoreSight trace setup, RAZWI reporting, scratchpad access policy tests, interrupt handling, and generated-address comparison against the Gaudi2 register database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_regs.h -->
