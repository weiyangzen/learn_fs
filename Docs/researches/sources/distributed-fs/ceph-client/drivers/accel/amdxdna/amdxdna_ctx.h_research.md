# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ctx.h

Purpose: declares AMD XDNA command formats, context/job structures, ERT command opcodes/states, inline command-state helpers, and ioctl entry points for context and command submission.

Important APIs/types: `struct amdxdna_cmd` models the shared ERT-style command header and payload; bit masks encode state, extra CU masks, payload count, and opcode. Payload structs describe NPU start, command chains, and preempt data. `struct amdxdna_hwctx` stores client association, firmware context ID, allocated columns, QoS/CU config, syncobj handle, and counters. `struct amdxdna_sched_job` extends DRM scheduler job with context, mm, fences, command BO, argument BO array, driver command, sequence, and optional AIE health report. Inline helpers get/set opcode/state through mapped GEM memory.

Control flow: ioctl and AIE2 context code include this header to create contexts, inspect command BOs, push jobs, wait on sequences, and synchronize debug BOs.

State and persistence: structures define in-memory state tied to a DRM file, context, or submitted job. Command state is stored in user-visible GEM command buffers and can be observed by userspace.

Dependencies: depends on AMD XDNA GEM, DRM scheduler, dma-fence, syncobj, and UAPI QoS/CU config types.

Risks: command header bitfields must match userspace ABI. Inline helpers silently return invalid state/opcode if vmap fails, so callers must handle invalid commands. Flexible arrays require correct allocation sizing.

Test signals: command parsing for all opcodes, malformed count/mask fields, chained command error reporting, debug BO sync, scheduler job cleanup, and UAPI struct compatibility.
