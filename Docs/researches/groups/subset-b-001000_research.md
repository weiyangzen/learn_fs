# subset-b-001000 Research

Grouped research for Goya ASIC register headers under `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_3_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_3_regs.h

Purpose: auto-generated Goya register-address map for DMA channel 3, an instance of the `DMA_CH` prototype. It exposes the memory-mapped offsets used to program direct linear DMA and tensor DMA transfers on the fourth DMA channel.

Important APIs/types/functions: no C functions or types are declared. The public interface is the `mmDMA_CH_3_*` macro family at the `0x419000` register window: channel configuration (`CFG0`, `CFG1`, `CFG2`), error/completion message address and data registers, LDMA source/destination/transfer-size/commit registers, status snapshots, read/write rate limit controls, TDMA source and destination base/ROI/size/valid-elements/start-offset/stride registers for five dimensions, and `MEM_INIT_BUSY`.

Control flow: this header has no executable flow. Driver code includes it through `goya_regs.h` and uses the constants as MMIO register identifiers when enabling, stopping, protecting, polling, or diagnosing DMA channel 3. The intended hardware sequence is configure addresses and transfer size, write `COMIT_TRANSFER`, then poll status/error/completion registers.

State and persistence: state lives in device registers, not in host memory. Programmed LDMA/TDMA descriptors, rate limit values, error-message targets, and status snapshots persist in the channel block until hardware reset or overwritten by the driver. `goya_blocks.h` maps the containing block as `mmDMA_CH_3_BASE` with a max offset of `0x200`.

Dependencies and integration: included by `goya_regs.h`; block-level base addresses come from `goya_blocks.h`. `goya_security.c` protects the channel 3 block with `goya_pb_set_block(hdev, mmDMA_CH_3_BASE)`, and `goya_coresight.c` references related DMA channel 3 CoreSight and bus-monitor bases from `goya_blocks.h`.

Risks: generated address drift is high impact because a wrong offset can start transfers from the wrong memory, corrupt destination memory, or hide channel errors. The macro name uses the generated spelling `COMIT_TRANSFER`, so manual code must match the header. TDMA has many repeated dimensional registers, making off-by-one or channel-3/channel-4 copy mistakes easy.

Test signals: compile coverage catches missing macros and include breakage. Runtime signals are successful DMA transfers through channel 3, valid completion messages, idle/status bits clearing after stop or reset, error-message delivery on invalid transactions, security-protection checks in `goya_security.c`, and CoreSight/bus-monitor visibility for DMA channel 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_3_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_4_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_4_regs.h

Purpose: auto-generated Goya register-address map for DMA channel 4, another `DMA_CH` instance. It gives the driver the offsets needed to program the fifth DMA channel's linear and tensor transfer engines.

Important APIs/types/functions: no functions or structs are present. The API is the `mmDMA_CH_4_*` macro set rooted at `0x421000`: global configs, error-message and read/write completion message registers, LDMA source/destination address and size registers, transfer commit, status registers, rate limiting controls, TDMA source/destination base and five ROI dimensions, and `MEM_INIT_BUSY`.

Control flow: the file is declarative. Driver control flow writes these registers via MMIO: initialize configuration and notification targets, stage LDMA or TDMA fields, commit, then observe status/completion/error registers. Stop/reset/protection logic targets the block through `goya_blocks.h`.

State and persistence: channel state is hardware-resident. Descriptors, rate-limiter configuration, error-message configuration, and in-flight transfer state remain in the channel until changed or reset. `goya_blocks.h` defines `mmDMA_CH_4_BASE` and a wider section than channels 0-3, so callers must use the block table instead of inferring layout solely from channel 3.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` protects `mmDMA_CH_4_BASE`; `goya_coresight.c` exposes channel 4 trace, CTI, ETF, SPMU, and bus-monitor bases. The queue-manager 4 register window in `dma_qm_4_regs.h` is adjacent and typically feeds this channel.

Risks: channel 4 is structurally similar to channel 3 but has a different base (`0x421000`) and block section size, so copy-paste errors can program or protect the wrong engine. Incorrect LDMA/TDMA address fields can corrupt device or host memory, and stale completion/error target registers can send notifications to the wrong queue.

Test signals: compile inclusion through `goya_regs.h`, DMA channel 4 transfer smoke tests, error-path tests that force message writes, security block protection validation, status/idle polling after stop/reset, and CoreSight/bus-monitor activity for channel 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_4_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_masks.h

