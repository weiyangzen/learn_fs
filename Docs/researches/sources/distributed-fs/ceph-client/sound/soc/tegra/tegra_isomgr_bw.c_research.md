# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.c

## Purpose
Implements interconnect bandwidth voting for Tegra ADMAIF streams by tracking per-PCM-device audio bandwidth and setting aggregate ICC write bandwidth.

## Important APIs/types/functions
Public functions are `tegra_isomgr_adma_register`, `tegra_isomgr_adma_unregister`, and `tegra_isomgr_adma_setbw`. It consumes `struct tegra_admaif` and manages `struct tegra_adma_isomgr`.

## Control flow
Register allocates state, gets the `"write"` ICC path, derives max PCM devices and max bandwidth, allocates playback/capture arrays, initializes the mutex, and attaches state to ADMAIF. `setbw` validates runtime/PCM, skips no-op transitions, computes running bandwidth from channels/rate/sample bytes, clamps aggregate to max, updates accounting, then calls `icc_set_bw`.

## State, dependencies, integration, risks, tests
State is the ICC path, mutex, aggregate bandwidth, maxes, and `bw_per_dev[stream][device]`. Dependencies are Tegra ADMAIF, ALSA runtime state, and Linux interconnect. Risks include unit mismatches, stale accounting after failures, unsupported formats, and no ICC path. Test multi-stream start/stop, invalid device indexes, ICC traces, and cleanup.
