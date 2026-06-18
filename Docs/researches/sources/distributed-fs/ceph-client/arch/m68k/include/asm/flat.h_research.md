<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/flat.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/flat.h

## Purpose
This header supplies m68knommu platform initialization for uClinux flat-format executables.

## Important APIs, Types, And Functions
- Includes `<asm-generic/flat.h>` for generic flat loader definitions.
- `FLAT_PLAT_INIT(regs)` sets register `d5` to `current->mm->start_data` when an mm is present.

## Control Flow
During flat binary exec setup, the loader invokes `FLAT_PLAT_INIT()` to seed architecture-specific register state before entering userspace.

## State And Persistence Behavior
The macro mutates the new task's saved register frame. It reads `current->mm->start_data` and persists the value in `%d5` for the executed program.

## Dependencies And Integration Points
It depends on generic flat binary support and `current`/mm state. It integrates with m68knommu exec and FDPIC/flat userspace startup expectations.

## Risks And Edge Cases
The macro silently does nothing without `current->mm`. Userspace ABI may depend on `d5` containing the data segment base, so changing it can break flat binaries.

## Test Signals
Execute flat binaries on m68knommu, verify startup register expectations, and test processes with valid mm setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/flat.h -->
