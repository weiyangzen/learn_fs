# Research: subset-b-001004

Grouped research for Goya TPC register-map headers and Goya common hardware identity/event headers. Each section preserves the source path and is bounded by reconciliation markers for splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_qm_regs.h

Purpose: auto-generated Goya TPC3 queue-manager MMIO register map. It exports 78 `mmTPC3_QM_*` address macros from `0xEC8000` through `0xEC830C`, matching `mmTPC3_QM_BASE` in `goya_blocks.h` and included transitively by `goya_regs.h`.

Important API surface: global QMAN configuration/status/protection registers, producer queue registers (`PQ_BASE_*`, `PQ_SIZE`, `PQ_PI`, `PQ_CI`, `PQ_PUSH*`, rate-limit controls), completion queue registers (`CQ_*`, status mirrors, read rate limits, `CQ_IFIFO_CNT`), command processor message base registers, LDMA offsets, fence counters/read data, current instruction, barrier/debug, and queue buffer readback windows.

Control flow and state: this header has no executable flow. Runtime state lives in hardware queues, queue indices, CP fence counters, status registers, and buffer windows accessed by driver `RREG32`/`WREG32` paths. Persistence is only hardware-visible register state; the file itself is generated constants.

Dependencies and integration: consumers rely on exact offsets relative to Goya CFG space. `goya_security.c` uses TPC3 QM addresses to configure protection bits, and QMAN setup/test paths depend on compatible PQ/CQ layout and `QMAN_PQ_ENTRY_SIZE`.

Risks and test signals: wrong offsets can break queue submission, interrupt completion, security windows, or fence waits. Test via queue bring-up, TPC QMAN self-tests, MMIO access fault checks, security protection-bit validation, and compile checks after regenerating bitfield headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_rtr_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_rtr_regs.h

Purpose: auto-generated Goya TPC3 router register map for the `TPC_RTR` block. It defines 150 `mmTPC3_RTR_*` offsets from `0xEC0100` to `0xEC0604`, corresponding to `mmTPC3_RTR_BASE` and `TPC3_RTR_MAX_OFFSET` in `goya_blocks.h`.

Important API surface: high-bandwidth and low-bandwidth arbitration registers for read requests, read responses, write requests, and write responses in east/west/north/south/local directions; arbiter max registers; debug arbiter registers; split coefficients/configuration; read/write saturation, token reset, and timeout controls; HBW and LBW range hit/mask/base tables; regulator access/result registers; scrambling enable and non-linear scrambling controls.

Control flow and state: no functions are present. Hardware control flow is external: initialization or debug code writes arbitration/range/split values, then the TPC router routes memory traffic according to those registers. State persists in the device until reset or reprogramming.

Dependencies and integration: included by `goya_regs.h`; base ranges are also used by coresight funnel/debug metadata and security setup. Router configuration must agree with address decoding, HBW/LBW topology, and TPC enable masks.

Risks and test signals: address or range-table mistakes can misroute traffic, starve ports, or corrupt isolation. Test with TPC memory traffic, HBW/LBW range hit diagnostics, protection-bit access tests, timeout/error interrupt paths, and comparison against generated hardware specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cfg_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cfg_regs.h

Purpose: auto-generated TPC4 execution/configuration register map. It defines 432 `mmTPC4_CFG_*` offsets from `0xF06400` through `0xF06E2C`, matching `mmTPC4_CFG_BASE` and the `0x2000` CFG section in `goya_blocks.h`.

Important API surface: two descriptor banks exist: `KERNEL_*` and `QM_*`. Each bank contains eight tensor descriptors with base low/high, padding, tensor config, and five dimension size/stride/base-offset triplets; kernel base address high/low; five-dimensional TID base/size registers; 32 scalar register file (`SRF`) values; kernel config and sync-object message. Shared TPC controls cover TBUF, semaphore, VFLAGS/SFLAGS, LFSR, status, CFG/SM base translation, command/execute/stall, icache base, MSS/TSB config, interrupt cause/mask, ARUSER/AWUSER, and MBIST controls.

Control flow and state: the header does not run code. Driver or firmware writes descriptors and control registers before launching or stalling TPC work. Persistent state is hardware register state, especially descriptor banks and interrupt/status fields.

Dependencies and integration: included via `goya_regs.h`; security code references CFG registers for protection-bit masks and runtime code uses TPC index loops bounded by `TPC_MAX_NUM`.

