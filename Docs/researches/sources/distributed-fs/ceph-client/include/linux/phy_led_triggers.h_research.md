# sources/distributed-fs/ceph-client/include/linux/phy_led_triggers.h

## Purpose
PHY link-speed LED trigger integration for PHYLIB.

## Important APIs, Types, and Functions
When `CONFIG_LED_TRIGGER_PHY` is enabled, defines name-size constants, `struct phy_led_trigger` embedding `struct led_trigger`, and declares `phy_led_triggers_register()`, `phy_led_triggers_unregister()`, and `phy_led_trigger_change_speed()`. Disabled builds provide success/no-op stubs.

## Control Flow
PHY probe/register paths create LED triggers, link speed changes update the active trigger, and teardown unregisters triggers.

## State and Persistence
Triggers persist per PHY while registered. Names encode MDIO bus/address and speed suffix; `struct phy_device` stores trigger pointers when LED support is enabled.

## Dependencies and Integration Points
Depends on LED trigger subsystem and `linux/phy.h`. Integrates PHY state changes with LED class trigger selection.

## Risks
Name-size calculations must match MDIO identifiers. Trigger updates must track speed/link transitions without stale LED state. Disabled stubs can mask absent visual feedback.

## Test Signals
LED trigger registration tests, link speed transition tests, sysfs LED trigger visibility, and build coverage with LED trigger support enabled/disabled.
