<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/bpf_perf.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/bpf_perf.h

## Purpose
This public libperf header describes the bpffs-pinned attribute map contract used by BPF-assisted perf-stat sessions. It provides a small shared struct and default map-name constant for coordinating leader BPF programs.

## Important APIs, Types, and Functions
- `struct perf_event_attr_map_entry` contains two kernel object IDs: `link_id` for the leader program's BPF link and `diff_map_id` for the associated diff map.
- `BPF_PERF_DEFAULT_ATTR_MAP_PATH` names the default pinned attr-map file as `perf_attr_map`.

## Control Flow and State
The header has no executable control flow. Its comment defines the state model: a bpffs hash map is keyed by `struct perf_event_attr`, locked with `flock()` on the pinned file, and stores IDs rather than references. Perf-stat sessions hold their own BPF link references so leader programs and maps are released after all sessions exit.

## Dependencies and Integration Points
It includes Linux integer types and integrates with BPF perf-stat code that is outside this file. It is part of libperf's installed public API surface.

## Risks and Test Signals
The main risk is semantic drift between this shared layout and the BPF-side map value. Because it stores IDs only, consumers must correctly reacquire objects and hold references. No direct unit test appears in this subset; validation is expected from BPF perf-stat integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/bpf_perf.h -->
