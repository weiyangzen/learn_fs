# Research: subset-b-000996

Grouped research for Gaudi2 generated ASIC register and mask headers under `sources/distributed-fs/ceph-client`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h

## Purpose
`gaudi2_regs.h` is the top-level Gaudi2 register aggregation header. It includes the generated register blocks and masks needed by Gaudi2 driver code and adds driver-facing offset macros for replicated blocks such as dcores, TPCs, EDMAs, HMMUs, NICs, PDMAs, rotators, VDEC/DEC blocks, ARC auxiliaries, queue managers, routers, and security/RAZWI windows.

## Important APIs, types, and functions
The file exports macros only. Important exports include block-spacing macros such as `DCORE_OFFSET`, `NIC_QM_OFFSET`, `PDMA_OFFSET`, `NIC_OFFSET`, and `NIC_UMR_OFFSET`; queue-manager register offsets such as `QM_PQ_BASE_LO_0_OFFSET`, `QM_CP_CFG_OFFSET`, `QM_PQC_*_OFFSET`, and `QM_SEI_STATUS_OFFSET`; ARC helper offsets such as `ARC_HALT_REQ_OFFSET`, `ARC_HALT_ACK_OFFSET`, and `ARC_REGION_CFG_OFFSET(region)`; MMU/STLB offsets for bypass, enable, invalidation, hop configuration, thresholds, and range invalidation; router RAZWI capture offsets; bridge/special block offsets; and HBM SPI interrupt bits. It includes this shard's NIC, PCIe, VDEC, and PDMA generated headers directly or through earlier includes.

## Control flow
There is no executable control flow. Driver init, reset, error handling, MMU setup, security setup, queue setup, and debug paths include this file and use its offsets to apply one programming loop across multiple replicated hardware instances. For example, a driver loop can start from a per-engine base address and add a common `*_OFFSET` macro instead of switching on every instance-specific generated symbol.

## State and persistence
The header stores no software state. Its constants define persistent hardware ABI assumptions: physical MMIO addresses, per-block spacing, register layout offsets, and interrupt bit positions. These values persist across driver builds and must match the Gaudi2 RTL/register generation for the targeted ASIC revision.

## Dependencies and integration points
It depends on many generated Gaudi2 `*_regs.h` and `*_masks.h` files plus `gaudi2_blocks_linux_driver.h`. Consumers include `gaudi2.c`, `gaudi2_security.c`, `gaudi2_masks.h`, queue-manager setup, MMU configuration, router/RAZWI handling, PCIe initialization, and NIC/PDMA programming.

## Risks and test signals
The largest risk is silent register drift: a bad included block or offset macro can program the wrong engine while still compiling. Offset macros derived from instance 0/1 base differences assume uniform layout across all replicated engines. Test signals are successful Gaudi2 probe, reset, MMU enable/invalidate, queue submission on PDMA/NIC/TPC/MME paths, PCIe interrupt delivery, RAZWI reporting at plausible addresses, and absence of hardware protection or SEI errors after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_cgm_regs.h

## Purpose
`nic0_qm0_cgm_regs.h` defines the tiny clock-gating management register block for NIC0 queue manager 0. It is an auto-generated address catalog for the QMAN clock-gating unit.

## Important APIs, types, and functions
The file exports `mmNIC0_QM0_CGM_CFG`, `mmNIC0_QM0_CGM_STS`, and `mmNIC0_QM0_CGM_CFG1`. There are no C types or functions.

## Control flow
No code executes here. Gaudi2 initialization or power-management code can write the CFG registers to enable, disable, or tune clock gating and read STS to confirm the queue-manager clock-gating state. Replicated NIC queue-manager code should combine these base addresses with `NIC_QM_OFFSET`/`NIC_OFFSET` style calculations from `gaudi2_regs.h` when programming other NIC instances.

## State and persistence
The persistent state is hardware register state: clock-gating configuration and status for NIC0 QM0. The driver does not persist values in this header; it relies on reset-time programming and hardware retention rules.

## Dependencies and integration points
This header is included through `gaudi2_regs.h` and pairs with the larger `nic0_qm0_regs.h` QMAN map. It integrates with NIC bring-up, queue-manager power gating, reset quiesce checks, and any low-power handling that must avoid gating active queues.

## Risks and test signals
Wrong clock-gating addresses can leave the NIC QM stuck gated, ungated, or reporting false idle. Tests should exercise NIC queue submission after reset and low-power transitions, and should check that CGM status agrees with driver idle/active expectations before and after queue-manager reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_cgm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_regs.h

## Purpose
`nic0_qm0_regs.h` is the auto-generated register map for NIC0 queue manager 0, a QMAN instance. It exposes the MMIO addresses used to configure NIC command queues, completion queues, command processors, arbitration, persistent queue cache, error reporting, and ARC-facing queue-manager status.

## Important APIs, types, and functions
The file exports register macros only. Major groups include `GLBL_*` configuration, status, protection, AXCACHE, and error registers; four persistent queue register sets (`PQ_BASE_*`, `PQ_SIZE_*`, `PQ_PI_*`, `PQ_CI_*`, `PQ_CFG*`, `PQ_STS*`); five completion queue register sets (`CQ_CFG*`, `CQ_PTR_*`, `CQ_TSIZE_*`, status and IFIFO); command-processor message bases, fences, barriers, predicates, current instruction, DMA offset, input data, and debug/credit registers; persistent queue cache registers (`PQC_HBW_*`, `PQC_LBW_*`, `PQC_SIZE_*`, `PQC_PI_*`, `PQC_CFG`, `PQC_SECURE_PUSH_IND`); and arbiter credit, weight, master/slave, fullness, and error registers.

## Control flow
No executable C flow exists. Runtime flow is imposed by queue-manager setup code: program global/protection settings, configure PQ and CQ base/size/control registers, initialize command-processor message and fence locations, configure PQC and arbiter policy, then unmask/handle errors and monitor status. Submission paths update producer indices and doorbell-related registers indirectly through QMAN mechanisms; debug/reset paths read `CP_CURRENT_INST_*`, `CP_STS_*`, CQ status, and arbiter state.

