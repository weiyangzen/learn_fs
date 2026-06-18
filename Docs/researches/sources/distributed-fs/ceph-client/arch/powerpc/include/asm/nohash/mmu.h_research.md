<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu.h

## Purpose
This is the nohash MMU selector header. It includes the processor-family-specific MMU contract for 44x, e500/Book3E, or 8xx builds.

## Important APIs, Types, And Functions
The file has no direct APIs beyond conditional includes: `asm/nohash/32/mmu-44x.h` for `CONFIG_44x`, `asm/nohash/mmu-e500.h` for `CONFIG_PPC_E500`, and `asm/nohash/32/mmu-8xx.h` for `CONFIG_PPC_8xx`.

## Control Flow
There is no runtime control flow. Compile-time Kconfig selection determines which register definitions, context type, and page-size helpers are visible to the rest of the architecture.

## State And Persistence Behavior
It owns no state. The included header defines the MMU state model for the selected platform.

## Dependencies And Integration Points
It is included by architecture page/MMU code that wants a uniform nohash include path without knowing the selected embedded MMU family.

## Risks And Edge Cases
Misconfigured Kconfig combinations can leave no MMU family included or expose incompatible definitions. Adding a new nohash family requires updating this selector and downstream page-table selectors consistently.

## Test Signals
Cross-build 44x, e500, and 8xx configs and verify `asm/mmu.h` consumers see exactly one compatible nohash backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu.h -->
