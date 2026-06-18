# subset-b-003489 Research

This grouped report covers AMDGPU include headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include`. Each section is source-tree aligned and delimited for reconciliation into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_5_0.h

## Purpose
This header defines SDMA1 interrupt vector source IDs for SDMA 5.0 hardware. It is a pure preprocessor contract: consumers include it to translate IH source IDs into named SDMA1 interrupt conditions such as atomic completion, page faults, preemption, doorbell errors, and SRBM access faults.

## Important APIs, Types, and Constants
There are no functions or types. The exported constants are `SDMA1_5_0__SRCID__*` macros. Important values include atomic return done `217`, atomic timeout `218`, IB preempt `219`, ECC `220`, page fault/null/XNACK `221`-`223`, trap `224`, semaphore timeouts `225`-`226`, SRAM ECC `228`, run-list preempt `240`, VM hole `242`, context empty `243`, invalid doorbell `244`, frozen `245`, poll timeout `246`, and SRBM write protection `247`.

## Control Flow
The header has no executable control flow. Its control-flow role is indirect: AMDGPU interrupt dispatch code compares interrupt ring entries against these numeric source IDs and then routes handling to the SDMA fault, preemption, trap, or recovery path.

## State and Persistence
The file stores no runtime state. The macro values are persistent ABI-like hardware constants; changing them would alter driver interpretation of firmware/hardware interrupt packets.

## Dependencies and Integration Points
The only dependency is the C preprocessor and the include guard `__IRQSRCS_SDMA1_5_0_H__`. It integrates with SDMA interrupt setup and IH decoding for the first SDMA engine instance on SDMA 5.0 ASICs.

## Risks and Test Signals
The main risk is numeric drift from hardware documentation or copy/paste mismatch with sibling SDMA engines. Tests should exercise interrupt decode paths by injecting or observing SDMA page fault, XNACK, trap, preempt, and doorbell events and confirming the selected handler and log label match the source ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma2/irqsrcs_sdma2_5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma2/irqsrcs_sdma2_5_0.h

## Purpose
This header defines SDMA2 interrupt source IDs for SDMA 5.0. It gives the third SDMA instance its own macro namespace while preserving the same source ID assignments used by other SDMA 5.0 engines.

## Important APIs, Types, and Constants
There are no functions or structs. The `SDMA2_5_0__SRCID__*` macros cover atomic completion and timeout, IB preemption, ECC and SRAM ECC, UTCL2 page fault/null/XNACK conditions, traps, semaphore timeouts, run-list preempt, VM holes, context empty, invalid doorbells, frozen state, poll timeout, and SRBM write protection. Values span `217` through `247` with gaps matching the hardware table.

## Control Flow
No code executes in this header. Runtime users branch on interrupt vector source IDs and use this namespace to bind an interrupt to SDMA2-specific engine handling rather than another SDMA instance.

## State and Persistence
No mutable state is present. The macro values are stable hardware-facing constants and should be treated like firmware ABI.

## Dependencies and Integration Points
The file depends only on its include guard. It integrates with the AMDGPU interrupt handler, SDMA engine interrupt registration, queue preemption handling, GPUVM fault reporting, and recovery paths that need to know which SDMA engine generated the event.

## Risks and Test Signals
Risk is mostly accidental divergence from SDMA1/SDMA3 or wrong engine namespace use in handler registration. Test signals include per-engine SDMA fault injection, page fault recovery logs identifying SDMA2, and validation that preempt/context-empty interrupts are not attributed to another engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma2/irqsrcs_sdma2_5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma3/irqsrcs_sdma3_5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma3/irqsrcs_sdma3_5_0.h

## Purpose
This header defines SDMA3 interrupt source IDs for SDMA 5.0 ASIC support. It mirrors the SDMA 5.0 event map in an SDMA3-specific macro namespace.

## Important APIs, Types, and Constants
It exports only `#define` constants, including `SDMA3_5_0__SRCID__SDMA_ATOMIC_RTN_DONE`, `SDMA_ATOMIC_TIMEOUT`, `SDMA_IB_PREEMPT`, `SDMA_ECC`, `SDMA_PAGE_FAULT`, `SDMA_PAGE_NULL`, `SDMA_XNACK`, `SDMA_TRAP`, semaphore timeout IDs, `SDMA_SRAM_ECC`, `SDMA_PREEMPT`, `SDMA_VM_HOLE`, `SDMA_CTXEMPTY`, `SDMA_DOORBELL_INVALID`, `SDMA_FROZEN`, `SDMA_POLL_TIMEOUT`, and `SDMA_SRBMWRITE`.