## State and persistence
The persistent state is hardware queue state. PQ/CQ base addresses and sizes describe host or device memory rings; PI/CI registers track queue progress; fence counters and command-processor status survive until reset or explicit reinitialization; arbiter credits and PQC entries track in-flight queue work. The header itself stores no state.

## Dependencies and integration points
It is included by `gaudi2_regs.h`. Generic queue-manager code relies on common offset macros in `gaudi2_regs.h` being derived from the PDMA QMAN layout and compatible with this NIC QMAN layout. It integrates with NIC command submission, collective networking, security/protection setup, interrupt/error handling, and reset diagnostics.

## Risks and test signals
Queue-register misprogramming can corrupt DMA-visible rings, wedge command processors, or report completions to the wrong CQ. Replication risk is high because NIC QM0 addresses are often used as the base pattern for other NIC QMs. Test signals include successful NIC queue bring-up, PI/CI movement under traffic, correct CQ completions, sane fence counters, no PQC secure-push/protection violations, and useful command-processor current-instruction data on forced queue hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm_arc_aux0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm_arc_aux0_regs.h

## Purpose
`nic0_qm_arc_aux0_regs.h` defines the ARC auxiliary register block attached to the NIC0 queue-manager ARC. It covers ARC halt/reset/debug control, address-region configuration, context IDs, software interrupts, ECC status, termination errors, cache/pipeline controls, DCCM queue access, and QMAN/ARC interrupt plumbing.

## Important APIs, types, and functions
The file exports `mmNIC0_QM_ARC_AUX0_*` macros only. Key groups are run/halt/reset registers (`RUN_HALT_REQ`, `RUN_HALT_ACK`, `RST_VEC_ADDR`, `ARC_RST*`), ARC identity/debug registers, SRAM/PCIe/CFG/HBM and general-purpose address windows, context ID and CID offset registers, `SW_INTR_*`, IRQ masks, SEI/REI status/clear/mask/halt controls, ECC syndrome/address registers for DCCM/I-cache/D-cache, LBW termination diagnostics, DCCM queue push/pop/control registers, and QMAN-related interrupt masks/status.

## Control flow
There is no C control flow. Firmware bring-up and reset flows write reset vectors and memory windows, release or halt the ARC, wait for halt acknowledgements, configure region access, and use software interrupts for host-to-ARC signaling. Error paths read SEI/REI/ECC/termination status and may halt the ARC depending on mask configuration.

## State and persistence
Hardware state includes ARC execution state, configured address windows, context IDs, interrupt masks, outstanding software interrupt bits, ECC records, and DCCM queue contents. These values are reset-sensitive and must be reprogrammed after ARC or device reset.

## Dependencies and integration points
The header is included by `gaudi2_regs.h` and works with `nic0_qm0_regs.h` for the queue-manager datapath. It is structurally similar to `pdma0_qm_arc_aux_regs.h`, enabling common ARC auxiliary handling with per-block bases. Consumers include firmware load/start, reset, queue-manager diagnostics, event collection, and security configuration.

## Risks and test signals
Bad ARC auxiliary addresses can prevent NIC firmware from starting or can route ARC memory accesses to the wrong SRAM/HBM/PCIe window. Interrupt-mask mistakes may hide fatal ARC errors or halt on benign events. Test signals include ARC halt/run handshakes completing, firmware reaching expected ready state, software interrupts being observed, no unexpected SEI/REI/ECC status after traffic, and correct error capture when injecting ARC/DCCM faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm_arc_aux0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qpc0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qpc0_regs.h

## Purpose
`nic0_qpc0_regs.h` is the generated register map for NIC0 QPC0, the queue-pair context/control block used by Gaudi2 NIC offload. It defines request/response QPC cache controls, gateway access to QPC entries, congestion-control tuning, doorbell handling, event and congestion queues, work-queue bases, interrupt controls, and debug counters.

## Important APIs, types, and functions
The file exports `mmNIC0_QPC0_*` macros. Major groups are request/response QPC cache invalidate/status/static/base/clean-list registers; error FIFO configuration, indices, masks, credits, and base addresses; gateway busy/control/data/mask registers; congestion-control parameters (`CC_*` alpha, threshold, window, timeout, rollback); doorbell FIFO override/config arrays; secured and privileged doorbell words; QPC debug/status counters; interrupt base/data/cause/mask/clear/en/config registers; response/request ring PI/CI/CFG registers; event and congestion queue base/log-size/producer/consumer/index callback registers; QMAN doorbell bridge registers; TX/RX WQ base, size, MMU bypass, thresholds, and backpressure registers; and static/dynamic WQE template registers.

## Control flow
No code executes here. NIC bring-up configures QPC static state, cache bases, error/event/congestion queues, doorbell security, and WQ templates. Runtime packet submission or RDMA-like operation updates doorbells and queue indices; hardware uses the QPC cache and gateway state to fetch/modify queue-pair contexts. Error and congestion flows push records into FIFOs or queues and raise interrupts through the mapped interrupt registers.

## State and persistence
Hardware persists QPC cache content, queue-pair context pointers, doorbell FIFO state, congestion windows, retry counters, event/congestion queue indices, and WQ configuration until reset or reinitialization. Gateway registers provide a transient read/modify/write path into internal QPC state. The header itself has no software-owned state.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block integrates with NIC firmware, kernel NIC setup, userspace queue provisioning, MSI/MSI-X interrupt routing, security/privilege doorbell policy, and MMU bypass decisions for work queues.

## Risks and test signals
Misconfigured QPC registers can corrupt queue-pair state, lose doorbells, disable congestion control, or misroute event completions. Cache invalidation requires polling the correct status bits; proceeding early can use stale QP state. Test signals include QPC cache invalidation completion, successful secured and privileged doorbell paths, event/congestion queue PI/CI movement, interrupts on injected QP errors, and stable TX/RX WQ operation under congestion and timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qpc0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_completion_queue_ci_1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_completion_queue_ci_1_regs.h

## Purpose
`nic0_umr0_0_completion_queue_ci_1_regs.h` defines a two-register NIC UMR aperture used to submit or expose completion-queue consumer-index updates for NIC0 UMR0_0 lane/index 1.

