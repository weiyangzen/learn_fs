# sources/cloud-native/containers-storage/pkg/parsers/parsers_test.go

Purpose: tests generic parsers from `parsers.go`.

Important APIs, types, and functions: `TestParseKeyValueOpt` and `TestParseUintList`.

Control flow: key/value tests check invalid missing-separator inputs and valid trimming/value-preserving cases. uint-list tests compare returned maps for singles, ranges, duplicates, leading zeros, and order variations, then assert malformed strings fail.

State and persistence: no state or persistence.

Dependencies and integration points: depends on `reflect` and `testing`. It protects parsing behavior expected by cgroup-style callers.

Risks and edge cases: map comparison ignores ordering, as intended. Tests do not include extremely large ranges or integer overflow.

Test signals: confirms accepted grammar and exact error behavior for common invalid forms.
