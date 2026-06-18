# subset-b-000969 register header research

This grouped report covers seven auto-generated HabanaLabs Gaudi ASIC register headers. Each section is source-tree-aligned and wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_ctrl_regs.h

## Purpose

`mme2_ctrl_regs.h` is an auto-generated hardware register address map for the Gaudi MME2 control block, marked as prototype `MME`. It exposes 717 `#define` constants whose names begin with `mmMME2_CTRL_`, covering the MME2 descriptor/programming surface from `mmMME2_CTRL_ARCH_STATUS` at `0x160000` through `mmMME2_CTRL_SHADOW_3_DESC_DUMMY` at `0x160DA4`. It contains no executable code; its value is the stable ABI between the driver and the MME2 memory-mapped register file.

## Important APIs, types, and functions

There are no C functions, structs, enums, or inline helpers. The only exported interface is preprocessor constants included indirectly through `include/gaudi/asic_reg/gaudi_regs.h`. The macro families are the API:

- `ARCH_*` registers describe the active MME descriptor image: status, base addresses for S/L/O tensors, descriptor headers, convolution fields, iteration controls, tensor valid-elements/loop-stride/ROI/spatial fields, AGU offsets, sync-object fields, AXI-user data, performance event selectors, padding values, metadata, rate limiter, and dummy descriptor words.
- `SHADOW_0_*` through `SHADOW_3_*` replicate the same descriptor layout for four shadow descriptor slots. The file has 548 shadow defines and 137 active `ARCH_*` defines, so the shadow banks dominate the address surface.
- Non-descriptor control/debug registers include `CMD`, `RESET`, `PROT`, interrupt cause/mask, `QM_SLV_*`, `QM_STALL`, `AGU_SYNC`, `AGU_SM`, `TE_CLOSE`, PCU rate-limiter/dummy registers, EUS rollup, power-control, sync object, and CoreSight-adjacent base registers referenced from other generated headers.

## Control flow

The header has no runtime control flow. Driver control flow appears where consumers write or read these addresses using low-level accessors such as `WREG32()` and `RREG32()`. In `gaudi.c`, MME2-related initialization and enablement are paired with the MME2 QMAN registers; in `gaudi_coresight.c`, MME2 control block base constants are used to enumerate trace/debug components. The intended hardware flow is descriptor programming into `ARCH_*` or shadow banks, command/queue interaction via QMAN, then status, interrupt, and debug reads.

## State and persistence behavior

The macros themselves are compile-time constants and persist only in the built driver image. The state they name is volatile device state in the Gaudi MME2 control register file. Writes to descriptor, AGU, padding, metadata, sync-object, and rate-limiter addresses program hardware behavior until reset, reprogramming, or power management clears it. Shadow descriptor banks are especially stateful: changing a generated address in one bank can silently redirect a descriptor field to the wrong hardware slot.

## Dependencies and integration points

The direct include path is `gaudi_regs.h`, which is then used by Gaudi driver code and common Gaudi mask definitions. This header must stay synchronized with other MME headers and block base definitions. `mme3_ctrl_regs.h` has the same normalized layout with an `MME3` prefix and a base range of `0x1E0000`; this MME2 file is the `0x160000` instance. Integration points include MME engine setup, descriptor construction code that emits register writes, interrupt/debug handling, power-management sequences, and CoreSight lookup tables.

## Risks

The main risk is address drift from hardware documentation or generated source: no compiler type checking can detect a semantically wrong register address. Because the file repeats many similarly named tensor/AGU/descriptor fields across active and shadow banks, off-by-one generation errors or prefix/base mismatches can be difficult to diagnose. MME2/MME3 symmetry is useful but also risky: copying an MME3 define into MME2 logic would compile while touching the wrong hardware range. Since this file carries only addresses, field-width validation must come from matching mask headers or hardware tests.

## Test signals