## Important APIs, types, and functions
The exported macros are `mmNIC0_UMR0_0_COMPLETION_QUEUE_CI_1_CQ_NUMBER` and `mmNIC0_UMR0_0_COMPLETION_QUEUE_CI_1_CQ_CONSUMER_INDEX`. There are no C functions or types.

## Control flow
No code executes in the header. Runtime queue completion handling writes or maps a completion queue number and its consumer index through this UMR window so hardware can observe CQ progress. Correct sequencing is generally CQ selection followed by CI update, with ordering handled by the register access path or mapped doorbell semantics.

## State and persistence
The hardware aperture holds the currently written CQ number and consumer index. It is transient queue state and is reset or overwritten as completions are consumed. The header stores no software state.

## Dependencies and integration points
The file is included by `gaudi2_regs.h` and is related to NIC QPC/QMAN completion handling. It pairs with `nic0_umr0_0_unsecure_doorbell0_regs.h` for user-mapped or unsecure NIC submission/control apertures and with replicated UMR offsets via `NIC_UMR_OFFSET`.

## Risks and test signals
The risk is off-by-instance or off-by-CQ writes: updating the wrong consumer index can stall a CQ or falsely free entries. Test signals include CQ CI movement visible to hardware, no CQ overflow under high completion rates, correct behavior for UMR0_0 versus replicated UMR windows, and completion processing recovery after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_completion_queue_ci_1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_unsecure_doorbell0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_unsecure_doorbell0_regs.h

## Purpose
`nic0_umr0_0_unsecure_doorbell0_regs.h` defines the four 32-bit words of the unsecure NIC doorbell aperture for NIC0 UMR0_0 doorbell 0. It is the generated address contract for posting non-secure doorbell payloads.

## Important APIs, types, and functions
The exports are `mmNIC0_UMR0_0_UNSECURE_DOORBELL0_UNSECURE_DB_FIRST32`, `SECOND32`, `THIRD32`, and `FOURTH32`. No functions or types are defined.

## Control flow
The header has no executable flow. A submission path writes a doorbell payload across these four words in hardware-defined order. Hardware interprets the payload to notify a NIC queue/QP/QMAN path. Replication across UMR windows depends on the `NIC_UMR_OFFSET` macro from `gaudi2_regs.h`.

## State and persistence
Doorbell registers are transient command apertures. Writes are consumed by hardware and should not be treated as durable state. Reset or security-mode changes can alter whether this unsecure aperture is usable.

## Dependencies and integration points
It integrates with NIC user-mapped regions, QPC doorbell handling, queue submission, and security policy. The secured/privileged alternatives are represented in `nic0_qpc0_regs.h`, while this header specifically names the unsecure UMR doorbell window.

## Risks and test signals
Partial or reordered writes can post malformed doorbells. Exposing the unsecure aperture under the wrong security policy can bypass intended privilege checks. Test signals include successful non-secure NIC submissions, ordering barriers around multiword doorbell writes, expected rejection or masking in secure mode, and no stray doorbells after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_umr0_0_unsecure_doorbell0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_aux_regs.h

## Purpose
`pcie_aux_regs.h` defines the Gaudi2 PCIe auxiliary control/status register map. It covers APB timeout, scratch registers, PHY initialization, BAR windows, PCIe command attributes, link/power management, FLR, interrupt controls, diagnostic buses, RAS descriptors, and low-level reset/PHY state.

## Important APIs, types, and functions
The file exports `mmPCIE_AUX_*` address macros only. Notable groups include `SW_GENERAL_PURPOSE_*`, `PHY_INIT`, BAR start/limit registers for BAR0-BAR5, bus-master/memory-space enables, max read request and payload sizing, extended tags, RCB, no-snoop and relaxed-order enables, FLR active/done/interrupt/control registers, LTR and LTSSM controls, system interrupt disable/status, link-up and PM state registers, DBI access registers, diagnostic status buses, CDM/RAS descriptor registers, D-state/PME/L0s/L1/L2 state, PERST, DBI read-only write disable, PHY reset hold, SRIS mode, and bus-master clear interrupt controls.

## Control flow
There is no C flow. Probe and PCIe init code uses these addresses to configure endpoint behavior, BAR decode, link features, and interrupts. Reset and FLR flows poll active/done/status registers. Diagnostic paths read link, PM, APB, and RAS state to explain PCIe failures.

## State and persistence
The hardware persists PCIe endpoint configuration and link/power state until conventional reset, FLR, hot reset, or driver reprogramming. Some fields mirror PCI configuration space while others are Gaudi2-side auxiliary state. Scratch registers may be used by firmware/driver handshakes depending on platform policy.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this map complements `pcie_dbi_regs.h` and `pcie_wrap_regs.h`. It integrates with Linux PCI probe, reset, power management, MSI/MSI-X setup, BAR resource management, and firmware-managed PHY/link sequences.

## Risks and test signals
BAR or command-register mistakes can make MMIO inaccessible or allow unintended host access. FLR/PM sequencing bugs can leave outstanding transactions or stale DBI state. Test signals include stable PCI enumeration, BAR sizing/mapping, link-up checks, FLR completion, MSI/MSI-X delivery, no APB timeout events, and diagnostic status that matches expected link speed/state after suspend/resume or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dbi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dbi_regs.h

## Purpose
`pcie_dbi_regs.h` maps the PCIe DesignWare DBI/configuration-space register block for Gaudi2. It gives the driver symbolic addresses for standard PCI header fields, capabilities, AER, secondary PCIe capabilities, link training features, lane margining, LTR, RAS/vendor-specific areas, and analysis counters.

## Important APIs, types, and functions
The file exports `mmPCIE_DBI_*` macros only. Key groups include device/vendor, command/status, class/revision, BAR0-BAR5, subsystem IDs, capability pointer, MSI and MSI-X capability registers, PCIe capability and device/link control/status registers, AER uncorrectable/correctable status/mask/severity and header-log registers, secondary PCIe and 16 GT/s capability/status/control registers, lane margin control/status per lane, LTR capability/latency registers, RAS/vendor-specific headers, and event/time-based analysis control/data registers.

