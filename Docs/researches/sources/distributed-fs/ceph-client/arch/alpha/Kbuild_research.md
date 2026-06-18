<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/Kbuild -->
# sources/distributed-fs/ceph-client/arch/alpha/Kbuild

## Purpose
Alpha architecture Kbuild entry point. It declares the architecture subdirectories participating in the build and a boot directory to include in cleaning.

## Important APIs, Types, And Functions
- `obj-y += kernel/ mm/` always descends into Alpha kernel and memory-management code.
- `obj-$(CONFIG_MATHEMU) += math-emu/` conditionally builds floating-point/math emulation support.
- `subdir- += boot` marks the boot subdirectory for clean recursion without normal object descent from this file.

## Control Flow
When root Kbuild descends into `arch/$(SRCARCH)/`, these assignments add Alpha subdirectories to the recursive build based on configuration. The boot directory is excluded from ordinary object aggregation here but participates in cleanup.

## State And Persistence
No direct file writes. It controls which subdirectory builds generate objects, archives, and clean artifacts under the Alpha architecture tree.

## Dependencies And Integration Points
Consumed by top-level Kbuild via `obj-y += arch/$(SRCARCH)/`. It depends on `CONFIG_MATHEMU` from Alpha Kconfig and on Kbuild files in `kernel/`, `mm/`, `math-emu/`, and `boot/`.

## Risks And Edge Cases
Omitting a required subdirectory prevents its objects from entering vmlinux. Incorrect conditional descent can break configurations that require math emulation. The clean-only boot handling assumes separate architecture Makefile rules build boot artifacts.

## Test Signals
Build Alpha defconfigs with and without `CONFIG_MATHEMU`, inspect recursive descent and linked objects, and verify `make ARCH=alpha clean` removes boot artifacts as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/Kbuild -->
