
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/pmu.h

## Purpose
Defines PMU command and message structures for Nouveau firmware interactions, especially ACR WPR setup and falcon bootstrap through the PMU.

## Important APIs, types, and functions
- `struct nv_pmu_args` stores queue indexes and offsets/sizes for PMU command/message queues.
- Unit IDs include `NV_PMU_UNIT_INIT` and `NV_PMU_UNIT_ACR`.
- `struct nv_pmu_init_msg` reports PMU init, queue IDs, queue indexes, offsets, and sizes.
- `struct nv_pmu_acr_cmd/msg` are generic ACR command/message headers.
- Specific ACR payloads include init WPR region, bootstrap single falcon, and bootstrap multiple falcons command/message structs.
- Flag constants select reset yes/no for bootstrap operations.

## Control flow
This header defines the wire format. Runtime PMU code sends a command with the unit and command type, then receives the matching message carrying error/status. ACR flows initialize the WPR region and then bootstrap one or more falcons, optionally resetting them.

## State and persistence
No C state is kept. Queue descriptors and command/message payloads mirror firmware-managed PMU queue state. WPR and falcon boot state persists in firmware/hardware after commands complete.

## Dependencies and integration points
Used by Nouveau's PMU and ACR code to communicate with PMU firmware. It complements `sec2.h`, which provides similar ACR bootstrap structures through SEC2 on newer GPUs.

## Risks
Command IDs, units, and flags must match firmware ABI. Queue offset/size parsing errors can corrupt command/message queues. Bootstrapping multiple falcons has bitmask/status coupling that must be decoded correctly by callers.

## Test signals
PMU init queue discovery, WPR setup, single and multiple falcon bootstrap, reset/no-reset variants, and error status handling should be covered on PMU-ACR GPUs.
