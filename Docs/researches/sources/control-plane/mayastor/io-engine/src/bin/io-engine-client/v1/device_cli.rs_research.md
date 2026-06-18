<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/device_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/device_cli.rs

### Purpose
This file implements v1 host block-device discovery. It is the v1 equivalent of the device CLI and accounts for v1 filesystem mountpoint lists.

### Important APIs, Types, And Functions
`DeviceArgs` supports `DeviceCommands::List(ListArgs)`. `ListArgs` carries `--all`. `get_partition_type` formats partition scheme and type ID. `list_block_devices` calls `ctx.v1.host.list_block_devices`.

### Control Flow
The command sends `ListBlockDevicesRequest { all }`. JSON output serializes the response. Default output consumes the device vector, extracts optional filesystem data, joins multiple mountpoints and devlinks, formats availability, partition type, size, model, and device path, then prints a table.

### State, Persistence, And Dependencies
The module is read-only against remote host state. It depends on v1 host protobufs, colored JSON, SNAFU, and shared table formatting. It feeds operator decisions for pool creation/import.

### Risks And Test Signals
The table can be wide for many mountpoints or symlinks. Since it consumes the response in both branches, future code must avoid borrowing after `into_inner`. Tests should cover multiple mountpoints, missing filesystem/partition, `--all`, empty lists, and JSON output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/device_cli.rs -->
