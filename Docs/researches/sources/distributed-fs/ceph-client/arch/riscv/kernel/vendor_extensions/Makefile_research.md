<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/Makefile

Purpose: Selects vendor-extension implementation and hwprobe objects for RISC-V builds.

Important APIs/types/functions: Uses `obj-$(CONFIG_RISCV_ISA_VENDOR_EXT_*)` rules for Andes, MIPS, SiFive, and T-Head objects.

Control flow: Kbuild includes vendor extension data and hwprobe files according to enabled configs.

State and persistence: Build-time only.

Dependencies and integration points: Feeds `vendor_extensions.c` aggregate list and `sys_hwprobe.c` vendor key dispatch.

Risks: Missing object selection can make configured extensions undiscoverable.

Test signals: Build each vendor config and query corresponding hwprobe vendor keys.

Source read size: 9 lines, 433 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/Makefile -->
