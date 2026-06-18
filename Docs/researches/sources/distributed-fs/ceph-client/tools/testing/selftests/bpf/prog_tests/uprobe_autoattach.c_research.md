# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_autoattach.c

## Purpose
Validates skeleton autoattach for uprobes and uretprobes against both local functions and shared-library functions resolved by name.

## APIs, Types, and Functions
Defines local noinline `autoattach_trigger_func()` and public `test_uprobe_autoattach()`. Uses `test_uprobe_autoattach.skel.h`.

## Control Flow, State, and Persistence
The skeleton opens/loads and autoattaches. The test sets its pid, calls the local trigger function with eight arguments, then opens `/dev/null` to trigger libc/shared-library probes. It validates BSS counters, captured parameters, return codes, and architecture-dependent register argument slots. State is transient in BSS and the temporary `FILE *`.

## Dependencies and Integration
Depends on libbpf skeleton autoattach metadata, uprobe/uretprobe support, shared-library symbol resolution, and `FUNC_REG_ARG_CNT` architecture limits.

## Risks and Test Signals
Risks include compiler inlining despite `noinline`, libc symbol differences, and missing register arguments on some architectures. Signals are exact BSS counters, argument values, and return values after local and shared-library triggers.
