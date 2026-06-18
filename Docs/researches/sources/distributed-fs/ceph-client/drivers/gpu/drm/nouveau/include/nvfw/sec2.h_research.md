
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/sec2.h

## Purpose
Defines SEC2 command/message structures for initialization, unload, and ACR falcon bootstrap in Nouveau firmware flows.

## Important APIs, types, and functions
- `struct nv_sec2_args` stores command/message queue indexes.
- Unit IDs cover init, unload, and ACR for v1 and v2 firmware ABIs.
- `struct nv_sec2_init_msg` and `nv_sec2_init_msg_v1` report initialization and queue location/size metadata.
- `struct nv_sec2_acr_cmd/msg` are generic ACR headers.
- `struct nv_sec2_acr_bootstrap_falcon_cmd/msg` and `_v1` define falcon id, flags, and error/status fields for bootstrap.

## Control flow
Runtime SEC2 code receives an init message to discover queue indexes, then sends ACR bootstrap commands to SEC2 firmware. Newer v2 unit IDs and v1 bootstrap payloads support ABI variants.

## State and persistence
No local state is declared. The structs represent firmware queue payloads; resulting falcon boot and SEC2 state persists in firmware/hardware.

## Dependencies and integration points
Used by Nouveau SEC2 and ACR implementations. It is the SEC2 counterpart to PMU ACR command definitions.

## Risks
ABI version mismatches between unit IDs and payload layouts can make firmware ignore commands or report misleading errors. Reset flags affect falcon lifecycle and must be chosen carefully during resume or multi-falcon boot.

## Test signals
SEC2 firmware init, queue discovery, bootstrap success/failure statuses, v1/v2 unit handling, and unload paths are key runtime signals.
