# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-usb.h

Purpose: This OMAP1 header centralizes USB OTG, UDC, and transceiver register constants shared by legacy platform, gadget, PHY, and OHCI drivers.

Important APIs/types/functions: It defines OMAP1/OMAP2 OTG and UDC base addresses, OTG register offsets, and bitfield macros for transceiver mode, idle, reset, SRP/HNP, VBUS/session status, pad enable, host/device enable, pullup/pulldown, and USB line controls.

Control flow: USB platform code and drivers use these constants to reset/configure OTG, select transceiver modes, manage host/device roles, and read session/VBUS state.

State and persistence: OTG/UDC hardware registers hold role, pad, VBUS, and transceiver control state until changed or reset.

Dependencies and integration: Integrates with OMAP1 USB gadget, OHCI host, PHY/transceiver, and board support code.

Risks and test signals: Shared constants make cross-driver coordination fragile; bad role bits can disable host/device operation. Test host and gadget modes, OTG reset, VBUS/session detection, suspend/resume, and board-specific transceiver wiring.
