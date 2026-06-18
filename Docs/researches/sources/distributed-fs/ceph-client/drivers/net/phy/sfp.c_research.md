# sources/distributed-fs/ceph-client/drivers/net/phy/sfp.c

## Purpose
`sfp.c` is the platform driver for SFF/SFP cages. It manages GPIO and soft EEPROM control/status signals, reads module EEPROM over I2C or SMBus, applies vendor quirks, negotiates module power and rate-select behavior, creates MDIO-over-I2C buses for copper modules, reports ethtool EEPROM and hwmon data, and runs the hotplug/device/link state machines that connect the socket to `sfp-bus.c`.

## Important APIs, Types, And Functions
`struct sfp` is the central state container: device, I2C adapter, optional MDIO bus, SFP bus, module PHY, GPIOs/IRQs, state masks, delayed works, module/device/main state-machine fields, EEPROM ID, power/rate-select fields, quirk pointer, hwmon data, and debugfs entry. `struct sff_data` describes SFF vs SFP GPIO requirements and module validation. Key functions include I2C/SMBus accessors, `sfp_i2c_mdiobus_create()`, soft-state helpers, hwmon readers, quirk fixups, `sfp_sm_mod_probe()`, `sfp_sm_module()`, `sfp_sm_main()`, `sfp_check_state()`, `sfp_probe()`, `sfp_remove()`, and the `sfp_module_ops` socket operations.

## Control Flow
Probe allocates `struct sfp`, gets the referenced I2C adapter, obtains optional GPIOs, reads initial state, asserts TX disable, emits an insert event if a module is already present, requests GPIO IRQs or enables polling, registers the socket with `sfp_register_socket()`, and creates debugfs. GPIO IRQs or poll work call `sfp_check_state()`, which snapshots hardware/soft state, computes changed presence/LOS/TX_FAULT bits, and dispatches events under RTNL and `sm_mutex`.

The module state machine waits for serial EEPROM readiness after insertion, retries slow EEPROM reads, validates checksums, handles broken byte-only EEPROMs, applies Cotsworks EEPROM repair, finds quirks, determines power and rate-select policy, reports insertion upstream, switches high-power modules if allowed, then reaches present state. The main state machine waits for upstream device-up, starts soft polling when A2 is usable, enables TX, handles TX fault recovery, creates MDIO-over-I2C for copper modules, probes C22/C45/RollBall PHYs, starts the module upstream, and reports link up/down based on LOS semantics. Removal or device-down unwinds PHY attachment, MDIO bus, module start, TX enable, and soft polling.

## State And Persistence
Hardware signal state is protected by `st_mutex`; module/device/link state is protected by `sm_mutex`; state-machine entry points usually run under RTNL. Persistent state includes EEPROM identity, quirk-selected masks, high-power status, rate-select thresholds, delayed work timers, optional registered `phy_device`, and optional hwmon registration. The driver writes module EEPROM/control bytes for soft TX disable, rate select, high-power selection, and one Cotsworks EEPROM correction path.

## Dependencies And Integration Points
The driver depends on platform/OF matching (`sff,sff` and `sff,sfp`), GPIO descriptors, I2C/SMBus, mdio-i2c, phylib, RTNL, workqueues, hwmon, debugfs, ethtool module EEPROM APIs, and `sfp-bus.c` socket operations. It is the downstream socket half used by phylink-capable network devices.

## Risks And Edge Cases
The state machines are timing-sensitive and must tolerate slow or broken modules. Byte-only EEPROM fallback disables coherent 16-bit hwmon reads. Some quirks deliberately ignore LOS/TX_FAULT pins or change MDIO protocol, so regression coverage needs real hardware variants. Cotsworks EEPROM rewriting is invasive and must not trigger on unrelated modules. Missing `tx-disable` can leave optical modules emitting when unplugged. Error handling must avoid leaving MDIO buses or module PHYs registered after removal or upstream detach.

## Test Signals
Use hotplug insertion/removal, boot-with-module-present, GPIO IRQ and polling-only cages, SMBus-only adapters, valid and invalid EEPROM checksums, high-power modules above and below host limits, RollBall and C45 copper modules, LOS polarity variants, TX fault recovery exhaustion, ethtool EEPROM page reads, hwmon registration and alarms, debugfs state output, upstream open/close sequencing, and remove/shutdown races with delayed work.
