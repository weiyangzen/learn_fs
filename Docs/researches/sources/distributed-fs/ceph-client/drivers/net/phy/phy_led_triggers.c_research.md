<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_led_triggers.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_led_triggers.c

Purpose: Provides legacy PHY LED trigger support that exposes one link trigger and one trigger per supported speed, then updates those triggers when link speed changes.

Important APIs and functions: `phy_led_trigger_change_speed()` is called by link-up/link-down paths to set LED trigger state. `phy_led_triggers_register()` allocates and registers the per-PHY trigger set. `phy_led_triggers_unregister()` unregisters and frees those triggers. Static helpers map speeds to triggers, turn all triggers off when no link exists, format trigger names as `bus:addr:suffix`, and register/unregister individual `led_trigger` objects.

Control flow: Registration asks `phy_supported_speeds()` for distinct speeds from `phydev->supported`, creates the `link` trigger, allocates speed triggers, registers each speed trigger using the human-readable speed string, initializes `last_triggered`, and calls `phy_led_trigger_change_speed()` to reflect current link state. On speed changes, no-link clears the previous speed and link triggers; link-up finds the matching speed trigger, enables the link trigger if this is the first active speed, disables the previous speed trigger when speed changes, and enables the new speed trigger.

State and persistence: Mutates `phydev->phy_num_led_triggers`, `phy_led_triggers`, `led_link_trigger`, and `last_triggered`. Trigger registrations persist in the LED subsystem until unregistered. No durable state is stored.

Dependencies and integration points: Depends on `linux/leds.h`, `linux/phy.h`, `linux/phy_led_triggers.h`, netdevice logging, and `phy_supported_speeds()` from internal phylib. It is called from PHY probe/remove and from `phy_link_up()`/`phy_link_down()` in the state machine.

Risks: Registration unwind must unregister only successfully created triggers and free both link and speed arrays. If current `phy->speed` is not represented in the registered speed list, the code logs an alert and turns triggers off. `phy->attached_dev` is used for alert logging, so calls before attachment would need care. Trigger names depend on MDIO bus ID/address and speed string stability.

Test signals: Probe/remove with zero, one, and many supported speeds; allocation or registration failure at each stage; link down clearing LEDs; speed transitions between supported modes; unsupported speed alert path; repeated register/unregister cycles during driver reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_led_triggers.c -->
