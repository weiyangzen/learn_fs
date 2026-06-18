## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm-cci.h

### Purpose
Provides the ARM64 platform hook for secure CCI access.

### Important APIs, Types, And Functions
Defines `platform_has_secure_cci_access()` as an inline function that always returns `false`.

### Control Flow
No complex flow. Callers query the helper and receive a fixed negative answer on ARM64.

### State, Persistence, And Dependencies
No state or persistence. It assumes no ARM64 platform exposes secure CCI access through this hook.

### Integration Points
Used by ARM CCI/cache-coherent interconnect code to decide whether secure-only CCI registers can be accessed.

### Risks
If a future platform requires secure CCI access from the kernel, this hardcoded false value would need revisiting. The current conservative answer avoids illegal secure register access.

### Test Signals
Build CCI-related ARM64 configs and boot platforms using CCI drivers, confirming they do not attempt secure-only accesses.