Useful signals are build coverage for all includes, probe/init success on Gaudi hardware, MME queue execution tests, descriptor programming tests that exercise S/L/O tensors and shadow descriptors, interrupt/status tests around `INTR_CAUSE` and `ARCH_STATUS`, and debug tooling that confirms CoreSight/base-address tables resolve MME2 blocks correctly. Static checks can compare the normalized MME2 and MME3 layouts and assert that the base delta remains intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_ctrl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_qm_regs.h

## Purpose

`mme2_qm_regs.h` is an auto-generated address map for the Gaudi MME2 QMAN block, marked as prototype `QMAN`. It exports 406 `mmMME2_QM_*` register constants from `mmMME2_QM_GLBL_CFG0` at `0x168000` through `mmMME2_QM_GLBL_MEM_INIT_BUSY` at `0x168D00`. The file gives the driver the addresses needed to configure, enable, doorbell, monitor, and debug MME2 command queues.

## Important APIs, types, and functions

There are no functions or types. The macro surface is the API and is organized like the common Gaudi QMAN register layout:

- `GLBL_*` registers configure global enable/stop/protection/error behavior, secure and non-secure properties, status, message enables, AXCACHE, error capture, and memory-init busy state.
- `PQ_*` registers configure four producer queues: base low/high, size, producer/consumer indices, config, AXI user fields, and status.
- `CQ_*` registers configure five completion queues and status/IFIFO fields.
- `CP_*` registers configure command processor message bases, LDMA offsets, fence counters/data, current instruction, barrier, status, debug, and AXI user fields.
- `ARB_*` registers configure arbitration, weighted round-robin, master/slave credit flow, choice queues, message properties, base addresses, state, and error status.
- `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, `HBW_RD_RATE_LIM_*`, `LBW_WR_RATE_LIM_*`, and `IND_GW_APB_*` cover clock gating, local address ranges, strict priority, rate limiting, and indirect APB gateway access.

## Control flow

The header itself has no control flow. In `gaudi.c`, `gaudi_init_mme_qmans()` uses the MME2 QMAN address range as the north-west MME queue manager. It computes an offset from `mmMME2_QM_GLBL_CFG0 - mmMME0_QM_GLBL_CFG0`, initializes four upper command streams plus a lower CP stream, programs PQ bases/sizes/indices and CP message/LDMA registers through common MME QMAN helpers, and then enables the block with `WREG32(mmMME2_QM_GLBL_CFG0, QMAN_MME_ENABLE)`. Runtime doorbell selection maps `GAUDI_QUEUE_ID_MME_0_0` through `_0_3` to `mmMME2_QM_PQ_PI_0` through `_3`.

## State and persistence behavior

The macros are immutable build-time constants. The registers they name hold live queue-manager state: queue base DMA addresses, producer/consumer indices, command processor fence counters, completion queue state, arbiter credits, error-capture addresses, and protection/ASID properties. That state persists in hardware until reset, queue teardown, or explicit reprogramming. `GLBL_CFG0` enable bits and `GLBL_CFG1` stop/flush bits directly affect whether queued MME work can progress.

## Dependencies and integration points

This file is included via `gaudi_regs.h`. It integrates with `gaudi_masks.h`, which uses MME0 QMAN masks for shared bit layouts while MME2 supplies the instance-specific address range. `gaudi.c` uses these addresses for MME queue initialization, queue doorbells, QMAN power gating, MMU non-secure property programming through `gaudi_mmu_prepare_reg()`, and engine-idle/debug checks. It depends on common QMAN concepts shared by DMA, TPC, MME, and NIC QMAN generated headers.

## Risks

A wrong address can corrupt queue state, send doorbells to the wrong queue, or enable/stop the wrong QMAN instance. The producer-queue and command-processor offsets are regular enough that arithmetic users assume the generated order is stable; inserting or moving a register without matching hardware changes would break offset-based setup. The file lacks masks, so consumers must use compatible QMAN mask headers for bit packing. MME2/MME0 base-delta calculations also mean that base-address errors affect multiple queue IDs.

## Test signals

Build tests should verify include compatibility. Hardware or simulator tests should cover MME QMAN initialization, queue submission on all four MME2 streams, lower CP configuration, producer index doorbells, MME reset/stop/flush sequences, MMU ASID programming of `GLBL_NON_SECURE_PROPS_*`, and QMAN idle detection. Static checks can compare the normalized QMAN layout against other QMAN instances such as NIC0 QM0/QM1 and ensure exactly four PQ and five CQ families remain present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme3_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme3_ctrl_regs.h

## Purpose

`mme3_ctrl_regs.h` is the auto-generated hardware register address map for the Gaudi MME3 control block, also marked as prototype `MME`. It exports 717 `mmMME3_CTRL_*` constants from `mmMME3_CTRL_ARCH_STATUS` at `0x1E0000` through `mmMME3_CTRL_SHADOW_3_DESC_DUMMY` at `0x1E0DA4`. Its normalized macro layout matches `mme2_ctrl_regs.h`; the meaningful difference is the MME3 prefix and address range.

## Important APIs, types, and functions

There are no functions, structs, or runtime helpers. The exported API is the set of register address macros:

- Active `ARCH_*` descriptor registers describe the live descriptor image for MME3, including tensor S/L/O geometry, AGU offsets, convolution parameters, iteration controls, sync-object fields, padding, metadata, performance selectors, and rate limiting.
- `SHADOW_0_*` through `SHADOW_3_*` provide four replicated descriptor banks with the same field families as `ARCH_*`.
- Control and debug definitions include command/reset/protection, interrupt cause/mask, QM slave and stall controls, AGU sync/state-machine registers, TE close, PCU and EUS control/status, power, and sync-object related addresses.

## Control flow

This header has no executable control flow. Consumer code drives control flow by writing descriptors, commands, and control bits to these addresses. `gaudi_coresight.c` references MME3 control block base constants for STM, ETF, BMON, and SPMU arrays; `gaudi.c` writes MME3-specific control registers such as EUS rollup where needed. MME3 compute work is coordinated with QMAN programming from separate QMAN headers and with descriptor/control state exposed here.

## State and persistence behavior

The defines are compile-time constants. The addressed MME3 registers are volatile hardware state. Descriptor and shadow banks persist in the device until overwritten or reset; command, interrupt, protection, and power-control registers affect current hardware execution state. Because the active and shadow descriptor layouts are replicated, correct persistence depends on writing the intended bank and field consistently throughout descriptor lifecycle operations.

## Dependencies and integration points

The file is included by `gaudi_regs.h` and consumed by Gaudi driver paths that need MME3 control addresses. It is tightly coupled to `mme2_ctrl_regs.h` by layout symmetry and to generated block/base headers used by CoreSight and monitoring code. It also integrates with MME queue-manager setup indirectly: QMANs submit work, while this control bank exposes descriptor and engine-control registers used by the MME hardware executing that work.

## Risks

The chief risk is silent hardware misprogramming from generated address mismatch. Since MME2 and MME3 layouts are identical after prefix/base normalization, accidental cross-instance use compiles cleanly but touches the wrong engine. Descriptor banks have many fields with similar names; wrong bank or tensor suffix errors can corrupt compute addressing and be hard to attribute. Lack of field masks in this file means bit-level correctness depends on other generated headers and hardware validation.

## Test signals

Expected signals include successful driver build, Gaudi probe with MME3 present, MME workloads that schedule onto the MME3 engine path, descriptor/shadow-bank programming tests, MME3 interrupt/status handling, and CoreSight/debug enumeration for MME3 STM/ETF/BMON/SPMU blocks. A useful static test is a normalized diff against `mme2_ctrl_regs.h` to confirm the register sequence remains identical while base addresses differ intentionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme3_ctrl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mmu_up_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mmu_up_regs.h

## Purpose

`mmu_up_regs.h` is a compact auto-generated register map for the Gaudi upper MMU block, marked as prototype `MMU`. It exports 25 `mmMMU_UP_*` address constants from `mmMMU_UP_MMU_ENABLE` at `0xC1100C` to `mmMMU_UP_MMU_BYPASS` at `0xC1106C`. The file names MMU enablement, ordering, feature, interrupt, fault-capture, RAZWI, credit, and bypass registers.

## Important APIs, types, and functions

There are no functions or types. The important macro groups are:

- Control/configuration: `MMU_ENABLE`, `FORCE_ORDERING`, `FEATURE_ENABLE`, `VA_ORDERING_MASK_31_7`, `VA_ORDERING_MASK_49_32`, `LOG2_DDR_SIZE`, `SCRAMBLER`, `MMU_BYPASS`.
- Initialization/status: `MEM_INIT_BUSY`, `SLICE_CREDIT`, `PIPE_CREDIT`, `DBG_MEM_WRAP_RM`.
- Interrupt and SPI handling: `SPI_MASK`, `SPI_CAUSE`, `SPI_INTERRUPT_CLR`, `SPI_INTERRUPT_MASK`, `SPI_CAUSE_CLR`.
- Fault capture: `PAGE_ERROR_CAPTURE`, `PAGE_ERROR_CAPTURE_VA`, `ACCESS_ERROR_CAPTURE`, `ACCESS_ERROR_CAPTURE_VA`.
- RAZWI tracking: `RAZWI_WRITE_VLD`, `RAZWI_WRITE_ID`, `RAZWI_READ_VLD`, `RAZWI_READ_ID`.

## Control flow

The header has no direct control flow. In `gaudi.c`, MMU initialization writes `mmMMU_UP_MMU_ENABLE` to enable translation and `mmMMU_UP_SPI_MASK` to configure MMU interrupt masking after STLB/cache setup. Later error handling reads `RAZWI_WRITE_VLD` and `RAZWI_READ_VLD`, decodes initiator IDs from `RAZWI_*_ID`, clears valid bits, and reads page/access capture registers to report faults and call the page-fault handler. This makes the header part of both initialization and asynchronous fault-reporting paths.

## State and persistence behavior

The macros are build-time constants. The hardware registers hold persistent device state until changed or reset: MMU enable/bypass status, ordering masks, interrupt cause/mask, captured fault virtual addresses, RAZWI initiator IDs, and credit counters. Fault-capture registers are latch-like: the driver reads valid bits, reports the captured address, then clears capture state by writing zero to the capture register or valid register.

## Dependencies and integration points

`gaudi_regs.h` includes this header. `gaudi.c` integrates it with STLB setup, cache invalidation, page-fault handling (`hl_handle_page_fault()`), RAZWI reporting, event masks, and engine-id mapping. Some field masks used with these addresses, such as page/access capture valid and VA high-bit masks, come from companion generated mask headers included through the broader Gaudi register set rather than from this address-only file.

## Risks

MMU register errors are high impact: a wrong enable or bypass address can disable address translation guarantees, and wrong capture addresses can hide or misreport memory faults. Fault handlers rely on clear-on-write behavior and valid bits; if the address map or masks diverge, stale faults may repeat or real faults may be dropped. RAZWI initiator decoding depends on the ID registers matching the hardware format, so address mistakes can misidentify engines and mislead recovery/debug work.

## Test signals

Useful tests include Gaudi MMU initialization, cache invalidation, page-fault injection, access-error injection, RAZWI read/write injection, interrupt mask/cause handling, and validation that captured virtual addresses are reported with correct high and low bits. Static build checks should verify `gaudi.c` still resolves all `mmMMU_UP_*` and companion `MMU_UP_*_MASK` macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mmu_up_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_masks.h

## Purpose

`nic0_qm0_masks.h` is an auto-generated bitfield definition header for the Gaudi NIC0 QM0 QMAN block. Unlike the `_regs.h` files, it does not define addresses; it defines 534 `NIC0_QM0_*_SHIFT` and `NIC0_QM0_*_MASK` macros that describe how to pack and unpack fields inside NIC QMAN registers. It is the bit-layout companion to `nic0_qm0_regs.h`, and the driver also reuses the same masks with other NIC QMAN instances when their register layout is identical.

## Important APIs, types, and functions

There are no functions or types. The macro groups cover the common QMAN bitfields:

- Global enable, stop, flush, protection, error, status, and message-enable fields for PQF, CQF, CP, and arbiter units.
- Secure and non-secure properties with ASID and MMBP fields for five property slots.
- PQ/CQ base, size, PI/CI, credit, inflight, busy, IFIFO, pointer, transfer-size, and control fields.
- CP message base, LDMA offset, fence data/count, status, current-instruction, barrier, debug, ARUSER, and AWUSER fields.
- Arbiter configuration, choice queue, WRR weight, master/slave credit, message AWUSER/security properties, state, fullness, error, and credit status fields.
- Clock-gating (`CGM_*`), local range, strict priority, HBW/LBW rate limiting, AXCACHE, indirect APB gateway, global error address/data, and memory-init busy fields.

The driver consumes these masks through `FIELD_PREP()` and direct mask tests, most visibly in `gaudi_masks.h` for `NIC_QMAN_ENABLE`, `NIC_QMAN_GLBL_ERR_CFG_MSG_EN_MASK`, and `NIC_QMAN_GLBL_ERR_CFG_STOP_ON_ERR_EN_MASK`.

## Control flow

The header has no control flow. It affects control flow by determining the values written to address macros from `nic0_qm0_regs.h` and related NIC QMAN register headers. For example, `gaudi_init_nic_qman()` writes `NIC_QMAN_ENABLE` to `mmNIC0_QM0_GLBL_CFG0 + nic_offset`, and that composite value is built from `NIC0_QM0_GLBL_CFG0_PQF_EN_MASK`, `CQF_EN_MASK`, and `CP_EN_MASK`. Stop/flush and error handling paths similarly depend on these bit definitions to affect the intended QMAN subunits.

## State and persistence behavior

The macros are compile-time constants only. The state they describe lives in hardware registers: enable bits, stop/flush requests, protection settings, queue credits, pointer values, command processor fences, arbiter credits, rate limiter state, and captured error data. Incorrect masks can persistently program wrong fields even when the address is correct, causing queues to stay disabled, errors not to generate messages, or idle/power-gating status to be misread.

## Dependencies and integration points

`gaudi_regs.h` includes this header after the Gaudi NIC QMAN register address headers. `gaudi_masks.h` depends on it for reusable NIC QMAN composite values. `gaudi.c` writes NIC QMAN global config/error/protection registers and reads status registers whose interpretation depends on these masks. The same bit layout is reused with `mmNIC0_QM1_*` addresses and with offset-derived NIC instances, so this single mask header is broader than only NIC0 QM0.

## Risks

Mask errors are as dangerous as address errors: a wrong shift or mask can enable the wrong queue fetcher, fail to stop a command processor, corrupt ASID/MMBP protection, misconfigure queue credits, or hide arbiter errors. Several fields use all 32 bits, while others are narrow status/control fields; consumers must not assume uniform widths. Because NIC0 QM1 uses the same masks but different addresses, maintainers must distinguish bit-layout sharing from address sharing.

## Test signals

Build tests should cover `FIELD_PREP()` uses for every referenced mask. Runtime tests should initialize NIC QMANs, submit work on all NIC streams, exercise stop/flush/error paths, verify RAZWI/error IRQ routing, read idle status through `GLBL_STS0` and `CGM_STS`, and validate ASID programming for NIC QMAN non-secure properties. Static tests can compare mask families against the corresponding register families and verify expected field widths for enable, stop, error, and status composites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_regs.h

## Purpose

`nic0_qm0_regs.h` is the auto-generated register address map for the Gaudi NIC0 QM0 QMAN instance. It exports 406 `mmNIC0_QM0_*` constants from `mmNIC0_QM0_GLBL_CFG0` at `0xCE0000` through `mmNIC0_QM0_GLBL_MEM_INIT_BUSY` at `0xCE0D00`. It gives the driver the base instance used to initialize NIC QMANs and to derive offsets for additional NIC QMAN blocks.

## Important APIs, types, and functions

There are no functions or types. The address macros follow the shared QMAN layout:

- `GLBL_*`: global config, protection, error config/capture, secure/non-secure properties, status, message enables, AXCACHE, and memory-init busy.
- `PQ_*`: four producer queues with base, size, PI, CI, config, AXI user, and status registers.
- `CQ_*`: five completion queue config/status/pointer/transfer/control and IFIFO registers.
- `CP_*`: command processor message base registers, LDMA offsets, fences, status, current instruction, barrier, debug, and AXI user registers.
- `ARB_*`: arbiter config, WRR, master/slave credits, message properties, base, state, error, and credit status.
- `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, rate-limiter, and indirect APB gateway registers.

