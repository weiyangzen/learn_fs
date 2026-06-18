# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vortex.c

## Purpose
Registers Vortex86 CPU vendor/model metadata without applying special initialization.

## Important APIs, Types, And Functions
`vortex_cpu_dev` declares vendor `Vortex`, CPUID identifier `Vortex86 SoC`, family/model names for Vortex86DX, MX, and EX, and vendor enum `X86_VENDOR_VORTEX`.

## Control Flow
CPU identification matches the vendor string and uses legacy model tables. The family 6 model 0 name is only a fallback for Vortex86EX; EX2 can provide a product-name CPUID string elsewhere.

## State, Persistence, And Dependencies
Only static CPU vendor registration state is introduced. It depends on generic CPU detection and legacy model name formatting.

## Integration Points
Feeds vendor/model display and `cpuinfo_x86` vendor selection for Vortex86 systems.

## Risks
No quirks are applied. Any future Vortex CPU requiring feature masking, timer handling, or cache setup must be added elsewhere.

## Test Signals
Matching systems should identify as Vortex and print the expected model name without additional init side effects.
