# subset-b-001001 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme2_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme2_rtr_regs.h

## Purpose

`mme2_rtr_regs.h` is an auto-generated Goya ASIC register-offset header for the `MME2_RTR` block, whose prototype is `MME_RTR`. It gives C preprocessor names to MMIO addresses in the MME2 router block. The router is part of the internal fabric around the matrix-math engine path and exposes arbitration, credit, split, range-match, range-base, register-lane, and scrambler control registers.

## Important APIs, types, and data

There are no functions, structs, enums, or inline helpers. The only API is the macro namespace `mmMME2_RTR_*`. Important groups are HBW read/write request and response arbitration registers, LBW read/write request and response arbitration registers, per-direction arbitration maxima, HBW and LBW credit limits, debug arbitration controls, ten `SPLIT_COEF_*` registers, split read/write saturation and timeout controls, HBW range hit/mask/base registers, LBW range hit/mask/base registers, `RGLTR` read/write-result registers, and `SCRAMB_EN`/`NON_LIN_SCRAMB`.

The address span starts at `0x80100` and ends at `0x80604`, with the implicit block base around `0x80000`. HBW range state uses eight mask/base slots split into low and high halves; LBW range state uses sixteen mask/base slots. The same register layout appears in the sibling MME router headers with a different base address.

## Control flow

The file has no executable control flow. Runtime control flow appears in consumers that include generated Goya register headers and pass these constants to `RREG32()`/`WREG32()`-style MMIO helpers. Typical sequences configure fabric credits and arbitration before engine traffic is enabled, install range masks before exposing address windows, read range-hit/debug state during fault handling, and update scrambler controls during device initialization or low-level diagnostics.

## State and persistence behavior

The macros are compile-time constants and persist only through compiled code. Writes to the named registers change volatile device hardware state. Router range registers and scrambler controls can affect all subsequent traffic through this router until a reset or reprogramming; debug and hit registers are hardware-observable state rather than host persistence. The header itself does not allocate memory, store host state, or serialize configuration.

## Dependencies and integration points

The header depends only on normal C preprocessing and its include guard. It is generated from the Goya register database and is consumed by Goya device code, low-level security/range programming, coresight/performance plumbing, and any diagnostic path that needs direct router MMIO offsets. It integrates with sibling generated headers that provide masks for related fields and with common HabanaLabs register access helpers.

## Risks and edge cases

The main risk is address drift between this generated file and the hardware spec. A single wrong offset can cause writes to another router register or to an adjacent block. HBW masks are split across low/high registers while LBW masks are not, so code must not mechanically reuse LBW programming for HBW. Range endpoints and split timeouts are fabric-sensitive; overbroad masks can route or block unintended traffic. `WPLIT_WR_TST_TOLEN` appears with a likely generator spelling anomaly and should be treated as an ABI macro name, not corrected by hand.

## Test signals

Static signals are successful compilation of all Goya code that includes generated register headers and grep-based checks that the MME2 router namespace remains unique. Runtime signals include successful Goya probe/reset, no unexpected router protection or range-hit errors during MME workloads, expected values when debugfs or low-level diagnostic code reads these offsets, and correct behavior after programming LBW/HBW ranges around restricted regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme2_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme3_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme3_rtr_regs.h

## Purpose

`mme3_rtr_regs.h` is the generated register-offset map for the Goya `MME3_RTR` block. It represents the same `MME_RTR` prototype as `MME2_RTR`, but relocated to the MME3 router address window. The macros let driver code name MME3 fabric-router registers without embedding numeric MMIO constants.

## Important APIs, types, and data

This file exports only `#define` constants in the `mmMME3_RTR_*` namespace. The register families are HBW arbitration and credit control, LBW arbitration and SRAM credit control, debug arbitration maxima, split coefficients and split read/write timeout controls, HBW and LBW range-hit/mask/base programming, register-lane access/result registers, and scrambler controls.

The first listed register is `mmMME3_RTR_HBW_RD_RQ_E_ARB` at `0xC0100`; the final register is `mmMME3_RTR_NON_LIN_SCRAMB` at `0xC0604`. Relative offsets match `mme2_rtr_regs.h`, so this file is a base-address specialization rather than a distinct programming model.

## Control flow

No control flow exists inside the header. Consumers use these constants in MMIO access sequences for router initialization, range setup, fabric debugging, and reset recovery. When software needs to apply one policy across several MME routers, it can use the repeated layout and substitute the MME3 base window.

