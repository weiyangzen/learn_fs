# sources/distributed-fs/ceph-client/arch/powerpc/kernel/suspend.c

## Purpose
Defines PowerPC hibernation/suspend memory exclusion for the kernel `__nosave` section.

## Important APIs, Types, and Functions
- `pfn_is_nosave(pfn)` computes physical PFN bounds for `__nosave_begin` to aligned `__nosave_end`.

## Control Flow and State
The function is a pure range test used by suspend image code when deciding which PFNs not to save.

## State and Persistence Behavior
No mutable state. It reflects linker section addresses into PFN ranges.

## Dependencies and Integration Points
Depends on `asm/sections.h`, `__pa()`, `PAGE_SHIFT`, and suspend core `pfn_is_nosave` hooks.

## Risks
Incorrect section boundaries or alignment would cause hibernation to save volatile memory or omit required memory.

## Test Signals
Validate hibernation image creation, inspect nosave PFN bounds, and test linker changes that move `__nosave` symbols.
