<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kallsyms.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kallsyms.h

## Purpose
This header provides minimal kallsyms-style symbol lookup hooks for lockdep and tools diagnostics.

## APIs And Flow
It defines `KSYM_NAME_LEN`, forward declares `struct module`, and provides `kallsyms_lookup()` returning `NULL`. With `HAVE_BACKTRACE_SUPPORT`, `print_ip_sym()` calls `backtrace_symbols()` for a single instruction pointer and prints via `printk`; otherwise it is an empty stub.

## State, Dependencies, Risks, Tests
State is transient stack storage and libc-allocated symbol strings in the optional backtrace path. Dependencies include `linux/kernel.h`, `linux/types.h`, optional `<execinfo.h>`, and printk-compatible logging. Risks are weak symbol fidelity compared with kernel kallsyms, allocation behavior in diagnostics, and silent empty output when backtrace support is absent. Tests should build both config paths and verify a known address produces useful diagnostic text when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kallsyms.h -->
