# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_y.c

## Research

This module is the `y` counterpart to the module-order kfunc test. It defines `bpf_test_modorder_rety()` as an `__bpf_kfunc` returning `'y'`, places it into a BTF kfunc ID set, and registers that set for `BPF_PROG_TYPE_SCHED_CLS` from module initialization.

The API surface is intentionally tiny: one kfunc, one `btf_kfunc_id_set`, and module init/exit functions. Control flow is registration-only; exit does no explicit cleanup. State is limited to the loaded module and registered kfunc set owned by `THIS_MODULE`. It depends on the same kernel BTF/kfunc/module infrastructure as the `x` module.

Its integration role is to provide a second module with a similarly named but distinct kfunc so selftests can validate module BTF ordering, lookup, and call target disambiguation. Risks are the same as `bpf_test_modorder_x.c`: module BTF absence, registration failure, name drift, or changed verifier handling for module kfuncs. Test signals are successful load and a BPF program being able to resolve/call `bpf_test_modorder_rety()` and distinguish its return value from the `x` module.
