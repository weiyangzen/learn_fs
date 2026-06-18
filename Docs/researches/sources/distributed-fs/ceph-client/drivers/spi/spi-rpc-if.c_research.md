# sources/distributed-fs/ceph-client/drivers/spi/spi-rpc-if.c

## Purpose

`spi-rpc-if.c` adapts the Renesas RPC-IF memory controller core to the Linux `spi-mem` API. It does not implement low-level register access itself; instead it translates `spi_mem_op` and direct-map requests into `struct rpcif_op` operations and delegates hardware work to `memory/renesas-rpc-if.h` helpers.

## Important APIs, Types, and Functions

`rpcif_spi_mem_prepare()` is the central translator from `struct spi_mem_op` to RPC-IF command, address, dummy, and data fields. `rpcif_spi_mem_supports_op()` filters operations through default spi-mem support plus RPC-IF limits of <=4-bit bus widths and <=4 address bytes. Direct-map hooks are `rpcif_spi_mem_dirmap_create()`, `rpcif_spi_mem_dirmap_read()`, and `xspi_spi_mem_dirmap_write()`. Manual operations use `rpcif_spi_mem_exec_op()`.

Probe/remove and PM hooks are `rpcif_spi_probe()`, `rpcif_spi_remove()`, `rpcif_spi_suspend()`, and `rpcif_spi_resume()`. The registered `spi_controller_mem_ops` exposes supports-op, exec-op, dirmap-create, dirmap-read, and dirmap-write.

## Control Flow

Probe allocates a SPI host with embedded `struct rpcif`, initializes RPC-IF software state from the parent device, points the SPI controller OF node at the parent, enables runtime PM on `rpc->dev`, declares one chip select and half-duplex 8-bit SPI with dual/quad mode bits, initializes hardware in SPI mode, and registers the controller. `exec_op` prepares the operation and calls `rpcif_manual_xfer()`. Direct-map reads/writes verify that offset plus length stays within 32-bit RPC address space, prepare the template with adjusted offsets/lengths, then call `rpcif_dirmap_read()` or `xspi_dirmap_write()`.

## State and Persistence Behavior

This file keeps little state of its own. `struct rpcif` owned by the common RPC-IF layer stores the device, direct-map capability, XSPI capability, and hardware state. Persistent effects are flash-memory reads/writes/erases performed by spi-mem clients; the adapter has no filesystem persistence.

## Dependencies and Integration Points

The driver is tightly coupled to the Renesas RPC-IF core API: `rpcif_sw_init()`, `rpcif_hw_init()`, `rpcif_prepare()`, `rpcif_manual_xfer()`, `rpcif_dirmap_read()`, and `xspi_dirmap_write()`. It integrates with platform devices by using the parent hardware device as the real RPC-IF device and registers a child SPI controller named `rpc-if-spi`.

## Risks and Edge Cases

Address-range checks reject direct-map accesses beyond `U32_MAX`, but manual `exec_op` does not perform the same explicit bound check in this file. Direct-map writes require `rpc->xspi`; non-XSPI hardware only supports direct-map reads. The resume path calls `rpcif_hw_init(dev, false)` using the SPI device pointer rather than `rpc->dev`; correctness depends on the PM callback device matching what the RPC-IF core expects. Operation support is deliberately conservative: octal or >4-byte-address operations are rejected here.

## Test Signals

Test normal spi-nor probe, manual register reads/writes, direct-map reads, XSPI direct-map writes, operations at the 32-bit address boundary, dual/quad bus-width combinations, suspend/resume reinitialization, and absence of direct-map support when `rpc->dirmap` or `rpc->xspi` is false.