## Control flow
There is no executable flow. PCIe setup and diagnostics write DBI registers to expose endpoint identity, BAR layout, MSI/MSI-X tables, capability behavior, and error handling. Error paths read AER and lane/link logs. Some writes may require toggling DBI read-only write enable through the auxiliary block before touching normally read-only fields.

## State and persistence
DBI state is PCIe endpoint configuration state. It can be reset by FLR, hot reset, conventional reset, or controller reinitialization and must align with Linux PCI core expectations. AER/log registers persist error evidence until cleared.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pcie_aux_regs.h` for controller-side command and DBI access policy and with `pcie_wrap_regs.h` for MSI-X and transaction wrapping. It interfaces indirectly with Linux PCI enumeration and error recovery.

## Risks and test signals
Incorrect DBI definitions can cause invalid PCI identity, broken BAR mapping, missing MSI-X, or misleading AER logs. Test signals include successful enumeration with expected vendor/device/class IDs, correct BAR resources, enabled MSI-X vectors, valid link capabilities, AER injection/reporting, and no DBI write failures when changing writable config-space fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dbi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_masks.h

## Purpose
`pcie_dec0_cmd_masks.h` defines generated bit shifts and masks for the PCIe decoder command software registers. These masks describe fields inside `pcie_dec0_cmd_regs.h` `SWREG*` registers.

## Important APIs, types, and functions
The file exports `PCIE_DEC0_CMD_*_SHIFT` and `*_MASK` macros. Field groups cover software hardware version/build metadata, external normal/abnormal interrupt sources, reset or ready indications, AXI read/write channel status signals (`AR*`, `AW*`, `R*`, `B*`, `W*`), decoder idle/busy or protocol state, and interrupt/status fields encoded in the SWREG register bank.

## Control flow
There is no executable flow. Driver or diagnostic code reads `mmPCIE_DEC0_CMD_SWREG*` registers and applies these masks to extract individual status bits. Initialization may write fields by composing shifted values with these masks.

## State and persistence
The masks have no state. The underlying SWREG fields represent decoder status, version, interrupt causes, and AXI handshake state that persists in hardware until cleared, updated, or reset.

## Dependencies and integration points
This header is included by `gaudi2_regs.h` and pairs directly with `pcie_dec0_cmd_regs.h`. It also matches similar decoder command masks for dcore VDEC blocks, allowing shared decode/interrupt handling across PCIe and dcore decoders.

## Risks and test signals
Mask drift is subtle: code may read the right register but interpret the wrong bit. Test signals include version fields decoding to expected values, normal and abnormal interrupt bits matching hardware events, AXI status bits agreeing with bridge/controller traces, and interrupt clear/mask flows affecting only intended fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_regs.h

## Purpose
`pcie_dec0_cmd_regs.h` defines the PCIe decoder command register bank as generated `SWREG` addresses. It is the address companion to `pcie_dec0_cmd_masks.h`.

## Important APIs, types, and functions
The file exports `mmPCIE_DEC0_CMD_SWREG0` through selected higher registers including `SWREG26` and `SWREG64`-`SWREG67`. There are no functions or types.

## Control flow
No code runs here. Driver diagnostics and interrupt handling read the SWREG bank, use `pcie_dec0_cmd_masks.h` to decode fields, and may write command/status fields when clearing or configuring decoder behavior.

## State and persistence
The hardware SWREG bank stores decoder-visible software/status state: version metadata, interrupt causes, AXI channel observations, and command/status words. State is reset by decoder or PCIe reset and otherwise persists until hardware updates or driver clears fields.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file integrates with PCIe VDEC bridge-control registers and special registers. `gaudi2_regs.h` also defines `BRDG_CTRL_BLOCK_OFFSET` and `SPECIAL_BLOCK_OFFSET` using decoder-command bases, making this block an anchor for nearby PCIe VDEC address calculations.

## Risks and test signals
Wrong SWREG addresses break decoder status and interrupt diagnosis while leaving the driver build clean. Test signals include expected hardware version/builddate decode, interrupt status matching bridge-control cause registers, and correct behavior when abnormal decoder conditions are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_dec_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_dec_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_dec_regs.h` defines the AXUSER override/control registers for the PCIe VDEC0 bridge decoder traffic class.

## Important APIs, types, and functions
The file exports macros for high-bandwidth AXUSER attributes: `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, read/write override low/high registers, and low-bandwidth attributes `LB_COORD`, `LB_LOCK`, `LB_RSVD`, and `LB_OVRD`. No functions or types are defined.

## Control flow
There is no executable flow. Security and bridge setup code programs these registers before PCIe decoder traffic is allowed to issue, selecting ASID, MMU bypass, ordering, snoop, QoS, and override behavior for decoder-originated AXI transactions.

## State and persistence
The hardware persists AXUSER policy for decoder traffic until reset or reprogramming. These fields influence every matching transaction rather than one command.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pcie_vdec0_brdg_ctrl_regs.h`, bridge masks, PCIe decoder command registers, MMU/security setup, and AXI fabric protection rules.

## Risks and test signals
Wrong AXUSER policy can bypass MMU/security unexpectedly, break ordering, or reduce performance through bad QoS/snoop settings. Tests should validate decoder transactions under secure and non-secure modes, MMU bypass policy, no-snoop behavior, and absence of AXI protection faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_dec_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h` defines AXUSER controls for abnormal MSI-X traffic emitted by the PCIe VDEC0 bridge-control block.

## Important APIs, types, and functions
Exports mirror the common AXUSER schema: high-bandwidth ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved, emem cpage, core, end-to-end coordinate, write/read override low/high, and low-bandwidth coordinate/lock/reserved/override registers. There are no functions or types.

## Control flow
The header has no control flow. Interrupt setup/security code programs this policy so abnormal MSI-X writes carry the expected AXI attributes when an error path signals the host.

## State and persistence
The programmed AXUSER registers persist as transaction policy until reset. Because this path is for abnormal interrupts, bugs may only appear during error injection or real fault handling.

## Dependencies and integration points
It is included by `gaudi2_regs.h` and integrates with PCIe VDEC bridge interrupt cause/mask registers, MSI-X gateway/wrapper registers, and host interrupt delivery.

## Risks and test signals
If abnormal MSI-X attributes are wrong, fatal/error interrupts may be dropped, blocked by protection, or written with incorrect ordering. Test signals include injected abnormal bridge events producing MSI-X, correct host vector routing, and no AXI security/protection error on the interrupt write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h` defines AXUSER policy registers for PCIe VDEC0 bridge MSI-X traffic associated with L2C events.