Risks and test signals: bad tensor/TID offsets corrupt kernels; bad stall/execute or interrupt offsets hang recovery. Test with TPC kernel launch, descriptor programming, interrupt masking, MBIST, security windows, and generated-header diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cmdq_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cmdq_regs.h

Purpose: auto-generated TPC4 command-queue register map for the `CMDQ` block. It exports 58 `mmTPC4_CMDQ_*` offsets from `0xF09000` to `0xF0930C`, matching the TPC4 CMDQ section in `goya_blocks.h`.

Important API surface: global config/protection/error/status registers; completion queue configuration and ARUSER; CQ pointer low/high, target size, control, status mirrors, queue status words, read rate limiter controls, input FIFO count, CP message base registers, LDMA source/destination/size/commit offsets, fence read-data/counter registers, CP status/current instruction/barrier/debug registers, and CQ debug buffer access.

Control flow and state: no code executes here. Hardware command flow is through a completion-oriented command processor: software programs CQ and CP state, hardware consumes commands/messages and reports progress through status and fence counters. State is MMIO-resident and reset-sensitive.

Dependencies and integration: included by `goya_regs.h`; security setup uses CMDQ ranges for protection masks; async event IDs include `GOYA_ASYNC_EVENT_ID_TPC4_CMDQ`, giving failure reporting a stable event number.

Risks and test signals: wrong CQ or CP offsets lead to lost completions, broken LDMA commands, or stuck fences. Test via command queue bring-up, CP fence timeout paths, CQ buffer readback, interrupt/error injection, and security access validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_qm_regs.h

Purpose: auto-generated TPC4 queue-manager register map. It defines 78 `mmTPC4_QM_*` offsets from `0xF08000` to `0xF0830C`, corresponding to `mmTPC4_QM_BASE`.

Important API surface: global configuration/protection/error/status, PQ base/size/PI/CI/config/ARUSER/push/status/rate-limiter registers, CQ config/pointer/size/control/status/read-rate-limit registers, CQ FIFO count, CP message bases, CP LDMA offsets, fence data/counters, current instruction, barrier/debug, and PQ/CQ buffer readback registers.

Control flow and state: the header is declarative. Queue setup code writes PQ/CQ descriptors and pushes producer indices; hardware advances consumer indices and fence counters. Register contents are transient device state and are not persisted by software.

Dependencies and integration: included by `goya_regs.h`; TPC QMAN SRAM placement in `goyaP.h` depends on the shared QMAN model, and async events map TPC4 QM faults to `GOYA_ASYNC_EVENT_ID_TPC4_QM`.

Risks and test signals: offset drift breaks queue submission, MMU attributes, queue-status polling, or protection-bit setup. Test with TPC4 QMAN queue tests, command submission under load, fence wait/timeout paths, MMIO security checks, and generated register-map comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_rtr_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_rtr_regs.h

Purpose: auto-generated TPC4 router register map. It defines 150 `mmTPC4_RTR_*` offsets from `0xF00100` through `0xF00604`, matching the `TPC_RTR` layout and TPC4 router base.

Important API surface: HBW/LBW read-request, read-response, write-request, write-response arbiters for five directions; per-direction max registers; debug arbiter controls; split coefficient table and split read/write rate controls; HBW 64-bit range mask/base pairs; LBW 16-entry range mask/base tables; regulator command/result registers; scrambling controls.

Control flow and state: no C control flow. The registers parameterize router arbitration and address-range steering for TPC4 traffic. Values persist in hardware until reset or reconfiguration.

Dependencies and integration: included through `goya_regs.h`; block base and max offset are declared in `goya_blocks.h`; security and debug/coresight code interact with surrounding TPC router/funnel regions.

Risks and test signals: range-mask errors can expose or misroute memory; arbitration errors can cause throughput collapse or timeouts. Test with TPC4 memory access patterns, HBW/LBW routing coverage, error interrupt checks, and validation against generated hardware XML/spec output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cfg_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cfg_regs.h

Purpose: auto-generated TPC5 configuration map. It has the same normalized layout as TPC4/TPC6/TPC7 CFG and defines 432 `mmTPC5_CFG_*` offsets from `0xF46400` to `0xF46E2C`.

