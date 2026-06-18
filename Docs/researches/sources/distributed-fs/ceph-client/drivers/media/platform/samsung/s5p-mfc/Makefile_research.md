# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Makefile

## Purpose
This Makefile defines the object composition of the Samsung S5P MFC codec driver. It builds one composite object, `s5p-mfc.o`, when `CONFIG_VIDEO_SAMSUNG_S5P_MFC` is enabled.

## Important APIs, Types, and Constants
The Makefile lists the driver units: core/interrupt handling (`s5p_mfc.o`, `s5p_mfc_intr.o`), decoder and encoder front ends (`s5p_mfc_dec.o`, `s5p_mfc_enc.o`), firmware/control/PM (`s5p_mfc_ctrl.o`, `s5p_mfc_pm.o`), hardware operations (`s5p_mfc_opr.o`, `s5p_mfc_opr_v5.o`, `s5p_mfc_opr_v6.o`), and command dispatch (`s5p_mfc_cmd.o`, `s5p_mfc_cmd_v5.o`, `s5p_mfc_cmd_v6.o`).

## Control Flow and State
There is no runtime state. The build composition matters because `s5p_mfc.c` initializes operation and command tables implemented in other objects. Omitting any listed object would break version-specific hardware dispatch or V4L2 entry points.

## Dependencies and Integration Points
It integrates with the kernel kbuild system through `obj-$(CONFIG_VIDEO_SAMSUNG_S5P_MFC)`. The operation and command files correspond to register families declared in the researched headers, while decoder and encoder files provide V4L2 ioctl and vb2 queue ops used by the core probe/open paths.

## Risks
The driver supports later hardware through v6-style command dispatch and extended operation/register tables, but the Makefile only has v5 and v6 command/operation source names. That is intentional if later hardware is an extension of v6 ops, but it is a review point for new hardware support. Build tests should catch missing object references.

## Test Signals
Test with `CONFIG_VIDEO_SAMSUNG_S5P_MFC=m` and `=y`, and with compile-test enabled. Linker output should include a single composite object exporting the platform driver and resolving decoder, encoder, control, PM, command, and operation symbols.
