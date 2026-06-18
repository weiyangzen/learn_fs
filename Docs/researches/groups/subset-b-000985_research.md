# subset-b-000985 Research

This grouped report covers the requested Gaudi2 HabanaLabs generated ASIC register headers. Each section preserves the source path in its title and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_axuser_regs.h

Purpose: auto-generated GPL-2.0 C preprocessor register map for the Gaudi2 `DCORE0_TPC0_CFG_AXUSER` slice, under the TPC prototype. It exports 19 `mmDCORE0_TPC0_CFG_AXUSER_*` MMIO address constants from `0x400BE00` through `0x400BE4C` for TPC configuration AXUSER attributes.

Important APIs/types/functions: no C types or functions are declared. The API is the macro set for high-bandwidth and low-bandwidth AXI user controls: `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, write/read override low/high registers, and corresponding LB override registers.

Control flow: none in this file. Driver control flow is external: code includes `gaudi2_regs.h`, then passes these absolute register constants to MMIO read/write helpers or to tables describing protected register regions.

State and persistence behavior: the macros name persistent device register state in the TPC configuration block. Writes affect hardware AXUSER transaction tagging, security/domain selection, snoop/order behavior, QoS, and override routing until reset or reprogramming. The header itself stores no software state.

Dependencies and integration points: included by `gaudi2_regs.h`; reachable from Gaudi2 driver code that includes that aggregate header. It aligns with `gaudi2_blocks_linux_driver.h` block-base metadata for `DCORE0_TPC0_CFG` and with security/access logic in `gaudi2_security.c`, which relies on generated register ranges. Mask definitions for related TPC CFG fields live in `dcore0_tpc0_cfg_masks.h`.

Risks: incorrect addresses or stale generation can silently program the wrong TPC transaction attributes. AXUSER mistakes are security-sensitive because ASID, MMU bypass, secure/non-secure attributes, ordering, and snoop fields affect memory isolation and coherency. Since the file has only macros, compile success does not prove the values match the hardware specification.

Test signals: build coverage catches missing include guards or macro spelling regressions. Meaningful validation comes from generated-header diff review against the hardware register database, MMIO smoke tests that read/write documented AXUSER fields on Gaudi2 hardware, and security tests that ensure protected or privileged AXUSER controls cannot be misused from untrusted paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_axuser_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_regs.h

Purpose: generated register map for the TPC kernel configuration region of `DCORE0_TPC0_CFG`. It exports 53 `mmDCORE0_TPC0_CFG_KERNEL_*` address macros from `0x400B508` to `0x400B5D8`.

Important APIs/types/functions: no functions or types. Macro families define the kernel base address low/high registers, thread-id base and size registers for dimensions 0 through 4, tensor ID, kernel configuration registers, coefficient/preload sections, and low/high combined base-size registers for each dimension.

Control flow: none locally. Runtime code uses these constants while preparing TPC kernel execution descriptors or debug access sequences, programming address and geometry registers before execution is triggered through the broader TPC CFG block.

State and persistence behavior: names hardware state that describes the active TPC kernel: instruction base pointer, TID ranges, dimensional sizes, and kernel configuration metadata. Values persist in device MMIO state until overwritten or reset and directly influence the tensor processor's work partitioning.

Dependencies and integration points: included through `gaudi2_regs.h` with adjacent tensor, QM, sync-object, AXUSER, CFG, and mask headers. It is coupled to `dcore0_tpc0_cfg_kernel_tensor_0_regs.h` for tensor memory descriptors and to `dcore0_tpc0_cfg_regs.h` for command, execute, status, and interrupt registers.

Risks: off-by-one address generation in dimensional arrays can corrupt neighbor kernel or tensor configuration fields. The split low/high address registers require callers to preserve 64-bit address ordering and alignment. Mismatched TID size programming can lead to wrong work distribution or hardware faults.

Test signals: compile inclusion through `gaudi2_regs.h`; generated register-database consistency checks; command submission tests that launch TPC kernels with multidimensional TID spaces; negative tests for invalid tensor geometry and address alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_tensor_0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_tensor_0_regs.h

Purpose: generated register map for TPC kernel tensor slot 0 in `DCORE0_TPC0_CFG`. It exports 20 `mmDCORE0_TPC0_CFG_KERNEL_TENSOR_0_*` constants from `0x400B000` to `0x400B04C`.

Important APIs/types/functions: no executable API. The macros describe tensor base address low/high, padding value, tensor configuration, and five dimensions worth of size and stride registers, including high size/stride forms for dimension 4.

Control flow: none. External driver paths program these registers before launching or emulating a TPC kernel, typically paired with `dcore0_tpc0_cfg_kernel_regs.h` for kernel geometry and `dcore0_tpc0_cfg_regs.h` for execution control.

State and persistence behavior: MMIO register values define tensor memory layout for hardware. They persist in the TPC CFG block until reset/reprogramming and affect address generation, padding behavior, dimensional iteration, and stride calculation.

Dependencies and integration points: included by `gaudi2_regs.h`; semantically paired with the QM tensor version in `dcore0_tpc0_cfg_qm_tensor_0_regs.h`. It depends on callers knowing hardware packing semantics, as this header provides only addresses, not field masks for each tensor descriptor field.

Risks: wrong stride or size address use causes data corruption or invalid DMA-like tensor accesses. High/low address register ordering is error-prone. Because this file only maps tensor 0, callers must not assume it covers every tensor slot without consulting neighboring generated headers.

Test signals: register generation checks, compile checks through aggregate include, TPC kernel tests using nontrivial strides/padding/dimensions, and hardware debug reads confirming descriptor writes land at expected offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_kernel_tensor_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_masks.h

Purpose: generated bit-field mask and shift definitions for `DCORE0_TPC0_CFG` TPC registers. It exports 165 value masks plus matching shift macros over the TPC CFG register set.

Important APIs/types/functions: macro-only API. It defines field access metadata for TPC count/id, stall-on-error, clock gates, input-queue rate limiting, TSB MTRR, lock values, CGU disable controls, FP16/FP8 rounding and bias controls, dcache/scoreboard flags, arbitration weights, LUT base addresses, status bits, command/execute/stall fields, interrupt cause/mask fields, opcode execution, thread IDs, and occupancy/credit counters. Important downstream masks include status fields consumed by `gaudi2_masks.h` to form `TPC_IDLE_MASK`.

Control flow: none. External code combines these `_SHIFT` and `_MASK` macros with register values read from addresses in `dcore0_tpc0_cfg_regs.h`.

State and persistence behavior: this header does not store state, but describes the bit layout of persistent hardware state in the TPC CFG block. Correct use determines how software reads status, enables/disables subunits, masks interrupts, and programs execution controls without clobbering unrelated bits.

Dependencies and integration points: included through `gaudi2_regs.h`; directly referenced by `gaudi2_masks.h` for idle/status aggregation. It must match the addresses in `dcore0_tpc0_cfg_regs.h` and functional submaps such as kernel/tensor/QM configuration headers.

Risks: field masks are more fragile than raw register addresses because incorrect bit positions can produce valid-looking writes with wrong side effects. Clock-gate, CGU, interrupt, and protection-related fields can affect availability, fault reporting, and isolation. Callers must apply masks before writes and preserve reserved bits according to hardware rules.

Test signals: static checks that every mask/shift pair is internally consistent; generated diff checks against hardware XML/RTL register specs; runtime tests for TPC idle detection, interrupt masking, rate-limit controls, and status polling; warnings from compile if expected mask names disappear from `gaudi2_masks.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_regs.h