## Control Flow
There is no direct control flow. The definitions influence interrupt dispatch tables and comparisons in the SDMA/IH code path.

## State and Persistence
The file contains no runtime state, allocation, locking, or persistence. Its values persist at build time in any code using the macros.

## Dependencies and Integration Points
The include guard is the only local dependency. Integration points are SDMA3 interrupt registration, queue management, VM fault paths, trap reporting, and recovery code for hangs or invalid doorbell events.

## Risks and Test Signals
The highest risk is using the wrong SDMA namespace or source number when wiring SDMA3 interrupts. Tests should verify SDMA3-specific interrupts are enabled and decoded correctly, especially page fault, XNACK, frozen, preempt, and SRBM protection events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma3/irqsrcs_sdma3_5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/smuio/irqsrcs_smuio_9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/smuio/irqsrcs_smuio_9_0.h

## Purpose
This header declares the SMUIO 9.0 interrupt source ID for `GPIO19`. It is a small hardware source map used by interrupt handling code that needs a symbolic name for source ID `83`.

## Important APIs, Types, and Constants
The file exports one macro: `SMUIO_9_0__SRCID__SMUIO_GPIO19` with value `83`. There are no functions, structs, or enums.

## Control Flow
The file has no executable flow. It affects control flow only when interrupt decoding code compares an IH entry source ID to the GPIO19 macro and dispatches SMUIO handling.

## State and Persistence
No runtime state is stored. The GPIO source ID is a build-time hardware constant.

## Dependencies and Integration Points
The header depends only on the include guard. It integrates with SMUIO interrupt registration and any platform-specific GPIO interrupt paths that identify this source.

## Risks and Test Signals
Risk is low but concentrated in numeric correctness. Tests or validation should confirm that SMUIO GPIO19 interrupts arrive as source ID `83` on SMUIO 9.0 hardware and do not conflict with other block source IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/smuio/irqsrcs_smuio_9_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/thm/irqsrcs_thm_9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/thm/irqsrcs_thm_9_0.h

## Purpose
This header defines thermal controller interrupt source IDs for THM 9.0. It names low-to-high and high-to-low digital thermal threshold crossings.

## Important APIs, Types, and Constants
The exported macros are `THM_9_0__SRCID__THM_DIG_THERM_L2H` value `0` for ASIC temperature rising above the high threshold, and `THM_9_0__SRCID__THM_DIG_THERM_H2L` value `1` for temperature falling below the low threshold.

## Control Flow
There is no executable code. The constants drive branch selection in thermal interrupt handling, where L2H typically triggers throttling/alarm handling and H2L signals recovery or hysteresis state transition.

## State and Persistence
The header contains no state. The values encode the persistent hardware interrupt contract for THM 9.0.

## Dependencies and Integration Points
It depends only on the include guard. It integrates with AMDGPU thermal management, interrupt enablement for `CG_THERMAL_INT`, and power-management paths that react to thermal threshold crossings.

## Risks and Test Signals
Incorrect source mapping could invert or miss thermal transitions. Test signals include inducing threshold crossings in controlled thermal tests and confirming L2H/H2L logs and power-management reactions occur in the correct order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/thm/irqsrcs_thm_9_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/uvd/irqsrcs_uvd_7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/uvd/irqsrcs_uvd_7_0.h

## Purpose
This header names UVD 7.0 video interrupt source IDs. It covers encoder general-purpose, encoder low-latency, and UVD system-message interrupts.

## Important APIs, Types, and Constants
The exported macros are `UVD_7_0__SRCID__UVD_ENC_GEN_PURP` value `119`, `UVD_7_0__SRCID__UVD_ENC_LOW_LATENCY` value `120`, and `UVD_7_0__SRCID__UVD_SYSTEM_MESSAGE_INTERRUPT` value `124`.

## Control Flow
The header has no direct control flow. Video interrupt handlers use these IDs to route encoder completions or firmware/system messages to the UVD ring and job completion logic.

## State and Persistence
No mutable state exists. These source IDs are stable hardware values used at build time by UVD support code.

