# sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_test.go

Purpose: unit tests for IRQ CPU mask math and irqbalance config file updates.

Important APIs/types/functions: tests `calcIRQSMPAffinityMask`, `updateIrqBalanceConfigFile`, plus helper functions `countLines`, `writeTempFile`, and `cpuSetOrDie`.

Control flow: table tests apply set/clear operations to masks and compare both affinity and inverted banned masks. Config-file test repeatedly updates the banned CPU line and verifies line count stays constant.

State and persistence behavior: uses temporary config files and removes them after tests.

Dependencies and integration points: uses Ginkgo/Gomega, bufio/os, and cpuset parsing.

Risks: tests do not cover non-ASCII mask input, too-short masks for high CPU indexes, or complex shell config syntax.

Test signals: catches endian/padding regressions and unbounded growth of irqbalance config files.
