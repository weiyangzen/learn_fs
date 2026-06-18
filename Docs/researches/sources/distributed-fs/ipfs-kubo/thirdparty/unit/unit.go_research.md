## sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit.go

Purpose: defines binary information-size constants and a string formatter for byte counts.

Important APIs/types/functions: `type Information int64` represents sizes. Constants `KB`, `MB`, `GB`, `TB`, `PB`, and `EB` are powers of 1024 using `iota`. `Information.String` chooses the largest unit whose threshold is strictly less than the value, divides by that unit, and returns an integer string like `12 MB`.

State and persistence: stateless pure formatting code.

Dependencies and integration points: imports only `fmt`; likely used by user-facing size output in older Kubo code.

Risks and test signals: threshold comparisons use `>` rather than `>=`, so exactly `1 KB` formats as `1024 B`, not `1 KB`. The function truncates fractional units. Any callers requiring conventional human-readable output should account for this behavior.