## State and persistence behavior

The header has no mutable host state. Hardware writes to MME3 router registers persist in the device until reset or replacement writes. Range-base/mask registers determine what addresses the MME3 router recognizes, arbitration and credit registers affect live traffic scheduling, and scrambler controls affect address/data transformation behavior on the path.

## Dependencies and integration points

The file depends only on its include guard and the generated-register inclusion convention. It integrates with Goya initialization, security/range programming, coresight/monitoring code that maps MME router trace/funnel blocks, and common register access macros. The sibling router files are direct peers and should remain layout-compatible.

## Risks and edge cases

Because the file is auto-generated, hand edits are risky and would diverge from the authoritative register database. Code that computes offsets across router instances must account for the `0x40000` stride between these MME router blocks. HBW uses split high/low mask and base fields; LBW uses a single 32-bit mask/base per slot. Misprogramming range slots can silently redirect, expose, or block fabric traffic.

## Test signals

Compile coverage should prove that all macros referenced by Goya code exist. Runtime validation is successful probe/reset and MME workload execution with no unexpected MME3 router range-hit or fabric errors. Low-level register dump tools should show MME3 values at the `0xC0xxx` window while preserving the same relative layout as other MME router instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme3_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme4_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme4_rtr_regs.h

## Purpose

`mme4_rtr_regs.h` maps the Goya `MME4_RTR` fabric-router register block. It is generated from the `MME_RTR` prototype and provides stable preprocessor names for MME4 router MMIO offsets used by kernel driver initialization, diagnostics, and range-control paths.

## Important APIs, types, and data

There are no C APIs beyond `#define` constants. The `mmMME4_RTR_*` namespace covers HBW read/write request and response arbitration, HBW credit limits, LBW arbitration and SRAM credits, debug arbiters, split coefficients/configuration, split read/write saturation/reset-token/timeout fields, HBW and LBW range-hit/mask/base arrays, `RGLTR` access/result registers, and scrambler enable/non-linear scrambler controls.

The MME4 register window starts with `mmMME4_RTR_HBW_RD_RQ_E_ARB` at `0x100100` and reaches `mmMME4_RTR_NON_LIN_SCRAMB` at `0x100604`. It is layout-identical to MME2, MME3, MME5, and MME6 router headers except for base address.

## Control flow

The header itself is declarative. Driver code consumes these constants when programming router policy or reading hardware state. Typical control flow is: reset or quiesce the relevant path, write arbitration/credit/range/scrambler registers, enable traffic, then read status/range-hit/debug registers when diagnosing faults.

## State and persistence behavior

Only hardware state changes when these constants are used in MMIO writes. The register contents live in the device and are not persisted by this header. Range masks and bases may remain effective across command submissions, while status and hit registers reflect current or latched hardware observations.

## Dependencies and integration points

This generated file is included by Goya register umbrella headers and low-level device code. It integrates with common HabanaLabs MMIO helpers, Goya reset/security code, and fabric observability through coresight-related blocks. Its main contract is that relative offsets match the `MME_RTR` prototype used by the other router instances.

## Risks and edge cases

A wrong MME4 base or stride calculation can write into a different block. Since this file has no masks, consumers must pair it with the correct field definitions or full-register values from hardware documentation. HBW range programming requires careful low/high pairing. Generated spelling and naming must be treated as ABI for in-tree code even if awkward.

## Test signals

Builds should catch missing macro names. Runtime signals include clean Goya initialization, no MME4 router-related unexpected fault logs, correct register dump ordering from `0x100100` through `0x100604`, and consistent behavior when the same router configuration is applied to MME2-MME6 instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme4_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme5_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme5_rtr_regs.h

## Purpose

`mme5_rtr_regs.h` is the generated Goya register map for the `MME5_RTR` router. The block follows the `MME_RTR` prototype and participates in routing high-bandwidth and low-bandwidth traffic around the MME fabric. The header gives symbolic names to the MME5 router MMIO offsets.

## Important APIs, types, and data

The exported surface is the `mmMME5_RTR_*` macro set. It includes HBW and LBW arbitration registers for east/west/north/south/local directions, maximum arbitration counters, credit controls, debug arbiters, split coefficients and split control fields, HBW range hit plus eight split low/high mask/base entries, LBW range hit plus sixteen mask/base entries, register-lane result registers, and scrambler controls.

