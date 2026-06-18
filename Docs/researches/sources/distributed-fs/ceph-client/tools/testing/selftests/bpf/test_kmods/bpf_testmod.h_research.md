# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.h

## Research

This header defines shared ABI structures for the `bpf_testmod` kernel module and BPF/user-space tests that interact with it. It is intentionally type-heavy and logic-free.

The context structures `bpf_testmod_test_read_ctx`, `bpf_testmod_test_write_ctx`, and `bpf_testmod_test_writable_ctx` describe tracepoint payloads and writable tracepoint mutation state. `bpf_iter_testmod_seq` defines the simple iterator state used by module iterator kfuncs. `bpf_testmod_ops`, `ops2`, `ops3`, `bpf_testmod_st_ops`, and `bpf_testmod_multi_st_ops` define struct_ops layouts used by BPF programs to install callbacks into the module. The primary `bpf_testmod_ops` structure intentionally includes nullable/refcounted arguments, shadow-copy fields, unsupported fields, data fields, and forty trampoline function pointers to test multi-page trampoline allocation.

State and persistence are external to the header. Once compiled into module/BPF objects, these layouts become BTF ABI contracts. Dependencies include Linux integer types and forward declarations for `task_struct`, `cgroup`, `module`, and `hlist_node`.

Risks are layout drift and annotation mismatches. Because BPF verifier and struct_ops tests depend on exact field names, offsets, function prototypes, and BTF-emitted types, changing this header can affect many tests. Test signals include successful BTF matching between BPF programs and module types, struct_ops map creation/attach, correct nullable/refcounted argument verification, and trampoline stress tests.
