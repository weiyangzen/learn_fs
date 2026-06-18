# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_no_cfi.c

## Research

This kernel module verifies that BPF struct_ops registration rejects missing CFI stubs and succeeds when stubs are provided. It defines `struct bpf_test_no_cfi_ops` with two function pointers and dummy verifier/init/register callbacks.

The init path is the test. `bpf_test_no_cfi_init()` first calls `register_bpf_struct_ops()` with `test_no_cif_ops` while `cfi_stubs` is unset. Success would mean the negative case failed, so the module returns `-EINVAL` if registration unexpectedly succeeds. It then sets `test_no_cif_ops.cfi_stubs` to `__test_no_cif_ops`, a struct populated with stub functions, and retries registration; the second return value becomes the module init result. Exit is empty.

State is kernel struct_ops registration state owned by the module. Dependencies include BPF struct_ops infrastructure, CFI stub enforcement, module support, and BTF for `bpf_test_no_cfi_ops`. Integration is through module-load tests that expect this module to load only because the second registration succeeds after the first rejection.

Risks include semantic changes in struct_ops CFI requirements, lack of cleanup if a future registration path partially succeeds, and the confusing `cif` spelling in local variable names. Test signals are module load success plus implicit evidence that missing stubs were rejected; unexpected first-registration success fails the module load with `-EINVAL`.
