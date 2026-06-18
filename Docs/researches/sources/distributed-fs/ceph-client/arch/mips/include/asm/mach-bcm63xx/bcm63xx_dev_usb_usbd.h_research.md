# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_usb_usbd.h

**Purpose:** Defines platform data and registration for the BCM63xx USB device controller.

**Important APIs/types/functions:** Exports `struct bcm63xx_usbd_platform_data` with `use_fullspeed` and `port_no`, and `bcm63xx_usbd_register(const struct bcm63xx_usbd_platform_data *pd)`.

**Control flow:** Board setup passes speed limitation and PHY port selection to the USB device registration helper; the USB gadget driver then uses those resources.

**State and persistence behavior:** No local state. Platform data persists with the registered USB device and controls hardware mode/port selection.

**Dependencies and integration points:** Depends on CPU register/IRQ tables for USBD and DMA resources, USB gadget core, PHY/port wiring, and board hardware limits.

**Risks:** Wrong `port_no` can enable the wrong PHY. Ignoring `use_fullspeed` may advertise unsupported high-speed mode. USBD resources are absent on many SoCs and must be guarded.

**Test signals:** Probe gadget mode on supported boards, test full-speed-only boards, enumerate on host, transfer data over RX/TX DMA endpoints, and verify absence on host-only SoCs.
