# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params-test.c

Purpose: KUnit tests for UC-Logic parameter parsing and event-hook cleanup helpers compiled into `hid-uclogic-params.c` with HID KUnit enabled.

Important APIs, types, and functions: `struct uclogic_parse_ugee_v2_desc_case` parameterizes expected parse result, string descriptor bytes, descriptor parameters, and frame type. `hid_test_uclogic_parse_ugee_v2_desc()` calls `uclogic_params_parse_ugee_v2_desc()` and checks X/Y logical maxima, physical maxima, pressure max, button count, and frame type. `hid_test_uclogic_params_cleanup_event_hooks()` uses a fake HID device/drvdata to initialize UGEE v2 event hooks, then calls `uclogic_params_cleanup_event_hooks()` repeatedly to assert idempotence.

Control flow: KUnit array params run invalid, zero-resolution, buttons, dial, and mouse cases. The cleanup test allocates fake state, invokes the real hook initializer, then verifies repeated cleanup leaves `p.event_hooks == NULL`.

State and persistence: all allocations are KUnit-scoped except the production helper allocations, which the cleanup path frees. No persistent data.

Dependencies and integration: depends on KUnit, `hid-uclogic-params.h`, and `hid-uclogic-rdesc.h`; included directly from the params C file to access static helpers.

Risks: parse tests cover the 12-byte form but not the 14-byte XP-PEN Pro extension except indirectly through production code. Cleanup idempotence is tested, but allocation-failure paths and work cancellation timing are not deeply exercised.

Test signals: run the `hid_uclogic_params_test` KUnit suite. Failures indicate descriptor parsing, frame classification, or hook cleanup regressions.