Purpose: generated register map for the queue-manager-facing TPC kernel configuration region in `DCORE0_TPC0_CFG`. It exports 53 `mmDCORE0_TPC0_CFG_QM_*` address constants from `0x400BAE4` to `0x400BBB4`.

Important APIs/types/functions: macro-only API for QM kernel base address low/high, TID base/size per dimension, tensor ID, kernel configuration, coefficient sections, and base-size high/low registers. The layout mirrors the non-QM kernel configuration header with a separate address window.

Control flow: none. Driver code or firmware-facing setup paths program these registers when a queue manager drives TPC kernel execution state.

State and persistence behavior: represents MMIO-backed queue-manager kernel launch state. Programmed values persist until reconfigured/reset and affect the command processor or QM path's view of kernel address and thread geometry.

Dependencies and integration points: included by `gaudi2_regs.h`; tightly related to `dcore0_tpc0_cfg_qm_tensor_0_regs.h`, `dcore0_tpc0_cfg_qm_sync_object_regs.h`, and `dcore0_tpc0_qm_regs.h`. It integrates with security tables that expose or restrict selected QM ranges.

Risks: duplicated kernel-layout names with a QM prefix create copy/paste risk between `CFG_KERNEL` and `CFG_QM` spaces. Address mistakes could route setup through the wrong launch path. 64-bit addresses split across low/high macros require ordering discipline.

Test signals: compare against non-QM kernel register spacing where expected; hardware queue submission tests that program TPC kernels via QM; register readback on Gaudi2 after command submission; generated-register diff review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_sync_object_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_sync_object_regs.h

Purpose: minimal generated map for QM sync-object registers in the TPC CFG block. It exports two addresses: `mmDCORE0_TPC0_CFG_QM_SYNC_OBJECT_MESSAGE` at `0x400BADC` and `mmDCORE0_TPC0_CFG_QM_SYNC_OBJECT_ADDR` at `0x400BAE0`.

Important APIs/types/functions: no functions/types. The macro pair names the message payload and target address registers used for synchronization object signaling through the TPC queue-manager configuration path.

Control flow: none locally. External command or firmware paths write the message and address in the correct hardware-defined order as part of sync-object signaling.

State and persistence behavior: describes two hardware registers whose contents define a synchronization-object write. Incorrect persisted values may signal the wrong completion object or fail to notify waiters.

Dependencies and integration points: included by `gaudi2_regs.h`; adjacent to `dcore0_tpc0_cfg_qm_regs.h` address space and conceptually linked to queue completion, fences, and sync manager blocks.

Risks: the two-register protocol is ordering-sensitive. Address/message inversion, partial programming, or stale contents can break host/device synchronization and cause hangs or premature completion.

Test signals: queue completion tests involving sync objects; MMIO write-order review; integration tests that wait on TPC QM completions; generated map validation for the two adjacent addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_sync_object_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_tensor_0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_tensor_0_regs.h

Purpose: generated register map for queue-manager tensor slot 0 configuration in the TPC CFG block. It exports 20 `mmDCORE0_TPC0_CFG_QM_TENSOR_0_*` constants from `0x400B5DC` to `0x400B628`.

