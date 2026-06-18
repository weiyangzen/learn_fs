# sources/distributed-fs/ceph-client/kernel/trace/kprobe_event_gen_test.c

## Purpose

`kprobe_event_gen_test.c` is a loadable test module for the in-kernel kprobe event generation API. It programmatically creates one kprobe event and one kretprobe event against `do_sys_open`, enables them in the top-level tracing instance, and deletes them on module removal. It is intended as a smoke/integration test for dynamic event command generation, not as production tracing logic.

## Important APIs, Types, and Functions

- Global event handles: `gen_kprobe_test` and `gen_kretprobe_test`, both `struct trace_event_file *`.
- Architecture-specific argument macros map `do_sys_open` arguments to register/stack expressions for x86, arm64, arm, and riscv; unsupported architectures pass `NULL` argument fields.
- `trace_event_file_is_valid()` checks `input && !IS_ERR(input)`.
- `test_gen_kprobe_cmd()` allocates a dynamic event command buffer, initializes `struct dynevent_cmd`, creates a `gen_kprobe_test` kprobe event, adds fields, obtains the event file, and enables the event.
- `test_gen_kretprobe_cmd()` does the same for `gen_kretprobe_test`, using `$retval`.
- `kprobe_event_gen_test_init()` runs both tests at module load.
- `kprobe_event_gen_test_exit()` disables events, drops event-file references, and deletes the generated events.

## Control Flow

On load, `kprobe_event_gen_test_init()` first calls `test_gen_kprobe_cmd()`. That routine allocates `MAX_DYNEVENT_CMD_LEN`, initializes the command with `kprobe_event_cmd_init()`, starts a command with `kprobe_event_gen_cmd_start()`, appends remaining fields via `kprobe_event_add_fields()`, finalizes with `kprobe_event_gen_cmd_end()`, looks up the event through `trace_get_event_file(NULL, "kprobes", "gen_kprobe_test")`, and enables it with `trace_array_set_clr_event()`. If any post-creation step fails, it releases references when necessary and deletes the event with `kprobe_event_delete()`.

The kretprobe path mirrors the kprobe path but uses `kretprobe_event_gen_cmd_start()` and `kretprobe_event_gen_cmd_end()` to create a return probe event with `$retval`. If kretprobe creation fails after the kprobe succeeded, the init path only attempts kretprobe cleanup; the kprobe remains active until module init returns failure handling by the module loader or later exit path, which is a subtle cleanup area to inspect if changing this module.

On unload, both events are disabled before deletion. This ordering matters because trace events cannot be removed while enabled. Each valid `trace_event_file` is returned with `trace_put_event_file()` before the dynamic event is deleted.

## State and Persistence Behavior

The module's persistent state is only the two event-file pointers and the dynamic events registered in the tracing subsystem. The command buffers are temporary and freed before returning. Event lifetime is tied to module lifetime: generated events appear under the `kprobes` event system while the module is loaded and should be removed by `rmmod`.

## Dependencies and Integration Points

This test depends on the dynamic event generator API in `<linux/trace_events.h>`, kprobe/kretprobe event support, trace event lookup/refcounting, and top-level trace-array event enable/disable. It is gated by `CONFIG_KPROBE_EVENT_GEN_TEST` and must be built as a module. It depends on architecture register naming for meaningful field extraction.

## Risks and Edge Cases

- `KPROBE_GEN_TEST_FUNC` is hard-coded to `do_sys_open`; if that symbol is renamed, absent, not probeable, or ABI-specific, module load fails.
- Unsupported architectures pass `NULL` argument fields, so the kprobe event may be less useful or API behavior may differ.
- Failure during the second test requires careful cleanup of the first event if this code is modified; as written, the module init returns the second failure after attempting kretprobe cleanup.
- Events must be disabled before deletion; skipping disable can make removal fail.
- `trace_event_file_is_valid()` treats `ERR_PTR` as invalid but cleanup paths also sometimes set globals to `NULL` only after failed setup.

## Test Signals

The documented manual test is: build with `CONFIG_KPROBE_EVENT_GEN_TEST`, insert `kernel/trace/kprobe_event_gen_test.ko`, open files to trigger `do_sys_open`, and inspect `/sys/kernel/tracing/trace` for repeated `gen_kprobe_test` and `gen_kretprobe_test` events. Removal with `rmmod` should disable and delete both events without warnings.
