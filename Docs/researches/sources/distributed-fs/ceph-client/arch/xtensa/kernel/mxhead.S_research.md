<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mxhead.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/mxhead.S

Purpose: provides the secondary reset vector for Xtensa MX/SMP configurations. Important symbol is `_SecondaryResetVector`, with local setup labels `_SetupOCD` and `_SetupMMU`.

Control flow jumps from the secondary reset vector to OCD/window/PS setup, optionally initializes the MMU inside vmlinux, sets boot parameter register `a2` to NULL, loads `_startup`, and jumps there. Persistent state initialized includes window registers, PS interrupt level, MMU mappings, and secondary boot register arguments. Dependencies include cache/MMU initialization macros, MX registers, XCHAL window support, and `_startup` from `head.S`. Integration points are SMP secondary CPU bringup, reset-vector linker sections, and platform/MX boot hardware. Risks are vector placement, inconsistent setup relative to primary `_start`, missing MMU initialization, and literal-range constraints in reset-vector text. Test signals include SMP boot with `CONFIG_SECONDARY_RESET_VECTOR`, secondary CPU online, vector map inspection, and CPU hotplug restart paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mxhead.S -->
