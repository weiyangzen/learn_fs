## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vsgx.S

Purpose: vDSO helper for entering or resuming Intel SGX enclaves from userspace.

Important API/function: `__vdso_sgx_enter_enclave`. It interprets `struct sgx_enclave_run` fields by fixed offsets, validates `EENTER..ERESUME`, uses `ENCLU`, records exit/exception information, optionally calls a userspace handler, and emits a vDSO exception-table entry around ENCLU.

Control flow: prologue saves RBP/RBX, validates input leaf and reserved fields, loads TCS and asynchronous-exit pointer, executes ENCLU, records normal EEXIT, and either returns zero or invokes the userspace callback. Exception fixup lands at `.Lhandle_exception`, stores vector/error/address fields passed by `extable.c`, and follows the same exit-handler path. Positive callback return values request another ENCLU attempt.

State/persistence: writes into caller-provided `sgx_enclave_run`, including leaf/exit reason, exception vector, error code, and address. It preserves ABI stack alignment and clears DF before callback.

Integration points: SGX UAPI, vDSO extable, x86 trap fixup, linker symbol export under `CONFIG_X86_SGX`, and userspace enclave runtimes.

Risks: reserved-field validation, LVI `lfence`, callback stack alignment, and exception metadata are security-sensitive. Test signals include SGX selftests, enclave exception handling, callback retry behavior, invalid input tests, readelf extable checks, and LVI mitigation inspection.