## Important APIs, types, and functions
The exported macros follow the AXUSER template: `HB_ASID`, `HB_MMU_BP`, ordering/snoop/reduction/atomic/QoS/reserved/core attributes, E2E coordinates, read/write override registers, and LB coordinate/lock/reserved/override registers. It defines no functions or data structures.

## Control flow
No executable flow exists. Initialization programs these registers before enabling bridge interrupts so L2C-related MSI-X writes use the desired ASID, security, MMU, ordering, and fabric metadata.

## State and persistence
AXUSER settings are persistent hardware policy for this interrupt class until reset or explicit reconfiguration. They affect interrupt write transactions rather than software-visible memory.

## Dependencies and integration points
Included through `gaudi2_regs.h`, this block works with bridge-control interrupt masks/causes and PCIe wrapper MSI-X delivery. It also depends on systemwide security/MMU assumptions encoded by Gaudi2 init.

## Risks and test signals
Incorrect policy can make L2C MSI-X interrupts fail only under cache/fabric events, which makes regressions hard to notice. Test signals include L2C event injection, correct MSI-X vector arrival, and no protection, MMU, or ordering violations in bridge/fabric logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h` maps AXUSER attributes for normal MSI-X traffic from PCIe VDEC0 bridge control.

## Important APIs, types, and functions
The file exports the standard bridge AXUSER register set for HB ASID/MMU bypass/ordering/no-snoop/write-reduction/read-atomic/QoS/reserved/emem/core/E2E/override controls plus LB coordinate/lock/reserved/override controls. There are no functions or types.

## Control flow
There is no C flow. During interrupt setup, driver or firmware code programs this block so normal MSI-X writes are accepted by the PCIe/fabric path and use the correct transaction metadata.

## State and persistence
The settings persist in hardware until reset and govern normal interrupt traffic. They are part of device bring-up state rather than per-interrupt state.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this header ties bridge-control normal interrupt causes to PCIe wrapper/MSI-X gateway behavior and to the broader AXI security/MMU setup.

## Risks and test signals
The common risk is interrupt delivery failure due to wrong ASID/MMU bypass/security/no-snoop attributes. Test signals include normal bridge interrupt delivery, successful MSI-X masking/unmasking, no dropped vectors under load, and no AXI protection errors during interrupt writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h` defines AXUSER registers for VCD-class MSI-X traffic from the PCIe VDEC0 bridge.

## Important APIs, types, and functions
It exports the same AXUSER macro families as the other bridge MSI-X blocks: HB ASID, MMU bypass, ordering, no-snoop, write reduction, read atomic, QoS, reserved/core/page fields, E2E coordinate, read/write overrides, and LB coordinate/lock/reserved/override. No code or types are present.

## Control flow
The header has no control flow. Runtime control is in initialization/error paths that program attributes before enabling VCD interrupt signaling and then rely on the hardware block to stamp outgoing MSI-X transactions.

## State and persistence
These registers are persistent per-traffic-class policy until reset or reconfiguration. They are normally static after bring-up.

## Dependencies and integration points
Included by `gaudi2_regs.h`, it integrates with bridge-control VCD interrupt masks/causes, MSI-X gateway logic in `pcie_wrap_regs.h`, and Gaudi2 security/MMU/fabric policy.

## Risks and test signals
Misconfigured VCD MSI-X attributes can cause event loss for only this interrupt class. Test signals include VCD event injection, correct vector delivery, no abnormal bridge interrupt escalation, and no AXI attribute/protection faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_masks.h

## Purpose
`pcie_vdec0_brdg_ctrl_masks.h` defines shifts and masks for PCIe VDEC0 bridge-control registers. It is the bitfield companion to `pcie_vdec0_brdg_ctrl_regs.h`.

## Important APIs, types, and functions
The file exports `PCIE_VDEC0_BRDG_CTRL_*_SHIFT` and `*_MASK` macros. Field groups cover CGM disable/idle masks and counters, APB arbitration watchdogs, graceful idle/stop status, cause/mask/clear registers, decoder/MSI-X AWADDR/WDATA fields, error-capture fields for LBW/HBW addresses, AXI response/status, free-run and busy counters, statistic counter enable, VCD interrupt mask/cause fields, and normal/L2C/abnormal interrupt source fields.

## Control flow
No code executes in the header. Driver code reads/writes bridge-control registers and uses these masks to set one field without corrupting adjacent fields. Interrupt handlers decode cause registers, mask selected classes, clear latched events, and inspect error address/data fields.

## State and persistence
The masks are stateless. Underlying bridge-control state includes interrupt latches, clear/mask bits, idle counters, decoder/MSI-X LBW transaction payload capture, and statistics counters. This state persists until clear or reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with `pcie_vdec0_brdg_ctrl_regs.h` and the AXUSER per-traffic-class headers. It is also related to decoder command masks and PCIe wrapper interrupt delivery.