Important APIs/types/functions: macro-only API for tensor base address low/high, padding value, tensor configuration, dimension sizes, strides, and dimension 4 high size/stride fields.

Control flow: none. Runtime programming is performed by external queue submission or firmware paths that set tensor descriptors before issuing TPC work through the QM route.

State and persistence behavior: names MMIO state controlling tensor memory layout as seen by the QM-driven TPC execution path. State persists in registers until reset/rewrite and influences memory address generation and bounds interpretation.

Dependencies and integration points: included through `gaudi2_regs.h`; mirrors `dcore0_tpc0_cfg_kernel_tensor_0_regs.h` at a separate address range. It is used alongside `dcore0_tpc0_cfg_qm_regs.h` and sync-object registers.

Risks: parallel non-QM/QM tensor maps can be confused. Bad base/stride/size programming risks data corruption, invalid access, or command hangs. High/low address pieces must be coherent.

Test signals: TPC QM tensor execution tests using tensor 0; descriptor readback after programming; generated layout comparison against hardware register source; stress cases for multidimensional strides and padding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_tensor_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_regs.h

Purpose: generated main TPC configuration register map for `DCORE0_TPC0_CFG`. It exports 103 `mmDCORE0_TPC0_CFG_*` address constants from `0x400BC18` through `0x400BDFC`.

Important APIs/types/functions: no executable API. Register families cover TPC identity/count, stall and clock controls, input-queue rate limiting, TSB MTRR and masks, lock registers, CGU controls, floating point rounding/bias, dcache and scoreboard controls, arbitration weights, LUT base addresses, semaphores/flags, status, base address translation, command/execute/stall, icache base, read/write rate limits, interrupt cause/mask, work-queue credits, opcode execution, and inflight/occupancy counters.

Control flow: none internally. External driver code sequences writes to configuration, command, and execute registers, then polls status/interrupt fields using masks from `dcore0_tpc0_cfg_masks.h`.

State and persistence behavior: this is the core TPC control MMIO state. Writes can change execution readiness, cache/clock behavior, protection attributes, interrupt delivery, and kernel launch behavior until reset or explicit reprogramming.

Dependencies and integration points: included by `gaudi2_regs.h`; masks are in `dcore0_tpc0_cfg_masks.h`. `gaudi2_masks.h` uses related status masks to define idle checks, and `gaudi2_security.c` relies on generated register ranges and selected register allowlists.

Risks: this header spans control, status, and interrupt surfaces. Wrong addresses can stall engines, mask interrupts, misprogram lookup-table bases, or corrupt command execution. Some names contain generated spelling quirks such as `ADDERESS` and `OCCOUPY`; downstream code must use the generated spelling exactly.

Test signals: full driver compile, TPC reset/idle tests, interrupt mask/cause tests, command launch smoke tests, generated address comparison, and security policy checks for privileged control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_special_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_special_regs.h

Purpose: generated special access-control/security register map for `DCORE0_TPC0_CFG_SPECIAL`. It exports 81 `mmDCORE0_TPC0_CFG_SPECIAL_*` constants from `0x400BE80` to `0x400BFFC`.

Important APIs/types/functions: macro-only API. The file defines global privilege registers `GLBL_PRIV_0..31`, global non-secure registers `GLBL_NON_SEC_0..15`, and global secure registers `GLBL_SEC_0..31` for the TPC CFG special window.

Control flow: none. External security initialization or debug code programs/reads these policy registers to control access attributes for TPC CFG register regions.

State and persistence behavior: names persistent hardware policy state controlling privilege/security metadata. Changes may affect which agents can access TPC CFG resources until reset or reconfiguration.

Dependencies and integration points: included by `gaudi2_regs.h` and aligned with block-base definitions in `gaudi2_blocks_linux_driver.h`. It complements the main TPC CFG and AXUSER maps and is relevant to `gaudi2_security.c` access-region configuration.

Risks: security register maps are high impact. Incorrect generation or programming can expose privileged TPC registers, block legitimate driver access, or create mismatched secure/non-secure views.

Test signals: generated map validation, security-table tests, privilege boundary tests, boot-time access checks under secure/non-secure modes, and review that special register windows remain restricted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_special_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_busmon_0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_busmon_0_regs.h

Purpose: generated register map for TPC0 EML bus monitor 0. It exports 70 `mmDCORE0_TPC0_EML_BUSMON_0_*` address constants from `0x7000` to `0x7FFC`.

Important APIs/types/functions: macro-only API for bus-monitor control/reset/interrupt clear, trigger threshold, start/end address windows for monitored regions, event and interrupt registers, counters, match filters, debug/auth/lock registers, and CoreSight-style peripheral/component ID registers.

Control flow: none. External diagnostics or tracing code configures monitor windows and reads counters/status to observe bus activity.

State and persistence behavior: represents trace/monitor hardware configuration and captured counters. State can persist across a running diagnostic session until reset/clear, and lock/auth registers can affect accessibility.

Dependencies and integration points: included by the aggregate register include when EML/trace support needs symbolic addresses. It is conceptually paired with the ETF, funnel, SPMU, and STM EML headers for a trace fabric around TPC0.

Risks: relative-looking addresses in this EML map may be offsets within an EML aperture rather than the absolute DCORE0 TPC CFG range used by other files. Callers must combine them with the correct base. Misconfigured monitor ranges can miss events or leak sensitive address activity through debug interfaces.

