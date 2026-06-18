# sources/distributed-fs/ceph-client/drivers/usb/serial/visor.c

## Purpose
`visor.c` supports Handspring Visor, Palm OS, Sony Clie, and related PDA USB serial devices. It binds a large legacy ID set, queries device connection information for some Palm OS versions, adjusts endpoint mappings for quirky devices, and delegates most data movement to generic USB serial.

## Important APIs, Types, and Functions
The file defines three `usb_serial_driver` instances: `visor`, `clie_5`, and `clie_3.5`. Important callbacks are `visor_probe()`, `palm_os_3_probe()`, `palm_os_4_probe()`, `visor_calc_num_ports()`, `clie_5_calc_num_ports()`, `clie_3_5_startup()`, `visor_open()`, `visor_close()`, and `visor_read_int_callback()`. It uses constants and structures from `visor.h` for vendor request codes and connection-info layouts.

## Control Flow, State, and Persistence
Probe rejects Samsung ACM devices that reuse a Palm ID and requires active configuration 1. Devices with `driver_info` call either the Palm OS 3 or Palm OS 4 probe helper. The OS 3 path requests `VISOR_GET_CONNECTION_INFORMATION`, validates and logs up to two logical ports, stores `num_ports` temporarily in serial data for `calc_num_ports()`, and sends a broken bytes-available request whose result is ignored. The OS 4 path requests extended connection info for debug logging. `visor_calc_num_ports()` retrieves stored port count and may swap bulk-in and interrupt-in endpoints for Handspring/Kyocera Treo-style devices. `clie_5_calc_num_ports()` maps both logical ports to the second bulk-out endpoint. `clie_3_5_startup()` performs GET_CONFIGURATION and GET_INTERFACE requests expected by older Sony devices.

Open verifies a read URB exists, starts generic bulk reading, and submits interrupt-in URB if present. Close calls generic close, kills interrupt-in, and sends `VISOR_CLOSE_NOTIFICATION`. Interrupt callbacks only debug-log and resubmit; data readiness is not otherwise interpreted.

Runtime state is minimal. Temporary serial data carries detected port count between probe and port-count calculation; all long-lived data is generic core state.

## Dependencies and Integration Points
The driver depends on USB serial core generic callbacks, TTY/USB APIs, CDC class constants for rejecting ACM conflicts, and `visor.h` protocol definitions. It integrates through three subdrivers sharing one combined USB ID table.

## Risks and Test Signals
Risks include legacy devices returning malformed connection-info lengths, endpoint swapping breaking assumptions for unusual Treo/Kyocera layouts, broad Samsung ID conflicts, and close-notification failures being ignored. Test signals include Palm OS 3 port-count query, Palm OS 4 extended-info query, Sony Clie 3.5 startup requests, Clie 5 endpoint remap, Treo endpoint swap, generic open/close with interrupt endpoint, and ACM Samsung rejection.
