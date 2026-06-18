<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470_board_data.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470_board_data.c

## Purpose
Provides static regulator constraints, consumer supplies, GPIO lookup tables, software-node properties, and DMI mappings for Windows-designed TPS68470 INT3472 boards.

## Important APIs, Types, And Data
Defines board data for Microsoft Surface Go/Go 2, Surface Go 3, Dell Latitude 7212 Rugged Extreme Tablet, and MSI Prestige 14 AI+ Evo C2VMG. Regulator init data maps TPS68470 rails to camera sensor supplies with fixed voltage constraints. GPIO lookup tables map `tps68470-gpio` pins to sensor reset/powerdown/enable signals. MSI adds a GPIO software node property `daisy-chain-enable`.

## Control Flow
`int3472_tps68470_get_board_data()` iterates all DMI matches, compares each candidate `dev_name` to the active I2C client name, and returns the first exact match. `tps68470.c` then installs the lookup tables and passes regulator data to MFD cells.

## State And Persistence
All data is static. Lookup tables are registered and unregistered by `tps68470.c`.

## Dependencies And Integration Points
Depends on DMI, regulator machine constraints, GPIO machine lookups, TPS68470 platform data, and exact I2C ACPI device names.

## Risks And Test Signals
Risks include exact DMI/device-name mismatches, wrong rail voltages, missing always-on constraints, and GPIO pin drift between board revisions. Test each listed product for board-data selection, regulator voltage/consumer mapping, GPIO reset/powerdown behavior, and camera sensor probe success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470_board_data.c -->