The address window is `0x140100` through `0x140604`. Relative offsets are the same as the other generated MME router instances, enabling instance-generic code if it computes or tables the base correctly.

## Control flow

There is no internal logic. Consumers write these offsets during fabric setup and read them during diagnostics. Range and scrambler setup should happen while the relevant router traffic is safely quiesced or during early initialization; debug/range-hit reads may occur in fault paths.

## State and persistence behavior

The header has no host-side state. MMIO writes to these registers update volatile device state that persists across workloads until reset/reconfiguration. Arbitration and credit settings shape scheduling; range registers define address recognition; hit/result registers provide hardware observation.

## Dependencies and integration points

The file depends on generated-header inclusion and standard preprocessing. It integrates with Goya-specific initialization, security/range programming, and hardware monitoring paths through common register access helpers. It should be regenerated with the rest of the Goya ASIC register set rather than edited independently.

## Risks and edge cases

The repeated layout invites mechanical loops, but any loop must use the correct base stride and must not assume every MME-adjacent block follows the router layout. Range masks are easy to mispair, especially HBW low/high halves. Bad arbitration or credit values can create performance stalls or fabric starvation rather than immediate compile-time failures.

## Test signals

Useful checks are a clean module build, register-dump comparison against the expected MME5 window, successful MME command execution under load, absence of unexpected range-hit/fabric errors, and regression coverage for any code that applies router range programming across all MME router instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme5_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme6_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme6_rtr_regs.h

## Purpose

`mme6_rtr_regs.h` is the generated register-offset map for the Goya `MME6_RTR` block. It supplies symbolic MMIO offsets for the final MME router instance in this header group and shares the `MME_RTR` prototype layout with MME2-MME5.

## Important APIs, types, and data

The file defines only `mmMME6_RTR_*` macros. The key register groups are HBW arbitration and credit controls, LBW arbitration and SRAM credit controls, debug arbiters and maxima, split coefficients and split read/write control, HBW and LBW range hit/mask/base arrays, `RGLTR` read/write-result registers, and scrambler enable/non-linear scrambler registers.

The address range is `0x180100` to `0x180604`. HBW range entries are eight-slot low/high pairs; LBW range entries are sixteen single-register mask/base slots.

## Control flow

The header is declarative, with no branches or calls. Device code uses these constants for MMIO reads/writes during router setup, reset, security/range configuration, and hardware debug. Any multi-router sequence should treat this file as the `0x180000` base specialization of the common router layout.

## State and persistence behavior

State is in hardware only. Writes to arbitration, split, range, and scrambler registers persist in the MME6 router until reset or overwrite. Reads of range-hit and result registers observe the device state; no host persistence is created by the header.

## Dependencies and integration points

It depends on the generated register database and include guard. Integration points are Goya low-level register programming, fabric diagnostics, security/range policies, and common HabanaLabs MMIO access helpers. The sibling router headers form a consistency set and should be regenerated together.

## Risks and edge cases

The final router instance has the largest address base in this group, so integer type assumptions in consumers should preserve full offsets. Manual correction of generated names can break include users. Misprogrammed range registers may only show up as later fabric faults or inaccessible address windows, making runtime validation important.

## Test signals

Compile all Goya/HabanaLabs code, run Goya probe/reset, execute MME workloads, and inspect any router range-hit or scrambler-related debug output. Register dumps should show the same relative layout as MME2-MME5 at the `0x180xxx` address window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme6_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_masks.h

## Purpose

`mme_cmdq_masks.h` defines generated bit shifts and masks for the Goya MME command-queue (`MME_CMDQ`) register block. It complements `mme_cmdq_regs.h`: that file names register offsets, while this file names the fields packed into each 32-bit register.

## Important APIs, types, and data

The file exports `MME_CMDQ_*_SHIFT` and `MME_CMDQ_*_MASK` macros. Important field groups include global enables for PQF, CQF, CP, and DMA; stop/flush bits; protection and error-protection bits; error interrupt/message/stop-on-error controls; error address/write-data capture fields; secure and non-secure ASID/MMBP properties; global idle/stop/error status; CQ credit and max-inflight fields; CQ pointer/size/control and mirrored status fields; CQ credit/free/inflight/busy/empty status; read-rate limiter token/saturation/timeout fields; CP message-base addresses; LDMA descriptor offset registers; four fence read-data and count registers; CP ready/stop/fence status bits; current instruction low/high fields; barrier guard bits; and CQ debug buffer access fields.

