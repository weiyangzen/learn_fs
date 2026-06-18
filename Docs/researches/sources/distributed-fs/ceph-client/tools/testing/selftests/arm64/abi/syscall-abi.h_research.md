# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.h

Purpose: shared SVCR bit definitions for the arm64 syscall ABI C and assembly code.

Important APIs/types/functions: defines `SVCR_ZA_MASK`, `SVCR_SM_MASK`, `SVCR_ZA_SHIFT`, and `SVCR_SM_SHIFT`.

Control flow: no runtime flow.

State and persistence: none.

Dependencies/integration: included by `syscall-abi.c` and `syscall-abi-asm.S` to keep bit positions consistent.

Risks and test signals: incorrect constants would invalidate all SME streaming/ZA checks.