Purpose: auto-generated bitfield definitions for the Goya DMA macro block. It describes field shifts and masks for address range routing, read/write enable and credit throttling, SRAM busy status, and RAZWI transaction capture fields.

Important APIs/types/functions: the API is the `DMA_MACRO_*_SHIFT` and `DMA_MACRO_*_MASK` macro set. Key fields include low-bandwidth range hit/mask/base with 16 entries and 26-bit values, high-bandwidth range hit/mask/base with 8 entries and 50-bit address split into `49_32` and `31_0`, `WRITE_EN`, `WRITE_CREDIT`, `READ_EN`, `READ_CREDIT`, and RAZWI valid/id fields for LBW and HBW reads/writes.

Control flow: there is no executable flow. Driver code combines these masks with `dma_macro_regs.h` addresses to configure the DMA macro's routing windows and credits or to decode captured RAZWI status.

State and persistence: bitfields describe hardware register state. Range tables and credit enables remain in the DMA macro registers until changed or reset. RAZWI valid/id fields persist as hardware diagnostic state until cleared by the device-specific procedure.

Dependencies and integration: pulled into `goya_regs.h`, then `goya_masks.h`. Register addresses live in `dma_macro_regs.h`, block bases in `goya_blocks.h`, and CoreSight/debug visibility for the DMA macro is listed in `goya_coresight.c`.

Risks: masks encode hardware contract width. A wrong high-address split, range mask, or hit-block field could route requests to an unintended target or fail to catch forbidden access. RAZWI IDs are diagnostic/security-relevant; decoding them with the wrong mask can misidentify the offending initiator.

Test signals: compile-time use in DMA setup code, register readback of configured HBW/LBW ranges, successful DMA routing across expected memory windows, RAZWI/error-injection diagnostics, and no unexpected SRAM-busy or credit starvation during stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_regs.h

Purpose: auto-generated address map for the Goya DMA macro block, the shared DMA routing/control layer below the individual DMA queue managers and channels.

Important APIs/types/functions: no functions or types. The `mmDMA_MACRO_*` macros cover LBW range hit/mask/base registers (`0x4B0000` onward), HBW range hit and split mask/base arrays, read/write enable and credit registers, `SRAM_BUSY`, and RAZWI valid/id capture registers for LBW and HBW read/write transactions.

Control flow: declarative register map only. Typical driver flow writes range masks/bases and read/write credits during device initialization, enables the macro, then reads `SRAM_BUSY` or RAZWI capture registers during reset/error handling. Field manipulation depends on `dma_macro_masks.h`.

State and persistence: route range, credit, and enable state lives in the DMA macro MMIO block. Diagnostic RAZWI state is hardware-owned. The block base in `goya_blocks.h` is `mmDMA_MACRO_BASE` with max offset `0x15C`; the register offsets in this file match that range.

Dependencies and integration: included by `goya_regs.h`. `goya_coresight.c` lists DMA macro trace, SPMU, CTI, funnel, and bus-monitor bases; `goya_security.c` indirectly relies on correct block protection and routing constants for safe DMA operation.

Risks: the DMA macro is shared, so bad register addresses affect all DMA channels. Mismatched array counts between address and mask headers can leave some routing windows unconfigured. Credit values can cause deadlock/starvation if programmed inconsistently with router and queue-manager limits.

Test signals: device initialization readbacks, DMA transfers through LBW and HBW routes, RAZWI/security tests, DMA macro CoreSight trace and bus-monitor activity, and stress tests that exercise concurrent DMA channels without credit exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_masks.h

Purpose: auto-generated bitfield definitions for the DMA north router (`DMA_NRTR`), an `IF_NRTR`-style routing block that controls DMA HBW/LBW arbitration, split behavior, address-range mapping, regulators, and scrambling.

Important APIs/types/functions: exposes `DMA_NRTR_*_SHIFT` and `DMA_NRTR_*_MASK` macros. Key groups include HBW/LBW max credits for write request/write response/read request/read response, debug arbitration fields for east/west/north/south/local directions, per-direction max debug credits, split coefficients and split config flags (`FORCE_WAK_ORDER`, `FORCE_STRONG_ORDER`, `DEFAULT_MESH`, read/write rate-limit enables, `B2B_OPT`), split token/timeout fields, HBW/LBW range hit/mask/base fields, regulator enable/result fields, and scrambling enable fields.