There are no types or functions. All full-width address/data fields use `0xFFFFFFFF`, small counters use narrow masks such as `0xFFFF`, `0xFF`, `0xF`, or `0x3`, and control flags occupy individual bits.

## Control flow

No executable control flow is present. Consumers combine shifts and masks when constructing values for `WREG32()` or decoding values from `RREG32()`. A typical queue setup flow writes secure/non-secure properties, CQ pointer/size/control registers, CP message bases, LDMA offsets, error configuration, protection bits, and finally enables the command queue. Error or reset flow reads status/error fields, may request stop/flush, waits for idle/stop status, and clears or reinitializes state.

## State and persistence behavior

The macros themselves are stateless. The hardware fields they describe control persistent device state for the lifetime of the current queue configuration: ASID/MMBP security context, command buffer location, CP message routing, rate limiting, fence counters, and stop-on-error behavior. Error capture fields are latched hardware state until cleared by the corresponding device logic.

## Dependencies and integration points

This header integrates with `mme_cmdq_regs.h`, common queue-management code, and Goya MME command submission. It shares the same CMDQ prototype field layout as other HabanaLabs command queue blocks. Driver code must use the masks with the matching MME_CMDQ offsets; mixing them with QMAN offsets is only safe where the underlying CMDQ/QMAN prototype fields are intentionally identical.

## Risks and edge cases

Field packing is dense in global config, status, and CP status registers. Incorrect shifts can enable DMA/CP without the queue frontend, fail to stop on errors, or misdecode busy/idle state. ASID fields are 10 bits; truncation or stale ASID programming can route transactions through the wrong address space. Fence counters and increment values are narrow and can wrap if interpreted as full 32-bit counters. Full-width pointer fields are split across low/high registers and must be updated coherently.

## Test signals

Compile-time tests should verify every referenced MME_CMDQ field macro exists. Runtime signals include successful MME command queue initialization, correct idle/stop transitions on reset, expected CP fence behavior, no unexpected CQ busy/empty deadlocks, and accurate error logs when injected malformed or unauthorized command queue accesses trip `GLBL_STS1` or error capture registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_regs.h

## Purpose

`mme_cmdq_regs.h` provides generated MMIO offsets for the Goya `MME_CMDQ` block, whose prototype is `CMDQ`. It is the register-address companion to `mme_cmdq_masks.h` and identifies where the driver programs the MME command queue, command processor, LDMA offsets, fences, and debug buffer.

## Important APIs, types, and data

The file defines only `mmMME_CMDQ_*` offset macros. The global register range starts at `0xD9000` with `GLBL_CFG0`, `GLBL_CFG1`, protection, error capture, secure/non-secure properties, and global status. The CQ area begins at `0xD90B0` and includes configuration, ARUSER, pointer low/high, transfer size, control, status mirrors, credit/busy/free status, and read-rate limiter registers. The CP section from `0xD9120` includes four message-base address pairs, LDMA source/destination/size/commit offset registers, four fence read-data/count pairs, CP status, current instruction, barrier config, and debug. The debug CQ buffer access registers live at `0xD9308` and `0xD930C`.

There are no functions, structs, or side-effecting macros.

## Control flow

The header is read-only metadata. Device code uses these offsets to program queue state in a specific order: configure global protection/error policy, initialize CQ descriptors and limits, configure CP message and LDMA metadata, enable the relevant frontends, and later poll status or fence registers. Reset/teardown paths write stop/flush bits through `GLBL_CFG1` and check idle/stop status through the matching masks.

## State and persistence behavior

The file itself has no state. The addressed registers hold live queue state, including command buffer pointers, current instruction, CP message bases, LDMA offsets, fence counters, and error captures. These values persist in hardware across command submissions until reset or reinitialization.

## Dependencies and integration points

It depends on the Goya generated-register include model and pairs with `mme_cmdq_masks.h` for field composition. It integrates with HabanaLabs queue initialization, command submission, reset, and debug code using `RREG32()`/`WREG32()`. It is closely related to `mme_qm_regs.h`; the QMAN block includes both PQ and CQ, while this command-queue block exposes the command/CQ side at the `0xD9xxx` window.

## Risks and edge cases

