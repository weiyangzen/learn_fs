# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_device.c

Purpose: provides chip descriptors and KMS function tables for LS7A1000 and LS7A2000 display controllers.

Important APIs/types/functions: `ls7a1000_kms_funcs`, `ls7a2000_kms_funcs`, `ls7a1000_gfx`, `ls7a2000_gfx`, and `lsdc_device_probe`.

Control flow: PCI probe passes a chip id; `lsdc_device_probe` indexes the descriptor table and returns the `lsdc_desc`. Core modeset init then calls descriptor-provided hooks to create I2C, outputs, planes, and CRTCs.

State and persistence: descriptors are static constants containing max clock/size, cursor capabilities, pitch alignment, vblank counter capability, config register base, PLL offsets, chip id, and model string.

Dependencies and integration points: connects generic core code to chip-specific output, cursor, CRTC, and IRQ implementations. Uses register offsets from `lsdc_regs.h`.

Risks and test signals: descriptor values directly affect mode validation and hardware setup. Test both PCI IDs, max-mode limits, cursor sizes, pitch alignment, vblank counter path, and debugfs model reporting.