## Risks and test signals
Mask drift can lead to read-modify-write corruption, especially in interrupt clear/mask and watchdog fields. Tests should cover normal/abnormal/L2C/VCD interrupt decode, masking and clearing individual bits, bridge idle detection, MSI-X LBW payload capture, and counter enable/disable without disturbing unrelated fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_regs.h` maps the PCIe VDEC0 bridge-control register block. It provides addresses for clock gating, idle/graceful control, interrupts, MSI-X LBW write capture, gateway access, address/error capture, counters, and VCD interrupt masking.

## Important APIs, types, and functions
Exports include `mmPCIE_VDEC0_BRDG_CTRL_CGM_DISABLE`, `IDLE_MASK`, APB watchdog/count registers, `GRACEFUL`, interrupt cause/mask/clear registers, normal and abnormal MSI-X LBW address/data registers, gateway address/data/go/status registers, decoder status/error capture registers, free-run/busy counters with set-value low/high pairs, statistic counter enable, and `VCD_INTR_MASK`. No functions or types are declared.

## Control flow
There is no executable control flow. Init code configures clock/idle behavior and interrupt masks. Reset/quiesce code checks graceful/idle and busy counters. Interrupt paths read cause registers, inspect captured MSI-X or decoder address/data fields, clear events, and may use gateway registers for indirect bridge access.

## State and persistence
The bridge persists interrupt latches, masks, counter values, captured transaction/error addresses, and gateway transaction state until clear or reset. Counters may accumulate operational evidence across normal runtime until explicitly disabled or reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with `pcie_vdec0_brdg_ctrl_masks.h`, AXUSER traffic-class headers, `pcie_dec0_cmd_regs.h`, and `pcie_vdec0_ctrl_special_regs.h`. It integrates with PCIe error handling, MSI-X delivery, and VDEC/decoder reset sequencing.

## Risks and test signals
Wrong bridge-control addresses can hide interrupts, corrupt MSI-X writes, or fail reset quiesce checks. Test signals include bridge idle/graceful transitions, normal and abnormal interrupt injection, correct captured LBW address/data for MSI-X events, gateway access completion, and counters advancing only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_ctrl_special_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_ctrl_special_regs.h

## Purpose
`pcie_vdec0_ctrl_special_regs.h` defines the PCIe VDEC0 bridge special/control register block for privilege/security, memory gateway, ECC, global error reporting, spare registers, and security registers.

## Important APIs, types, and functions
The file exports `mmPCIE_VDEC0_CTRL_SPECIAL_*` macros. Major groups are `GLBL_PRIV_0` through `GLBL_PRIV_31`, memory gateway data/request/number/ECC select/control/error mask/global error mask/status/address/RM, global error mask/address/cause, spare registers, and `GLBL_SEC_0` through `GLBL_SEC_31`. No functions or types are present.

## Control flow
No code executes. Security initialization programs privilege and security arrays; diagnostic or RAS paths use the memory gateway and ECC controls; error handlers read global error cause/address and clear or mask relevant bits according to generated masks in related special mask headers.

## State and persistence
Hardware state includes privilege/security policy, memory gateway transaction state, ECC injection/reporting state, and global error latches. These values are reset-sensitive and may be reprogrammed during security init or device reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block is adjacent to PCIe VDEC bridge control and decoder command blocks. It integrates with `gaudi2_security.c`, bridge RAS/error handling, and any firmware policy for protected register access.

## Risks and test signals
Privilege/security register mistakes can expose protected VDEC/PCIe controls or block legitimate driver access. ECC/global error misconfiguration can mask real faults. Test signals include expected security aperture behavior, successful access to allowed registers, blocked unauthorized access, ECC/error injection producing the right global cause/address, and clean reset reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_ctrl_special_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_regs.h

## Purpose
`pcie_wrap_regs.h` defines the Gaudi2 PCIe wrapper register block around the PCIe controller. It covers MSI/MSI-X gatewaying, virtual UART, host access termination, LBW gateways, transaction metadata capture/override, MESO FIFO diagnostics, peer-to-peer tables, reset/hot-reset controls, AXI split/drain controls, PHY/core base addresses, interrupt indications, PMMU routing, ASID modification, CoreSight trace AXI control, and external-memory location mapping.

## Important APIs, types, and functions
The file exports `mmPCIE_WRAP_*` macros. Key groups include interrupt generator mask ranges and timer/control, MSI-X doorbell/mask/gateway/vector/table registers, VUART RX/TX, illegal LBW request capture, outbound address, LBW gateway address/data/go/status arrays, slave AW/AR misc TLP metadata, MESO FIFO counters/LFSR/backpressure controls, P2P table 0-63 plus enable/request/interrupt/terminate controls, CPU hot reset, PCIe cache/lock/prot/user overrides, outstanding/inflight controls, AXI split interrupts and drain controls, PHY/core base addresses, SPMU/AXI/IC interrupt indicators, PMMU router config, PSOC reset/boot done, ASID modification, FLR FSM control, drain address stamps, and external memory HBM/PC mapping.

## Control flow
No executable code is present. Probe/reset paths configure MSI-X gatewaying, outbound/LBW access, P2P routing, and reset controls. Error paths read illegal request, AXI split, drain, and interrupt indicator registers. Reset/quiesce flows use drain active/timeout/config and FLR FSM controls to stop traffic before reset.

## State and persistence
Wrapper state includes interrupt gateway tables, VUART data, captured illegal transaction state, P2P mappings, AXI override policy, drain status, ASID modification windows, and external-memory location maps. Most state must be rebuilt after FLR or device reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, it complements `pcie_aux_regs.h`, `pcie_dbi_regs.h`, PCIe VDEC bridge files, interrupt setup, firmware boot management, and memory-routing/security code.

## Risks and test signals
Incorrect wrapper programming can break MSI-X, host MMIO access, P2P transactions, reset drain, or security metadata. Test signals include MSI-X vector delivery, VUART operation if used, illegal LBW request capture on injection, P2P table behavior, successful FLR/hot reset, drain completion before reset, and no stale ASID/AXUSER overrides after reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_special_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_special_regs.h

## Purpose
`pcie_wrap_special_regs.h` maps the PCIe wrapper special register block for privilege/security, memory gateway/ECC, global error capture, spare values, and security policy registers.

## Important APIs, types, and functions
Exports include `mmPCIE_WRAP_SPECIAL_GLBL_PRIV_0` through `GLBL_PRIV_31`, memory gateway data/request/number/ECC select/control/error mask/global error mask/status/address/RM registers, `GLBL_ERR_MASK`, `GLBL_ERR_ADDR`, `GLBL_ERR_CAUSE`, spare registers, and `GLBL_SEC_0` through `GLBL_SEC_31`. There are no functions or types.

## Control flow
No C flow exists. Security setup writes privilege/security arrays; diagnostic/RAS code accesses gateway and ECC registers; global error handlers read cause/address and apply masks. Reset code should reinitialize policy after wrapper reset.

## State and persistence
Hardware persists access-control policy, memory gateway state, ECC/error latches, spare values, and security bits until reset or reprogramming. This state controls access to the surrounding PCIe wrapper block.

## Dependencies and integration points
Included by `gaudi2_regs.h`, the header integrates with `pcie_wrap_regs.h`, Gaudi2 security initialization, RAS/global error reporting, and firmware access policy.

## Risks and test signals
Wrong special-register policy can either expose protected PCIe wrapper controls or block required driver/firmware access. Test signals include security tests against privileged and secure registers, global error capture on injected illegal access, ECC status behavior if supported, and successful reprogramming after FLR/device reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_special_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_axuser_regs.h

## Purpose
`pdma0_core_ctx_axuser_regs.h` defines AXUSER attribute registers for PDMA0 core context transactions. It controls the metadata attached to DMA context-originated HB/LB AXI traffic.

## Important APIs, types, and functions
The file exports `mmPDMA0_CORE_CTX_AXUSER_*` macros for HB ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved/page/core/E2E fields, read/write overrides, and LB coordinate/lock/reserved/override controls. It has no functions or types.

## Control flow
No executable flow exists. PDMA initialization or security setup programs these registers before enabling context execution, ensuring DMA context reads/writes use correct ASID, MMU, ordering, snoop, and fabric metadata.

## State and persistence
The hardware persists AXUSER policy for PDMA0 context traffic until reset or reconfiguration. It is static policy, not per-transfer software state.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file complements `pdma0_core_ctx_regs.h`, `pdma0_core_regs.h`, and Gaudi2 MMU/security setup.

## Risks and test signals
Wrong attributes can cause DMA to bypass translation incorrectly, hit protection faults, or violate ordering/snoop expectations. Test signals include PDMA context transfers in secure and non-secure modes, MMU bypass tests, coherency/no-snoop validation, and absence of fabric protection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_regs.h

## Purpose
`pdma0_core_ctx_regs.h` defines the PDMA0 core context programming registers. These registers describe one programmed DMA context, including rate/power settings, transfer dimensions, source/destination offsets and bases, and commit.

## Important APIs, types, and functions
The file exports `mmPDMA0_CORE_CTX_*` macros. Important registers include rate-limit token, power low-power control, transfer engine row count, context index/index increment, context control, source transfer sizes, source and destination offset low/high pairs, source and destination base low/high pairs, destination transfer size, and `COMMIT`.

## Control flow
There is no code here. DMA setup writes context index/control, transfer sizes, base addresses, and offsets, then writes `COMMIT` to make the context visible to hardware. Status and core registers in `pdma0_core_regs.h` expose active context state during execution.

## State and persistence
The hardware context registers persist the current programmed DMA descriptor/context until overwritten, committed, or reset. Base/offset/size values are critical transfer state and must match MMU/security policy.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pdma0_core_regs.h` for global PDMA enable/status and `pdma0_core_ctx_axuser_regs.h` for transaction attributes. Queue-manager code may launch PDMA work that consumes these context definitions.

