<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sh/Kbuild

Purpose: This Kbuild file selects the core SuperH architecture subdirectories and optional components to build.

Important APIs/types/functions: It adds `kernel/`, `mm/`, and `boards/` to `obj-y`, adds `math-emu/` when `CONFIG_SH_FPU_EMU` is enabled, adds `cchips/hd6446x/` for HD6446x companion chips, and marks `boot` as a clean-only subdirectory.

Control flow: Kbuild includes the listed directories based on configuration symbols during the architecture build. Cleaning descends into `boot` even though normal object traversal is handled elsewhere.

State and persistence: It controls build artifact selection only; no runtime state exists.

Dependencies and integration points: It depends on SuperH Kconfig symbols and Kbuild directory conventions. It integrates the top-level SuperH build with memory management, board support, kernel code, FPU emulation, and companion-chip support.

Risks and test signals: Missing a directory excludes needed objects for a configuration; adding the wrong optional directory can break unrelated builds. Tests are SuperH defconfig/allmodconfig builds with and without FPU emulation and HD6446x support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kbuild -->