Pointer and size registers are split and must be programmed consistently. Enabling the CP or DMA before message bases and LDMA offsets are valid can cause memory errors. Debug buffer reads must use the buffer address/data protocol rather than arbitrary MMIO assumptions. Because this file has only offsets, consumers must use the matching mask header to avoid writing reserved or mispositioned bits.

## Test signals

Build the driver, run Goya queue initialization, submit MME commands, verify CP current-instruction and fence status change as expected, and validate reset paths stop and flush the queue without leaving busy bits stuck. Error injection should populate `GLBL_ERR_ADDR_*`, `GLBL_ERR_WDATA`, and `GLBL_STS1` consistently with the masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_masks.h

## Purpose

`mme_masks.h` defines generated field masks and shifts for the Goya MME tensor-engine register block. It describes how to encode and decode the architectural descriptor, execution controls, debug memory, credit controls, interrupt masks/status, and four shadow descriptor banks defined by `mme_regs.h`.

## Important APIs, types, and data

The file exports only `MME_*_SHIFT` and `MME_*_MASK` macros. Key architectural fields include `ARCH_STATUS` bits for A, B, CIN, COUT, TE, load/store, scoreboard emptiness, AXI idle state, and free accumulators; high/low base-address fields for A/B/CIN/COUT/BIAS tensors; `ARCH_HEADER` controls for signaling, transpose/lower-A, accumulation mask, bias/CIN load, output store, accumulator increment disables, tensor advance bits, compressed B, convolution-end masking, and data types; kernel-size and associated-dimension fields; COUT/CIN scaling; GEMMLOWP zero points, exponents, multiply enables, accumulation, bias accumulation, and ReLU enable; ROI base offsets, valid elements, loop strides, ROI sizes, spatial starts/strides, and spatial sizes for A/B/C tensors; sync-object message value/address/operation; padding, iteration, and split-bubble fields.

Execution and infrastructure fields include `MME_CMD_EXECUTE`, reset, stall, shared-memory base, debug-memory address/data/control/read-complete flags, log-shadow masks, store/AGU/SBA/SBB/SBC/WBC credit controls, ASID/MMBP control data for MME memory clients, TE credits, and REI/SEI/SPI status and masks. The shadow sections repeat the descriptor field layout for shadow banks 0 through 3.

## Control flow

No control flow exists in the header. Runtime code uses these masks to build descriptor words, program the live architectural registers or shadow descriptor banks, issue `MME_CMD_EXECUTE`, then poll status/interrupt/debug state. Shadow-bank fields allow the hardware or driver to retain multiple pending/logged descriptor images while execution state advances.

## State and persistence behavior

The macros are stateless constants. The fields they describe are persistent hardware state until reset or overwrite. Tensor base addresses and ROI/stride/dimension fields define memory accesses for MME operations. Header fields control whether inputs are advanced, outputs are stored, quantization/ReLU is applied, and sync-object messages are emitted. Status and shadow registers are observability state and can be used after errors to reconstruct which descriptor was active or logged.

## Dependencies and integration points

This header must match `mme_regs.h` exactly. It integrates with Goya command submission, descriptor construction, reset/stall/debug paths, interrupt handling, and ASID/MMU programming. It also connects to common HabanaLabs memory-management behavior because ASID/MMBP fields and tensor base addresses determine how MME transactions are translated.

## Risks and edge cases

This is a high-blast-radius field map. Incorrect descriptor field packing can make the MME read or write the wrong tensor memory, apply wrong data types, fail to signal completion, or corrupt accumulators. Address fields are split high/low and must be coherent. The header contains many repeated shadow-bank macros; consumers must use the bank matching the hardware state they intend to inspect or program. Narrow fields such as signal mask, kernel dimensions, zero points, exponents, and credit counts can truncate silently if callers fail to validate inputs.

## Test signals

Static validation is a successful build and generated-header consistency checks between live and shadow field names. Runtime signals include correct MME numerical output for representative GEMM/convolution workloads, expected completion signaling through sync objects, clean reset/stall recovery, meaningful shadow descriptor dumps after injected failures, no unexpected REI/SEI/SPI interrupts, and MMU/ASID tests proving MME reads and writes occur in the intended address space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_masks.h

## Purpose

`mme_qm_masks.h` defines generated bit masks and shifts for the Goya MME queue manager (`MME_QM`) block. It describes both the producer queue (PQ) and completion/command queue (CQ) sides of the QMAN prototype, along with global protection/error state, command processor metadata, fences, and debug buffers.

## Important APIs, types, and data

