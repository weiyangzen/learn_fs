# sources/distributed-fs/ceph-client/drivers/mcb/mcb-lpc.c

## Purpose
`mcb-lpc.c` implements an LPC/non-PCI carrier for MEN Chameleon Bus FPGAs on specific MEN systems discovered via DMI.

## Important APIs, Types, and Functions
Important elements are `struct priv`, `mcb_lpc_probe()`, `mcb_lpc_remove()`, `mcb_lpc_create_platform_device()`, fixed `sc24_fpga_resource` and `sc31_fpga_resource`, the `mcb_lpc_driver`, the DMI match table, and module init/exit.

## Control Flow, State, and Persistence
Module init checks DMI; a match callback allocates a platform device with a fixed memory resource. Probe requests and maps the resource, allocates an MCB bus, parses Chameleon cells, optionally shrinks the reserved mapping to the actual table size, and attaches discovered MCB devices. Remove releases the MCB bus, while devm handles IO mappings and memory regions. Persistent input is firmware/DMI identity plus FPGA descriptor memory; runtime state is `struct priv` and registered device-model objects.

## Dependencies and Integration Points
The file uses platform device APIs, DMI matching, IO memory mapping, `chameleon_parse_cells()`, and MCB namespace exports. It binds a synthetic `mcb-lpc` platform device only on supported MEN product versions.

## Risks and Test Signals
Risks include fixed physical resource assumptions, DMI table drift, resource remapping after table-size discovery, and exit unregistering a possibly unset platform device. Tests should cover matching and nonmatching DMI systems, parse failure cleanup, table sizes below and equal to `CHAM_HEADER_SIZE`, and module unload after failed init.
