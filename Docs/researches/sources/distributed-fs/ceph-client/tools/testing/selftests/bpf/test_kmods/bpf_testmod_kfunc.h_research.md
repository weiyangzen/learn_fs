# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod_kfunc.h

## Research

This header is the shared type contract for `bpf_testmod` kfunc selftests. It is included both by kernel module code and by BPF program code, with conditional includes and definitions for `__KERNEL__` versus BPF-side compilation.

It defines nested structures used to validate verifier handling of argument shapes, nested members, trusted pointers, reference-counted kfunc returns, pass/fail parameter layouts, address arguments, socket initialization arguments, and sendmsg arguments. Kernel-only definitions include `prog_test_member1`, `prog_test_member`, and `prog_test_ref_kfunc` with a `refcount_t`; BPF-side builds use `vmlinux.h`, `bpf_helpers.h`, and `__ksym` declarations. The header also provides prototypes or external symbol declarations consumed by BPF programs for module kfunc calls.

There is no control flow or persistent state in the header, but its types control verifier semantics for size-suffixed memory parameters, acquire/release pairs, nullable returns, trusted/RCU pointers, socket address bounds, and implicit arguments. Dependencies include vmlinux BTF on the BPF side and kernel definitions such as `refcount_t` on the module side.

Risks are ABI and annotation drift. If field order, names, or suffix conventions such as `__sz`, `__nullable`, or reference annotations change, verifier expectations and kfunc registration tests can fail. Test signals are successful BPF object compilation, kfunc resolution against module BTF, expected verifier accept/reject outcomes for pass/fail structures, and correct runtime behavior for reference and socket kfunc tests.
