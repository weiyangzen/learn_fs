# sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_32.c

Purpose: exports 32-bit x86 architecture metadata needed by crash dump tooling to interpret vmcore memory after a kernel crash.

Important APIs/functions: implements `arch_crash_save_vmcoreinfo()`.

Control flow: when crash vmcore metadata is generated, the function conditionally records the `node_data` symbol and `MAX_NUMNODES` length for NUMA builds and records the `X86_PAE` config flag for PAE builds.

State and persistence: it does not maintain local state. It appends key/value and symbol metadata into the global vmcoreinfo note consumed by kdump/crash utilities.

Dependencies and integration: depends on `linux/vmcore_info.h`, page-table configuration, `asm/setup.h`, NUMA globals, and the generic crash dump path that invokes `arch_crash_save_vmcoreinfo()`.

Risks: missing or stale metadata can prevent dump analyzers from locating per-node memory structures or selecting the correct 32-bit page-table format. Conditional compilation must match the actual built kernel configuration.

Test signals: kdump vmcoreinfo notes from 32-bit NUMA and PAE/non-PAE kernels should contain the expected symbols and config markers, and crash analysis tools should parse memory topology correctly.
