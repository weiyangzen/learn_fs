# sources/cloud-native/cri-o/server/metrics/metrics_test.go

Purpose: Ginkgo suite for small metrics helper behavior.

Important APIs and functions: `TestMetrics` registers the suite, framework setup/teardown, and specs for `metrics.SinceInMicroseconds`.

Control flow: compares elapsed microseconds for a time one millisecond in the past and for `time.Now()`.

State and persistence: no metrics registry or server endpoint state is created by these tests.

Dependencies and integration: Ginkgo/Gomega, CRI-O test framework, Go time package, metrics package.

Risks: test coverage is narrow and does not exercise metric registration, endpoint startup, TLS, unix sockets, or mutator label behavior.

Test signals: confirms the helper returns non-zero for elapsed time and zero for immediate timestamps at microsecond resolution.
