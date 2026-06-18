# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.c

## Purpose
Implements IOSM devlink integration for modem flashing, runtime devlink parameters, and modem coredump regions. It creates devlink regions for coredump files, sends RPSI commands over the IOSM devlink system channel, and wires devlink flash update to IOSM PSI/EBL/FLS flash helpers.

## Important APIs, Types, And Functions
Exports `ipc_devlink_send_cmd()`, `ipc_devlink_init()`, and `ipc_devlink_deinit()`. Internal functions include devlink param get/set for `erase_full_flash`, `ipc_devlink_get_flash_comp_type()`, `ipc_devlink_flash_update()`, `ipc_devlink_coredump_snapshot()`, `ipc_devlink_create_region()`, and `ipc_devlink_destroy_region()`. Static coredump metadata lists `report.json`, `coredump.fcd`, `cdd.log`, `eeprom.bin`, `bootcore_trace.bin`, and `bootcore_prev_trace.bin`.

## Control Flow
Initialization allocates a devlink instance, stores PCIe/device pointers, registers params, creates all coredump regions, obtains flash/coredump channel configuration for `IPC_MEM_CTRL_CHL_ID_7`, initializes that IPC channel, initializes read completion and RX list, and registers devlink. Flash update validates the IOSM image header and magic, allocates a modem response buffer, selects component type by image type string (`PSI`, `EBL`, or `FLS`), then calls the matching flash sequence and reports devlink status. Region snapshot calls `ipc_coredump_collect()`, and the final region sends coredump end; failures also end coredump collection. Deinit unregisters devlink, destroys regions, unregisters params, completes pending waits when needed, purges RX list if safe, closes the devlink system channel, and frees devlink.

## State And Persistence
`struct iosm_devlink` stores devlink context, PCIe/device pointers, runtime param `erase_full_flash`, coredump region ops/handles, shared coredump file info, and devlink SIO queue/completions. The static coredump `list[]` is shared metadata and receives per-entry `entry` numbers during region creation. Devlink regions persist until deinit.

## Dependencies And Integration Points
Depends on Linux devlink, vmalloc destructors for region snapshots, IOSM channel config, coredump helpers, flash helpers, IMEM sys devlink read/write/open/close, and PCIe/IMEM state. Kconfig selects `NET_DEVLINK` for IOSM.

## Risks
Static `list[]` is mutated with entry numbers and shared among devices, which can be problematic for multiple IOSM devices if per-device state differs. Error unwinding before channel init does not need to close the channel, but post-registration deinit must handle pending readers carefully. Flash component matching uses `strncmp()` over fixed length, so image type padding matters. `ipc_devlink_send_cmd()` CRC is a simple XOR over little-endian command words and must match modem firmware.

## Test Signals
Test devlink registration/unregistration, param get/set for `erase_full_flash`, flash updates for PSI/EBL/FLS/invalid images, invalid magic and short firmware, coredump region creation failure unwinding, snapshots for all six regions, pending read deinit, and multi-device behavior if supported.
