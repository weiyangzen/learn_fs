# sources/distributed-fs/ceph-client/drivers/usb/serial/visor.h

## Purpose
`visor.h` is the protocol and ID definition header for the Palm/Handspring/Sony Clie USB serial driver. It centralizes vendor/product IDs, vendor request codes, endpoint/function constants, and connection-info structure layouts consumed by `visor.c`.

## Important APIs, Types, and Functions
The header defines IDs for Handspring, Palm, GSPDA, Sony, Acer, Samsung, Tapwave, Garmin, Aceeca, Kyocera, and Fossil devices. It defines request codes `VISOR_REQUEST_BYTES_AVAILABLE`, `VISOR_CLOSE_NOTIFICATION`, `VISOR_GET_CONNECTION_INFORMATION`, and `PALM_GET_EXT_CONNECTION_INFORMATION`. `struct visor_connection_info` models the original Handspring/Palm OS 3 two-port response. `struct palm_ext_connection_info` models Palm OS 4 extended connection metadata with endpoint-number and function fields.

## Control Flow, State, and Persistence
The header has no executable flow or stored state. Its constants drive `visor.c` USB ID tables and control-message payload parsing. The structures are laid out with fixed-width little-endian fields matching device protocol responses.

## Dependencies and Integration Points
It is included only by `visor.c` in this subset and depends on kernel fixed-width integer and endian types being available through surrounding includes. Changes here directly alter which devices `visor.c` recognizes and how it interprets control response buffers.

## Risks and Test Signals
Risks include wrong product IDs causing incorrect binding, structure layout mismatches with device firmware, and stale comments around obscure Palm vendor requests. Test signals are compile coverage for `visor.c`, USB ID matching for each listed family, validating connection-info buffer sizes, and ensuring endpoint/function constants match the parser branches in `palm_os_3_probe()`.
