<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kbuild -->
# sources/distributed-fs/ceph-client/arch/xtensa/Kbuild

## Purpose
Top-level Kbuild include list for Xtensa architecture directories.

## Important APIs, Types, And Functions
It defines `obj-y += kernel/ mm/ platforms/`.

## Control Flow
During Kbuild evaluation, Xtensa always descends into architecture kernel, memory-management, and platform support directories for the selected configuration.

## State And Persistence
No runtime state. Build state is the object-directory traversal graph.

## Dependencies And Integration Points
Integrates Xtensa architecture code with the global kernel build system. The selected subdirectories depend on Kconfig and Makefiles beneath them.

## Risks And Edge Cases
Omitting one of these directories would produce missing core symbols. Adding platform or MM code elsewhere requires this traversal to remain complete.

## Test Signals
Build any Xtensa defconfig and verify Kbuild descends into `arch/xtensa/kernel`, `arch/xtensa/mm`, and `arch/xtensa/platforms`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kbuild -->