## Dependencies and Integration Points
The header depends only on the include guard. It integrates with UVD interrupt setup, video encode rings, fence signaling, and system-message handling.

## Risks and Test Signals
The main risk is mismatched source IDs causing video fences not to signal or firmware messages to be ignored. Test signals include UVD encode workloads on general-purpose and low-latency queues, interrupt counters, and successful fence completion after system-message interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/uvd/irqsrcs_uvd_7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vce/irqsrcs_vce_4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vce/irqsrcs_vce_4_0.h

## Purpose
This header defines VCE 4.0 context IDs for trap classes rather than source IDs. It names general-purpose, low-latency, and real-time VCE trap contexts.

## Important APIs, Types, and Constants
The macros are `VCE_4_0__CTXID__VCE_TRAP_GENERAL_PURPOSE` value `0`, `VCE_4_0__CTXID__VCE_TRAP_LOW_LATENCY` value `1`, and `VCE_4_0__CTXID__VCE_TRAP_REAL_TIME` value `2`. No functions or types are declared.

## Control Flow
No executable flow exists. The values are consumed by trap/interrupt code to identify which VCE queue context generated an event and therefore which ring or fence path to service.

## State and Persistence
The header stores no state. The context IDs are persistent hardware/firmware contract constants.

## Dependencies and Integration Points
The include guard is the only dependency. Integration points are VCE ring interrupt handlers, trap decode logic, and queue-specific encode completion paths.

## Risks and Test Signals
If context IDs are wrong, low-latency or real-time encode completions may be attributed to the wrong ring. Test signals include VCE workloads on all three queue classes and confirmation that fences complete on the expected ring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vce/irqsrcs_vce_4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_1_0.h

## Purpose
This header defines VCN 1.0 interrupt source IDs for UVD-compatible encoder and system-message events.

## Important APIs, Types, and Constants
It exports `VCN_1_0__SRCID__UVD_ENC_GENERAL_PURPOSE` value `119`, `VCN_1_0__SRCID__UVD_ENC_LOW_LATENCY` value `120`, and `VCN_1_0__SRCID__UVD_SYSTEM_MESSAGE_INTERRUPT` value `124`.

## Control Flow
There is no direct control flow. The constants guide VCN interrupt dispatch from IH packets to encoder completion or firmware-message handling.

## State and Persistence
No state is held. The constants persist through compilation into block-specific decode logic.

## Dependencies and Integration Points
The file has only an include guard dependency. It integrates with VCN 1.0 ring interrupt setup, firmware message processing, video job fence signaling, and UVD-compatible naming paths.

## Risks and Test Signals
Risk comes from the legacy UVD naming in a VCN header and potential confusion with later VCN JPEG source IDs. Test signals include VCN 1.0 encode workloads and system-message interrupt verification with expected source IDs `119`, `120`, and `124`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_2_0.h

## Purpose
This header expands the VCN interrupt source map for VCN 2.0 and VCN 2.6 poison events. It covers video encode/system messages, JPEG encode/decode, and poison interrupts.

## Important APIs, Types, and Constants
VCN 2.0 macros include UVD encoder general-purpose `119`, low-latency `120`, system-message `124`, JPEG encode `151`, and JPEG decode `153`. Additional VCN 2.6 macros define UVD poison `160`, DJPEG0 poison `161`, and EJPEG0 poison `162`.

## Control Flow
The header has no executable flow. Runtime code uses these IDs to branch between VCN encode, JPEG, firmware message, and hardware poison/error handling.

## State and Persistence
There is no mutable state. The values are hardware event identifiers.

## Dependencies and Integration Points
The header integrates with VCN 2.x interrupt registration, JPEG ring handling, multimedia fence signaling, and RAS/poison handling paths. It depends only on its include guard.

## Risks and Test Signals
Risks include treating VCN 2.6 poison IDs as generic VCN 2.0 IDs without ASIC gating, or misrouting JPEG encode/decode IDs. Tests should run VCN encode/decode and JPEG encode/decode workloads and validate poison interrupt decode on supported parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_4_0.h

## Purpose
This header defines VCN 4.0 interrupt source IDs for UVD trap/encode/system events, JPEG encode/decode engines, and poison events.