Important API surface: eight kernel tensor descriptors and eight QM tensor descriptors, each with base, padding, tensor config, and five dimension descriptors; kernel/QM base addresses, TID base/size registers, 32 SRF entries per bank, kernel config and sync-object messages; shared TPC state/control registers for TBUF, semaphore, flags, status, CFG/SM translation, command, execute, stall, icache, MSS, TSB, interrupts, ARUSER/AWUSER, and MBIST.

Control flow and state: declarative register constants only. Firmware/driver code fills descriptors and controls execution through these MMIO addresses. Runtime state exists in TPC5 hardware registers and interrupt/status bits.

Dependencies and integration: included via `goya_regs.h`; the register family is addressed alongside `TPC_MAX_NUM` loops and event IDs such as `GOYA_ASYNC_EVENT_ID_TPC5_KRN_ERR`.

Risks and test signals: generated-offset drift can program the wrong tensor/kernel field or leave TPC5 unprotected. Test with TPC5 kernel launch, descriptor validation, TPC interrupt cause/mask handling, MBIST, context/security setup, and register-map checksum comparison to sibling TPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cmdq_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cmdq_regs.h

Purpose: auto-generated TPC5 CMDQ register map. It exports 58 offsets from `mmTPC5_CMDQ_GLBL_CFG0` at `0xF49000` to `mmTPC5_CMDQ_CQ_BUF_RDATA` at `0xF4930C`.

Important API surface: global config/protection/error/status, CQ config and pointer/control/status registers, CQ read-rate limiter, FIFO count, CP message base addresses, LDMA offsets, fence read-data/counters, CP status/current instruction/barrier/debug, and CQ buffer debug access.

Control flow and state: no executable code. Software programs queue and CP registers; hardware consumes queue work and exposes progress through status and fences. State is MMIO hardware state.

Dependencies and integration: pulled in by `goya_regs.h`; TPC5 command queue base and section sizing are in `goya_blocks.h`; event handling uses `GOYA_ASYNC_EVENT_ID_TPC5_CMDQ`.

Risks and test signals: incorrect offsets can break completion processing or fence synchronization for only one TPC lane, making defects easy to miss in partial tests. Test with per-TPC queue tests, fence timeout/recovery, CQ status reads, interrupt event decoding, and security access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_qm_regs.h

Purpose: auto-generated TPC5 QMAN register map with 78 `mmTPC5_QM_*` offsets from `0xF48000` to `0xF4830C`.

Important API surface: QMAN global registers, PQ configuration/base/size/indices/push/status/rate-limiting, CQ configuration/pointers/control/status/rate-limiting, CP message and LDMA offsets, fence/counter/current-instruction/barrier/debug registers, and queue buffer readback windows.

Control flow and state: this file only names registers. TPC queue initialization and execution code writes PQ/CQ/CP values and polls or handles status/fence progress. Hardware retains these values until reset/reprogramming.

Dependencies and integration: included by `goya_regs.h`, paired with `mmTPC5_QM_BASE` and `TPC5_QM_SECTION` in `goya_blocks.h`, and linked to async event ID `GOYA_ASYNC_EVENT_ID_TPC5_QM`.

Risks and test signals: single-TPC address skew can send writes into adjacent blocks. Test TPC5-specific QMAN bring-up, queue stress, MMU/security attribute programming, fence counters, and generated map parity with TPC3/4/6/7 normalized layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_rtr_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_rtr_regs.h

Purpose: auto-generated TPC5 router map. It defines 150 `mmTPC5_RTR_*` offsets from `0xF40100` to `0xF40604`.

Important API surface: HBW/LBW arbitration for read/write request/response channels in five directions, arbiter maximums, debug arbiters, split coefficients/configuration and timeout/token controls, HBW/LBW range hit/mask/base registers, regulator command/result registers, and scrambling controls.

Control flow and state: no functions or branches. External initialization writes routing and arbitration parameters; the hardware router then applies them to TPC5 traffic. State is volatile device register state.

Dependencies and integration: included by `goya_regs.h`; base metadata in `goya_blocks.h`; surrounding driver code uses the TPC router blocks for security configuration and coresight routing.

Risks and test signals: bad route tables can isolate or misdirect TPC5 memory paths. Test with per-TPC memory traffic, arbitration throughput checks, range-hit diagnostics, protection-bit programming, and hardware spec diffing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cfg_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cfg_regs.h

Purpose: auto-generated TPC6 configuration register map. It exports 432 `mmTPC6_CFG_*` offsets from `0xF86400` to `0xF86E2C`, with the same normalized CFG layout as TPC4 and TPC5.