## Control flow

The header itself has no runtime control flow. `gaudi_init_nic_qman()` uses `mmNIC0_QM0_*` addresses plus a `nic_offset` and per-stream `q_off` to program PQ DMA base/size/indices, CP LDMA offsets, CP message bases, global error config and error message target, arbiter error message enable, watchdog timeout, global config/protection, and final QMAN enable. `gaudi_init_nic_qmans()` computes offsets using `mmNIC0_QM1_GLBL_CFG0 - mmNIC0_QM0_GLBL_CFG0` and `mmNIC1_QM0_GLBL_CFG0 - mmNIC0_QM0_GLBL_CFG0`, making this header the anchor for NIC QMAN address arithmetic.

## State and persistence behavior

The defines are compile-time constants. The hardware registers hold queue-manager state such as PQ base DMA addresses, PI/CI values, CP message base addresses for sync manager objects, LDMA offsets, error handler addresses/data, arbiter watchdog/configuration, protection trust, and enable bits. These values persist in the NIC QMAN until reset, port disablement, or reinitialization. Runtime doorbells write producer indices to `PQ_PI_*` registers derived from this map.

## Dependencies and integration points

`gaudi_regs.h` includes this file, and `nic0_qm0_masks.h` supplies bitfield definitions for its registers. `gaudiP.h` defines NIC QMAN macro and engine offsets from base constants. `gaudi.c` integrates this map with NIC port mask handling, queue initialization, queue doorbell selection, power/idle checks, MMU non-secure property programming, RAZWI/error IRQ routing, and debug engine dumps. It also cooperates with sync-manager register maps because CP message bases point to monitor and SOB objects.

