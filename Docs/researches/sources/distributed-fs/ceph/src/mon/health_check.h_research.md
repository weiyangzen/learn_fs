# sources/distributed-fs/ceph/src/mon/health_check.h

## Purpose
`health_check.h` defines encoded monitor health payloads: individual health checks, muted health entries, and maps of health checks by code. These types are used by monitor services to persist and report cluster health state.

## Important APIs, Types, and Control Flow
`health_check_t` stores severity, summary, detail lines, and count. It has DENC version 2 with backward-compatible count decoding, equality operators, formatter dumping, and test instances. `health_mute_t` stores code, TTL, sticky flag, summary, and count with DENC support and dump/test helpers. `health_check_map_t` wraps `std::map<std::string, health_check_t>` and provides `clear`, `empty`, `swap`, `add`, `get_or_add`, `merge`, equality, dumping, and generated test instances.

## State and Persistence Behavior
The types are pure value objects serialized through Ceph DENC macros. `PaxosService::encode_health()` persists `health_check_map_t` values into `MonitorDBStore` under the `health` prefix, while `load_health()` decodes them. Merge behavior preserves existing summaries and appends details/counts for duplicate codes.

## Dependencies and Integration Points
It depends on `include/health.h`, `utime_t`, and `Formatter`. It integrates with monitor service health logging, manager/user health reporting, mute handling, and Ceph's encoding test infrastructure via `generate_test_instances()`.

## Risks and Test Signals
Risks include duplicate `add()` assertions, count loss in old encodings, detail growth during merges, and mismatch between severity/summary for duplicate codes. Tests should cover DENC round trips across versions, formatter output with and without details, merge semantics, mute TTL/sticky serialization, and `PaxosService` health persistence.