Important API surface: kernel and QM descriptor banks for eight tensors, five-dimensional TID geometry, 32 SRF registers per bank, kernel base/config/sync message, TBUF/semaphore/flag/status registers, CFG and shared-memory address translation, command/execute/stall, icache base, MSS/TSB, interrupt cause/mask, ARUSER/AWUSER, and MBIST registers.

Control flow and state: declarative only. Execution flow is driven by writes from driver/firmware to descriptor and control registers, followed by hardware status/interrupt updates.

Dependencies and integration: included via `goya_regs.h`; associated with `mmTPC6_CFG_BASE` in `goya_blocks.h`, TPC loops bounded by `TPC_MAX_NUM`, and async events for TPC6 ECC/decoder/kernel errors.

Risks and test signals: offset mistakes can affect only TPC6 and survive broad tests if that engine is disabled or masked. Test with explicit TPC6 enablement, kernel dispatch, stall/recovery, interrupt cause/mask, MBIST, and protection-bit validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cmdq_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cmdq_regs.h

Purpose: auto-generated TPC6 CMDQ register map with 58 offsets from `0xF89000` through `0xF8930C`.

Important API surface: global configuration/protection/error/status, completion queue setup and status, queue read-rate limiter, CP message base registers, LDMA offsets, fence read/counter registers, CP status/current instruction/barrier/debug, and CQ buffer debug registers.

Control flow and state: no executable code. Runtime command flow is software-programmed CQ/CP MMIO state consumed by hardware; completion, FIFO, and fence values expose progress.

Dependencies and integration: included by `goya_regs.h`; mapped by `mmTPC6_CMDQ_BASE`; async event handling distinguishes `GOYA_ASYNC_EVENT_ID_TPC6_CMDQ`.

Risks and test signals: wrong offsets can hang TPC6 command processing or misreport completions. Test with TPC6 command queue self-tests, LDMA/fence operations, CQ status polling, interrupt decoding, and generated layout comparison with other TPC CMDQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_qm_regs.h

Purpose: auto-generated TPC6 QMAN register map defining 78 `mmTPC6_QM_*` offsets from `0xF88000` to `0xF8830C`.

Important API surface: global QMAN control/protection/error/status; PQ base, size, indices, config, ARUSER, push words, status and rate-limit controls; CQ config/pointers/size/control/status and rate-limit controls; CP message bases, LDMA offsets, fences, status/current instruction/barrier/debug, and queue buffer debug windows.

Control flow and state: no C flow. Software writes QMAN setup, pushes work, and observes hardware-updated indices/fences/status. State is volatile hardware state.

Dependencies and integration: included through `goya_regs.h`; base and section data come from `goya_blocks.h`; TPC QMAN SRAM offsets in `goyaP.h` assume this shared queue model.

Risks and test signals: offset drift may corrupt PQ/CQ state or security masks. Test TPC6 QMAN execution, fence waits, producer/consumer index updates, MMIO protection setup, event reporting for `GOYA_ASYNC_EVENT_ID_TPC6_QM`, and map parity across TPC QMAN headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_rtr_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_rtr_regs.h

Purpose: auto-generated TPC6 router register map. It defines 150 `mmTPC6_RTR_*` offsets from `0xF80100` through `0xF80604`.

Important API surface: HBW and LBW arbitration registers for read/write requests and responses, arbiter maxima, debug arbiters, split coefficients and read/write split control, HBW and LBW address range hit/mask/base tables, regulator read/write result registers, and scrambling controls.

Control flow and state: declarative register constants only. Runtime hardware routing depends on values written into these registers by initialization, debug, or firmware flows. State is volatile across reset.

Dependencies and integration: included by `goya_regs.h`; paired with `mmTPC6_RTR_BASE`; coresight and security code depend on matching router block locations.

Risks and test signals: route/range mistakes can cause data-path faults for TPC6 traffic and hard-to-diagnose timeout behavior. Test with TPC6 memory routes, HBW/LBW range coverage, arbitration stress, protection-bit programming, and generated spec comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cfg_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cfg_regs.h

Purpose: auto-generated TPC7 configuration map defining 432 `mmTPC7_CFG_*` offsets from `0xFC6400` through `0xFC6E2C`.

