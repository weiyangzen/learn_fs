# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-kunit-tests.c

## Purpose
This is a small KUnit test file for CoreSight framework behavior. It currently verifies default sink discovery across a simple source-to-helper topology.

## Important APIs, Types, And Functions
`coresight_test_device()` allocates a minimal `struct coresight_device` and `struct coresight_platform_data` from a KUnit device. `test_default_sink()` creates four synthetic devices: a bus source, an ETF linksink buffer, an ETR sysmem sink, and a CATU helper. It connects them with `coresight_add_out_conn()` and asserts that `coresight_find_default_sink(src)` returns the ETR rather than the intermediate ETF or helper.

## Control Flow And State
The test registers a KUnit device, constructs fake CoreSight devices in memory, assigns enough type/subtype metadata for sink search, and creates output connections in source order. No hardware is touched, no runtime PM is involved, and all allocations are device-managed under KUnit lifetime. The expected search flow is source to ETF to ETR, with the helper hanging off ETR but not changing the sink choice.

## Dependencies And Integration Points
The test includes `linux/coresight.h` and `coresight-priv.h`, and exercises exported framework connection and sink-selection helpers. It is registered via `kunit_test_suites()` under suite name `coresight_test_suite`.

## Risks And Test Signals
Coverage is intentionally narrow. It does not verify cycles, multiple sinks, per-CPU TRBE preference, disabled devices, missing `pdata`, or failure allocation paths. Its value is as a regression signal for default sink semantics, especially ensuring helper devices do not become selected sinks and that intermediate link-sinks do not mask a downstream sysmem sink when the source subtype is not `SOURCE_PROC`.