## Risks

Because offset arithmetic for multiple NIC ports is anchored on NIC0 QM0, a wrong base or register ordering error can propagate to many NIC instances. Per-stream arithmetic assumes each queue's related registers are spaced regularly by four bytes in the generated order. Misaddressed PQ/CP registers can corrupt DMA queue pointers or sync-manager message bases, while wrong global error registers can suppress or misroute RAZWI/error interrupts. This header must be kept consistent with `nic0_qm0_masks.h`.

## Test signals

Signals include successful Gaudi build, NIC QMAN initialization for enabled ports, queue submissions on NIC0 streams, producer-index doorbells, sync-stream collective message-base behavior, NIC QMAN RAZWI/error interrupt handling, stop/disable paths, idle checks using `GLBL_STS0` and `CGM_STS`, and MMU ASID property programming. Static tests should verify that normalized QMAN register names match `nic0_qm1_regs.h` and `mme2_qm_regs.h` where the layout is shared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm1_regs.h

## Purpose

`nic0_qm1_regs.h` is the auto-generated register address map for the Gaudi NIC0 QM1 QMAN instance. It exports 406 `mmNIC0_QM1_*` constants from `mmNIC0_QM1_GLBL_CFG0` at `0xCE2000` through `mmNIC0_QM1_GLBL_MEM_INIT_BUSY` at `0xCE2D00`. Its normalized QMAN layout matches `nic0_qm0_regs.h`, but it names the second QMAN engine for NIC0's paired NIC-port arrangement.