Important API surface: mirrored `KERNEL_*` and `QM_*` descriptor banks with eight tensor descriptors, five TID dimensions, 32 SRF registers, base/config/sync-message controls, plus common TPC registers for TBUF, semaphores, flags, status, CFG/SM base translation, command/execute/stall, icache, MSS, TSB, interrupts, ARUSER/AWUSER, and MBIST.

Control flow and state: no code. Software or firmware writes descriptor/control registers and hardware updates status/interrupt fields. State is in TPC7 hardware registers.

Dependencies and integration: included by `goya_regs.h`; base declared as `mmTPC7_CFG_BASE`; async events cover TPC7 ECC/decoder/kernel errors. TPC7 differs from prior routers by pairing with `TPC7_NRTR`, not `TPC7_RTR`.

Risks and test signals: final TPC lane often exposes off-by-one or topology-specific bugs. Test TPC7 kernel dispatch, descriptor programming, stall/recovery, interrupts, MBIST, security windows, and interaction with TPC7 NRTR routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cmdq_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cmdq_regs.h

Purpose: auto-generated TPC7 CMDQ map defining 58 offsets from `0xFC9000` to `0xFC930C`.

Important API surface: global config/protection/error/status, CQ configuration and pointer/control/status mirror registers, read-rate limiter, FIFO count, CP message bases, LDMA offsets, fence read/counter registers, CP current instruction/status/barrier/debug, and CQ buffer access.

Control flow and state: the header contains no execution. Runtime queue flow is created by MMIO writes to CQ/CP registers and hardware updates to status/fence registers.

Dependencies and integration: included by `goya_regs.h`; `goya_blocks.h` gives the unusually large TPC7 CMDQ section because TPC7 sits at the end of the TPC window; async event handling includes `GOYA_ASYNC_EVENT_ID_TPC7_CMDQ`.

Risks and test signals: TPC7-specific section sizing and end-of-range placement make boundary mistakes important. Test TPC7 queue bring-up, CP fence waits, completion interrupts, security masks, and full TPC0-TPC7 queue iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_nrtr_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_nrtr_regs.h

Purpose: auto-generated TPC7 north-router (`IF_NRTR`) map. It defines 102 `mmTPC7_NRTR_*` offsets from `0xFC0100` to `0xFC0604`, replacing the fuller `TPC_RTR` pattern used by TPC3-TPC6.

Important API surface: HBW/LBW max-credit registers, debug arbiters and maxima, split coefficients/configuration and read/write saturation/token/timeout controls, HBW 64-bit range hit/mask/base tables, LBW 16-entry range hit/mask/base tables, regulator command/result registers, and scrambling controls.

Control flow and state: no executable code. Hardware behavior is controlled by credit, split, range, regulator, and scrambling register values. State persists in the router block until reset/reconfiguration.

Dependencies and integration: included by `goya_regs.h`; base is `mmTPC7_NRTR_BASE`, with no `tpc7_rtr_regs.h` in this subset. CFG/CMDQ/QM for TPC7 integrate with this different routing block.

Risks and test signals: treating TPC7 as a normal RTR can miss credit-control differences. Test TPC7 memory routing, credit exhaustion/timeout behavior, range programming, security access, and end-of-topology traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_nrtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_qm_regs.h

Purpose: auto-generated TPC7 QMAN register map defining 78 offsets from `mmTPC7_QM_GLBL_CFG0` at `0xFC8000` through `mmTPC7_QM_CQ_BUF_RDATA` at `0xFC830C`.

Important API surface: global QMAN config/protection/error/status, PQ/CQ setup and status, producer/consumer indices, push words, rate limiter controls, CP message bases, LDMA offsets, fence and current instruction registers, barrier/debug, and queue buffer readback.

Control flow and state: no C flow. TPC7 queue work is driven by MMIO programming of these registers and observed through hardware-updated status and fence fields.

Dependencies and integration: included via `goya_regs.h`; associated with `mmTPC7_QM_BASE`; TPC queue SRAM reservation in `goyaP.h` includes TPC7 as the last QMAN slot; async event ID `GOYA_ASYNC_EVENT_ID_TPC7_QM` reports failures.

Risks and test signals: last-engine offset or SRAM-slot mistakes can affect only TPC7. Test full eight-TPC queue initialization, TPC7 QMAN stress, fence timeout paths, event reporting, and security mask setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc_pll_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc_pll_regs.h

Purpose: auto-generated TPC PLL register map. It defines 41 `mmTPC_PLL_*` offsets from `0xE01100` through `0xE01440` for configuring, resetting, gating, dividing, and monitoring the TPC clock PLL.

