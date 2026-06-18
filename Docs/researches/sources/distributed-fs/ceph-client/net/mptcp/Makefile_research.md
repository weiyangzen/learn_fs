<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Makefile -->
# sources/distributed-fs/ceph-client/net/mptcp/Makefile

## Purpose
Declares which object files compose the MPTCP core module/built-in object and optional companion modules for syncookies, diagnostics, KUnit tests, and BPF integration.

## Important APIs, Types, and Functions
`mptcp-y` aggregates protocol, subflow, options, token, crypto, control, path manager, diagnostics, MIB, netlink/userspace/kernel PM, sockopt, fastopen, scheduler, and generated PM netlink objects. Optional objects are controlled by `CONFIG_SYN_COOKIES`, `CONFIG_INET_MPTCP_DIAG`, `CONFIG_MPTCP_KUNIT_TEST`, and `CONFIG_BPF_SYSCALL`.

## Control Flow
There is no runtime flow. Kbuild uses these lists to link `mptcp.o`, `mptcp_diag.o`, `mptcp_crypto_test.o`, `mptcp_token_test.o`, and `bpf.o`.

## State and Persistence
Build composition is persistent in kernel build artifacts. Object ordering matters for link-time symbol resolution and initialization availability.

## Dependencies and Integration Points
Integrates Kconfig selections with Kbuild. It connects the files researched in this subset to the larger MPTCP implementation: `options.o`, `crypto.o`, `ctrl.o`, `pm.o`, `diag.o`, `mib.o`, `fastopen.o`, `mptcp_pm_gen.o`, and `pm_kernel.o`.

## Risks
Generated PM netlink code must remain in the core object list because kernel PM backend uses generated policies/ops. Optional `bpf.o` must stay tied to `CONFIG_BPF_SYSCALL`; otherwise BTF kfunc registration would compile without BPF infrastructure. Test object names must match their `*-objs` definitions.

## Test Signals
Build tests for builtin and module configurations, MPTCP without BPF, diagnostics as module, KUnit test modules, and symbol resolution for generated PM netlink functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Makefile -->