## Important APIs, types, and functions

There are no functions or C types. The register families mirror NIC0 QM0:

- Global configuration, protection, secure/non-secure properties, status, message-enable, error, AXCACHE, and memory-init registers.
- Four producer queue register groups and five completion queue register groups.
- Command processor message-base, LDMA, fence, status, current-instruction, barrier, debug, ARUSER, and AWUSER registers.
- Arbiter configuration, WRR, credit, choice queue, message property, state, error, and credit-status registers.
- Clock gating, local range, strict priority, rate limiting, and indirect APB gateway registers.

Bitfield interpretation is provided by `nic0_qm0_masks.h` because the two NIC0 QMAN instances share the same field layout.

## Control flow

The header has no executable control flow. It participates in runtime control flow through address selection. `gaudi_init_nic_qmans()` uses the delta `mmNIC0_QM1_GLBL_CFG0 - mmNIC0_QM0_GLBL_CFG0` to move between paired NIC QMAN instances as it walks NIC ports. Doorbell selection maps `GAUDI_QUEUE_ID_NIC_1_0` through `_1_3` to `mmNIC0_QM1_PQ_PI_0 + q_off` after checking `HW_CAP_NIC1`. Engine-idle/debug paths read `mmNIC0_QM1_GLBL_STS0 + offset` and `mmNIC0_QM1_CGM_STS + offset` for odd-numbered NIC ports.

