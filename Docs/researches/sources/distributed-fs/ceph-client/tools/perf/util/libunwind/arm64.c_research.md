<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libunwind/arm64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/libunwind/arm64.c

## Purpose

`libunwind/arm64.c` builds and exports ARM64 remote libunwind operations for perf, even when the host architecture differs.

## Important APIs, Types, and Functions

It defines `REMOTE_UNWIND_LIBUNWIND`, maps `LIBUNWIND__ARCH_REG_ID()` to `libunwind__arm64_reg_id()`, aliases `perf_event_arm_regs` to `perf_event_arm64_regs`, includes ARM64 perf-reg UAPI and the architecture unwind implementation, maps `NO_LIBUNWIND_DEBUG_FRAME_AARCH64` to the generic flag, includes local libunwind implementation, and exports `arm64_unwind_libunwind_ops`.

## Control Flow

Compile-time include composition generates architecture-specific unwind functions and assigns `_unwind_libunwind_ops` to the exported ARM64 ops pointer.

## State and Persistence Behavior

The exported ops pointer is static process state. Runtime unwind state is managed by generic libunwind code included here.

## Dependencies and Integration Points

It depends on libunwind headers, ARM64 perf register UAPI, `arch/arm64/util/unwind-libunwind.c`, and `util/unwind-libunwind-local.c`. It integrates with perf thread unwinding for ARM64 targets.

## Risks and Edge Cases

Because implementation files are included directly, macro ordering is critical. Debug-frame feature flags must match the target libunwind. Host/target register mapping must stay aligned with ARM64 UAPI.

## Test Signals

Cross-architecture unwind tests should sample ARM64 user stacks, verify register mapping, test builds with and without debug-frame support, and ensure host-non-ARM builds still expose ARM64 ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libunwind/arm64.c -->