The file exports `MME_QM_*_SHIFT` and `MME_QM_*_MASK` macros. Global fields cover PQF/CQF/CP/DMA enable, stop, flush, protection, error interrupt/message/stop-on-error policy, captured error address/write data, secure and non-secure ASID/MMBP properties, idle/stop status, and read/undefined-command/message/DMA error status.

PQ-specific fields include base low/high, queue size, producer/consumer indices, credit limit, max inflight, ARUSER no-snoop/word flags, four push words for pointer/size/control, credit/free/inflight/busy/empty status, and read-rate limiter controls. CQ fields mirror pointer, size, control, status, credit, busy, and rate-limit controls. CP fields include four message-base address pairs, LDMA offset registers, four fence read-data/count fields, CP ready/stop/fence status, current instruction, barrier guard, debug byte, and PQ/CQ buffer address/read-data debug access.

## Control flow

The header contains no executable logic. Consumers use it to construct queue-manager register values during queue creation and reset. A normal setup initializes PQ storage and indices, programs CQ and CP metadata, configures secure/non-secure properties and error handling, then enables PQF/CQF/CP/DMA. Submission updates PQ producer state or push registers; completion and diagnostics read CQ/PQ status, CP status, fence counters, and debug buffer windows.

## State and persistence behavior

The macros are compile-time constants. The hardware fields define persistent queue state across submissions: ring base/size/indices, inflight accounting, rate-limiter settings, CP message routing, LDMA offsets, fence counters, and security context. Error capture/status fields are latched device state and must be cleared by the appropriate reset or acknowledgement logic.

## Dependencies and integration points

This file pairs with `mme_qm_regs.h` and common QMAN programming code. It shares many field layouts with `mme_cmdq_masks.h`, but adds PQ-specific fields. It integrates with Goya queue allocation, doorbell handling, MMU ASID propagation, command submission, CP fence handling, and reset logic.

## Risks and edge cases

Queue state is sensitive to ordering. Enabling queue engines before base/size/ASID/CP metadata is valid can produce DMA or translation faults. Producer and consumer indices are full-width fields but ring size is configured separately; callers must keep them modulo the hardware queue length. Busy/empty bits live at high bits in status registers and should not be confused with inflight counters. ASID/MMBP fields are only 10/1 bits, so stale or truncated security context can misroute MME transactions.

## Test signals

Build-time checks should ensure all MME queue paths reference the correct QMAN field names. Runtime signals include queue initialization without stuck busy bits, successful MME command submission through PQ/CQ, correct fence increments, expected stop/flush idle transitions during reset, and accurate error capture when invalid queue descriptors or protected memory accesses are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_regs.h

## Purpose

`mme_qm_regs.h` provides generated MMIO offsets for the Goya MME queue manager, whose prototype is `QMAN`. It names the registers used to configure MME producer queues, completion queues, command processor message bases, LDMA offsets, fences, status, and debug buffer access.

## Important APIs, types, and data

The exported surface is the `mmMME_QM_*` offset namespace. The block starts at `0xD8000` with global config/protection/error/status registers. PQ registers from `0xD8060` include base low/high, size, producer/consumer indices, PQ config, ARUSER, push words, status, and read-rate limiter controls. CQ registers from `0xD80B0` include config, pointer/size/control, mirrored status, credit/busy/free status, rate limiting, and IFIFO count. CP registers from `0xD8120` include four message-base address pairs, LDMA offset registers, fence read-data/count pairs, CP status/current instruction/barrier/debug, and debug buffer windows from `0xD8300` to `0xD830C`.

There are no functions, data objects, or type declarations.

## Control flow

The file is declarative. Driver queue setup code writes the offsets in a hardware-defined sequence: global policy, PQ ring state, CQ state, CP message/LDMA metadata, and enable bits. Doorbell paths update PQ producer-related registers. Reset paths stop/flush through global config and poll status registers. Diagnostics use current-instruction, fence, and buffer readback offsets.

## State and persistence behavior

The addressed registers hold live queue-manager state in hardware. Ring bases and indices, CP message bases, LDMA offsets, and fences persist across submissions until reset or reprogramming. Debug buffer address/data registers expose transient internal state. The header itself stores nothing.

## Dependencies and integration points

This header must be used with `mme_qm_masks.h`. It integrates with Goya queue allocation constants such as `MME_QMAN_LENGTH`, common QMAN submission helpers, MMU ASID setup, and reset/error handling. It is structurally related to `mme_cmdq_regs.h`, but includes PQ-specific registers at the `0xD8xxx` base.

