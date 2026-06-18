# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/Makefile

Purpose: defines the common HabanaLabs object list and imports common MMU and PCI makefile fragments.

Important entries: includes `common/mmu/Makefile` and `common/pci/Makefile`, appends their object lists, and defines `HL_COMMON_FILES` with core common sources such as driver, device, context, ASID, ioctl, command buffer, queues, IRQ, sysfs, hwmon, memory, command submission, firmware interface, security, state dump, memory manager, and decoder. Adds `common/hldio.o` when `CONFIG_HL_HLDIO` is set.

Control flow: top-level HabanaLabs Makefile includes this fragment to populate `habanalabs-y`.

State and persistence: build metadata only.

Dependencies: common subfragments and all listed source files.

Risks: the `ifdef CONFIG_HL_HLDIO` conditional depends on Kbuild variable visibility; wrong conditional style can omit or include optional code unexpectedly.

Test signals: HLDIO enabled/disabled builds, common MMU/PCI fragment integration, and link checks for common symbols used by ASIC-specific files.
