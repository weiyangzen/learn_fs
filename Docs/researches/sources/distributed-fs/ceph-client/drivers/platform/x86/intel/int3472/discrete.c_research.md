<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete.c

## Purpose
Implements INT3472 devices whose camera power control is a set of discrete GPIOs and optional DSM-controlled clocks. It translates firmware GPIO descriptions into Linux sensor GPIO lookups, clocks, regulators, and LEDs.

## Important APIs, Types, And Functions
The file uses a GPIO DSM GUID to decode GPIO type, pin, and active value. `int3472_get_con_id_and_polarity()` maps firmware types and sensor-specific quirks to consumer names and polarity. `skl_int3472_handle_gpio_resources()` handles each ACPI GPIO resource, either mapping it to the sensor lookup table or consuming it to register a clock, regulator, privacy LED, or strobe LED. `int3472_discrete_parse_crs()` walks `_CRS`, registers DSM clock fallback, and adds the lookup table.

## Control Flow
Probe checks ACPI companion, applies DMI quirks, reads CLDB and requires `control_logic_type == 1`, allocates a flexible `int3472_discrete_device`, records clock source, discovers the sensor dependent device/name, initializes lookup-table state, parses GPIO resources, then clears ACPI dependencies so the sensor can probe.

## State And Persistence
State includes sensor ACPI reference/name, GPIO lookup table entries, registered clocks/regulators/LEDs, counted GPIOs, and quirks. Cleanup removes lookup tables and unregisters all framework objects.

## Dependencies And Integration Points
Depends on ACPI resource parsing, DMI quirks, gpiod machine lookups, GPIO descriptors, clk/regulator/LED helpers, and INT3472 common helpers.

## Risks And Test Signals
Risks include firmware DSM/resource mismatches, incorrect polarity inversion from sensor-on value, too many GPIOs, temporary lookup races, and missing cleanup on partial failures. Test representative sensors for reset/powerdown GPIO lookup, regulator enables, privacy LED registration, DSM and GPIO clocks, DMI quirk second-sensor supply, and sensor probe after dependencies are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete.c -->