## Risks and edge cases

Confusing QMAN and CMDQ address windows would send writes to the wrong block. Queue-base low/high pairs and size/index registers must be coherent. The push registers encode a descriptor as several consecutive words; partial programming can create malformed work. CP message base and LDMA offset registers must match the firmware/packet format expected by the command processor.

## Test signals

Successful driver build and Goya probe are the first checks. Runtime validation should submit MME work through the QMAN, verify producer/consumer progress, observe fence completion, reset while queues are active, and confirm status/error registers match expected masks when invalid descriptors are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_regs.h

## Purpose

`mme_regs.h` is the generated MMIO offset map for the Goya MME tensor-engine block. It defines where software writes tensor descriptors, execution controls, debug-memory accesses, credit controls, interrupt registers, and four shadow descriptor banks.

## Important APIs, types, and data

The file exports only `mmMME_*` register offsets. The live architectural descriptor starts at `0xD0000` with `ARCH_STATUS`, high/low base addresses for A, B, CIN, COUT, and BIAS, descriptor header, kernel size, associated dimensions, scaling and GEMMLOWP fields, ROI base offsets, valid elements, loop strides, ROI sizes, spatial starts/strides/sizes for A/B/C, sync-object message, padding, iteration count, and split-bubble control. Execution and debug controls include `MME_CMD`, `DUMMY`, `RESET`, `STALL`, shared-memory base, debug-memory address/data/control/read-complete, and `LOG_SHADOW`.

Infrastructure registers include store max credit, AGU, SBA/SBB/SBC/WBC credit and control data, TE/TE2DEC credits, REI/SEI/SPI status and masks. Four shadow banks, `SHADOW_0` through `SHADOW_3`, repeat the descriptor/status layout from roughly `0xD0400` through `0xD0BAC`.

## Control flow

There is no executable code in the header. Runtime MME programming writes descriptor fields, programs memory/security controls, optionally writes shadow-related controls, then writes `MME_CMD` to execute. Status, interrupt, and shadow registers are read during completion, error handling, or debug. Reset and stall registers are used by recovery paths to quiesce or reinitialize the MME.

## State and persistence behavior

MME registers describe live tensor operation state in hardware. Base address, ROI, stride, data type, quantization, and sync-object fields persist until overwritten and directly determine the next MME execution. Shadow banks preserve hardware-visible copies of descriptor state for logging or in-flight tracking. Interrupt masks/status and debug-memory registers are volatile hardware state; the header itself has no storage.

## Dependencies and integration points

This file pairs with `mme_masks.h` for field-level packing. It integrates with Goya command submission and firmware packet formats, MMU/ASID setup, sync-object completion signaling, reset logic, and debug paths. It also interacts with QMAN/CMDQ headers because queue-submitted work ultimately causes descriptors to reach this MME block.

## Risks and edge cases

The register map controls memory reads and writes by an accelerator. Bad base addresses, strides, valid-element counts, data types, or store controls can corrupt device memory or produce incorrect computation. Shadow registers are repeated and easy to index incorrectly. Reset/stall/debug registers should not be written while active work is assumed to complete normally. The generated file must stay synchronized with `mme_masks.h`; offset/field mismatches are high-risk.

## Test signals

Validation should include a clean build, successful Goya probe/reset, MME numerical workloads covering A/B/CIN/COUT/BIAS paths, quantized GEMMLOWP/ReLU cases, sync-object completion, interrupt status/mask behavior, and debug/shadow dump correctness after injected faults or forced stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_masks.h

## Purpose

`mmu_masks.h` defines generated field masks and shifts for the Goya MMU control block. It describes input FIFO thresholds, MMU enable, ordering controls, feature enable bits, virtual-address ordering masks, DDR-size/scrambler setup, memory-initialization busy state, SPI mask/cause, and page/access error capture fields.

## Important APIs, types, and data

The exported macros are `MMU_*_SHIFT` and `MMU_*_MASK`. `MMU_INPUT_FIFO_THRESHOLD` has separate 3-bit thresholds for PCI, PSOC, DMA, CPU, MME, TPC, and other clients. `MMU_MMU_ENABLE` has a single enable bit. `MMU_FORCE_ORDERING` has weak and strong ordering bits for DMA, PSOC, PCI, CPU, MME, TPC, and default traffic. `MMU_FEATURE_ENABLE` covers VA ordering, clean linked-list behavior, hop-offset enable, OBI ordering, strong-ordering reads, and trace enable. Ordering masks cover VA bits 31:7 and 49:32. Scrambler fields select address bit and single-DDR mode/ID. Error capture fields combine VA high bits and an entry-valid bit, with separate low-VA registers.

