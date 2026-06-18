<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm-cci.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arm-cci.h

## Purpose
ARM32 helper for deciding whether the platform has secure access to ARM CCI registers.

## Important APIs/types/functions
- `platform_has_secure_cci_access()` returns `mcpm_is_available()` when `CONFIG_MCPM` is enabled, otherwise false.

## Control flow
Compile-time conditional selects MCPM-backed detection or a false stub.

## State and persistence behavior
No state. Result reflects MCPM platform registration state when compiled with MCPM.

## Dependencies and integration points
Depends on `asm/mcpm.h` under `CONFIG_MCPM`. Used by ARM CCI/cache-coherency code that needs to know whether secure-only CCI registers can be touched.

## Risks and edge cases
MCPM availability is a proxy, not direct hardware detection. Platforms with secure CCI access but no MCPM will return false; platforms with MCPM but restricted secure access may need platform-specific care.

## Test signals
Build with and without `CONFIG_MCPM`; boot CCI/MCPM platforms and verify CCI secure register paths behave correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm-cci.h -->
