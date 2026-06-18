# sources/distributed-fs/ceph/src/mon/mon_types.h

## Purpose
`mon_types.h` collects monitor-wide value types, service indexes, on-disk magic, feature bitsets, and serialized status payloads shared across monitor components.

## Important APIs, Types, and Control Flow
The Paxos service index enum maps service slots such as MDS map, OSD map, log, monmap, auth, mgr, health, config, key-value, and NVMe gateway. `FeatureMap` tracks entity type to feature mask to count and excludes monitor features from ordinary add/remove unless `add_mon()` is used. `MonitorDBStoreStats`, `DataStats`, and `ScrubResult` encode monitor store/disk/scrub summaries. `mon_feature_t` wraps monitor feature bits with set operations, containment checks, printing, dumping, encoding, and decoding. The `ceph::features::mon` namespace defines release features from Kraken through Umbrella, release-independent features, supported/persistent/optional sets, and name lookup.

## State and Persistence Behavior
Most structures are serialized values stored or exchanged by monitor code. `DataStats` decodes older versions that stored KB values by converting them to bytes. `ProgressEvent` preserves older behavior by setting `add_to_ceph_s` when decoding old non-empty messages. `PoolAvailability` stores pool uptime/downtime accounting. `infer_ceph_release_from_mon_features()` maps the highest contained release feature to a release enum.

## Dependencies and Integration Points
It depends on Ceph feature definitions, base types, formatters, bit-string helpers, release names, message address types, and clocks. It is used by monitor sessions, monitor maps, store stats reporting, feature negotiation, release compatibility checks, progress reporting, and health/status output.

## Risks and Test Signals
Risks include feature-name mismatches, missing new features from supported/persistent sets, backward decode regressions, and inconsistent treatment of monitor features in `FeatureMap`. A notable compatibility signal is that `get_feature_by_name()` uses `"feature-pinging"` while `get_feature_name()` returns `"elector-pinging"`, so callers must be tested for expected accepted strings. Tests should cover encode/decode fixtures, feature set algebra, release inference ordering, FeatureMap add/remove assertions, and old-version decode paths.