## Control flow

The file has no control flow. Driver MMU initialization composes values with these masks to set thresholds, ordering, feature, scrambler, and enable registers. Fault-handling paths read page/access capture fields, test `ENTRY_VALID`, combine high and low VA pieces, report the fault, and clear or rearm capture state according to device policy.

## State and persistence behavior

The described registers are persistent MMU hardware configuration until reset or reprogramming. Enabling the MMU and setting ordering/scrambler behavior affects all translated client traffic, including MME and TPC. Page/access error capture registers hold latched fault addresses until cleared. The header itself is stateless.

## Dependencies and integration points

This header pairs with `mmu_regs.h` for offsets and with common HabanaLabs MMU code for page-table management. Goya platform constants define reserved page-table/cache/default-page memory, while the common driver provides hop shifts/masks, mapping operations, debugfs access, and fault reporting. MME/QMAN ASID fields depend on the MMU configuration described here.

## Risks and edge cases

Ordering and scrambler bits affect correctness beyond the MMU block; wrong values can cause subtle memory consistency or address-placement failures. Fault addresses are split across two registers and only valid when the valid bit is set. Threshold fields are narrow and can silently truncate. Page/access captures use VA bits 49:32 and 31:0, so callers must reconstruct addresses with correct width and shifting.

## Test signals

Build coverage should catch missing macros. Runtime signals include successful MMU enable during Goya initialization, correct mapping/unmapping behavior, no unexpected page/access errors during normal MME/TPC/DMA traffic, deliberate invalid-access tests that produce accurate captured VAs, and stable behavior under ordering-sensitive workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_regs.h

## Purpose

`mmu_regs.h` provides generated MMIO offsets for the Goya MMU control block. It names the registers used to configure translation enablement, ordering, features, address scrambling, busy status, SPI status, and page/access fault capture.

## Important APIs, types, and data

The file defines only `mmMMU_*` offset macros. The register window starts at `0x480000` with `INPUT_FIFO_THRESHOLD`, then includes `MMU_ENABLE`, `FORCE_ORDERING`, `FEATURE_ENABLE`, VA ordering masks, `LOG2_DDR_SIZE`, `SCRAMBLER`, `MEM_INIT_BUSY`, `SPI_MASK`, `SPI_CAUSE`, `PAGE_ERROR_CAPTURE`, `PAGE_ERROR_CAPTURE_VA`, `ACCESS_ERROR_CAPTURE`, and `ACCESS_ERROR_CAPTURE_VA` through `0x480040`.

There are no functions, structs, or field masks in this file; field definitions live in `mmu_masks.h`.

## Control flow

The header is declarative. Goya MMU initialization code writes these offsets in a hardware-defined sequence to configure thresholds/features/ordering/scrambler and then enable translation. Fault paths read the capture registers, combine high/low VA pieces using `mmu_masks.h`, log the fault, and clear capture state. Reset paths may reinitialize the whole window.

## State and persistence behavior

The addressed registers hold global MMU state for the device. Configuration affects all clients using translated memory, including MME queue managers and tensor accesses. Fault-capture registers retain latched addresses until handled. The header itself has no persistent state.

## Dependencies and integration points

It pairs with `mmu_masks.h` and common HabanaLabs MMU code. Goya-specific `goyaP.h` reserves page-table, default-page, and MMU cache-management regions; common code manages page tables and address translation. MME and QMAN ASID/MMBP programming relies on this MMU block being configured correctly.

## Risks and edge cases

Using offsets without the matching masks can write reserved bits. Enabling the MMU before page tables, default pages, or client ASIDs are ready can break all translated accesses. Fault capture requires valid-bit checks and correct high/low address reconstruction. Since this is a single global block, mistakes affect unrelated accelerator engines, not only MME.

## Test signals

Validation should include successful Goya probe with MMU enabled, page-table setup and teardown, debugfs MMU queries, deliberate page/access fault injection with accurate VA reporting, and MME/DMA/TPC workloads that prove translated clients remain functional after reset and under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_regs.h -->
