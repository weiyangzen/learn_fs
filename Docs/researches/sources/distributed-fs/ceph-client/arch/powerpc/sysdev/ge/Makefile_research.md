<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/Makefile

Purpose: Selects the GE FPGA interrupt controller object for builds.

Important APIs/types/functions: Adds `ge_pic.o` when `CONFIG_GE_FPGA` is enabled.

Control flow: No runtime behavior; Kbuild conditionally includes the GE PIC driver.

State and persistence: No state.

Dependencies and integration points: Integrates with PowerPC board/platform Kconfig that selects `CONFIG_GE_FPGA` and with `ge_pic.c`.

Risks: Incorrect config selection omits the cascaded board PIC driver and breaks non-PCI on-board interrupt delivery on GE FPGA platforms.

Test signals: Build matrix with `CONFIG_GE_FPGA=y` and disabled, plus board boot checking that `ge_pic.o` is linked only when expected.

Source read size: 2 lines, 75 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/Makefile -->
