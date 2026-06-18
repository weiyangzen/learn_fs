# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_irq.c

Purpose: handles Loongson display-controller vblank interrupts for LS7A1000 and LS7A2000 variants.

Important APIs/types/functions: `ls7a2000_dc_irq_handler` and `ls7a1000_dc_irq_handler`.

Control flow: both handlers read `LSDC_INT_REG`, return `IRQ_NONE` if no status bits are set, save status to `ldev->irq_status`, clear interrupt status using chip-specific semantics, and call `drm_handle_vblank` for CRTC0/CRTC1 VSYNC bits. LS7A2000 clears by writing ones; LS7A1000 clears by writing zeroes for VSYNC bits.

State and persistence: `ldev->irq_status` records the last interrupt register snapshot. Hardware interrupt enable/status bits persist in `LSDC_INT_REG`.

Dependencies and integration points: registered from PCI probe when `loongson_vblank` is enabled. CRTC vblank enable/disable toggles corresponding enable bits.

Risks and test signals: wrong clear semantics can storm or lose interrupts. Warnings on shared IRQ with no status may be noisy. Test vblank counters/events on both chips, shared IRQ behavior, and page-flip completion.
