# Research: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts_test.go

Purpose: tests host-file build, append, delete, update, concurrency, and benchmark behavior for the `etchosts` package. Important tests include `TestBuildDefault`, `TestBuildNoIPv6`, `TestUpdate`, prefix-regression tests for update/delete, `TestAdd`, `TestDelete`, `TestConcurrentWrites`, and `BenchmarkDelete`.

Control flow: tests use temporary files, compare exact default output ordering, verify IPv6 exclusion, update FQDN/short hostname records, ensure names with shared prefixes are not modified or removed, append and delete records, tolerate empty inputs and blank lines, and run concurrent add/delete loops through an errgroup. The benchmark builds a large host file and deletes selected records.

State/dependencies: tests exercise real file persistence and package path locks. Dependencies include `netip`, temp files, errgroup, and `gotest.tools`. Risks covered include ordering regressions, exact-match deletion, concurrent write corruption, and the historical hostname-prefix bug. Gaps include malformed file content beyond fuzzing, lock cache cleanup through `Drop`, and Windows path behavior.
