# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/mpfs.c

Purpose: implements the Microchip PolarFire SoC MUSB glue layer. It provides MPFS-specific FIFO configuration, VBUS/session control, OTG polling, interrupt acknowledgement, child `musb-hdrc` registration, clock handling, and optional Inventra DMA support.

Important APIs, types, and functions: `struct mpfs_glue` tracks parent device, child MUSB device, registered generic PHY, and clock. `mpfs_musb_mode_cfg` and `mpfs_musb_hdrc_config` describe dynamic FIFO layout, endpoint count, and RAM bits. Platform hooks are `mpfs_musb_init`, `mpfs_musb_exit`, `mpfs_musb_set_vbus`, optional `mpfs_musb_try_idle`, and optional Inventra DMA init/exit via `mpfs_ops`. `mpfs_musb_interrupt` reads/acknowledges Mentor USB/TX/RX interrupt registers and dispatches to `musb_interrupt`.

Control flow: probe allocates a `musb-hdrc` child, obtains/enables the parent clock, sets a 39-bit coherent DMA mask, creates platform data with MPFS config and `dr_mode`, registers a generic USB PHY, adds parent resources/data to the child, and registers it. Core init obtains the USB2 transceiver, sets up the OTG polling timer, forces dynamic FIFO mode, installs the ISR, and turns on VBUS through `musb_platform_set_vbus`. VBUS on sets active/default-A/A_WAIT_VRISE, asserts SESSION, and marks host mode; VBUS off clears active/default-A, moves to B_IDLE, clears SESSION, and marks device mode. The OTG timer polls DEVCTL to compensate for missing transceiver status-change IRQs.

State and persistence: no persistent storage. Runtime state includes clock enablement, generic PHY platform device, MUSB timer, DEVCTL/session bits, OTG state, endpoint FIFO configuration, and child platform-device state.

Dependencies and integration points: depends on OF, clocks, platform-device resources, DMA mask setup, `usb_phy_generic`, MUSB core, and optional Inventra DMA. It binds `microchip,mpfs-musb`.

Risks: `mpfs_remove` calls `usb_phy_generic_unregister(pdev)` instead of unregistering `glue->phy`, which looks like a type/ownership bug and should be verified. Error paths may call `usb_phy_generic_unregister(glue->phy)` even when `glue->phy` was not assigned due to earlier failures. The controller relies on polling for ID changes and forces VBUS on in init, so role behavior is sensitive to `dr_mode` and external VBUS driver property. Interrupt code manually acknowledges Mentor interrupt registers before calling the core; ordering changes can lose events. The 39-bit DMA mask must match actual interconnect/DMA support.

Test signals: compile with PolarFire Kconfig and optional Inventra DMA, probe `microchip,mpfs-musb` with host/peripheral/otg `dr_mode`, verify clock failure cleanup, generic PHY registration/unregistration, dynamic FIFO setup, VBUS on/off transitions, OTG polling from B_IDLE/A_WAIT states, interrupt acknowledgement and dispatch, DMA above 32-bit addresses if supported, and remove/unbind with leak/type-checking tools.