Important API surface: PLL numerator/denominator/output divider/config registers (`NR`, `NF`, `OD`, `NB`, `CFG`), lock/loss interrupt and bypass controls, data-change and reset registers, slip watchdog counter, four divider factor registers plus command/busy/select/enable sets, clock gater and clock relax registers, reference counter period and low/high thresholds, not-stable status, and frequency calculation enable.

Control flow and state: no functions. Clock-management code writes PLL/divider/reset/gate controls and reads lock/busy/stability/frequency status. State persists in clock hardware while powered.

Dependencies and integration: included early in `goya_regs.h`; `goyaP.h` defines default TPC PLL frequency-related values and `goya.c` exposes PLL/clock profile operations.

Risks and test signals: bad PLL offsets can destabilize every TPC, cause hangs, or report wrong telemetry. Test PLL profile changes, lock interrupt handling, frequency calculation, busy polling, clock gating, and recovery after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc_pll_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya.h

Purpose: small Goya hardware identity and memory-layout header. It defines BAR IDs/sizes, CFG/SRAM/DRAM/host physical regions, interrupt count, queue entry size, ASID count, protection-bit offset, and engine counts for DMA, TPC, and MME.

Important API surface: `SRAM_CFG_BAR_ID`, `MSIX_BAR_ID`, `DDR_BAR_ID`; `CFG_BAR_SIZE`, `MSIX_BAR_SIZE`, `CFG_BASE`, `CFG_SIZE`; `SRAM_BASE_ADDR`, `SRAM_SIZE`; `DRAM_PHYS_BASE`; `HOST_PHYS_BASE`, `HOST_PHYS_SIZE`; `GOYA_MSIX_ENTRIES`; `QMAN_PQ_ENTRY_SIZE`; `MAX_ASID`; `PROT_BITS_OFFS`; `DMA_MAX_NUM`, `TPC_MAX_NUM`, `MME_MAX_NUM`.

Control flow and state: no runtime flow. These constants drive compile-time checks and runtime address calculations. They are not persisted, but changing them changes driver memory mapping, queue layout, security masks, and loop bounds.

Dependencies and integration: included by `goyaP.h`; `GOYA_MSIX_ENTRIES` guards interrupt count, `QMAN_PQ_ENTRY_SIZE` sizes SRAM QMAN slots, `TPC_MAX_NUM`/`DMA_MAX_NUM` bound loops, and `PROT_BITS_OFFS` is used by security code.

Risks and test signals: incorrect constants can map the wrong BAR, exceed SRAM reservations, undercount engines, or misconfigure protection bits. Test with build-time assertions, PCI BAR probing, SRAM reservation checks, DMA/TPC loop coverage, MSIX allocation, and security programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_async_events.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_async_events.h

Purpose: Goya asynchronous event ID enumeration. It defines firmware/hardware event numbers from PCIe, TPC, MME, MMU, DMA, DDR, SRAM, PLL, PSOC, GPIO, thermal/power, queue, and driver-control domains, ending with `GOYA_ASYNC_EVENT_ID_LAST_VALID_ID = 1023` and `GOYA_ASYNC_EVENT_ID_SIZE`.

Important API surface: `enum goya_async_event_id` values are stable protocol IDs. Notable grouped ranges include TPC ECC (`36..57` step 3), TPC decoder (`117..138` step 3), PLL0-6 (`143..149`), TPC BMON/kernel errors (`190..261` step 10 per TPC), DMA channels, DDR0/DDR1 ECC and AXI events, TPC CMDQ/QM ranges (`430..445`), DMA QM/channel ranges (`449..459`), and control events such as `PI_UPDATE`, `HALT_MACHINE`, `SOFT_RESET`, and environment fix start/end.

Control flow and state: no functions, but `goya.c` switches over these IDs, increments `events_stat` and `events_stat_aggregate`, maps ranges to engine indices, and selects severity/reset handling.

Dependencies and integration: included by `goyaP.h`; array sizes in `struct goya_device` use `GOYA_ASYNC_EVENT_ID_SIZE`; user/debug reporting returns these stats.

Risks and test signals: changing IDs breaks firmware-driver ABI and event decoding. Test with firmware event injection, range-index calculations, bounds checking for invalid IDs, event-stat reporting, and reset/escalation policy coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_async_events.h -->
