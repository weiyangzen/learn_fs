<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.h

## Purpose
This header defines the MSI EC configuration schema used by `msi-ec.c` to describe firmware-specific EC register layouts.

## Important APIs, Types, And Functions
It defines driver name, universal firmware-info addresses and lengths, unknown/unsupported sentinel addresses, and configuration structs for charge control, webcam, Fn/Win swap, cooler boost, shift mode, super battery, fan mode, CPU/GPU sensors, mute LEDs, and keyboard backlight. `struct msi_ec_mode` maps names to EC values. `struct msi_ec_conf` aggregates all feature sub-configurations and the allowed firmware string list.

## Control Flow
There is no executable control flow. `msi-ec.c` fills these structs in static tables and copies the matching one at module init.

## State And Persistence
The header owns no state. Its structs describe EC-backed state owned by firmware.

## Dependencies And Integration Points
The header depends only on Linux integer types. It is a private contract between MSI EC configuration tables and code that reads/writes EC addresses.

## Risks And Edge Cases
Both `MSI_EC_ADDR_UNKNOWN` and `MSI_EC_ADDR_UNSUPP` are defined as `0xff01`, so code cannot distinguish them without external comments. Fixed-size mode arrays require manual NULL termination with `MSI_EC_MODE_NULL`.

## Test Signals
Build checks should validate structure initializers and array sizes. Runtime validation comes from correct firmware match and safe threshold behavior in `msi-ec.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.h -->
