<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls.h -->
# sources/distributed-fs/ceph-client/include/linux/syscalls.h

## Purpose

`syscalls.h` is the non-architecture-specific syscall declaration and definition-macro header. It provides `SYSCALL_DEFINE*` machinery, syscall tracing metadata generation, argument casting/sign-extension wrappers, compat aliases, split-64-bit helpers, and prototypes for generic, architecture-specific, and deprecated syscalls.

## Important APIs, types, and functions

Macro layers include `__MAP*`, `__SC_DECL`, `__SC_LONG`, `__SC_CAST`, `__SC_TEST`, `SYSCALL_METADATA`, `SYSCALL_TRACE_ENTER_EVENT`, `SYSCALL_TRACE_EXIT_EVENT`, `SYSCALL_DEFINE0`, `SYSCALL_DEFINE1` through `SYSCALL_DEFINE6`, `SYSCALL_DEFINEx`, `__SYSCALL_DEFINEx`, `SC_ARG64`, `SC_VAL64`, and `SYSCALL32_DEFINE*`. With tracing, each syscall can emit `struct syscall_metadata` and trace event calls. The prototype block lists kernel entry points for I/O, xattrs, fs, fd, process, time, scheduler, signal, IPC, networking, memory management, namespaces, security, BPF, Landlock, LSM, mount API, and legacy syscalls, guarded by architecture/config conditions.

## Control flow

For a normal syscall definition, `SYSCALL_DEFINE<n>` emits metadata, a public `sys_*` alias, a `__se_sys_*` sign-extension wrapper taking long-sized arguments, and an inline `__do_sys_*` implementation body. Entry code or syscall tables call the exported `sys_*` symbol. Tracing metadata is collected into special sections for ftrace syscall events. Architectures with custom wrappers can replace this machinery.

## State and persistence behavior

The header owns no runtime mutable state, but tracing metadata and event call descriptors are static kernel objects. Syscall prototypes are ABI contracts and must remain stable in calling convention and argument order.

## Dependencies and integration points

It depends on many UAPI and kernel types, `linux/unistd.h`, quota/key/personality headers, trace syscall support, and architecture syscall-wrapper headers. It integrates with syscall tables, entry code, ftrace, error injection, compat syscall definitions, static analysis, and virtually every syscall implementation file.

## Risks and test signals

Risks include ABI breakage from prototype changes, wrapper mismatches on 32-bit/64-bit or compat builds, sign-extension bugs, tracing metadata argument drift, split 64-bit argument ordering errors, and adding prototypes when `CONFIG_ARCH_HAS_SYSCALL_WRAPPER` expects arch ownership. Tests should include all-arch build coverage, syscall selftests, compat syscall tests, ftrace syscall event validation, BPF/seccomp interaction tests, error-injection builds, and static checks that syscall table entries match prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls.h -->
