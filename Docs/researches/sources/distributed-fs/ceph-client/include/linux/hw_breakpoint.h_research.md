# sources/distributed-fs/ceph-client/include/linux/hw_breakpoint.h

## Purpose
Declares the kernel hardware breakpoint interface built on perf events, plus fallback stubs for architectures without breakpoint support.

## APIs, Control Flow, and State
When `CONFIG_HAVE_HW_BREAKPOINT` is enabled, `hw_breakpoint_init()` initializes a `perf_event_attr` as a pinned breakpoint event with period 1, and `ptrace_breakpoint_init()` additionally excludes kernel hits. Registration APIs cover user/task breakpoints, wide per-cpu kernel breakpoints, direct perf breakpoint registration, modification, slot reservation/release, unregister, ptrace flush, and usage checks. `bp_type_idx` accounts for architectures with shared or separate instruction/data breakpoint registers. State is mostly in `perf_event`, architecture breakpoint info (`bp->hw.info`), and slot accounting managed by implementation files. Disabled builds return `NULL`, `-ENOSYS`, false, or no-op.

## Dependencies, Integration, Risks, and Tests
Depends on perf event internals and UAPI breakpoint definitions. Integrates with ptrace debug registers, perf, kernel watchpoints, and architecture-specific breakpoint backends. Risks include leaking reserved slots, modifying attrs without validation, assuming returned `NULL` vs `ERR_PTR`, and missing arch constraints on breakpoint length/type/alignment. Test signals include perf/hw-breakpoint selftests, ptrace watchpoint tests, slot exhaustion tests, and !CONFIG fallback builds.
