# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tpd12s015.c

Purpose: models the TI TPD12S015 HDMI ESD protection and level-shifter chip as a DRM bridge. It controls cable-power/HPD and level-shifter output-enable GPIOs, reports HDMI-A hotplug status from an HPD GPIO, and forwards bridge attachment to the downstream bridge.

Important APIs/types/functions: `struct tpd12s015_device` contains the embedded bridge, `ct_cp_hpd_gpio`, `ls_oe_gpio`, required `hpd_gpio`, and optional IRQ number. `tpd12s015_probe()` allocates the bridge, sets type `DRM_MODE_CONNECTOR_HDMIA` and detect op, finds the next bridge from graph port 1, obtains three GPIOs by index, optionally requests a threaded HPD IRQ on rising/falling edges, sets `DRM_BRIDGE_OP_HPD` when IRQ registration succeeds, and calls `drm_bridge_add()`. `tpd12s015_attach()` requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, attaches the next bridge, asserts level-shifter output enable, and waits 300 to 1000 us for the DC-DC converter. `tpd12s015_detach()` disables the level shifter. `tpd12s015_hpd_enable()`/disable toggle `ct_cp_hpd_gpio`, and `tpd12s015_hpd_isr()` calls `drm_bridge_hpd_notify()`.

Control flow: the bridge is intended to sit inside a bridge chain where a bridge connector owns the connector. Detection directly reads HPD GPIO. HPD notification is optional and only active when the HPD GPIO can be converted to an IRQ.

State and persistence: no separate software state is stored beyond GPIO descriptors and IRQ number. Hardware state is the GPIO levels. Attach leaves `ls_oe_gpio` asserted until detach, while HPD enable/disable toggles the HPD/cable-power control line.

Dependencies and integration points: depends on platform driver infrastructure, OF graph, GPIO consumer API, IRQ handling, and DRM bridge HPD/detect hooks. It integrates with downstream HDMI bridge/encoder chains and bridge connector polling/HPD logic.

Risks: attach returns `-EINVAL` if a connector-creating caller is used. GPIOs are positional and unnamed, so DT ordering is critical. There is no explicit remove-time detach of GPIO state beyond `drm_bridge_remove()`, so normal DRM detach sequencing must run. HPD IRQ absence leaves only polled detect behavior.

Test signals: graph probe/defer, three-GPIO DT ordering and polarity, attach with no-connector flag, HPD GPIO read for connected/disconnected states, IRQ-triggered HPD notify on both edges, and output-enable timing during bridge attach/detach.
