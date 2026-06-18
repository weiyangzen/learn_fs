# sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.cc

Purpose: implements the server selection algorithm for placing new chunk copies or slice parts across chunkservers while respecting labels, minimum version, prior selections, weights, load factors, and optional IP spreading.

Important APIs/types/functions: `prepareData()` synchronizes and resets `ChunkCreationHistory`, copies previous created-counts into local server counters, randomizes equal cases, stable-sorts by relative usage/weight/load, and optionally calls `sortAvoidingSameIp()`; `sortAvoidingSameIp()` groups servers by per-IP occurrence count to avoid adjacent same-IP selections; `chooseServersForLabels()` first satisfies explicit non-wildcard label counts, then fills remaining expected copies with any eligible unused servers, and increments history for selected servers.

Control flow: callers add candidate servers, call `prepareData(history)`, then call `chooseServersForLabels()` for each goal slice/part while passing a shared `used` vector. The method skips servers below `min_version` or already used in the chunk.

State and persistence behavior: history is caller-owned process memory, not persistent metadata. It resets when server list length, pointer identity, label, weight, or created-count threshold changes.

Dependencies/integration: depends on `Goal::Slice`, media labels, `matocsserventry`, global `gAvoidSameIpChunkservers`, `matocsserv_get_servip()`, and randomization utilities. Integrated into chunk creation in the master.

Risks and test signals: raw server pointers are used as identity in history and `used`, so lifetime/order changes reset balance. `std::random_shuffle` is legacy and affects determinism. Sorting multiplies counts by weights and relies on the million-chunk reset to avoid overflow. Tests should cover min-version filtering, label shortages, wildcard fill, used-vector exclusion across slices, weighted distribution, same-IP reordering, and history resets.