Test signals: trace/bus-monitor enable tests, counter increment validation under known TPC traffic, lock/auth access tests, and generated peripheral ID readback checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_busmon_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_etf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_etf_regs.h

Purpose: generated register map for the TPC0 EML embedded trace FIFO. It exports 45 `mmDCORE0_TPC0_EML_ETF_*` constants from `0x2004` to `0x2FFC`.

Important APIs/types/functions: macro-only API for ETF RAM size/status/read/write pointers, trigger/control/mode registers, buffer levels/watermarks, formatter flush/status controls, integration test registers, claim/lock/auth registers, and component ID registers.

Control flow: none. Trace control code uses these constants to enable buffering, flush captured trace data, and inspect FIFO state.

State and persistence behavior: names trace buffer state and configuration. Captured trace data and pointers persist until drained, reset, flushed, or overwritten according to hardware mode.

Dependencies and integration points: part of the EML trace fabric with SPMU event source, STM stimulus, funnel routing, and bus monitor sources. Included through the Gaudi2 register aggregation path if EML headers are referenced by driver diagnostics.

Risks: trace FIFO control is sensitive to ordering: enabling, flushing, and pointer reads must follow hardware rules. Wrong base interpretation can access unrelated trace registers. Trace capture can expose workload behavior.

Test signals: trace capture/flush tests, buffer watermark behavior under generated events, component ID readback, and generated map comparison to CoreSight/EML specifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_etf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_funnel_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_funnel_regs.h

Purpose: generated register map for the TPC0 EML trace funnel. It exports 26 `mmDCORE0_TPC0_EML_FUNNEL_*` constants from `0x6000` to `0x6FFC`.

Important APIs/types/functions: macro-only API for funnel control, priority control, integration ATB registers, ITCTRL, claim set/clear, lock access/status, auth status, device architecture/type, peripheral IDs, and component IDs.

Control flow: none. External trace setup code selects and prioritizes trace streams before they flow to downstream trace buffering or collection.

State and persistence behavior: funnel selection and priority registers are hardware routing state. They persist during a trace session and determine which EML sources are forwarded.

Dependencies and integration points: works with `dcore0_tpc0_eml_etf_regs.h`, `dcore0_tpc0_eml_spmu_regs.h`, `dcore0_tpc0_eml_stm_regs.h`, and bus monitor headers. Included via generated register aggregation for diagnostics/debug paths.

Risks: incorrect routing can drop trace streams or combine unexpected sources. Lock/auth fields must be respected to avoid exposing debug trace controls where prohibited.

Test signals: trace-path tests confirming selected sources appear downstream, priority behavior under multiple active sources, component ID readback, and security-mode access tests for lock/auth registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_funnel_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_spmu_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_spmu_regs.h

Purpose: generated register map for the TPC0 EML system performance monitoring unit. It exports 64 `mmDCORE0_TPC0_EML_SPMU_*` constants from `0x1000` to `0x1FFC`.

Important APIs/types/functions: macro-only API for performance event counters `PMEVCNTR0..5`, cycle counter low/high, trace control/status/enable, event type selectors, counter enables, interrupt enables/status/clear, overflow flags, software increment, lock/auth/device ID registers, and component/peripheral IDs.

Control flow: none. Profiling/debug code configures event selectors and enables counters, then reads event counts or interrupt/overflow status.

State and persistence behavior: event counter values accumulate in hardware and persist until reset or cleared. Enable and event-selector registers define the active profiling session.

Dependencies and integration points: EML trace/perf subsystem adjacent to ETF, STM, funnel, and bus monitor. Performance and trace collection code must use the correct EML base plus these offsets.

Risks: counter overflow, wrong event selection, or forgetting to clear state can produce misleading profiling data. Perf counters can reveal workload characteristics, so access controls matter.

Test signals: counter increments under controlled TPC workloads, overflow interrupt tests, reset/clear behavior, event selector validation, and component ID checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_spmu_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_stm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_stm_regs.h

Purpose: generated register map for the TPC0 EML system trace macrocell. It exports 54 `mmDCORE0_TPC0_EML_STM_*` constants from `0x3C04` to `0x3FFC`.

Important APIs/types/functions: macro-only API for STM DMA start/stop/status/control, hardware event enable/trigger/bank/mux registers, stimulus features, synchronization/access controls, integration test controls, claim/lock/auth, device architecture/type, peripheral IDs, and component IDs.

Control flow: none. External trace code configures STM stimulus/event generation and DMA behavior as part of hardware trace capture.

State and persistence behavior: STM configuration and DMA state live in hardware. Values persist for the trace session and can emit trace packets or DMA trace data depending on mode.

Dependencies and integration points: part of the EML CoreSight-like trace fabric with funnel and ETF. It may consume events from TPC logic and emit them to downstream trace buffers.

Risks: trace DMA and stimulus configuration are ordering-sensitive. Wrong addresses or base selection can corrupt trace setup. Debug trace output can expose sensitive workload timing.

Test signals: STM event generation tests, DMA start/stop behavior, downstream trace visibility through funnel/ETF, lock/auth access tests, and ID register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_stm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_arc_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_arc_aux_regs.h

Purpose: generated register map for the auxiliary ARC control/status block inside `DCORE0_TPC0_QM`. It exports 284 `mmDCORE0_TPC0_QM_ARC_AUX_*` address constants from `0x4008100` to `0x4008920`.

