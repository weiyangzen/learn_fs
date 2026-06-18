# sources/distributed-fs/ceph-client/drivers/power/supply/macsmc-power.c

## Purpose
This Apple Silicon platform driver exposes battery and AC adapter telemetry from the Apple SMC. It dynamically builds power-supply property lists based on available SMC keys, supports charge behavior controls, estimates energy from charge using a nominal cell voltage, and reacts to SMC power events including critical battery shutdown triggers.

## Important APIs, Types, and Functions
`struct macsmc_power` stores device/SMC pointers, mutable battery and AC descriptors, registered supplies, identity strings, feature flags for charge limit/inhibit/force-discharge mechanisms, cell data, notifier, critical work, and shutdown guards. `macsmc_battery_get_status()` combines SMC keys for charger presence/capability, AC current, full state, charge limits, and no-charge flags. Charge behavior helpers read/write `CH0I`, `CHTE`, or `CH0C`. `macsmc_battery_get_property()` maps many SMC keys to standard battery properties, including manufacture date parsing and BE-swapped `B0RM`. `macsmc_power_critical_work()` initiates hardware-protection or orderly shutdown on low voltage or SMC empty flags. `macsmc_power_event()` maps predicted SMC event IDs to supply changes or critical work.

## Control Flow
Probe gets the parent `apple_smc`, allocates state, sets up autocancel critical work, detects battery and AC presence from fundamental keys, builds battery properties and feature flags, resets charge inhibitors to auto, reads identity strings/cell count, registers battery if possible, builds AC properties based on available keys, registers AC if possible, and registers a blocking notifier with the SMC event chain. Remove unregisters the notifier.

## State and Persistence
Identity strings, feature flags, cell count, nominal voltage, and shutdown guard booleans are cached. The driver writes persistent SMC charge-behavior keys at probe and when userspace changes `CHARGE_BEHAVIOUR`. It does not cache telemetry; most properties read SMC keys live.

## Dependencies and Integration Points
It depends on the Apple SMC MFD API, SMC key naming macros, blocking notifier chain, power-supply charge-behavior support, reboot/hardware-protection APIs, and Apple Silicon firmware key availability. AC and battery registration are independent so one can succeed if the other fails.

## Risks
Event IDs are described as predicted, so notifications may miss or over-report firmware changes. Probe resets optimized charging/inhibitor keys, which changes firmware policy. Critical shutdown logic depends on SMC voltage/empty flags and must avoid duplicate shutdowns. Energy values are approximated from a fixed nominal cell voltage. Dynamic property arrays have hard limits and rely on accurate key probing.

## Test Signals
Test systems with battery only, AC only, and both supplies; key absence on newer firmware; status decisions for no charger, limited charging, BMS busy, full, and inhibited cases; charge-behavior get/set across old and new keys; critical event handling; manufacture date parsing; and notifier cleanup on remove.
