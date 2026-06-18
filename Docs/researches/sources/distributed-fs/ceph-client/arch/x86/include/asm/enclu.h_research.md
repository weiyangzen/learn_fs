
# sources/distributed-fs/ceph-client/arch/x86/include/asm/enclu.h

Purpose: SGX ENCLU leaf constants for enclave entry/exit/resume operations.

Important APIs and control flow: defines `EENTER`, `ERESUME`, and `EEXIT` leaf numbers. Actual instruction issuing and state transitions occur in SGX assembly/C code.

State, dependencies, and risks: state is SGX enclave CPU state outside this header. Dependencies include SGX feature support and ENCLU call sites. Risks include using wrong leaf numbers or exposing SGX paths on unsupported hardware. Test signals are SGX selftests and enclave transition tests.