Important APIs/types/functions: macro-only API spanning ARC run/halt request/ack, reset vector, debug mode, cluster/ARC IDs, wake events, DCCM address bases, CTI state, ARC reset request/status, scratchpads, cache/queue/DCCM controls, breakpoint and debug/status registers, error cause registers, queue base/producer/consumer/shadow fields, DCCM queue alert message, inflight counters, AXI ordering counters, and ARC upper DCCM enable.

Control flow: none in the header. External reset, firmware boot, security, and debug flows use these addresses to halt/run the ARC, set reset vectors, configure DCCM/queues, observe errors, or expose safe debug ranges.

State and persistence behavior: represents ARC microcontroller state associated with the TPC queue manager. State includes execution control, queue metadata, scratchpads, error latches, and counters. Values persist across normal operation until ARC reset, device reset, or explicit reprogramming.

Dependencies and integration points: included by `gaudi2_regs.h`; heavily referenced in `gaudi2_security.c` as register ranges and individual allowed registers. It integrates with `dcore0_tpc0_qm_regs.h` for QMAN queues and with TPC CFG QM kernel/tensor setup.

Risks: this is a sensitive firmware-control surface. Incorrect register access can halt firmware, corrupt DCCM queues, break command processing, or expose privileged debug state. Security tables must not overexpose ARC control registers.

Test signals: ARC boot/reset tests, queue-manager firmware liveness checks, security allowlist tests in `gaudi2_security.c`, debug halt/resume smoke tests, and generated address range validation against ARC auxiliary register specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_arc_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_axuser_nonsecured_regs.h

Purpose: generated register map for non-secured AXUSER attributes in `DCORE0_TPC0_QM`. It exports 19 `mmDCORE0_TPC0_QM_AXUSER_NONSECURED_*` constants from `0x400AB80` to `0x400ABCC`.

Important APIs/types/functions: macro-only API for HB AXUSER ASID, MMU bypass, strong order, no-snoop, write reduction, read atomic, QoS, reserved/core/emem page fields, E2E coordination, and HB/LB write/read override low/high controls.

Control flow: none. External QM setup or security initialization code programs these attributes to define how non-secure queue-manager transactions appear on the AXI fabric.

State and persistence behavior: names persistent hardware transaction-attribute registers. Incorrect values affect memory translation, ordering, coherency, and QoS for non-secure QM traffic.

Dependencies and integration points: included by `gaudi2_regs.h`; associated with the main QMAN map in `dcore0_tpc0_qm_regs.h` and protected by security policy code. Similar naming exists in TPC CFG AXUSER and VDEC bridge AXUSER headers.

Risks: high security risk because MMU bypass and ASID fields directly affect memory isolation. The `NONSECURED` suffix must not be confused with secure AXUSER contexts.

Test signals: secure/non-secure queue submission tests, MMU translation and isolation tests, register readback after initialization, and generated map diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_cgm_regs.h

Purpose: generated compact register map for the clock-gating manager sub-block of `DCORE0_TPC0_QM`. It exports three macros: `CGM_CFG` at `0x400AD80`, `CGM_STS` at `0x400AD84`, and `CGM_CFG1` at `0x400AD88`.

Important APIs/types/functions: no functions/types. The macro API names CGM configuration and status registers. `gaudi2_masks.h` defines `DCORE0_TPC0_QM_CGM_STS_AGENT_IDLE_MASK` and aliases `CGM_IDLE_MASK` for idle detection.

Control flow: none. Runtime code may write CGM config and poll CGM status when quiescing or power-managing the TPC QM.

State and persistence behavior: hardware clock-gating configuration and status persist in the QM block. Status indicates agent idle state; configuration can influence power and availability.

Dependencies and integration points: included by `gaudi2_regs.h`; status masks are integrated by `gaudi2_masks.h`; security and reset code may rely on this block when gating or checking QM idleness.

Risks: clock-gating mistakes can make the queue manager appear hung or prevent power savings. Polling an incorrect status bit can produce false idle decisions.

Test signals: idle polling tests, power/reset sequencing tests, readback of CGM status under active and idle workloads, and generated mask/address consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_cgm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_regs.h

Purpose: generated main queue manager register map for `DCORE0_TPC0_QM` using the QMAN prototype. It exports 517 `mmDCORE0_TPC0_QM_*` constants from `0x400A000` to `0x400AD70`.

Important APIs/types/functions: macro-only API covering global config/status/error registers, AX cache/protection, four producer queues, five completion queues, CQ pointers/status/IFIFO, CP message base registers, fences and counts, barrier/LDMA offsets, command processor status/current instruction/predicate/debug/credits/input data, PQC HBW/LBW queues, arbitration masks/weights/credits/choice offsets, WR64 base address windows, ARC CQ pointer registers, inflight counters, error-message controls, and performance-counter configuration.

Control flow: none inside the header. It supports the external QMAN control path: configure queues, push work, track completion queues, handle fences/barriers, poll command processor state, respond to errors, and tune arbitration.

State and persistence behavior: this file maps most persistent state for the TPC queue manager. Registers track queue bases/sizes/PIs/CIs, completion pointers, fences, CP execution state, arbitration credits, protection, errors, and counters. State persists across queue operation until reset or reinitialization.

