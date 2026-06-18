# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_experimental.h

Purpose: collects experimental BPF kfunc declarations and verifier-oriented helper macros for selftests using new kernel features.

Important APIs and macros: declares kfuncs for object allocation, task/VMA/css/kmem/dmabuf iterators, exceptions (`bpf_throw`), file/path/xattr helpers, workqueue helpers, preempt guards, arena address-space casts, and context checks. Macros include `bpf_obj_new`, `bpf_percpu_obj_new`, `__exception_cb`, `bpf_assert*`, `bpf_cmp_likely/unlikely`, `can_loop`, `cond_break`, `bpf_nop_mov`, and `bpf_guard_preempt`.

Control flow: most content is declarations and inline/asm macros. Assertion macros emit conditional BPF branches that call `bpf_throw`; loop macros emit `may_goto` or raw instruction encodings depending on compiler feature and endianness. Interrupt-context helpers read architecture-specific preempt count state with CO-RE fallbacks.

State and persistence: no own state, but exposes APIs that acquire references, allocate objects, or disable preemption; users must release resources and allow cleanup destructors to run.

Dependencies and integration points: depends on `vmlinux.h`, libbpf helper/tracing/core-read headers, BPF target architecture macros, weak kconfig variables, and kernel kfunc availability.

Risks: explicitly experimental and feature-sensitive; missing kfuncs or changed BTF names cause verifier/load failures; inline assembly is architecture/compiler sensitive; exception assertions cannot be used with lingering refs/locks.

Test signals: compile/load success across feature matrices, verifier acceptance of assertions/loops/casts, and runtime tests for context detection and kfunc behavior.
