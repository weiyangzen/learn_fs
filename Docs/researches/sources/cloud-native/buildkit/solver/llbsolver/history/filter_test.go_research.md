<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/filter_test.go

Purpose: validates build history filtering and limiting.

Important APIs and types: `TestHistoryFilters` creates three `BuildHistoryEvent` records with refs, frontend attrs, created/completed timestamps, then table-drives `filterHistoryEvents`.

Control flow: cases cover no match, ref prefix, repository inequality, repository parsed from git context, limit newest-first, invalid filter parsing, multi-field AND, relative completed/started time, duration, OR across filter strings, and no-filter limiting.

State and dependencies: test-only events based around `time.Now().Add(-24h)`. Dependencies include control API protobufs, testify, and timestamppb.

Integration points: protects `Queue.Listen` filtering behavior for CLI/API history requests.

Risks and test signals: good behavioral coverage for supported syntax. It does not cover `status` filters explicitly or RFC3339 absolute timestamps.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter_test.go -->
