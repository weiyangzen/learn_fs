# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/brcmstb_thermal.c

## Purpose
Broadcom STB AVS TMON thermal sensor driver. It exposes an OF thermal zone for AVS TMON blocks, supports process-node-specific conversion parameters, and on older 28nm TMON variants supports hardware low/high trip interrupts via `set_trips`.

## Important APIs, Types, and Functions
- `struct avs_tmon_trip` describes enable and threshold fields for low, high, and reset trips.
- `struct brcmstb_thermal_params` carries conversion offset/multiplier and the thermal-zone ops for a compatible.
- `struct brcmstb_thermal_priv` stores MMIO base, device, zone, and conversion params.
- `avs_tmon_code_to_temp()` and `avs_tmon_temp_to_code()` convert between 10-bit hardware codes and millicelsius.
- `brcmstb_get_temp()` reads `AVS_TMON_STATUS`, checks validity, extracts the code, converts, and floors at zero.
- `brcmstb_set_trips()` programs low/high interrupt thresholds and enables/disables interrupt sources.
- `brcmstb_tmon_irq_thread()` reads interrupt temperature, disables the triggered side until the framework moves trip windows, and calls `thermal_zone_device_update()`.
- Match data selects 8nm, 16nm, or 28nm parameter sets.

## Control Flow
Probe loads match data, maps resource 0, registers zone id 0 with the compatible's ops, and optionally requests a threaded IRQ. Temperature polling is a simple status read. For compatibles with `set_trips`, the thermal core calls `brcmstb_set_trips()` to program low and high windows; IRQ thread disables whichever threshold fired and reports an update using the interrupt temperature.

## State and Persistence
Driver state is the MMIO base and thermal zone. Threshold and enable state lives in TMON registers. Conversion parameters are immutable match data.

## Dependencies and Integration Points
Integrates with OF thermal zones, platform IRQs, MMIO resources, and thermal core `set_trips`. The IRQ is optional, so polling-only operation is possible.

## Risks and Edge Cases
- Conversion clamps only negative reported temperature to zero in `get_temp`; threshold conversion still accepts very low values and maps them to max code.
- The 8nm/16nm params omit `set_trips`, so platform DT/thermal policy must not assume hardware window interrupts there.
- IRQ thread depends on the thermal core reprogramming trips after an update; otherwise the relevant interrupt side remains disabled.
- Raw MMIO access uses `__raw_readl/writel`, so ordering expectations are hardware-specific.

## Test Signals
Unit conversion tests should cover min/max/rounding for low vs high trips. Integration tests should verify optional IRQ request, `set_trips(INT_MAX/-INT_MAX)` disable behavior, invalid status handling, and per-compatible ops selection.
