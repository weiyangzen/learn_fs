# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6adm.h

## Purpose
`q6adm.h` is the public internal header for the QDSP6 Audio Device Manager API. It provides path/topology constants, route payload shape, the opaque `struct q6copp` declaration, and prototypes for ADM open, close, COPP ID lookup, and matrix mapping.

## Important APIs and types
Constants include `ADM_PATH_PLAYBACK`, `ADM_PATH_LIVE_REC`, `MAX_COPPS_PER_PORT`, and `NULL_COPP_TOPOLOGY`. `struct route_payload` carries one session ID, the number of COPPs, and parallel arrays of COPP indexes and AFE port IDs. Function prototypes mirror the exported symbols in `q6adm.c`: `q6adm_open()`, `q6adm_close()`, `q6adm_get_copp_id()`, and `q6adm_matrix_map()`.

## Control flow and integration
The header has no control flow. It is included by QDSP6 routing/ASM code that needs to open ADM COPPs and map sessions. The opaque COPP pointer enforces that consumers use ADM APIs rather than directly mutating COPP internals.

## State and persistence behavior
State is represented indirectly through `struct q6copp *` handles returned by `q6adm_open()`. Callers are responsible for balancing `q6adm_close()` calls so the kref in `q6adm.c` can close DSP resources.

## Dependencies and integration points
The header relies on Linux device types and `uint16_t` availability through including C files. It is part of the QDSP6 audio control-plane API and integrates with APR-based ADM implementation.

## Risks and test signals
Risks include callers overfilling `route_payload` beyond `MAX_COPPS_PER_PORT`, not balancing open/close, or using a COPP index after close. Test signals include route payload validation in callers, build coverage for all consumers, and runtime route setup/teardown during PCM start/stop.
