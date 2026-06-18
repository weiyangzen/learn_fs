<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instruction_pointer.h -->
# sources/distributed-fs/ceph-client/include/linux/instruction_pointer.h

Purpose: Provides generic instruction-pointer capture macros for tracing and diagnostics.

Important APIs/types/functions: `_RET_IP_` expands to `__builtin_return_address(0)` as an unsigned long. `_THIS_IP_` uses a local label address to identify the current code location unless an architecture has already supplied it.

Control flow: Call sites expand the macros inline to capture return or current instruction addresses without a function call.

State/persistence: Stateless macro expansion over compiler-provided code addresses.

Dependencies/integration: Includes `asm/linkage.h` and is used by tracing, logging, warning, and profiling code that records call sites.

Risks: Return-address availability depends on compiler and frame layout; `_THIS_IP_` relies on local label address support.

Test signals: Architecture builds, WARN/trace call-site reporting, ftrace/perf samples, and compiler configurations with frame-pointer variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instruction_pointer.h -->
