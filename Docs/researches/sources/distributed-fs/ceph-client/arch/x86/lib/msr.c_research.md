# sources/distributed-fs/ceph-client/arch/x86/lib/msr.c

## Purpose
This file contains common x86 MSR utility functions. It allocates per-CPU MSR buffers, implements read-modify-write bit helpers for 64-bit MSR fields, and exposes tracepoint bridge functions for MSR/RDPMC instrumentation.

## Important APIs, Types, and Functions
`msrs_alloc()` and `msrs_free()` allocate and release `struct msr __percpu` arrays. `msr_set_bit()` and `msr_clear_bit()` are KVM-exported helpers backed by `__flip_bit()`, `msr_read()`, and `msr_write()`. Tracepoint wrappers under `CONFIG_TRACEPOINTS` are `do_trace_write_msr()`, `do_trace_read_msr()`, and `do_trace_rdpmc()`, and the file instantiates `CREATE_TRACE_POINTS` for `asm/msr-trace.h`.

## Control Flow
The bit helpers validate the bit index, read the MSR with `rdmsrq_safe()`, modify the requested bit in a copy, skip writes when no change is needed, and write the new value with `wrmsrq_safe()`. They return a negative error, `0` for no hardware write, or positive success for an accepted write. Trace wrappers simply call the generated tracepoint functions with the MSR/PMC number, value, and failure flag.

## State and Persistence
Persistent state is limited to allocated per-CPU MSR buffers owned by callers and the tracepoint definitions registered by the tracing subsystem. The bit helpers do not cache MSR state.

## Dependencies and Integration Points
The file integrates with Linux per-CPU allocation, `asm/msr.h` safe MSR primitives, KVM symbol export policy, and x86 MSR tracepoints. KVM can use `msr_set_bit()`/`msr_clear_bit()` without depending on local implementation details.

## Risks and Test Signals
Risks include non-atomic read-modify-write if another CPU or firmware mutates the same MSR concurrently, unsupported MSRs returning errors, and feature code misreading the positive return as a bit value. Test signals include allocation failure handling, unsupported MSR reads/writes, set/clear idempotence, tracepoint visibility when enabled, and KVM module linkage.
