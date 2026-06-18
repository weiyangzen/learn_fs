<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_usb_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_usb_power.c

## Purpose

`axp20x_usb_power.c` exposes the USB/VBUS input of AXP192, AXP202, AXP221, AXP223, AXP717, and AXP813 PMICs as a USB power supply. It reports VBUS health, presence, online state, voltage/current measurements where supported, input current limits, and USB charger type for variants with BC1.2 detection. Some variants also allow forcing the VBUS input offline.

## Important APIs, Types, And Functions

`struct axp20x_usb_power` stores the parent device/regmap, optional regmap fields, registered supply, variant data, optional IIO channels, delayed VBUS-detection work, DT maximum input current, cached VBUS status, and IRQ array. `struct axp_data` provides descriptor, IRQ names, current-limit table, reg fields, polling requirement, and callbacks for VBUS polling and ADC/IIO setup.

`axp20x_usb_power_get_property()` handles classic variants. It decodes `AXP20X_PWR_INPUT_STATUS`, `AXP20X_VBUS_IPSOUT_MGMT`, optional VBUS-valid fields, BC-detect fields, IIO or raw ADC values, and current-limit table selectors. `axp717_usb_power_get_property()` handles AXP717-specific status, fault, voltage-limit, current-limit, USB type, and voltage readings. Setters validate Vhold/current ranges, clamp to `input-current-limit-microamp`, disable BC1.2 before manual current writes to avoid races, and use either table selectors or AXP717 linear register formulas.

## Control Flow

Probe selects variant data, allocates state sized for IRQs, allocates mandatory and optional regmap fields, parses the DT maximum input current, initializes delayed work, enables VBUS monitoring and ADC/IIO channels when present, enables BC1.2 detection when available, registers the power supply, requests named regmap IRQs, and starts polling for variants needing it. IRQ handlers signal `power_supply_changed()` and debounce VBUS polling by 50 ms.

## State And Persistence

The driver caches `old_status` and `online` for polling decisions. Hardware state persists in PMIC registers: monitor enable, ADC enable, BC1.2 enable, Vhold, current limits, and optional VBUS disable. AXP717 health reads clear VBUS/VSYS fault bits by writing the fault register.

## Dependencies And Integration Points

It depends on the AXP20x MFD parent, regmap fields, regmap IRQs, IIO or raw AXP ADC access, `devm_delayed_work_autocancel()`, power-supply USB type support, and OF compatibles for six PMIC variants. It also integrates with firmware through `input-current-limit-microamp`.

## Risks And Edge Cases

AXP221/223/813 polling only runs while offline; wrong cached `online` state can delay change reporting. Current-limit tables contain `-1` unsupported entries, so setting `-1` is explicitly rejected and reads clamp out-of-range selectors to the table maximum. `ONLINE` writeability is intentionally exposed only when the register bit disables VBUS, because older variants interpret the bit oppositely. AXP717 raw ADC conversion uses `% AXP717_ADC_DATA_MASK`, which is unusual for masking and worth testing. Manual current writes disable BC detection until cable status changes re-enable it.

## Test Signals

Tests should cover plug/removal IRQs, debounce/poll behavior on AXP221/223/813, BC1.2 type mapping, current-limit clamping to DT maximum, VBUS disable on AXP813, AXP717 overvoltage health clearing, IIO and non-IIO ADC paths, and suspend/resume wake behavior with only `VBUS_PLUGIN` as wake IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_usb_power.c -->
