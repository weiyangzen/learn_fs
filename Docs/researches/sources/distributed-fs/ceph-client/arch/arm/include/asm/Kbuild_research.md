<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/Kbuild

## Purpose
Header export/generation manifest for ARM architecture include files.

## Important APIs/types/functions
- Generic header mappings: `early_ioremap.h`, `extable.h`, `flat.h`, and `parport.h`.
- Generated headers: `mach-types.h` and `unistd-nr.h`.

## Control flow
Kbuild uses `generic-y` to source generic versions of headers not supplied by ARM and `generated-y` to track generated architecture headers.

## State and persistence behavior
No runtime state. It controls generated/exported include tree contents during builds.

## Dependencies and integration points
Integrates with Kbuild header generation, UAPI/syscall generation, and asm-generic fallbacks.

## Risks and edge cases
Incorrect generic mapping can hide an architecture-specific header or break includes. Missing generated header declarations can cause stale or absent build products.

## Test signals
Run full ARM builds and header install checks; verify generated `mach-types.h` and `unistd-nr.h` exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/Kbuild -->
