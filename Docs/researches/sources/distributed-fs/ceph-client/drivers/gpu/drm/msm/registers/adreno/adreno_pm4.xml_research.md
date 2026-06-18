# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_pm4.xml

## Purpose
This XML file is the Freedreno/Adreno PM4 command-stream schema. It defines command processor packet types, event ids, draw initiators, register/memory operation payloads, indirect-buffer formats, shader-state load packets, binning packets, cache/CCU/LRZ events, timestamp and synchronization packets, and generation-specific opcode variants from A2xx through A8xx. It is not executable kernel logic itself; its practical API is the generated C header consumed by MSM Adreno ringbuffer emission code.

## Important APIs, Types, and Functions
The important generated symbols come from enums such as `vgt_event_type`, `pc_di_primtype`, `pc_di_src_sel`, `pc_di_face_cull_sel`, `pc_di_index_size`, `pc_di_vis_cull_mode`, `adreno_pm4_packet_type`, and `adreno_pm4_type3_packets`. Packet payload domains include `CP_LOAD_STATE`, `CP_LOAD_STATE4`, `CP_LOAD_STATE6`, `CP_DRAW_INDX`, `CP_DRAW_INDX_2`, `CP_DRAW_INDX_OFFSET`, `CP_DRAW_INDIRECT`, `CP_DRAW_INDX_INDIRECT`, `CP_DRAW_INDIRECT_MULTI`, `CP_DRAW_AUTO`, predication packets, `CP_SET_DRAW_STATE`, binning packets, register/memory copy and wait packets, `CP_DISPATCH_COMPUTE`, `CP_SET_RENDER_MODE`, `CP_COMPUTE_CHECKPOINT`, `CP_PERFCOUNTER_ACTION`, `CP_EVENT_WRITE`, and A7xx/A8xx additions such as timestamp, thread-control, resource-list, cache, memory-map, and barrier commands. Driver call sites use these as `CP_*`, `*_EVENT`, and field packer macros through `OUT_PKT3`, `OUT_PKT4`, `OUT_PKT7`, and `OUT_RING`.

## Control Flow
Kernel and userspace command submission builds PM4 streams by choosing a packet opcode, packing fields defined here, then placing the words in a ringbuffer or indirect buffer. Older generations use type3 packets for many paths, while A5xx+ use packet7 variants and generation-specific opcodes where numeric ids were reused. Control dependencies are expressed by wait packets, event writes, cache flush/invalidate events, SMMU table update commands, preemption/yield packets, and thread-synchronization packets rather than C control flow in this XML.

## State and Persistence Behavior
This schema defines how command streams mutate GPU state: shader program state, constants, UBO/UAV state, draw state objects, predicate state, binning state, render mode, SMMU context, scratch registers, counters, timestamps, cache/CCU/LRZ contents, and memory writes. The XML itself persists only as source for generated headers, but incorrect field definitions persist into every compiled packet writer and therefore into the ABI between the kernel/userspace command emitters and GPU firmware.

## Dependencies and Integration Points
It imports `adreno/adreno_common.xml` and common Freedreno copyright metadata, and it is consumed by the register generation pipeline that produces Adreno PM4 C macros. Integration points include `a2xx_gpu.c`, `a3xx_gpu.c`, `a4xx_gpu.c`, `a5xx_gpu.c`, `a5xx_preempt.c`, `a6xx_gpu.c`, crashdump/state capture code, Mesa/Freedreno command emitters, GPU firmware packet parsers, ringbuffer submit paths, preemption support, cache management, and SMMU context switching.

## Risks
The highest risk is opcode reuse across generations: a numeric packet or event value may mean different things on A4xx, A5xx, A6xx, A7xx, or A8xx, so missing or wrong `variants` attributes can emit a valid-looking but wrong command. Address field width differences, packet length expectations, predicate side effects, cache event semantics, protected-mode toggles, and SMMU update payloads are all sensitive. Errors here usually fail as GPU hangs, command processor faults, memory corruption, stale cache data, or unhandled preemption.

## Test Signals
Useful signals include generated-header build checks, GPU submit smoke tests on each supported generation, ringbuffer idle and fence completion tests, cache flush timestamp validation, SMMU context-switch tests, preemption/yield stress, IGT/MSM GPU tests, Mesa deqp/piglit coverage, crashdump decoding sanity, and fault-injection around invalid packets or register protection.
