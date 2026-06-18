<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.h

Purpose: Declares the GE FPGA PIC setup and IRQ retrieval API for board code.

Important APIs/types/functions: Declares `gef_pic_get_irq()` and `gef_pic_init(struct device_node *)`.

Control flow: No runtime flow; this is an include guard and prototypes only.

State and persistence: No state in the header.

Dependencies and integration points: Consumed by GE platform code and implemented by `ge_pic.c`.

Risks: Minimal; callers must pass a valid device node to `gef_pic_init()` and install `gef_pic_get_irq()` only after initialization.

Test signals: Compile coverage for GE FPGA platforms and successful linkage against `ge_pic.o`.

Source read size: 9 lines, 190 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.h -->