## Important APIs, Types, and Constants
Key macros include `VCN_4_0__SRCID__UVD_TRAP` `114`, encoder general-purpose `119`, low-latency `120`, system-message `124`, JPEG encode `151`, JPEG decode `153`, JPEG1 decode `149`, JPEG2 decode aliased to `VCN_4_0__SRCID__JPEG_ENCODE`, JPEG3-7 decode `171`-`175`, and poison IDs `160`-`162`.

## Control Flow
No code executes here. Interrupt dispatch uses the source ID to pick trap, encode, system-message, JPEG engine, or poison handling.

## State and Persistence
No runtime state exists. The aliasing of JPEG2 decode to JPEG encode is a persistent compile-time choice that consumers must understand.

## Dependencies and Integration Points
The include guard is the only local dependency. Integration points include VCN 4.0 interrupt registration, multi-JPEG decode routing, video fences, trap handling, and RAS poison reporting.

## Risks and Test Signals
The standout risk is the JPEG2 decode alias sharing source ID `151` with JPEG encode, requiring consumers to distinguish context by engine/ring if needed. Tests should validate all JPEG decode engines, trap events, and poison IDs on VCN 4.0 hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_5_0.h

## Purpose
This header defines VCN 5.0 interrupt source IDs for video trap/encode/system events, JPEG encode/decode engines, and poison events.

## Important APIs, Types, and Constants
It exports UVD trap `114`, encoder general-purpose `119`, encoder low-latency `120`, system-message `124`, JPEG encode `151`, JPEG decode `153`, JPEG1 decode `149`, JPEG2 decode `151`, JPEG3-7 decode `171`-`175`, JPEG8 decode `177`, JPEG9 decode `178`, and poison IDs UVD `160`, DJPEG0 `161`, and EJPEG0 `162`.

## Control Flow
There is no executable flow. The values guide VCN 5.0 interrupt dispatch and ring/fence completion selection.

## State and Persistence
No state is stored. The source IDs are stable event contracts.

## Dependencies and Integration Points
The file depends only on the include guard. It integrates with VCN 5.0 media block initialization, JPEG multi-engine interrupt handling, firmware system-message handling, trap routing, and RAS poison handling.

## Risks and Test Signals
Risks include numeric overlap between JPEG2 decode and JPEG encode, and missed support for newly added JPEG8/JPEG9 IDs. Test signals include per-engine JPEG decode coverage, VCN encode completion on both queues, trap event handling, and poison interrupt reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vmc/irqsrcs_vmc_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vmc/irqsrcs_vmc_1_0.h

## Purpose
This header defines VMC 1.0 and UTCL2 1.0 source IDs for GPU virtual memory faults and retries.

## Important APIs, Types, and Constants
VMC macros include `VMC_1_0__SRCID__VM_FAULT` `0`, `VMC_1_0__SRCID__VM_RETRY` `1`, `VMC_1_0__SRCID__VM_CONTEXT0_ALL` `256`, and `VMC_1_0__SRCID__VM_CONTEXT1_ALL` `257`. UTCL2 macros include `UTCL2_1_0__SRCID__FAULT` `0` and `UTCL2_1_0__SRCID__RETRY` `1`.

## Control Flow
There is no direct control flow. VM fault interrupt handlers use these IDs to distinguish fatal fault reporting from retry/XNACK-style behavior and to handle context-wide VMC events.

## State and Persistence
The header has no state. The constants are persistent hardware source identifiers used by GPUVM and KFD fault paths.

## Dependencies and Integration Points
It depends only on its include guard. Integration points include GMC/VMC interrupt registration, GPUVM fault decoding, UTCL2 retry handling, KFD memory fault events, and user-visible fault diagnostics.

## Risks and Test Signals
Wrong mapping can break page fault attribution or retry handling. Tests should include GPUVM invalid access, retry-capable memory faults, context fault decoding, and KFD event delivery for VM faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vmc/irqsrcs_vmc_1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vpe/irqsrcs_vpe_6_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vpe/irqsrcs_vpe_6_1.h

## Purpose
This header defines VPE 6.1 interrupt source IDs for command, preemption, fault, timeout, and doorbell conditions in the Video Processing Engine.

## Important APIs, Types, and Constants
The `VPE_6_1_SRCID__*` macros map source IDs `0`-`12`: atomic return done, trap, SRBM write protection, context empty, preempt, queue hang/command timeout, atomic timeout, poll timeout, VM hole, MMHUB general error NACK, MMHUB PRT NACK, invalid doorbell, and IB preempt.

