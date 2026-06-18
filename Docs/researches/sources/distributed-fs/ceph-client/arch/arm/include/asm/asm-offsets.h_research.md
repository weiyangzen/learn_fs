<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/asm-offsets.h

## Purpose
Thin include wrapper that exposes generated assembler offset definitions to ARM headers and assembly sources.

## Important APIs/types/functions
- Includes `<generated/asm-offsets.h>`.

## Control flow
No executable flow; preprocessing pulls in generated constants.

## State and persistence behavior
No runtime state. Build-generated offset constants persist in the build directory and are consumed by assembly.

## Dependencies and integration points
Depends on the kernel `asm-offsets` generation step. Included by `assembler.h` and other assembly-facing headers.

## Risks and edge cases
If generated offsets are stale or missing, assembly may build against wrong structure layouts or fail to compile.

## Test signals
Clean ARM build should regenerate `generated/asm-offsets.h`; assembly files using task/thread offsets should compile and boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/asm-offsets.h -->
