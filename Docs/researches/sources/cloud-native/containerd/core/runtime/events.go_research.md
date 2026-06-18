<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/events.go -->
# sources/cloud-native/containerd/core/runtime/events.go

## Purpose
Maps runtime task event payload types to containerd event topic strings.

## Important APIs, Types, And Functions
- Topic constants such as `/tasks/create`, `/tasks/start`, `/tasks/exit`, `/tasks/delete`, and `/tasks/checkpointed`.
- `GetTopic(e any) string` returns the topic for known `api/events` task event pointer types, otherwise logs and returns `/tasks/?`.

## Control Flow
`GetTopic` uses a type switch over event pointer types. Unknown inputs are logged at warning level and mapped to `TaskUnknownTopic`.

## State And Persistence
No state; pure mapping plus logging side effect.

## Dependencies And Integration Points
Depends on `github.com/containerd/containerd/api/events` and `log`. Used by runtime event publishers/bridges to determine event exchange topics.

## Risks And Edge Cases
Only pointer types match; non-pointer event values return unknown. Adding new event types requires updating this switch.

## Test Signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/events.go -->
