# sources/distributed-fs/ceph-client/drivers/extcon/extcon-sm5502.c

## Purpose
Silicon Mitus SM5502/SM5504/SM5703 MUIC extcon provider for USB switch, OTG, USB device, and DCP charger detection. It supports chip variants through per-type IRQ chips, initialization tables, and IRQ parsers, then reports USB, USB host, SDP, and DCP extcon states.

## Important APIs, Types, and Functions
`struct sm5502_muic_info` stores device, extcon, I2C/regmap, matched `sm5502_type`, regmap IRQ data, attach/detach flags, work, mutex, and delayed cold-plug work. `struct sm5502_type` selects IRQ descriptors, regmap IRQ chip, initialization data, OTG DEV_TYPE1 mask, and parse callback. `sm5502_muic_set_path()` writes manual DM/DP and VBUSIN switch fields. `sm5502_muic_get_cable_type()` reads ADC and DEV_TYPE1 to disambiguate OTG, USB, and TA. `sm5502_muic_cable_handler()` maps supported cable classes to switch settings and extcon states. Probe initializes regmap IRQ, requests virtual IRQs, registers extcon, schedules detection, and writes initialization registers.

## Control Flow
OF match data selects SM5502, SM5504, or SM5703 behavior. Probe sets up regmap and devm regmap IRQ chip, then maps each logical IRQ to a virtual IRQ and requests a threaded handler. The handler maps virtual IRQ to logical type, calls the variant parse function to set attach/detach flags, and schedules work. Work serializes under mutex and handles attach and detach by calling `sm5502_muic_cable_handler()`. The delayed worker runs after 17 seconds and handles initial attach state.

## State and Persistence
Variant initialization writes reset, control, and interrupt mask registers. Cable detach relies on a function-static `prev_cable_type` in `sm5502_muic_cable_handler()`, shared across all devices. Per-device state includes attach/detach booleans and the matched type table. No persistent storage exists outside hardware registers and extcon state.

## Dependencies and Integration Points
Uses extcon provider, I2C, regmap, devm regmap IRQ, threaded IRQs, OF match data, and PM wake IRQ toggling. Register constants and masks come from `extcon-sm5502.h`.

## Risks
The function-static previous cable type creates multi-instance risk. The initialization logic writes either `~val` or `val` depending on `invert`, and because writes are full-register writes, mask intent must be validated against hardware reset values. Unsupported ADC accessory classes are silently ignored after debug logs. Probe uses OF match data; pure I2C ID match data is present but the probe still requires an OF node and `device_get_match_data()`. Delayed work is not explicitly canceled in remove because there is no remove callback.

## Test Signals
Exercise SM5502 and SM5504 IRQ maps, USB SDP, DCP, ground/open OTG, detach after each supported attach, boot cold-plug, register initialization values, wake IRQ suspend/resume, and behavior when ADC/DEV_TYPE1 reads fail or when unsupported accessories are attached.
