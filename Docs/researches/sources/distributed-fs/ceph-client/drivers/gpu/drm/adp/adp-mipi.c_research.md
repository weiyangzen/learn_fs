# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp-mipi.c

## Purpose
`adp-mipi.c` implements the Apple Display Pipe MIPI DSI host and bridge companion. It maps the MIPI MMIO registers, sends and receives DSI packets through command/payload FIFOs, exposes `mipi_dsi_host_ops`, and attaches the next DRM bridge found in the OF graph.

## Important APIs, types, and functions
The main private type is `struct adp_mipi_drv_private`, containing a `mipi_dsi_host`, local DRM bridge, next bridge pointer, and MMIO base. Important functions are `adp_dsi_gen_pkt_hdr_write()`, `adp_dsi_write()`, `adp_dsi_read()`, `adp_dsi_host_transfer()`, host `attach`/`detach`, `adp_dsi_bridge_attach()`, `adp_mipi_probe()`, and `adp_mipi_remove()`.

## Control flow
Probe allocates a managed DRM bridge container, maps the MIPI resource, initializes host and bridge metadata, stores driver data, and registers the MIPI DSI host. On DSI device attach, it resolves the downstream bridge from graph port 1, adds the local bridge, and registers a component so the master ADP DRM device can bind. Transfers create a DSI packet, write payload words to `DSI_GEN_PLD_DATA` while polling FIFO status, write the packet header to `DSI_GEN_HDR`, and optionally poll/read response payload words. Detach removes the component and bridge; remove unregisters the host.

## State and persistence behavior
State is limited to the platform device lifetime: MMIO base, host registration, local bridge registration, and `next_bridge`. FIFO state lives in hardware registers. There is no persistent state.

## Dependencies and integration points
The file depends on platform devices, OF graph bridge lookup, Linux component framework, `readl_poll_timeout()`, DRM bridge APIs, and MIPI DSI host APIs. It integrates with `adp_drv.c` through the component framework and with downstream panel/bridge drivers through `drm_bridge_attach()`.

## Risks and edge cases
FIFO polling timeouts can fail transfers, and the code assumes 32-bit payload packing and little-endian header conversion. There is no explicit DSI mode programming, lane setup, or power sequencing in this file, so it relies on surrounding hardware/firmware state. Component bind/unbind callbacks are empty, making ordering dependent on host attach and main driver bridge resolution. Attach failure must remove the bridge to avoid stale registration.

## Test signals
Probe should map `apple,h7-display-pipe-mipi`, register a DSI host, attach a downstream panel/bridge, and complete DCS write/read transfers. Fault signals include FIFO full/empty timeouts, missing graph bridge, component add failure, detach cleanup, and module unload after active DSI devices.
