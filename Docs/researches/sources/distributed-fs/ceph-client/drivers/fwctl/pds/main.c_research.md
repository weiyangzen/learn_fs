# sources/distributed-fs/ceph-client/drivers/fwctl/pds/main.c

## Purpose
`pds/main.c` is the AMD/Pensando DSC fwctl provider. It discovers firmware RPC endpoints and operations through PDS admin queue commands, validates userspace RPCs against firmware-advertised limits and operation scopes, and submits indirect request and response payloads through DMA-mapped buffers.

## Important APIs, Types, and Functions
Key state is `struct pdsfc_dev`, which embeds `struct fwctl_device`, stores the PDS auxiliary device, caps, identify data, a coherent endpoint query page, and per-endpoint cached operation pages. `struct pdsfc_rpc_endpoint_info` stores endpoint id, operations DMA page, and a mutex. fwctl callbacks are `pdsfc_open_uctx()`, `pdsfc_close_uctx()`, `pdsfc_info()`, and `pdsfc_fw_rpc()`. Discovery and validation helpers include `pdsfc_identify()`, `pdsfc_get_endpoints()`, `pdsfc_init_endpoints()`, `pdsfc_get_operations()`, and `pdsfc_validate_rpc()`.

## Control Flow
Probe allocates the fwctl device, sends `PDS_FWCTL_CMD_IDENT` into a coherent identify buffer, queries root endpoints into a page-sized coherent buffer, allocates per-endpoint cache records, sets query/send caps, and registers fwctl. Open copies device caps into the user context. Validation rejects request or response lengths above firmware max sizes, checks that the endpoint exists, lazily queries and caches that endpoint's operation list under its mutex, translates firmware command attributes into fwctl scopes, and rejects unsupported or insufficient-scope operations.

RPC copies the input payload from a userspace pointer inside `struct fwctl_rpc_pds`, maps input for DMA to device, allocates and maps output for DMA from device, sends `PDS_FWCTL_CMD_RPC` with indirect request and response flags, copies output payload back to userspace, stores firmware retval from the completion, and returns the original RPC struct as output. Remove unregisters fwctl, frees cached operation pages, frees endpoints, and drops the fwctl object.

## State and Persistence
State is in memory and coherent DMA pages. Endpoint lists persist for device lifetime; operation lists are lazily cached per endpoint. There is no disk persistence. Per-endpoint mutexes serialize lazy query and cache installation.

## Dependencies and Integration Points
The driver depends on PDS admin queue APIs, PDS core interface definitions, auxiliary bus, DMA mapping, fwctl uapi, and `uapi/fwctl/pds.h`.

## Risks and Test Signals
`pdsfc_info()` allocates `struct fwctl_info_pds` and fills caps but does not assign `*length`, unlike the BNXT and mlx5 providers; the core may report zero provider-info length. In `pdsfc_validate_rpc()`, a failed operation query returns `-ENOMEM` for any `ERR_PTR`, losing the real error. DMA mapping cleanup is careful but should be tested for every allocation and mapping failure. Tests should cover identify failure, endpoint query failure, lazy operations caching under concurrent RPCs, all scope translations, max request/response limits, zero-length payloads, firmware completion retval propagation, remove after cached operations exist, and info length reporting.