## Control Flow
There is no code flow. VPE interrupt handlers use the IDs to select queue completion, trap, fault, preemption, or hang recovery behavior.

## State and Persistence
No runtime state is stored. The macro values are compile-time hardware constants.

## Dependencies and Integration Points
The header depends only on its include guard. It integrates with VPE ring scheduling, interrupt registration, MMHUB fault interpretation, doorbell validation, and recovery/hang detection.

## Risks and Test Signals
Risks include conflating VPE VM/MMHUB NACK causes with generic GPUVM faults, or missing queue-hang recovery. Test signals include VPE command submission, IB preempt, synthetic invalid doorbell, VM-hole access, and queue timeout recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vpe/irqsrcs_vpe_6_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_kfd_interface.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_kfd_interface.h

## Purpose
This header defines the private interface between AMDGPU KGD and AMD KFD. It is the bridge by which the compute driver learns GPU resources and calls graphics-driver services for queue programming, VM mapping, trap/debug setup, SDMA HQD management, and CU occupancy.

## Important APIs, Types, and Functions
Important data types include `enum kfd_preempt_type`, `struct kfd_vm_fault_info`, `struct kfd_local_mem_info`, `enum kgd_memory_pool`, `struct kfd_cu_occupancy`, `enum kfd_sched_policy`, `struct kgd2kfd_shared_resources`, and `struct tile_config`. The central API is `struct kfd2kgd_calls`, a function-pointer table implemented by per-GFX-generation AMDGPU files and consumed by KFD. Callbacks cover shader-memory programming, PASID/VMID mapping, interrupt init, HQD load/dump/destroy for CP and SDMA queues, VM page table programming, TLB invalidation by PASID or VMID, VM fault register reads, debug trap enable/disable, wave launch controls, address watchpoints, dequeue wait packet construction, CU occupancy, trap handler settings, HQD queue address/reset, and SDMA doorbell lookup.

## Control Flow
The header declares no executable code. Runtime flow is inversion-of-control: KFD stores a generation-specific `kfd2kgd_calls` table selected during device setup, then invokes callbacks when creating queues, handling faults, debugging processes, or tearing queues down. AMDGPU fills `kgd2kfd_shared_resources` during KFD device initialization so KFD can allocate VMIDs, queues, and doorbells within graphics-driver constraints.

## State and Persistence
The header defines state shapes but owns no storage. Persistent state lives in KFD device/process objects and AMDGPU device structures: VMID bitmaps, queue bitmaps, doorbell apertures, tile arrays, local memory information, and callback table pointers. Pointers in `tile_config` and shared resources are borrowed views into AMDGPU-owned configuration and must not outlive the device context.

## Dependencies and Integration Points
It includes Linux types, bitmap, DMA fence, `amdgpu_irq.h`, and `amdgpu_gfx.h`, and forward declares AMDGPU/KFD device structs. Integration points include `amdkfd/kfd_device.c`, KFD interrupt processing, topology/CRAT construction, KFD char device tile-config ioctl, AMDGPU GPUVM, and per-generation implementations such as `amdgpu_amdkfd_gfx_v9.c`, `gfx_v10.c`, `gfx_v11.c`, and `gfx_v12.c`.

## Risks and Test Signals
This is a private but high-risk ABI inside the driver. Risks include mismatched callback signatures, null callbacks on unsupported ASICs, stale borrowed pointers, incorrect VMID/PASID programming, and debug/trap operations on the wrong VMID or instance. Test signals include KFD queue creation/destruction, SDMA queue load/destroy, GPUVM fault delivery to KFD events, debugger watch/trap operations, topology reporting, tile-config ioctl behavior, and suspend/reset paths on all supported GFX generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_kfd_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_pp_interface.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_pp_interface.h

## Purpose
This header defines the AMDGPU power-management and SMU interface contract. It exposes SMU IP block declarations, power/clock/fan/sensor enums, a large `amd_pm_funcs` callback table, and versioned telemetry structures consumed by hwmon, sysfs/debugfs, display core, XGMI/partition code, and user-visible GPU metrics paths.

