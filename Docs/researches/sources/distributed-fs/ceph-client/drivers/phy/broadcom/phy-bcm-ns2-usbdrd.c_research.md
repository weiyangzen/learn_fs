# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-usbdrd.c

Purpose: Implements Northstar2 USB2 dual-role-device PHY support, including host/device mode register programming, extcon state publication, GPIO-based ID/VBUS detection, and PLL lock polling.

Important APIs and types: `struct ns2_phy_driver` owns mapped control windows, GPIOs, IRQs, extcon device, delayed work, and shared `ns2_phy_data`. `ns2_phy_data` stores the PHY and pending state (`EVT_HOST` or `EVT_DEVICE`). PHY ops implement `.init`, `.power_on`, and `.power_off`.

Control flow: probe maps `icfg`, `rst-ctrl`, `crmu-ctrl`, and `usb2-strap`, gets `id` and `vbus` GPIOs, allocates/registers extcon, configures debounce or delayed-work fallback, requests both edge-triggered IRQs, shuts down ports, creates the PHY, registers the provider, and queues initial detection. IRQs schedule `extcon_work()`, which reads GPIOs, updates extcon cable states, sets `new_state`, and calls `connect_change()` to switch mode registers. Power-on uses `new_state` to configure host or device P0CTL, resets, CRMU bits, PLL reset bits, and overcurrent polarity.

State and persistence: Runtime role is persisted in `data->new_state` and extcon state. Hardware role state is in ICFG/CRMU/strap registers. Delayed work is the debounce mechanism.

Dependencies and integration: It depends on GPIO descriptors, extcon, delayed workqueues, generic PHY, MMIO resources, and compatible `brcm,ns2-drd-phy`.

Risks and test signals: Probe uses managed resources but does not explicitly cancel delayed work on remove in this file. GPIO state combinations drive role decisions; disconnected state does not reset `new_state`. Test ID/VBUS transitions, debounce fallback, both IRQ paths, host/device power-on, PLL lock timeout, disconnect behavior, and extcon notifications to USB role consumers.
