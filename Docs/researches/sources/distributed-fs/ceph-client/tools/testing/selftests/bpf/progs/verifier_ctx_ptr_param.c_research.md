# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ctx_ptr_param.c

## Purpose

`verifier_ctx_ptr_param.c` tests BTF-based fentry/fexit context parameter inference for pointer-to-pointer arguments. It ensures `void **`, `void ***`, and `struct file **` parameters are not exposed to BPF as trusted kernel object pointers, but as scalar values.

## Important APIs, Types, and Functions

The programs attach to test kernel functions named `bpf_fentry_test_ppvoid`, `bpf_fentry_test_pppvoid`, `bpf_fentry_test_ppfile`, and `bpf_fexit_test_ret_ppfile`. Each program is naked inline assembly and uses `__msg` expectations to assert verifier register types, especially `R1=ctx()` and `R2=scalar()`.

## Control Flow

Each program receives the tracing context, reads the second logical argument from the fentry/fexit ctx layout, and returns zero. There is no data mutation. The point is the verifier log generated during load: the second parameter must remain scalar even when its C type contains kernel pointer-looking layers.

## State and Persistence Behavior

No maps or persistent state exist. The state under test is verifier argument-type materialization from BTF function prototypes and ctx slots. Returning these parameters as scalar prevents accidental direct dereference or trusted pointer use.

## Dependencies and Integration Points

The file depends on BTF for the test functions, libbpf tracing section attachment, and verifier tracing-context argument decoding. It integrates with selftest kfunc/fentry fixtures that provide the target prototypes.

## Risks and Test Signals

The main risk is a BTF decoder regression that marks pointer-to-pointer arguments as kernel pointers. The test signal is successful load with the expected verifier log showing scalar classification for the second argument in all four cases.