## Important APIs, Types, and Functions
Extern IP blocks include `pp_smu_ip_block` and SMU v11 through v15 IP blocks. Policy enums cover forced DPM levels, PM state types, VCE levels, fan control modes, clock domains, PP sensors, PP tasks, SMC power profiles, overdrive table commands, MP1 states, data-fabric C-state, power limit levels/types, XGMI PLPD, and PM policy controls. `struct amd_pm_funcs` is the main callback table: it supports power-state transitions, fan PWM/RPM, clock forcing and printing, sensor reads, power limits, power profiles, overdrive, MP1 state, SMU I2C, display clock/voltage requests, watermarks, BACO reset state, PP feature masks, XGMI pstate, GPU/temp/XCP/PM metrics, DPM tables, and RLC notification. Telemetry structures include `metrics_table_header`, many `gpu_metrics_v1_*`, `gpu_metrics_v2_*`, `gpu_metrics_v3_0`, flexible attribute layouts, board/baseboard/partition temperature and metric tables, and attribute encoding macros.

## Control Flow
The header has no implementations, but it defines callback-driven control flow. AMDGPU power-management code installs an `amd_pm_funcs` implementation for the active SMU/DPM backend; sysfs, hwmon, display core, reset, and metrics paths call through it. Metrics flow is versioned: callers inspect `common_header.structure_size`, `format_revision`, and `content_revision` before decoding layout-specific fields.

## State and Persistence
No global state is allocated here. The structs describe PM state that persists elsewhere: fan mode, DPM/OD tables, power profiles, clock limits, SMU firmware metrics buffers, XCP partition counters, energy accumulators, and board temperature sensors. Several metrics versions contain accumulated counters and firmware timestamps, so consumers must treat them as snapshots with monotonic or wrap-prone hardware semantics rather than configuration state.

## Dependencies and Integration Points
The header forward-declares display and clock structures and depends on AMDGPU core definitions supplied by includers. It integrates with SMU backend files, `amdgpu_pm.c`, hwmon/sysfs/debugfs interfaces, DC display clock negotiation, BACO/reset handling, XGMI fabric controls, partition/XCP telemetry, and firmware metrics tables returned by SMU.

## Risks and Test Signals
The highest risks are ABI/layout mistakes in metrics structures, unit mismatches across revisions, failing to check callback availability, and applying power/clock operations unsupported by a given ASIC. Flexible-array metric formats (`gpu_metrics_v1_9`, partition/temp v1_1) require careful bounds checking. Test signals include build coverage across SMU generations, sysfs power profile/OD/fan operations, hwmon sensor reads, display mode changes that request clocks and watermarks, GPU metrics decode by version, XGMI/partition metrics on multi-die parts, and reset/BACO flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_pp_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v11_api_def.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v11_api_def.h

## Purpose
This header defines the packed MES v11 scheduler firmware API. It is the binary command-frame contract used by the host driver to configure MES hardware resources, add/remove queues, schedule gangs, suspend/resume/reset queues, set logging, manage debug VMIDs, perform miscellaneous register/TLB/debugger operations, update root page tables, and pass AMD log buffers.

## Important APIs, Types, and Functions
Important constants are `MES_API_VERSION 1`, `AMDGPU_MES_LOG_BUFFER_SIZE 0x4000`, `API_FRAME_SIZE_IN_DWORDS 64`, and `API_NUMBER_OF_COMMAND_MAX 32`. Important enums include scheduler opcodes, priority levels, queue types, VM hub types, debug VMID operations, log operations/states, and misc opcodes. `union MES_API_HEADER` encodes type/opcode/dword size. Every command union overlays a typed struct with `max_dwords_in_api[64]`, enforcing fixed-size command frames. Key command unions include `MESAPI_SET_HW_RESOURCES`, `MESAPI_SET_HW_RESOURCES_1`, `MESAPI__ADD_QUEUE`, `REMOVE_QUEUE`, `SET_SCHEDULING_CONFIG`, `SUSPEND`, `RESUME`, `RESET`, `SET_LOGGING_BUFFER`, `QUERY_MES_STATUS`, `PROGRAM_GDS`, `SET_DEBUG_VMID`, `MISC`, `UPDATE_ROOT_PAGE_TABLE`, and `MESAPI_AMD_LOG`.

## Control Flow
There is no C implementation in this header. Runtime control flow is firmware-command based: host code fills one command union, sets `header.type`, `header.opcode`, and `header.dwsize`, writes it to the MES ring, then waits for `MES_API_STATUS` fence completion or query/log output. Queue lifecycle flow is typically set hardware resources, configure scheduling, add queues with process/gang/doorbell/MQD/wptr data, then suspend/resume/reset/remove as scheduling changes or faults occur.