Dependencies and integration points: included by `gaudi2_regs.h`; referenced extensively by `gaudi2_security.c` for allowed register ranges and specific register access. Works with `dcore0_tpc0_qm_arc_aux_regs.h`, `dcore0_tpc0_qm_cgm_regs.h`, AXUSER non-secured registers, and the TPC CFG QM kernel/tensor/sync-object headers.

Risks: high blast radius. Wrong queue pointer/base macros can corrupt command submission. Completion queue mistakes can hang waits or lose completions. Error mask misconfiguration hides faults. Security allowlists must distinguish safe queue descriptors from privileged global/ARC controls.

Test signals: queue submission/completion tests, fence/barrier tests, CP error injection and reporting, security allowlist coverage, reset and idle tests, performance counter smoke tests, and register database diff validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_dec_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_dec_regs.h

Purpose: generated AXUSER register map for the decoder path of `DCORE0_VDEC0_BRDG_CTRL`. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_DEC_*` constants from `0x41E3C00` to `0x41E3C4C`.

Important APIs/types/functions: macro-only API for HB ASID/MMU bypass/ordering/no-snoop/write-reduction/read-atomic/QoS/reserved/emem/core attributes, E2E coordination, and HB/LB read/write override registers for the VDEC decoder bridge traffic.

Control flow: none. External VDEC bridge initialization uses these addresses to assign transaction attributes for decoder-originated traffic.

State and persistence behavior: persistent MMIO transaction attributes for the decoder bridge. Values influence memory protection, ordering, snooping, and QoS until reset/rewrite.

Dependencies and integration points: included by `gaudi2_regs.h`; related to main bridge control registers in `dcore0_vdec0_brdg_ctrl_regs.h` and field masks in `dcore0_vdec0_brdg_ctrl_masks.h`.

Risks: MMU bypass or wrong ASID/QoS settings can break memory isolation or performance. Similar AXUSER files for MSIX channels increase copy/paste risk.

Test signals: VDEC bridge initialization readback, memory isolation tests for decoder traffic, AXI violation tests, and generated-address comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_dec_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h

Purpose: generated AXUSER map for the abnormal MSI-X path of `DCORE0_VDEC0_BRDG_CTRL`. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_ABNRM_*` constants from `0x41E3B00` to `0x41E3B4C`.

Important APIs/types/functions: no functions/types. Macros cover the same HB/LB AXUSER attribute and override fields as other bridge AXUSER maps, scoped to abnormal MSI-X notifications.

Control flow: none. Interrupt/bridge initialization code programs these registers so abnormal interrupt writes use the intended transaction attributes.

State and persistence behavior: persistent transaction attribute state for abnormal MSI-X writes. Misprogramming affects interrupt write routing, protection, and ordering.

Dependencies and integration points: included by `gaudi2_regs.h`; semantically tied to ABNRM interrupt mask/wait/counter registers in `dcore0_vdec0_brdg_ctrl_regs.h` and corresponding mask definitions.

Risks: wrong attributes can lose or misroute abnormal event MSI-X writes. Security-sensitive fields such as ASID and MMU bypass must match the interrupt delivery design.

Test signals: abnormal interrupt injection tests, MSI-X delivery/readback tests, AXI violation monitoring, and generated map validation against VDEC bridge spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h

Purpose: generated AXUSER register map for the L2C MSI-X path of the VDEC0 bridge. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_L2C_*` constants from `0x41E3900` to `0x41E394C`.

Important APIs/types/functions: macro-only API for HB ASID/MMU bypass/order/snoop/reduction/atomic/QoS/reserved/core/emem fields, E2E coordination, and HB/LB override registers for L2C MSI-X traffic.

Control flow: none. External interrupt bridge setup uses these constants to program attributes for L2C-originated MSI-X writes.

State and persistence behavior: hardware transaction attributes persist and govern L2C MSI-X write behavior.

Dependencies and integration points: included by `gaudi2_regs.h`; linked to L2C GIC/MSI-X mask, wait counter, APB write, completion queue, and MSI-X LBW address/data registers in `dcore0_vdec0_brdg_ctrl_regs.h`.

Risks: misconfigured L2C MSI-X attributes can cause lost interrupts, invalid memory writes, or isolation breaches.

Test signals: L2C interrupt delivery tests, bridge status/counter readbacks, AXUSER initialization checks, and generated address validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h

Purpose: generated AXUSER map for the normal MSI-X path of `DCORE0_VDEC0_BRDG_CTRL`. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_NRM_*` constants from `0x41E3A00` to `0x41E3A4C`.

Important APIs/types/functions: macro-only set for HB/LB AXUSER attributes and override registers, scoped to normal MSI-X interrupt writes.

Control flow: none. Driver interrupt setup programs these attributes before normal interrupt flows are enabled.

State and persistence behavior: persistent MMIO state affects transaction identity, protection, ordering, snooping, and QoS for normal MSI-X writes.

Dependencies and integration points: included by `gaudi2_regs.h`; connected to NRM interrupt masks, wait counters, APB write controls, completion queue address fields, and MSI-X LBW write data in the main VDEC bridge control map.

Risks: attribute mistakes can break normal interrupt delivery or violate memory protection. Similar ABNRM/L2C/VCD files require careful channel-specific use.

Test signals: normal MSI-X delivery tests, bridge wait/counter observations, security/isolation tests for interrupt writes, and generation diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h

