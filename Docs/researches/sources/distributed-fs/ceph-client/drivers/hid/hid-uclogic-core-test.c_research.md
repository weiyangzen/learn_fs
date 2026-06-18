# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core-test.c

Purpose: KUnit coverage for UC-Logic raw event hook matching, compiled into `hid-uclogic-core.c` when `CONFIG_HID_KUNIT_TEST` is enabled.

Important APIs, types, and functions: `struct uclogic_raw_event_hook_test` describes a byte event, its size, and expected match result. `hook_events[]` are the registered hooks; `test_events[]` cover exact matches and mismatches by size, trailing bytes, and ordering. `fake_work()` is a no-op scheduled work target. `hid_test_uclogic_exec_event_hook_test()` allocates a synthetic `uclogic_params.event_hooks` list with KUnit memory, initializes each `uclogic_raw_event_hook`, then calls the otherwise-static `uclogic_exec_event_hook()`.

Control flow: test setup creates the hook list, appends two work items, then iterates over test events and asserts that the boolean return equals expectation. The work item can be scheduled for matching events, but no behavior is asserted beyond match detection.

State and persistence: all state is KUnit-managed heap data scoped to the test. Work structs use a no-op function, so persistent effects are absent.

Dependencies and integration: depends on KUnit and `hid-uclogic-params.h`; included directly from the core C file to access static symbols.

Risks: the test validates exact byte/size matching but not work completion, cancellation, or cleanup interactions. It is useful for preventing accidental prefix/substring matching regressions.

Test signals: this file is itself the test signal. Run the `hid_uclogic_core_test` KUnit suite with HID KUnit enabled.