## State and persistence behavior

The macros persist only in the compiled driver. The named hardware state includes QM1 queue bases, producer/consumer indices, CP message bases, LDMA offsets, fence counters, arbiter state, global error routing, protection bits, and enable/stop state. That state remains active until hardware reset, port disablement, or reconfiguration. Because the driver often uses QM0 masks with QM1 addresses, address and mask consistency are both required for correct persistent hardware configuration.

## Dependencies and integration points

`gaudi_regs.h` includes this file. `gaudiP.h` uses base deltas involving QM1 to define NIC engine offsets. `gaudi.c` uses QM1 addresses for NIC1 queue doorbells, MMU non-secure property preparation when `HW_CAP_NIC1` is set, idle checks for odd ports, and offset progression across NIC pairs. It is structurally paired with `nic0_qm0_regs.h` and uses `nic0_qm0_masks.h` for bit fields.

## Risks

The main risk is mismatched arithmetic between QM0 and QM1. If the QM1 base or layout drifts, loops that derive offsets for paired NIC ports will program wrong register banks. Since masks are not namespaced for QM1, maintainers might incorrectly expect a separate `NIC0_QM1_*_MASK` header; using QM0 masks is intentional only while the layouts remain identical. Doorbell errors in this file directly affect user-visible NIC queue progress.

## Test signals

Tests should cover enabled NIC1/odd-port initialization, queue submissions on all four QM1 streams, producer-index doorbells for `GAUDI_QUEUE_ID_NIC_1_*`, MMU ASID programming of `mmNIC0_QM1_GLBL_NON_SECURE_PROPS_*`, QMAN idle/debug reads, and stop/disable paths. Static tests should compare normalized QM1 names to QM0 names and verify the expected `0x2000` base delta between `0xCE0000` and `0xCE2000`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm1_regs.h -->