## Risks and test signals
Incorrect size or base registers can cause memory corruption. Context index/increment mistakes can overwrite the wrong context. Test signals include PDMA memcpy/fill tests over small and large transfers, boundary/offset tests, context commit visibility, status matching the active context, and protection faults for intentionally invalid addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_masks.h

## Purpose
`pdma0_core_masks.h` provides generated bit shifts and masks for PDMA0 core registers. It is the bitfield companion for `pdma0_core_regs.h`.

## Important APIs, types, and functions
The file exports `PDMA0_CORE_*_SHIFT` and `*_MASK` macros. Field groups cover core enable, halt, flush, protection value, clock gating, read/write global controls, HBW/LBW max outstanding and max transfer size, ARCACHE/AWCACHE and inflight limits, memory-init busy/done/status, error message address/write data, status registers, and selected read-context status fields.

## Control flow
There is no executable control flow. Driver code uses these masks for read-modify-write programming of PDMA enable/halt/flush, tuning outstanding transactions, setting cache/protection metadata, checking memory initialization, and decoding error/status registers.

## State and persistence
The masks are stateless; the underlying PDMA core registers contain persistent enable/halt, outstanding, cache, error, and status state until reset or reprogramming.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this header pairs with `pdma0_core_regs.h` and is used by PDMA init/reset/error handling. It also relates to `pdma0_core_special_masks.h` for special/global error and security fields.

## Risks and test signals
Mask drift can corrupt adjacent control fields and cause hard-to-debug DMA hangs. Test signals include successful enable/halt/flush cycles, correct max outstanding/size behavior under stress, decoded error-message addresses matching injected faults, and status masks reporting active/idle context accurately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_regs.h

## Purpose
`pdma0_core_regs.h` maps the PDMA0 core global register block. It provides addresses for enabling, halting, flushing, protection, clock gating, read/write channel tuning, memory initialization, error messaging, and status.

## Important APIs, types, and functions
Exports include `mmPDMA0_CORE_CFG_0`, `CFG_1`, `PROT`, `CKG`, read global/HBW/LBW max outstanding and max size/cache/inflight registers, write global/HBW/LBW equivalent registers, memory init start/busy/done/status, error message address low/high and data, status registers `STS0`/`STS1`, and read-context status selection/size/base/id registers. No functions or types are present.

## Control flow
The header has no C flow. PDMA init writes global configuration, protection/cache settings, and outstanding limits, then enables the core. Reset/quiesce paths halt or flush and poll status. Error paths program or read error-message registers. Diagnostics select read-context status and inspect active context details.

