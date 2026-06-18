<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drm.h

Purpose: Declares TVE200 register offsets/bitfields, the driver private structure, and cross-file prototypes for the TVE200 DRM driver.

Important APIs/types/functions: Defines frame base, interrupt, control, reset, burst, retry, format, resolution, endian, YCbCr ordering, vblank trigger, BGR, and enable bits. `struct tve200_drm_dev_private` stores `drm`, connector/panel/bridge, simple display pipe, mapped regs, peripheral clock, and TVE pixel clock. Prototypes include `tve200_display_init()` and `tve200_irq()`.

Control flow: The header drives control-flow decisions in display and probe files by encoding how register fields map to DRM modes, bus flags, and formats.

State and persistence: It declares runtime state shape but stores no state itself. The private struct is allocated per platform device.

Dependencies and integration points: Includes `drm_simple_kms_helper` and Linux IRQ return types. It ties the display implementation to platform lifecycle code.

Risks and test signals: Bitfield mistakes directly affect hardware programming. Tests are mostly hardware or register-trace based: verify control values for RGB/YUV formats, interrupt mask/clear bits, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_drm.h -->
