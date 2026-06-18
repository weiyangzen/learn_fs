# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.h

Purpose: shared validation and packing helper for ptrace VMX/VSX tests.

Important APIs/types/functions: defines `VEC_MAX`, `VSX_MAX`, `VMX_MAX`, `validate_vsx()`, `validate_vmx()`, `compare_vsx_vmx()`, `load_vsx_vmx()`, and prototypes for assembly `loadvsx()`/`storevsx()`.

Control flow: validators compare ptrace-exposed arrays against the synthetic 128-word load buffer. `validate_vsx()` checks the high doubleword mapping for VSX 0-31. `validate_vmx()` and `compare_vsx_vmx()` branch on compile-time endianness because VMX pairs are stored in alternate order on little endian. `load_vsx_vmx()` converts a flat buffer into ptrace write payloads.

State and persistence behavior: the header has no persistent state; it operates on caller-owned buffers. It is intentionally included directly by tests, so function definitions are emitted into each translation unit.

Dependencies and integration points: assumes `TEST_FAIL/TEST_PASS` and `printf()` from including test context, and assembly helpers supplied elsewhere in the ptrace directory.

Risks and test signals: off-by-one or endian mistakes cause explicit index/value diagnostics. Because this is a header with definitions, multiple inclusion in one object would be unsafe.
