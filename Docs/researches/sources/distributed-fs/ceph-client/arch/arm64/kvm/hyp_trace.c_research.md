# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.c

## Purpose
This file registers and manages remote tracing for nVHE hypervisor events. It creates shared trace buffers, maps or shares pages with hyp, synchronizes a hyp trace clock with kernel boot time, exposes tracefs controls, and bridges event enable/reset/swap operations to hyp calls.

## Important APIs, Types, and Functions
- `struct hyp_trace_clock` stores cycle/boot epochs, mult/shift conversion, delayed work, completion, and running state.
- `__hyp_clock_work()` computes clock conversion and updates hyp through `__tracing_update_clock`.
- `struct hyp_trace_buffer` stores the hyp trace descriptor and descriptor size.
- Buffer lifecycle functions include `hyp_trace_load()`, `hyp_trace_unload()`, `hyp_trace_buffer_share_hyp()`, and `hyp_trace_buffer_unshare_hyp()`.
- Trace callbacks implement load/unload, enable tracing, reader-page swap, reset, enable event, and tracefs initialization.
- `kvm_hyp_trace_init()` validates platform support, initializes event IDs, and registers the remote tracer.

## Control Flow
Trace initialization exits early for VHE kernels, rejects out-of-line arch timer counter workarounds that hyp tracing cannot handle, assigns event IDs, and calls `trace_remote_register()`. When a remote trace buffer is loaded, the code allocates a descriptor, maps it into hyp when host-owned hyp mappings are available, allocates backing pages for simple ring-buffer pages, lets trace_remote initialize per-CPU buffers, shares metadata and data pages with hyp, and calls `__tracing_load`.

Tracing enable starts the clock worker, waits for the initial conversion, and calls hyp to enable tracing. The delayed worker periodically compares arch-counter-derived time against kernel boot time, recalculates mult/shift when drift appears, fast-forwards epochs before overflow, and pushes updates into hyp. Event enabling either calls hyp directly for protected KVM or vmap-writes the hyp event's shared atomic flag for normal nVHE.

## State and Persistence
Persistent runtime state includes the global `hyp_clock`, global `trace_buffer`, allocated trace descriptors, ring buffer pages, bpage backing storage, shared page ownership state, tracefs files, and event IDs generated from linker ranges. The clock worker remains scheduled while tracing is enabled.

## Dependencies and Integration Points
It depends on `trace_remote`, `tracefs`, `simple_ring_buffer`, arch timer snapshots, hyp tracing ABI functions such as `__tracing_load`, `__tracing_enable`, `__tracing_swap_reader`, `__tracing_reset`, and KVM hyp mapping/sharing helpers from `mmu.c`. Event definitions are pulled in through `asm/kvm_define_hypevents.h`.

## Risks and Edge Cases
Important risks include leaking shared pages on partial allocation failure, freeing with an incorrect descriptor size, clock drift beyond trace precision, unsupported timer workarounds, and event-enable races between host and hyp. Protected KVM changes the event-enable path because direct host writes are not allowed.

## Test Signals
Enable hyp tracing through tracefs, toggle individual events, swap reader pages on each CPU, reset buffers, unload/reload tracing, and run under pKVM and non-pKVM nVHE. Watch for allocation unwind warnings, clock drift warnings, trace event timestamp monotonicity, and page sharing errors.
