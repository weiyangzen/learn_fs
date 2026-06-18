# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.c

## Purpose
Host-side SGX selftest runner. It builds and enters a small test enclave, validates vDSO entry behavior, TCS selection, PTE and EPCM permission transitions, SGX2 page augmentation/removal/type changes, and error reporting through `struct sgx_enclave_run`.

## Important APIs, types, and functions
Key helpers include vDSO dynamic table/symbol functions (`vdso_get_dyntab()`, `vdso_get_dyn()`, `vdso_get_symtab()`, `vdso_symtab_get()`), SGX2/EPC helpers (`sgx2_supported()`, `get_total_epc_mem()`), enclave offset helpers (`encl_get_tcs_offset()`, `encl_get_data_offset()`), and `setup_test_encl()`. The `ENCL_CALL` macro chooses preserved-register wrapper or raw vDSO call; `EXPECT_EEXIT` validates clean enclave exits. Tests use Linux SGX ioctls `SGX_IOC_ENCLAVE_RESTRICT_PERMISSIONS`, `SGX_IOC_ENCLAVE_MODIFY_TYPES`, and `SGX_IOC_ENCLAVE_REMOVE_PAGES`.

## Control flow
Every test initializes an enclave with `setup_test_encl()`, which loads, measures, builds, maps each segment with its intended protection, and discovers `__vdso_sgx_enter_enclave`. Basic tests write/read magic values through enclave operations and exercise clobbered versus unclobbered vDSO calls. Permission tests first prove normal access, then change PTE or EPCM permissions and expect specific page fault vectors/error codes before restoring access by `mprotect()` or enclave-side `EMODPE`. Augmentation tests map unused enclave address space, trigger or preemptively accept EAUG pages via enclave `EACCEPT`, and verify read/write. TCS creation adds stack/TCS/SSA pages, initializes a TCS page inside the enclave, changes its type to TCS, enters through it, then removes/reuses pages. Removal tests validate correct failure without `EACCEPT`, invalid access after trim, invalid access after accept without final removal, and successful removal of an untouched page.

## State and persistence
`FIXTURE(enclave)` owns `struct encl` and `struct sgx_enclave_run`. Enclave memory, SGX page types, pending/modified/trim states, exception fields, and selected TCS are runtime state. No persistent disk state is written beyond build artifacts; the test maps `/proc/self/maps` only for diagnostics in setup failure.

## Dependencies and integration points
Depends on `load.c`, `sigstruct.c`, `call.S`, `test_encl.elf`, Linux SGX vDSO, `/dev/sgx_enclave`, CPUID SGX leaves, SGX2 hardware and kernel ioctl support for dynamic tests, and `kselftest_harness.h`.

## Risks
SGX tests are hardware-, firmware-, kernel-, and mount-policy-sensitive. Oversubscription/removal can take a long time and has a 900-second timeout. The tests rely on exact SGX page fault error codes, enclave size power-of-two rules, and fixed segment ordering. Dynamic page flows must use a second TCS after AEX in some cases to repair state safely.

## Test signals
Expected pass signals include clean `EEXIT`, zero exception fields, exact magic value round trips, ioctl counts equal to requested lengths, and specific page fault vectors/error codes such as `14`, `0x7`, `0x8007`, and `0x8005`. Skip signals cover missing SGX2, unsupported ioctls (`ENOTTY`), unsupported hardware (`ENODEV`), and kernels without initialized-enclave page addition.
