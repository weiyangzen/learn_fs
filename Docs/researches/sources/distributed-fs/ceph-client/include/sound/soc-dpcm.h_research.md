<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-dpcm.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-dpcm.h

## Purpose
`soc-dpcm.h` declares Dynamic PCM support, which connects ASoC front-end PCMs to backend DAIs at runtime based on DAPM routes and stream state.

## Important APIs, types, and functions
Enums define update sources (`NO`, `BE`, `FE`), FE/BE link states, PCM runtime states, and trigger ordering. `struct snd_soc_dpcm` links one FE to one BE and tracks list membership and debugfs state. `struct snd_soc_dpcm_runtime` tracks FE/BE client lists, users, hardware params, runtime update type, state, pending trigger, backend start/pause refs, and FE pause. Iteration macros walk FE and BE links. APIs include substream lookup, runtime update, DPCM debugfs, path get/put/add, BE startup/stop/disconnect/hw_params/hw_free/prepare/trigger, pending-state clear, DAPM stream event, and widget list/path helpers.

## Control flow
When an FE starts or routes change, DPCM walks DAPM paths to find BEs, creates or frees FE/BE links, starts backend DAIs, applies or merges hw_params, prepares/triggers BEs according to ordering, and unwinds through rollback helpers on failure.

## State and persistence behavior
DPCM state is per runtime and per stream: linked FE/BE lists, users, current state, copied hw_params, pending triggers, and backend reference counters. It is temporary runtime state removed when routes disconnect or the card is torn down.

## Dependencies and integration points
It depends on ALSA PCM params, ASoC runtime/card, DAPM widget lists, and debugfs. It is tightly coupled to FE/BE DAI link flags in `soc.h`.

## Risks and test signals
Risks include FE/BE state-machine mismatches, rollback leaks, backend refcount underflow, trigger ordering errors, stale DAPM paths after route changes, typo-prone stream parameters, and pause/resume edge cases. Test signals include dynamic route changes while open, BE sharing across FEs, merged format/channel/rate, prepare/trigger rollback, pause then stop, suspend/resume, and debugfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-dpcm.h -->
