# sources/distributed-fs/ceph-client/drivers/regulator/pf1550-regulator.c

Purpose: implements the regulator child driver for the NXP/Freescale PF1550 PMIC behind the PF1550 MFD core. It registers three switchers, VREFDDR, and three LDOs and forwards PMIC IRQs to regulator notifications.

Important APIs/types/functions: `struct pf1550_desc` wraps each `regulator_desc` with standby voltage and standby enable register data. `struct pf1550_regulator_info` keeps the parent MFD data, copied descriptors, and registered `rdevs[]`. `pf1550_set_ramp_delay()` programs buck ramp bits. `pf1550_set_suspend_enable()`, `pf1550_set_suspend_disable()`, and the two suspend-voltage helpers implement suspend behavior. Descriptor macros build the regulator table.

Control flow: platform probe obtains parent `struct pf1550_ddata`, gets the parent regmap, copies static descriptors, adjusts SW1/SW2 voltage mode based on OTP DVS enable bits, registers every regulator, stores driver data, and requests all platform IRQs. The threaded IRQ handler maps platform IRQ index to current-limit, LDO fault, or thermal events and emits regulator notifier events.

State and persistence: descriptors are copied at probe because SW1/SW2 ops and voltage tables may be changed based on parent OTP-derived state. Runtime state is devm-managed. Regulator settings are PMIC register state; the driver does not persist policy beyond hardware writes.

Dependencies and integration: depends on the PF1550 MFD header for IDs, register addresses, IRQ numbers, and parent data. Integrates with platform bus, parent regmap, and regulator framework. Device tree matching and regmap ownership live in the MFD layer.

Risks and test signals: `pf1550_set_ramp_delay()` divides `6250 / ramp_delay` after accepting zero because only `< 0` is rejected, so zero input is a bug risk. IRQ notifier targeting appears hard-coded to names such as `SW3`/`LDO3` for groups. Test with DVS enabled/disabled OTP states, all IRQ indices, ramp-delay corner cases, suspend voltage setting, and missing parent regmap.