Purpose: generated AXUSER map for the VCD MSI-X channel of the VDEC0 bridge. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_VCD_*` constants from `0x41E3800` to `0x41E384C`.

Important APIs/types/functions: macro-only API for HB transaction attributes, E2E coordination, and HB/LB override registers for VCD MSI-X traffic.

Control flow: none. Interrupt setup code writes these registers as part of VCD MSI-X channel initialization.

State and persistence behavior: hardware AXUSER state persists and controls VCD MSI-X transaction identity/protection/order behavior.

Dependencies and integration points: included by `gaudi2_regs.h`; connected to VCD interrupt mask, flow mask, wait counters, software-register/APB write, completion queue, and MSI-X address/data registers in `dcore0_vdec0_brdg_ctrl_regs.h`.

Risks: wrong VCD MSI-X attributes can misroute interrupts or bypass intended translation/protection. Care is needed to avoid mixing VCD and other MSI-X channel address windows.

Test signals: VCD interrupt delivery tests, bridge counter/status readback, AXI violation checks, and generated register map comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_masks.h

Purpose: generated field shift/mask definitions for `DCORE0_VDEC0_BRDG_CTRL`. It exports 167 value masks plus associated shifts for VDEC bridge control, interrupt, AXI violation, counter, and completion/termination fields.

Important APIs/types/functions: macro-only API for CGM disable, idle mask, APB watchdog/CGM counters, graceful stop/pending, interrupt cause bits for VCD/L2C/NRM/ABNRM HBW/LBW/APB/DEC/TRC/SPI/AXI errors, HBW/LBW AXI violation causes, sticky violation clear bits, interrupt masks, GIC masks, DEC AXPROT and legal AXSIZE fields, ARC message fields, hardware event trace selection/address, free-run and busy counters, stat enable, per-channel wait/MSI-X counters, address/data fields, AXI split BRESP error, LBW master interface state, and last AW/AR transaction capture fields.

Control flow: none. External code uses masks/shifts when composing reads/writes to addresses in `dcore0_vdec0_brdg_ctrl_regs.h`.

State and persistence behavior: describes bit layout of persistent bridge control and status registers. Correct masking is required to preserve unrelated bits while acknowledging causes, clearing sticky violations, configuring counters, and masking interrupts.

Dependencies and integration points: included by `gaudi2_regs.h`; must match the main VDEC bridge register map. It complements the AXUSER channel headers for decoder and MSI-X paths.

Risks: interrupt cause and AXI violation masks are fault-reporting critical. Wrong bit masks can hide errors, clear the wrong sticky state, or report incorrect fault sources. Control fields such as graceful stop and CGM disable affect reset/power sequencing.

Test signals: interrupt cause/mask injection tests, AXI violation tests, graceful stop state tests, counter enable/readback tests, and static validation that masks do not overlap unexpectedly unless specified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_regs.h

Purpose: generated main register map for the VDEC0 bridge control block. It exports 111 `mmDCORE0_VDEC0_BRDG_CTRL_*` constants from `0x41E3100` to `0x41E3734`.

Important APIs/types/functions: macro-only API for clock/idle/graceful control, interrupt causes and masks, HBW/LBW AXI violation reporting and sticky clear, VCD/L2C/NRM/ABNRM GIC and MSI-X masks, decoder AXPROT/legal size controls, ARC message start/finish words, hardware event trace registers, decoder free-run/busy counters, stat counter enable, per-channel wait/MSI-X counters, software/APB write address/data, completion queue HBW addresses, MSI-X LBW address/data, AXI split BRESP error ID, LBW master interface monitoring, and captured last AW/AR transaction terms.

Control flow: none locally. Driver control flow programs bridge protection/interrupt/counter state, enables or masks channel flows, observes fault causes, and manages graceful stop or idle detection.

State and persistence behavior: maps persistent VDEC bridge hardware state for control, interrupt routing, fault latches, counters, and transaction capture. Some status fields are sticky until cleared through dedicated registers.

Dependencies and integration points: included by `gaudi2_regs.h`; fields decoded with `dcore0_vdec0_brdg_ctrl_masks.h`; channel transaction attributes come from the five VDEC bridge AXUSER headers. The block participates in video decode interrupt delivery and AXI fault handling.

Risks: broad operational surface. Fault mask mistakes can hide AXI violations, MSI-X address/data mistakes can misdeliver interrupts, and graceful/CGM controls can break reset or power sequencing.

Test signals: VDEC interrupt tests across VCD/L2C/NRM/ABNRM channels, AXI violation injection and sticky-clear tests, decoder busy/free-run counter readback, graceful stop/idle tests, and generated address verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_ctrl_special_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_ctrl_special_regs.h

Purpose: generated special privilege/security register map for the VDEC0 control block. It exports 81 `mmDCORE0_VDEC0_CTRL_SPECIAL_*` constants from `0x41E4E80` to `0x41E4FFC`.

Important APIs/types/functions: macro-only API with `GLBL_PRIV_0..31`, `GLBL_NON_SEC_0..15`, and `GLBL_SEC_0..31` registers for VDEC0 control special access metadata.

Control flow: none. Security initialization and low-level access-control code use these registers to configure privileged, secure, and non-secure views of the VDEC control block.

State and persistence behavior: persistent hardware access policy state. Values remain active until reset/reconfiguration and affect which agents may access VDEC control registers.

Dependencies and integration points: included by `gaudi2_regs.h`; aligned with VDEC bridge control and AXUSER maps. It should correspond to special block ranges in `gaudi2_blocks_linux_driver.h` and access policy code.

Risks: wrong special-register programming can expose protected video decode controls or block legitimate driver access. Generated repetition across special files makes address-base mistakes easy to miss.

Test signals: secure/non-secure access tests, boot-time access policy validation, generated map diff review, and negative tests for forbidden VDEC control writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_ctrl_special_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_mme_ctrl_lo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_mme_ctrl_lo_regs.h

Purpose: generated lower-control register map for the DCORE1 MME engine. It exports 70 `mmDCORE1_MME_CTRL_LO_*` constants from `0x42CB000` to `0x42CB4EC`.

Important APIs/types/functions: macro-only API for architecture status/command, sync object data/address/value registers, tensor section selectors for A/B/COUT, QM stall, log shadow registers, base address registers, tensor A/B/COUT base descriptors, non-tensor start/end regions, AGU master/slave controls for inputs and outputs, sync-object address/value fields, slave WBC AXI E2E attributes, and ETF memory repair/wrap registers.

Control flow: none. External MME setup code programs tensor/non-tensor descriptors, AGU controls, sync objects, and commands, then reads status.

State and persistence behavior: MMIO-backed state controls DCORE1 MME command execution, tensor addressing, AGU behavior, queue-manager stall, sync-object signaling, and repair-related registers. Values persist until reset or next programming sequence.

Dependencies and integration points: included by `gaudi2_regs.h`; block base/sections are defined in `gaudi2_blocks_linux_driver.h`. It is structurally mirrored by `dcore3_mme_ctrl_lo_regs.h` at a different DCORE address base.

Risks: MME tensor/AGU address programming errors can corrupt data or hang compute. Sync object mistakes affect completion semantics. DCORE-specific base addresses must not be mixed between DCORE1 and DCORE3.

Test signals: MME command smoke tests on DCORE1, tensor descriptor readback, sync-object completion tests, AGU addressing stress tests, and generated comparison with DCORE3 where layouts should match except base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_mme_ctrl_lo_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_sync_mngr_glbl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_sync_mngr_glbl_regs.h

Purpose: generated global sync-manager register map for DCORE1 using the SOB_GLBL prototype. It exports 590 `mmDCORE1_SYNC_MNGR_GLBL_*` constants from `0x431E000` to `0x431E94C`.

Important APIs/types/functions: macro-only API for sync-manager interrupt mask/cause, local-to-host completion masks, ASID security/privilege controls, LBW delay, PI size/mode, SOB-only and CQ interrupt controls, 64 completion queue base address low/high entries, 64 CQ size-log2 entries, 64 CQ producer indices, 64 CQ security entries, 64 CQ privilege entries, 64 CQ ASID entries, 64 CQ message address/data entries, CQ increment modes, and related per-CQ global configuration.

Control flow: none in this header. Runtime synchronization code configures completion queues, security/ASID policy, producer indices, message targets, and interrupt controls for sync objects and completions.

State and persistence behavior: maps persistent global synchronization state for DCORE1. CQ base/size/PI/security/ASID/message registers define how hardware completions are written and how sync-manager events are delivered. State persists until reset or reconfiguration.

Dependencies and integration points: included by `gaudi2_regs.h`; base/section metadata in `gaudi2_blocks_linux_driver.h`. It integrates with queue managers, sync-object programming, host completion mechanisms, and security policy around ASID/privileged access.

Risks: large repeated CQ arrays are vulnerable to index/address drift. Misprogrammed completion queues can write to wrong host/device memory, violate security, or deadlock waits. ASID/security/privilege fields are isolation-critical.

Test signals: completion queue setup tests for low and high indices, sync-object completion tests, ASID/privilege negative tests, interrupt cause/mask tests, generated array stride validation, and hardware readback of representative CQ entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_sync_mngr_glbl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore3_mme_ctrl_lo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore3_mme_ctrl_lo_regs.h

Purpose: generated lower-control register map for the DCORE3 MME engine. It exports 70 `mmDCORE3_MME_CTRL_LO_*` constants from `0x46CB000` to `0x46CB4EC`.

Important APIs/types/functions: macro-only API equivalent in layout to DCORE1 MME low control: architecture status/command, sync object registers, tensor section selectors, QM stall, log shadow, base address descriptors, tensor A/B/COUT descriptors, non-tensor regions, AGU input/output master/slave controls, WBC AXI E2E attributes, and ETF memory repair/wrap registers.

Control flow: none. External MME programming paths use these constants when targeting the DCORE3 MME instance.

State and persistence behavior: persistent MMIO state for DCORE3 MME execution, tensor addressing, AGU routing, sync completion, and repair controls. Values persist until reset/reprogramming.

Dependencies and integration points: included by `gaudi2_regs.h`; block metadata in `gaudi2_blocks_linux_driver.h`. It mirrors `dcore1_mme_ctrl_lo_regs.h`, enabling per-DCORE engine programming with the same logical layout but different absolute address base.

Risks: DCORE3/DCORE1 confusion is the main integration risk. Using the wrong base silently programs the wrong MME. Tensor/AGU/sync mistakes can cause data corruption, hangs, or incorrect completion signaling.

Test signals: DCORE3-specific MME command tests, cross-check that DCORE1 and DCORE3 layouts differ by expected address base only, sync-object completion validation, AGU stress tests, and generated source diff review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore3_mme_ctrl_lo_regs.h -->
