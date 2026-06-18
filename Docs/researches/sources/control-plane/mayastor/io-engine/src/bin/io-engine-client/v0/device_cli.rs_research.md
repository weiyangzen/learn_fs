<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/device_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/device_cli.rs

### Purpose
This file implements the v0 block-device discovery CLI. It lists host block devices, optionally including devices already in use, and formats partition, filesystem, and device-link metadata.

### Important APIs, Types, And Functions
`DeviceArgs` supports `DeviceCommands::List(ListArgs)`. `ListArgs` carries the `--all` flag. `get_partition_type` formats optional partition metadata, and `list_block_devices` performs the RPC and output conversion.

### Control Flow
The handler calls `list_block_devices`. That sends `ListBlockDevicesRequest { all }` to the v0 Mayastor client. JSON output consumes and prints the full response. Default output extracts optional filesystem fields, optional partition type, availability, model, path, and quoted devlinks into a wide table.

### State, Persistence, And Dependencies
The command is read-only. It depends on host device scanning performed by io-engine, v0 protobuf structs, `colored_json`, and the shared table printer. It integrates with pool creation workflows because operators use the output to pick candidate devices.

### Risks And Test Signals
Output width can become large with many symlinks. v0 has a single `mountpoint` string, unlike v1's mountpoint list. Tests should cover devices with and without partition/filesystem fields, `--all` propagation, empty results, devlink quoting, and JSON output consuming the response without later borrows.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/device_cli.rs -->
