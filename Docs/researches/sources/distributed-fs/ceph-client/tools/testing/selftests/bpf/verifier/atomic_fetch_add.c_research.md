# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch_add.c

Purpose: focused tests for `BPF_ADD | BPF_FETCH`, checking correct old-value return, stack update, read-initialization requirements, frame-pointer immutability, and rejection of atomic writes to kernel memory exposed through tracing contexts.

Important APIs/types/functions: uses `BPF_ATOMIC_OP`, stack stores and loads, `BPF_PROG_TYPE_TRACING`, `BPF_TRACE_FENTRY`, and `.kfunc = "bpf_fentry_test7"` to exercise read-only kernel memory.

Control flow: accepted 64-bit and 32-bit smoke tests store `3`, add `1`, check that the source register receives old value `3`, then check the stack slot is `4`. Rejection cases try to use `R10` as the atomic source, use uninitialized source or destination registers, or perform fetch-add through an fentry argument pointer.

State and persistence behavior: mutable state is stack memory except the kernel-memory test, where verifier state must tag the traced object as read-only. `R10` must remain a read-only frame pointer even when used as the atomic fetch source.

Dependencies and integration points: integrated with tracing verifier support and kfunc attachment metadata. The `.prog_type`, `.expected_attach_type`, and `.kfunc` fields are necessary for the kernel-memory test path.

Risks: weakening these checks could allow atomic modification of frame pointers, uninitialized register use, or mutation of read-only kernel memory from tracing programs.

Test signals: accepted smoke tests return zero on success; expected rejections include `frame pointer is read only`, `!read_ok`, unprivileged `R10 leaks addr into mem`, and `only read is supported`.
