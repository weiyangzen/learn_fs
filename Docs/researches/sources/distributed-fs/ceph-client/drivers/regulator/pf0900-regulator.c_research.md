# sources/distributed-fs/ceph-client/drivers/regulator/pf0900-regulator.c

Purpose: implements the NXP PF0900 PMIC regulator driver over I2C. It exposes five buck switchers, three LDOs, and VAON through the regulator framework, with optional I2C CRC support and IRQ-driven regulator fault notifications.

Important APIs/types/functions: `struct pf0900` stores the device, custom regmap, IRQ, I2C address, CRC flag, and `rdevs[]`. `struct pf0900_regulator_desc` extends `regulator_desc` with suspend enable and standby voltage metadata. `pf0900_regmap_read()` and `pf0900_regmap_write()` implement the custom `regmap_bus`, using SMBus byte transfers normally and SMBus word transfers with SAE-J1850 CRC when `nxp,i2c-crc-enable` is set. Regulator operations are split into VAON, DVS buck, and LDO op tables. `pf0900_irq_handler()` maps status registers to regulator notifier events.

Control flow: probe requires an IRQ, allocates state, reads match data, enables optional CRC, initializes regmap, validates device family/id, registers all regulators, requests the threaded IRQ, clears the default power-up interrupt, masks it, and unmasks switch/LDO current-limit, under-voltage, and over-voltage events. IRQ handling reads each fault register, clears asserted bits, then calls `regulator_notifier_call_chain()` for affected switch or LDO/VAON regulators.

State and persistence: runtime state is devm-managed. The regmap uses `REGCACHE_MAPLE` while all chip registers are treated volatile. Suspend voltage caches avoid duplicate standby writes but are memory-only. Hardware register settings persist only as PMIC state.

Dependencies and integration: depends on I2C/SMBus, regmap, OF regulator parsing, GPIO consumer headers, and regulator core helpers. Device tree compatible is `nxp,pf0900`; regulator children are under `regulators`.

Risks and test signals: CRC mode must match hardware framing exactly. The device-id check only rejects some mismatches, so board DT correctness matters. IRQ paths assume all `rdevs[]` entries were registered before events. Test by probing with and without CRC, validating regulator voltage tables, suspend voltage writes, IRQ fault clearing/notifier events, and failure paths for bad ID, missing IRQ, and SMBus errors.