Control flow: no code executes here. Driver code writes the paired addresses in `dma_nrtr_regs.h` using these masks to set credit budgets, routing coefficients, range tables, and optional rate limiting. Error handling can read result and diagnostic registers with the same masks.

State and persistence: all state is in router registers. Credits and routing/range configuration persist until rewritten or reset. Regulator and scrambling settings affect subsequent transactions rather than host-side state.

Dependencies and integration: included via `goya_regs.h` and used with `dma_nrtr_regs.h`. `goya_security.c` explicitly protects `mmDMA_NRTR_BASE`, and `goya_blocks.h` maps the block at `0x7FFC1C0000`.

Risks: router credit and range fields shape global DMA traffic. Incorrect masks can starve directions, reorder traffic unexpectedly, or map transactions to an unintended mesh path. The generated typo `WPLIT_WR_TST_TOLEN` must be matched exactly by any code using that register family.

Test signals: boot-time router programming, DMA traffic across all mesh directions, read/write rate-limit behavior, forced error/range-hit tests, register readback of split and range tables, and security tests confirming the router block is protected from untrusted access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_regs.h

Purpose: auto-generated register-address map for the Goya DMA north router (`DMA_NRTR`). It gives the driver MMIO offsets for DMA mesh arbitration, split policy, range routing, regulators, and scrambling.

Important APIs/types/functions: no functions or types. The `mmDMA_NRTR_*` macros cover HBW/LBW max credits, debug arbitration registers for E/W/N/S/L directions, split coefficient slots 0-9, split config and token/timeout registers, HBW range hit plus 8 split low/high mask/base entries, LBW range hit plus 16 mask/base entries, regulator config/result registers, and scrambling controls.

Control flow: declarative. Driver initialization can program credits, split policies, and range tables; runtime diagnostics can read arbitration and range-hit/status registers. Field layout is defined by `dma_nrtr_masks.h`.

State and persistence: router state is hardware-resident and persists until reset or explicit rewrite. It affects all DMA traffic passing through the DMA north-router block. `goya_blocks.h` maps the containing block at `mmDMA_NRTR_BASE` and max offset `0x608`.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` calls `goya_pb_set_block(hdev, mmDMA_NRTR_BASE)`, so these offsets participate in the protected-register layout. The structure mirrors router headers for MME/TPC/PCI blocks, enabling common driver logic to reason about mesh routers.

Risks: incorrect offsets can break global DMA routing, cause deadlock via bad credits, or bypass intended range controls. Address range arrays must stay aligned with the mask header widths. Scrambling/regulator controls can have security and data-integrity impact if programmed incorrectly.

Test signals: successful DMA initialization, transfer throughput under concurrent channels, readback of configured routing ranges, forced bad-route or RAZWI scenarios, rate-limit behavior, and protection-bit checks covering the DMA router window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_masks.h

Purpose: auto-generated bitfield definitions for DMA queue manager 0, the canonical Goya DMA `QMAN` mask header. Because queue-manager instances 1-4 share the same register layout, higher-level macros in `goya_masks.h` reuse many `DMA_QM_0_*` shifts and masks for all DMA QMAN instances.

Important APIs/types/functions: the public interface is `DMA_QM_0_*_SHIFT` and `DMA_QM_0_*_MASK`. Important groups are global enables/stops/flushes/protection/error configuration, secure and non-secure ASID/MMBP properties, idle/error status bits, producer queue base/size/PI/CI/config/push/status/rate-limit fields, completion queue config/pointer/size/control/status/rate-limit/IFIFO fields, command processor message-base addresses, LDMA offset registers, fence read-data/count fields, CP status/current-instruction/barrier/debug fields, and internal PQ/CQ buffer debug access.

Control flow: no local control flow. Driver code uses these masks with `dma_qm_0_regs.h` through `dma_qm_4_regs.h` to enable/stop the queue manager, configure queues, push work, set error messaging and protection, poll idle state, and debug CP/PQ/CQ state.

State and persistence: masks describe persistent device register fields. Queue bases, indices, credits, secure properties, fence counters, and error configuration remain programmed until reset or rewritten. Status fields reflect live hardware execution and error state.

Dependencies and integration: included by `goya_regs.h` and consumed by `goya_masks.h` to build aggregate constants such as `QMAN_DMA_ENABLE`, `QMAN_DMA_STOP`, `QMAN_DMA_ERR_MSG_EN`, and `DMA_QM_IDLE_MASK`. `goya_security.c` uses the queue-manager register addresses to calculate protection-bit masks for each DMA QMAN block.

Risks: this file is a layout authority for all DMA queue managers, not just instance 0. A wrong shift/mask can affect enable/stop semantics, security properties, queue indexing, or error handling across every DMA engine. The mixed global/PQ/CQ/CP/debug register groups make it easy to use a status mask on a control register or vice versa.

Test signals: compile coverage through `goya_masks.h`, queue-manager bring-up, queue push/completion tests, stop/flush/idle polling, secure/non-secure access validation, CP fence tests, error-message injection, and DMA stress tests that validate producer/completion queue accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_regs.h

Purpose: auto-generated register-address map for DMA queue manager 0, the QMAN instance at `0x400000` that schedules and feeds DMA channel 0.

Important APIs/types/functions: no C functions or types. The `mmDMA_QM_0_*` macros describe global config/protection/error/status registers, producer queue base/size/indices/config/push/status/rate-limit registers, completion queue configuration and status registers, command processor message-base and LDMA offset registers, fence counters, CP status/current instruction/barrier/debug registers, and PQ/CQ buffer debug windows.

Control flow: declarative register map. Runtime driver flow uses these addresses to configure queue memory, enable the QMAN, push DMA jobs, process completions, poll idle/stop status, and handle errors. Bitfield operations use `dma_qm_0_masks.h`.

State and persistence: queue configuration, PI/CI indices, CP message bases, security properties, and rate limits live in hardware registers until changed or reset. Queue contents live in memory referenced by the base/size registers; this header only names the control registers.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` calculates protection bit words from many `mmDMA_QM_0_*` addresses, so address alignment and offsets are part of the security model. `goya_masks.h` uses the companion mask header to create DMA QMAN aggregate constants.