## State and persistence
Hardware state includes enable/halt/flush status, transaction tuning, memory-init state, error-message target/data, and active read context status. Values persist until reset or explicit reprogramming.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pdma0_core_masks.h`, `pdma0_core_ctx_regs.h`, PDMA queue-manager headers, and Gaudi2 reset/security/MMU setup.

## Risks and test signals
Bad core control addresses can wedge DMA or allow transfers with wrong protection/cache policy. Test signals include PDMA enable/disable, halt/flush completion, memory init completion, transfer throughput within expected outstanding limits, correct error reporting on invalid transfers, and status registers showing idle after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_special_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_special_masks.h

## Purpose
`pdma0_core_special_masks.h` defines bit shifts and masks for the PDMA0 core special register block, covering privilege, memory gateway, ECC, and global error fields.

## Important APIs, types, and functions
Exports include `PDMA0_CORE_SPECIAL_GLBL_PRIV_*` masks, memory gateway data/request/address/MID/valid/mask fields, memory count/ECC selection/control/error mask/status/address/RM fields, and global error mask/address/cause fields for APB unmapped read/write, privileged write, and secure write violations. It declares no functions or types.

## Control flow
No code executes. Security and diagnostic code uses these masks to program privilege/security policy, perform memory gateway accesses, configure ECC/error reporting, and decode global APB access violations.

## State and persistence
The masks are stateless. The underlying special registers persist access-control policy, gateway state, ECC status, and global error latches until reset or clear.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this header is the bitfield companion to PDMA special registers included elsewhere in the Gaudi2 generated set. It integrates with `gaudi2_security.c`, PDMA RAS handling, and APB protection diagnostics.

## Risks and test signals
Wrong masks can invert security policy or hide APB violations. Test signals include privileged/secure APB write tests, unmapped access error capture, gateway request completion, ECC/error injection where available, and correct clearing/masking of global error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_special_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_arc_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_arc_aux_regs.h

## Purpose
`pdma0_qm_arc_aux_regs.h` maps the ARC auxiliary block for the PDMA0 queue-manager ARC. It controls ARC halt/reset/debug, memory-region mapping, software interrupts, ECC/error reporting, DCCM queues, and QMAN interrupt/status interaction.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_ARC_AUX_*` macros. Important groups are run/halt/reset/debug and identity registers, SRAM/PCIe/CFG/HBM/general-purpose address windows, context ID and CID offset registers, software interrupt registers, IRQ masks, ARC SEI/REI status/clear/mask/halt registers, ECC syndrome/address registers, LBW terminate error captures, DCCM queue push/pop/control/status registers, ARC cache/pipeline controls, and QMAN interrupt mask/status registers.

## Control flow
There is no C flow. PDMA firmware/ARC startup writes reset vector and address windows, releases the ARC, signals via software interrupts, and monitors run/halt acknowledgement. Reset/error flows halt the ARC and read SEI/REI/ECC/termination diagnostics.

## State and persistence
Hardware persists ARC execution state, address mappings, interrupt masks/pending bits, context IDs, ECC records, DCCM queue state, and QMAN interrupt status until reset or reprogramming.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with PDMA QMAN and core registers. It is structurally parallel to the NIC ARC auxiliary map, allowing shared ARC helper code with per-block bases.

## Risks and test signals
Bad memory-window setup can make PDMA ARC firmware fetch from the wrong address or corrupt memory. Interrupt-mask errors can hide ARC fatal conditions. Test signals include PDMA ARC firmware ready, halt/run handshake completion, software interrupt delivery, no unexpected ECC/SEI/REI status under DMA load, and useful diagnostics on injected ARC faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_arc_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_nonsecured_regs.h

## Purpose
`pdma0_qm_axuser_nonsecured_regs.h` defines AXUSER attributes for non-secured PDMA0 queue-manager traffic.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_AXUSER_NONSECURED_*` macros for HB ASID, MMU bypass, ordering, no-snoop, write reduction, read atomic, QoS, reserved/page/core/E2E metadata, read/write override low/high registers, and LB coordinate/lock/reserved/override controls. It has no functions or types.

## Control flow
No code executes. Initialization programs these registers before non-secure PDMA queue traffic is enabled. Queue submissions then inherit this transaction metadata when the QMAN reads/writes queues or messages.

## State and persistence
The hardware persists non-secure QMAN AXUSER policy until reset or reconfiguration. It governs a traffic class, not individual software descriptors.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block integrates with `pdma0_qm_axuser_secured_regs.h`, PDMA QMAN setup, MMU/security mode, and fabric protection configuration.

## Risks and test signals
Incorrect non-secure attributes can cause queue reads/writes to bypass translation wrongly or fail protection checks. Test signals include non-secure PDMA queue submission, MMU/protection fault injection, no-snoop/coherency validation, and correct behavior when switching security modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_secured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_secured_regs.h

## Purpose
`pdma0_qm_axuser_secured_regs.h` defines AXUSER attributes for secured PDMA0 queue-manager traffic.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_AXUSER_SECURED_*` macros for HB ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved/page/core/E2E metadata, read/write override registers, and LB coordinate/lock/reserved/override controls. No C functions or types exist.

## Control flow
There is no executable flow. Secure-mode initialization programs these attributes before secured QMAN queues or firmware-controlled submissions run. Hardware applies them to secured PDMA QMAN AXI transactions.

## State and persistence
The attributes persist as secured traffic policy until reset or explicit reprogramming. They must stay consistent with firmware security expectations and the MMU/protection tables.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with the non-secured AXUSER block, PDMA QMAN/core setup, and `gaudi2_security.c`.

## Risks and test signals
Wrong secured attributes can break secure firmware operation or accidentally downgrade protected traffic. Test signals include secure PDMA queue operation, protection tests distinguishing secured from non-secured traffic, correct ASID/MMU behavior, and no APB/fabric secure-write errors during queue traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_secured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_cgm_regs.h

## Purpose
`pdma0_qm_cgm_regs.h` defines the PDMA0 queue-manager clock-gating management register block.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_CGM_CFG`, `mmPDMA0_QM_CGM_STS`, and `mmPDMA0_QM_CGM_CFG1`. There are no types or functions.

## Control flow
The header has no executable control flow. Power or reset code writes the CGM configuration registers and reads status to confirm whether the PDMA0 QMAN clock-gating state is compatible with queue activity, reset, or low-power entry.

## State and persistence
Hardware persists CGM configuration and status until reset or reprogramming. Incorrect state can affect the QMAN even though the PDMA core registers are otherwise correctly configured.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block complements PDMA QMAN, ARC auxiliary, AXUSER, and core maps. It is part of PDMA bring-up, idle, reset, and power-management sequencing.

## Risks and test signals
Clock gating at the wrong time can wedge command processing or hide idle state. Test signals include PDMA queue submission before and after low-power transitions, CGM status matching expected active/idle state, and reset flows that do not time out waiting for the QMAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_cgm_regs.h -->
