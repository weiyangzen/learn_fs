# sources/distributed-fs/ceph-client/drivers/cdx/controller/mc_cdx_pcol.h

## Purpose
This generated-style protocol header defines the CDX subset of the MCDI management-controller protocol: message header fields, error codes, CDX bus/device commands, payload layouts, and v2 extended-command encapsulation.

## Important APIs, Types, and Functions
The file defines protocol constants rather than functions. Important groups are `MCDI_HEADER_*` bit fields, `MCDI_CTL_SDU_LEN_MAX_V2`, `MC_CMD_ERR_*` values, CDX commands `MC_CMD_CDX_BUS_ENUM_BUSES`, `MC_CMD_CDX_BUS_ENUM_DEVICES`, `MC_CMD_CDX_BUS_GET_DEVICE_CONFIG`, `MC_CMD_CDX_BUS_DOWN`, `MC_CMD_CDX_BUS_UP`, `MC_CMD_CDX_DEVICE_RESET`, `MC_CMD_CDX_DEVICE_CONTROL_SET`, `MC_CMD_CDX_DEVICE_CONTROL_GET`, `MC_CMD_CDX_DEVICE_WRITE_MSI_MSG`, and extended wrapper `MC_CMD_V2_EXTN`.

## Control Flow
Runtime code in `mcdi.c` uses the header layout to construct MCDI v2 request headers and parse responses. `mcdi_functions.c` uses command IDs, input lengths, output lengths, offsets, and field widths to populate firmware requests and decode returned topology/resource/control data.

## State and Persistence Behavior
No kernel state is allocated. The constants encode a firmware ABI; changes must be synchronized with firmware. Firmware-side state includes bus reset state, device control flags, device resources, MSI message data, and enumeration generation behavior described in comments.

## Dependencies and Integration Points
The macros depend on bitfield helpers from `<linux/cdx/bitfield.h>` through the MCDI wrapper headers. They integrate with RPMsg payloads and the controller firmware running on the RPU/R5.

## Risks
This header is the contract for every firmware operation. Wrong offsets or lengths corrupt requests, reject valid responses, or misconfigure device DMA/MSI. Comments indicate enumeration may return `EAGAIN` when resources change, so callers should be robust to retry needs. Some command comments describe quiescence guarantees for reset/bus-down; controller safety relies on firmware honoring them. The protocol supports 64-bit fields that are only 32-bit aligned, so access helpers must avoid unsafe direct casts.

## Test Signals
Protocol tests should compare structure lengths and offsets against firmware definitions, validate request byte streams for every command, decode sample responses, exercise each `MC_CMD_ERR_*` translation path, and test firmware behavior during bus reset, PL reload, MSI programming, and generation changes.