Risks: wrong offsets can corrupt queue state or protection-bit calculations. The QMAN register window is cloned across instances, so instance-specific code should not hard-code `DMA_QM_0` when programming channels 1-4 unless deliberately using shared layout masks.

Test signals: queue bring-up, producer/completion queue accounting, command processor fence behavior, error-message generation, stop/idle polling using `DMA_QM_IDLE_MASK`, and protection-bit tests in secure/non-secure execution paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_1_regs.h

Purpose: auto-generated register-address map for DMA queue manager 1, a QMAN clone at `0x408000` that schedules DMA channel 1 work.

Important APIs/types/functions: no functions or types. The `mmDMA_QM_1_*` macros mirror queue manager 0's global, producer queue, completion queue, command processor, fence, status, rate-limit, and debug register layout with instance-1 addresses.

Control flow: no executable flow. Driver code writes these addresses to initialize queues and security properties, pushes descriptors through PQ push registers, observes CQ/CP status, handles errors, and stops/flushes the engine. Bit shifts and masks are reused from `dma_qm_0_masks.h` through `goya_masks.h`.

State and persistence: hardware registers hold queue bases, indices, CP message addresses, credits, fences, error configuration, and status. The state persists until reset or explicit reconfiguration. Queue backing memory is external to this header.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` enumerates `mmDMA_QM_1_*` offsets to set protection bits for the instance-1 QMAN window. The block base is `mmDMA_QM_1_BASE` in `goya_blocks.h`.

Risks: the file is a generated clone, so any divergence from queue manager 0 must be intentional. Using instance-0 addresses when configuring instance 1 would target the wrong channel, while using instance-1 addresses with instance-0 block math would break protection calculations.

Test signals: channel 1 queue execution, stop/idle status, CQ completions, CP fence status, error-message delivery, and security protection readback for the `mmDMA_QM_1_BASE` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_2_regs.h

Purpose: auto-generated register-address map for DMA queue manager 2, the QMAN instance at `0x410000` associated with DMA channel 2.

Important APIs/types/functions: no C API beyond `mmDMA_QM_2_*` macros. It mirrors the QMAN register families: global enable/stop/protection/error/status, PQ base/size/index/push/status/rate-limit, CQ config/pointers/status/rate-limit/IFIFO, CP message-base and LDMA offset registers, fence counters, CP status/current instruction/barrier/debug, and internal PQ/CQ buffer debug access.

Control flow: declarative. The driver uses the constants during QMAN initialization, job submission, completion processing, stop/reset, and error handling. Field definitions come from the shared queue-manager mask layout in `dma_qm_0_masks.h`.

State and persistence: register state is persistent in the hardware block until reset or reprogramming. In-flight work and status are live hardware state; queue buffers are memory referenced by the base registers.

Dependencies and integration: included through `goya_regs.h`; `goya_blocks.h` defines `mmDMA_QM_2_BASE`; `goya_security.c` includes this instance when calculating protected QMAN register ranges.

Risks: address-copy errors between QMAN instances can make the driver poll or program the wrong engine. Since secure properties and error-message registers are per instance, wrong values can create isolation or diagnosability gaps for channel 2 traffic.

Test signals: DMA channel 2 submissions and completions, idle/stop polling, fence and CP status validation, error-injection with message delivery, and protection-bit validation for the `0x410000` register window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_3_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_3_regs.h

Purpose: auto-generated register-address map for DMA queue manager 3, the QMAN instance at `0x418000` that is adjacent to DMA channel 3.

Important APIs/types/functions: no functions or structs. The `mmDMA_QM_3_*` macros provide the same QMAN surface as instances 0-2: global config/protection/error/status, PQ and CQ setup/status/rate-limit registers, CP message and LDMA offset registers, fences, CP status/debug, and queue-buffer debug windows.

Control flow: this is a constants-only header. Runtime code uses it to set up channel 3's queue-manager state, push work, handle completions/errors, and stop or poll the QMAN. Shared bitfields are supplied by `dma_qm_0_masks.h` and aggregate helpers in `goya_masks.h`.

State and persistence: all state is device register state. Queue pointers, indices, credits, secure properties, and error handling remain until reset/rewrite; status and fence counters reflect live channel execution.

Dependencies and integration: included by `goya_regs.h`; protected through `goya_security.c` using QMAN register addresses; block base and section are in `goya_blocks.h`. It pairs with `dma_ch_3_regs.h` and DMA channel 3 CoreSight/bus-monitor block bases.

Risks: channel 3 has both a QMAN window and a separate DMA channel window. Confusing `0x418000` QMAN registers with `0x419000` channel registers can break queue submission or transfer programming. Protection-bit calculations assume these offsets remain aligned on the expected 4-KiB window.

Test signals: channel 3 queue submission/completion, CP fence progress, QMAN stop/idle bits, error-message delivery, protected register access checks, and CoreSight/bus-monitor confirmation during channel 3 workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_3_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_4_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_4_regs.h

Purpose: auto-generated register-address map for DMA queue manager 4, the QMAN instance at `0x420000` that feeds DMA channel 4.

Important APIs/types/functions: exposes only `mmDMA_QM_4_*` macros. The register families are global enable/stop/protection/error/status, producer queue configuration and push/status/rate-limit, completion queue config/status/rate-limit/IFIFO, command processor message bases and LDMA offsets, fence read-data/count, CP status/current instruction/barrier/debug, and internal queue-buffer debug registers.

Control flow: declarative. Driver logic uses these addresses for queue-manager initialization, job push, completion handling, error routing, stop/flush, and diagnostic reads. Bitfields are shared with `dma_qm_0_masks.h`.

State and persistence: queue-manager configuration and status live in the DMA QMAN 4 hardware block. State survives until reset or rewrite; queue memory is external and referenced by base/size registers.

Dependencies and integration: included by `goya_regs.h`, block-base defined by `goya_blocks.h` as `mmDMA_QM_4_BASE`, and protected by `goya_security.c`. It is paired with `dma_ch_4_regs.h` and channel 4 debug/trace bases.

Risks: QMAN 4 and channel 4 are adjacent (`0x420000` and `0x421000`), so off-by-window mistakes are plausible. Incorrect secure properties or error configuration affect isolation and fault handling for this DMA channel.

Test signals: channel 4 queue execution, CQ completions, stop/idle polling, CP fence behavior, forced error-message generation, and protection-bit coverage of the QMAN 4 register window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_4_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_blocks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_blocks.h

Purpose: auto-generated top-level Goya hardware block map. It defines 64-bit base addresses, maximum offsets, and section sizes for router, DMA, MME, SRAM, CPU, MMU, PLL, DDR, PCIe, PSOC, TPC, CoreSight, bus-monitor, and trace blocks.

Important APIs/types/functions: no functions or types. The API is a large macro set such as `mmDMA_NRTR_BASE`, `DMA_NRTR_MAX_OFFSET`, `DMA_NRTR_SECTION`, `mmDMA_QM_0_BASE` through `mmDMA_QM_4_BASE`, `mmDMA_CH_3_BASE`, `mmDMA_CH_4_BASE`, `mmMC_PLL_BASE`, `mmIC_PLL_BASE`, `mmDMA_MACRO_BASE`, `mmMME1_RTR_BASE`, and many CoreSight/debug block bases. The repeated triplet pattern lets driver code reason about block windows and protection/register access limits.

Control flow: none in the header. Runtime code uses base macros to configure protected blocks, locate CoreSight components, validate register offsets, and translate block-relative register maps into full device addresses.

State and persistence: the file itself is static compile-time metadata. It describes persistent device address space layout but stores no runtime state. Hardware block state persists in the MMIO regions named here.

Dependencies and integration: included by `goya_regs.h`, then indirectly by `goya_masks.h`, `goya.c`, `goya_security.c`, and `goya_coresight.c`. `goya_security.c` calls protection helpers on block bases such as `mmMME1_RTR_BASE`, `mmDMA_NRTR_BASE`, `mmDMA_CH_3_BASE`, and `mmDMA_CH_4_BASE`. `goya_coresight.c` uses CoreSight, SPMU, CTI, funnel, and bus-monitor bases from this header.

Risks: this is a root address authority. A bad base, max offset, or section size can redirect MMIO to the wrong hardware, leave registers unprotected, or make debug discovery operate on the wrong component. Section sizes are not uniform; deriving instance layout arithmetically instead of using macros can fail.

Test signals: driver probe succeeds, protected-block setup covers expected windows, CoreSight registration finds the expected components, DMA/MME/TPC/PCIe register access lands in valid ranges, and register access tests do not trigger unexpected bus faults or RAZWI events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_blocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_masks.h

Purpose: hand-maintained aggregate mask header for Goya register programming. It builds convenient multi-bit constants for queue-manager enable/stop/error/protection, reset control, interrupt decoding, idle checks, and a few cross-instance aliases.

Important APIs/types/functions: no functions or types. Key macros include `QMAN_DMA_ENABLE`, `QMAN_DMA_FULLY_TRUSTED`, `QMAN_DMA_PARTLY_TRUSTED`, `QMAN_DMA_STOP`, `QMAN_DMA_IS_STOPPED`, `QMAN_DMA_ERR_MSG_EN`, equivalent MME/TPC QMAN and CMDQ enable/stop/error/protection masks, reset masks (`DMA_MME_TPC_RESET`, `RESET_ALL`, `CA53_RESET`, CPU reset assert/deassert masks), HBW/LBW interrupt ID decoding masks and shifts, idle masks (`DMA_QM_IDLE_MASK`, `TPC_QM_IDLE_MASK`, `TPC_CMDQ_IDLE_MASK`, `TPC_CFG_IDLE_MASK`, `MME_QM_IDLE_MASK`, `MME_CMDQ_IDLE_MASK`, `MME_ARCH_IDLE_MASK`, `MME_SHADOW_IDLE_MASK`), TPC stall aliases, DMA QMAN stop-shift aliases for instances 1-4, and PSOC ETR AXI control masks.

Control flow: no executable flow, but these macros encode control decisions used by driver flows: enable engines, stop/flush engines, configure trusted/protected behavior, enable error messages/stop-on-error, assert resets, decode interrupts, and poll idleness before reset or power transitions.

State and persistence: the macros are compile-time constants. They affect persistent hardware state when written into Goya MMIO registers by the driver. Idle and interrupt masks decode live status/error words.

Dependencies and integration: includes `goya_regs.h`, which pulls in all needed register and bitfield headers. Included by `goya.c` and `goya_coresight.c`; it centralizes bit combinations so device initialization and teardown code do not repeat long shift expressions.

Risks: unlike the generated address headers, this file composes behavior. Missing a stop/error/protection bit can leave a hardware subunit active, unprotected, or silent on fault. Over-broad reset masks can reset more of the chip than intended. Aggregate masks based on instance-0 bitfields assume identical layouts across cloned queue managers.

Test signals: device bring-up and teardown, stop/idle polling before reset, reset sequencing, interrupt decode correctness, error injection that checks stop-on-error and message generation, and secure/non-secure access tests for trusted/partly trusted DMA modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_regs.h

Purpose: umbrella register include for the Goya ASIC. It aggregates block-base definitions, per-block register-address headers, selected mask headers, and a small set of chip-level register aliases into one include for Goya driver code.

Important APIs/types/functions: no functions or structs. Its public surface is all included `mm*` register macros and bitfield masks, plus local aliases for PCIe DBI device/MSI-X doorbell registers, sync-manager SOB and monitor ranges, and `mmGIC_DISTRIBUTOR__5_GICD_SETSPI_NSR`. It includes the DMA headers in this work item (`dma_qm_0_regs.h` through `dma_qm_4_regs.h`, `dma_ch_3_regs.h`, `dma_ch_4_regs.h`, `dma_macro_regs.h`, `dma_nrtr_regs.h`, `dma_macro_masks.h`, `dma_qm_0_masks.h`, `dma_nrtr_masks.h`) and the MME/PLL/router headers.

Control flow: include-time composition only. Driver code includes `goya_regs.h` to gain a single namespace of register macros for initialization, security setup, CoreSight registration, queue programming, MMU/PCIe/PSOC handling, and diagnostics.

State and persistence: no runtime state. It defines compile-time constants that point at persistent hardware registers. Hardware persistence follows each referenced block.

Dependencies and integration: included directly by `goya_security.c` and `goya_coresight.c`, and indirectly by `goya_masks.h` used in `goya.c`. It is the primary integration point tying generated address maps to Goya driver implementation.

Risks: broad umbrella headers hide dependencies. A missing include can break distant driver code; a stale include can expose the wrong register layout. The local sync-manager and PCIe aliases are not in separate generated headers here, so they need the same scrutiny as generated definitions.

Test signals: full Goya driver compile, include-order checks, probe-time register accesses, sync-manager and interrupt tests, PCIe doorbell/device-ID reads, and runtime use by security and CoreSight setup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/ic_pll_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/ic_pll_regs.h

Purpose: auto-generated register-address map for the Goya IC PLL block, an instance of the generic `PLL` prototype controlling interconnect clock generation/division/stability monitoring.

Important APIs/types/functions: no functions or types. The `mmIC_PLL_*` macros cover PLL numerator/frequency/output-divide/bypass configuration (`NR`, `NF`, `OD`, `NB`, `CFG`), loss/lock interrupt and bypass registers, data-change and reset controls, slip watchdog counter, four divider factor/command/select/enable/busy channels, clock gater and relax registers, reference counter period/threshold registers, `PLL_NOT_STABLE`, and frequency calculation enable.

Control flow: declarative. Clock-management code writes factor/divider/reset/config registers, issues divider factor commands, waits for busy/lock/stability status, and configures reference threshold monitoring. This header only supplies addresses.

State and persistence: PLL configuration and divider state live in hardware registers and persist until reset or reprogramming. Lock/stability/busy registers report live hardware state. `goya_blocks.h` maps the block base as `mmIC_PLL_BASE`.

Dependencies and integration: included by `goya_regs.h` together with other PLL headers. It shares the same `PLL` layout as `mc_pll_regs.h`, `cpu_pll_regs.h`, and `tpc_pll_regs.h`, so common PLL-management code can use consistent naming patterns.

Risks: clock programming is high impact. Wrong addresses can destabilize the interconnect, hang MMIO, or cause timing-related data corruption. Divider command/busy sequencing must be respected by caller code; this header does not enforce ordering.

Test signals: clock initialization, PLL lock interrupts/status, divider factor readback, frequency calculation/stability status, suspend/resume or reset clock reprogramming, and stress tests under interconnect load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/ic_pll_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mc_pll_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mc_pll_regs.h

Purpose: auto-generated register-address map for the Goya MC PLL block, the memory-controller clock PLL instance using the generic `PLL` prototype.

Important APIs/types/functions: no C functions or types. `mmMC_PLL_*` macros describe the same PLL register families as IC PLL but rooted at `0x4A1100`: `NR`, `NF`, `OD`, `NB`, `CFG`, lock/loss/reset/data-change controls, slip watchdog, four divider factor/command/select/enable/busy groups, clock gater/relax registers, reference counter period and thresholds, `PLL_NOT_STABLE`, and frequency calculation enable.

Control flow: constants-only. Clock or hardware-manager code programs PLL ratios and dividers, commands divider updates, waits for busy/lock/stability status, and monitors reference thresholds through these addresses.

State and persistence: configuration persists in the MC PLL hardware until reset or rewrite. Busy/lock/not-stable fields are live hardware status. `goya_blocks.h` maps the containing block as `mmMC_PLL_BASE`.

Dependencies and integration: included by `goya_regs.h`. Its layout mirrors `ic_pll_regs.h`, enabling shared PLL-management assumptions while preserving the MC-specific base address.

Risks: MC PLL mistakes can destabilize memory-controller timing, leading to hangs or memory data loss. Because the register names are a clone of other PLLs, base-address confusion between MC and IC/CPU/TPC PLLs is a realistic integration risk.

Test signals: memory-clock bring-up, PLL lock/stability checks, divider programming readback, memory stress under configured clocks, and reset/suspend/resume paths that reinitialize or validate the MC PLL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mc_pll_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_masks.h

Purpose: auto-generated bitfield definitions for MME router 1, an `MME_RTR` block. It describes HBW/LBW arbitration, credit, split, range, regulator, and scrambling fields for traffic entering or leaving the first MME router.

Important APIs/types/functions: no functions or types. The `MME1_RTR_*_SHIFT` and `MME1_RTR_*_MASK` macros cover HBW read-request, read-response, write-request, and write-response arbitration across east/west/north/south/local directions; HBW per-direction max credits and request/response max credits; LBW read/write request/response arbitration and credits including SRAM master/slave credits; debug arbitration and max-credit fields; split coefficients/config/rate-limit token/timeout fields; HBW and LBW range hit/mask/base fields; regulator enables/results; and scrambling controls.

Control flow: no executable flow. Driver initialization can use these masks with `mme1_rtr_regs.h` to configure MME mesh routing, credit budgets, range mapping, and optional regulator/scrambling behavior. Diagnostic paths can decode arbiter/range/regulator status.

State and persistence: all described fields are hardware register fields. Arbitration weights, credits, split configuration, range tables, and regulator/scrambling settings persist until reset or rewrite. Status/result fields reflect live or latched hardware diagnostics.

Dependencies and integration: included through `goya_regs.h` and paired with `mme1_rtr_regs.h`. `goya_security.c` protects `mmMME1_RTR_BASE`, and `goya_coresight.c` references MME1 router funnel/debug bases from `goya_blocks.h`. The layout is similar to DMA and TPC router mask headers, supporting common routing concepts.

Risks: MME router masks control performance, ordering, and address routing for accelerator traffic. Bad credit/arbitration masks can starve a direction or deadlock traffic; bad range masks can route requests incorrectly; regulator/scrambling mistakes can affect security or data integrity. The generated typo `WPLIT_WR_TST_TOLEN` must be preserved when referenced.

Test signals: MME workload throughput and correctness, router credit/range readback, error injection or range-hit diagnostics, reset/reprogramming paths, protected-register access checks for `mmMME1_RTR_BASE`, and performance tests under concurrent MME/DMA/TPC traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_regs.h

Purpose: auto-generated register-address map for MME router 1, the first MME mesh router block using the `MME_RTR` prototype.

Important APIs/types/functions: no functions or structs. The `mmMME1_RTR_*` macros map HBW read-request/read-response/write-request/write-response arbitration and credit registers, LBW arbitration and credits, debug arbitration and max credits, split coefficients and config/token/timeout controls, HBW and LBW range hit/mask/base arrays, regulator config/result registers, and scrambling controls.

Control flow: declarative. Driver initialization and tuning code can program routing and credit tables, split behavior, range maps, and regulator/scrambling settings using these offsets and `mme1_rtr_masks.h`. Diagnostic code can read arbitration, range-hit, and result registers.

State and persistence: router state is in hardware. Programmed arbitration weights, credits, range tables, and split config persist until reset or rewrite; status/result registers expose current or latched hardware behavior. `goya_blocks.h` defines `mmMME1_RTR_BASE` and max offset `0x608`.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` protects the MME1 router block, and `goya_coresight.c` references related MME1 router funnel/CoreSight bases. The register layout parallels other router headers such as `dma_nrtr_regs.h`.

Risks: MME router misprogramming can affect accelerator traffic ordering, throughput, and address routing. Incorrect offsets or array bounds can overwrite the wrong router controls. Since this is one MME router among several, using MME1 addresses for other MME instances would target the wrong hardware.

Test signals: MME workload execution, router configuration readbacks, traffic/performance counters under load, range-hit diagnostics, regulator/scrambling validation where supported, reset sequencing, and protected-block access checks for the MME1 router window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_regs.h -->
