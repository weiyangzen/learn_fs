<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/archrandom.h

## Purpose
ARM32 architecture random header that disables SMCCC TRNG probing and falls back to generic archrandom behavior.

## Important APIs/types/functions
- `smccc_probe_trng()` returns false.
- Includes `asm-generic/archrandom.h`.

## Control flow
No dynamic flow beyond callers seeing `smccc_probe_trng()` as false.

## State and persistence behavior
No state. It affects whether SMCCC TRNG is treated as available.

## Dependencies and integration points
Integrates with generic random/archrandom infrastructure and SMCCC feature probing.

## Risks and edge cases
ARM32 platforms with firmware TRNG support through SMCCC will not expose it via this hook. Entropy must come from other random sources.

## Test signals
Build random subsystem on ARM32; verify no SMCCC TRNG provider is registered from this path and generic fallbacks compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/archrandom.h -->
