# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.h

## Purpose
Defines Tegra ADMA isomgr bandwidth state and the public API used by ADMAIF.

## Important APIs/types/functions
`STREAM_TYPE` is two for playback/capture. `struct tegra_adma_isomgr` stores a mutex, ICC path, per-device bandwidth arrays, current aggregate bandwidth, max PCM device count, and max bandwidth. It declares register, unregister, and set-bandwidth functions.

## Control flow
No executable logic. The C file initializes this state at ADMAIF registration and updates it on stream running/stopped transitions.

## State, dependencies, integration, risks, tests
The object is attached to ADMAIF and persists for device lifetime. Dependencies are Linux mutex/ICC/device types and ASoC stream types. Risks are stream-index misuse and lifecycle drift with devm allocations. Compile with ADMAIF and verify runtime bandwidth accounting.
