# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test_inject.go

Purpose: test-only override of resource cleanup retry count.

Important APIs/types/functions: `defaultRetryTimes = 3` under `//go:build test`.

Control flow: selected at compile time instead of the production defaults file; `retry` uses this smaller value automatically.

State and persistence behavior: package variable only; no persistence.

Dependencies and integration points: integrates with `resourcecleaner_test.go` to keep retry tests bounded.

Risks: tests must run with the intended build tag or retry expectations and timing change.

Test signals: supports the assertion that an always-failing cleanup function is invoked three times.
