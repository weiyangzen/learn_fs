# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_defaults.go

Purpose: production default retry budget for resource cleanup callbacks.

Important APIs/types/functions: package variable `defaultRetryTimes = 20`.

Control flow: `retry` in `resourcecleaner.go` reads this value when constructing exponential backoff.

State and persistence behavior: mutable package-level variable in production builds, though intended as a constant-like default.

Dependencies and integration points: selected by `//go:build !test`; overridden by `resourcecleaner_test_inject.go` in test builds.

Risks: as a variable, in-package code could modify it. Production cleanup can take a long time because each callback has 20 exponential-backoff steps starting at 500 ms.

Test signals: paired test build file lowers retries to make failure tests fast.