## State and Persistence
The header defines serialized state layouts. Persistent MES state exists in firmware and GPU memory pointed to by fields such as scheduler context, process/gang context, MQD, write pointer, logging buffer, event interrupt history, fences, and page-table addresses. The `#pragma pack(push, 4)` setting is part of the ABI and must match firmware expectations.

## Dependencies and Integration Points
The header is consumed by `amdgpu/mes_v11_0.c` and common MES code. It integrates with AMDGPU queue management, KFD process queues, GPUVM page table updates, debug trap/shader debugger setup, GDS programming, reset/hang detection, firmware logging, and interrupt/fence completion handling.

## Risks and Test Signals
The primary risk is binary layout drift: field order, packing, bitfields, enum values, and 64-dword frame size must match MES firmware. Additional risks include using CPU virtual addresses where GPU MC addresses are required, wrong doorbell offsets, missing status-fence setup, and command variants gated by scheduler API version. Test signals include MES queue add/remove on gfx/compute/SDMA queues, firmware fence completion, suspend/resume/reset behavior, logging buffer wrap behavior, debug VMID allocation/release, misc register read/write/wait commands, and GPUVM root page table update under active workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v11_api_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v12_api_def.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v12_api_def.h

## Purpose
This header defines the packed MES v12 scheduler firmware API. It evolves the v11 command-frame ABI with 8-byte packing, API version `0x14`, larger logging, richer error reporting, RRMT register remapping, cooperative/debug context setup, extended queue/reset fields, query subcommands, SE mode switching, gang submit setup, and explicit TLB invalidation commands.

## Important APIs, Types, and Functions
Important constants include `MES_API_VERSION 0x14`, `AMDGPU_MES_LOG_BUFFER_SIZE 0xC000`, 64-dword frames, and 32 command slots. `MES_ERR_CODE` encodes API error, scheduler opcode, misc opcode, category, and error bit into the high 32 bits of a completion fence value. New or expanded enums include `MES_RRMT_MODE`, `MES_ERROR_CATEGORY_CODE_12`, `MES_API_QUERY_MES_OPCODE`, and `MES_SE_MODE`. Command unions mirror v11 but add fields such as `enable_mes_fence_int`, unmapped doorbell handling, MES debug/co-op context, full shader memory config, timestamps, context-array indexes, connected queue indexes, query subcommands, RRMT options for register commands, `SET_GANG_SUBMIT`, `SET_SE_MODE`, and `INV_TLBS`.

## Control Flow
Runtime flow remains command-ring based: driver code fills a fixed frame, submits it to MES, then waits for API status fence completion and optional interrupt. v12 adds a specified error-completion encoding and documents that MES can interrupt with source ID 181/EOP when processing finishes if fence interrupt support is enabled. Queue management uses add/remove/suspend/resume/reset commands with richer identifiers so firmware can manage process/gang context arrays and connected queues.

## State and Persistence
The header owns no storage but defines persistent firmware-visible state. GPU memory addresses reference scheduler contexts, debug contexts, co-op shared buffers, cleaner shader fences, process and gang contexts, MQDs, write pointers, log buffers, TLB invalidation ranges, and output buffers. `#pragma pack(push, 8)` is ABI-critical and differs from v11.

## Dependencies and Integration Points
It is consumed by `amdgpu/mes_v12_0.c`, `mes_v12_1.c`, common MES code, and KFD queue paths. Integration points include MES scheduler initialization, hardware resource programming, queue add/remove, SDMA/gfx/compute scheduling, TLB invalidation, debug VMID setup, shader debugger control, SE mode power/performance switching, gang submit coordination, logging, health queries, and firmware error reporting.

## Risks and Test Signals
Risks include mixing v11 and v12 packing/layouts, failing to gate fields by scheduler API version, incorrect error decoding, using the wrong address type for `wptr_addr`, malformed RRMT steering on multi-die parts, and incomplete TLB invalidation range selection. Test signals include MES v12/v12.1 queue lifecycle tests, API fence interrupt handling, error-path decoding from `MES_ERR_CODE`, TLB invalidation by PASID and VMID, debug VMID setup including VM setup operation, RRMT register read/write on multi-die ASICs, SE mode switching, gang submit setup, and logging buffer stress with wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v12_api_def.h -->
