<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-selectmap.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-selectmap.c

## Purpose
`xilinx-selectmap.c` is a transport driver that loads Xilinx Spartan-7, Artix-7, Kintex-7, and Virtex-7 bitstreams through the SelectMAP parallel configuration interface while reusing the common Xilinx FPGA manager core.

## Important APIs, types, and functions
`struct xilinx_selectmap_conf` embeds `struct xilinx_fpga_core` and stores the mapped data register. `xilinx_selectmap_write()` writes each byte to the mapped base address. `xilinx_selectmap_probe()` maps the resource, optionally configures active-low CSI_B and RDWR_B GPIOs, and calls `xilinx_core_probe()`.

## Control flow
Probe allocates the transport config, assigns the common core device and write callback, maps the SelectMAP MMIO resource, requests optional `csi` and `rdwr` GPIOs as inactive-high outputs, then delegates GPIO PROGRAM_B/INIT_B/DONE acquisition and manager registration to `xilinx_core_probe()`. During programming, the common core calls `xilinx_selectmap_write()` for data and completion padding; the transport loops byte-by-byte through MMIO writes.

## State and persistence behavior
Runtime state consists of the embedded core and MMIO base pointer. GPIOs and memory mappings are devm-managed. No persistent state exists.

## Dependencies and integration points
It depends on platform devices, OF compatible strings for 7-series SelectMAP variants, GPIO descriptors, MMIO helpers, and `xilinx-core`. It integrates as a transport layer beneath the FPGA manager core.

## Risks and edge cases
The byte-write loop has no hardware-ready polling, so board timing must be satisfied by the bus and common core sequence. Optional CSI/RDWR GPIOs are configured but not stored or toggled after probe. Incorrect resource width or GPIO polarity can silently break programming.

## Test signals
Build/probe for each compatible, successful firmware load through the manager, byte-write instrumentation on the MMIO aperture, optional GPIO absence/presence handling, and failure propagation from `xilinx_core_probe()` are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-selectmap.c -->
