# sources/distributed-fs/ceph-client/kernel/trace/synth_event_gen_test.c

## Purpose

This test module exercises in-kernel synthetic event creation and generation APIs. It creates synthetic events through command-building and descriptor-array paths, enables them, emits test records through multiple tracing APIs, and removes them on module exit.

## Important APIs, Types, and Functions

It uses `synth_event_gen_cmd_start()`, `synth_event_add_field()`, `synth_event_gen_cmd_end()`, `synth_event_create()`, `trace_get_event_file()`, `trace_array_set_clr_event()`, `synth_event_trace_array()`, `synth_event_trace_start()`, `synth_event_add_next_val()`, `synth_event_add_val()`, `synth_event_trace_end()`, `synth_event_trace()`, `trace_put_event_file()`, and `synth_event_delete()`. Test functions are `test_gen_synth_cmd()`, `test_empty_synth_event()`, `test_create_synth_event()`, `test_add_next_synth_val()`, `test_add_synth_val()`, and `test_trace_synth_event()`.

## Control Flow

Module init creates `gen_synth_test` by starting a command with four fields and adding three more; creates `empty_synth_test` by starting empty and adding all fields; creates `create_synth_test` from a static descriptor array; enables each event; emits records using array, sequential-value, named-value, and variadic trace helpers; then disables events before returning. Error paths delete events already created and release event files. Module exit disables all events, puts event files, and deletes the synthetic events.

## State and Persistence Behavior

Static pointers hold the three `trace_event_file` references while the module is loaded. Synthetic event definitions exist in the tracing subsystem until deleted. The test values are transient trace records in the trace buffer.

## Dependencies and Integration Points

It depends on `linux/trace_events.h`, dynamic synthetic event APIs, module ownership (`THIS_MODULE`), top-level tracing instance access, and the synthetic event subsystem.

## Risks and Edge Cases

Init error cleanup is staged and must match the events already created. Exit assumes all three event pointers were successfully initialized, which is fine after successful module load but would be unsafe if partial init somehow reached exit. Events must be disabled before deletion. The values are intentionally bogus and include string pointers cast to `u64`, which is acceptable for this kernel API test but not general user input.

## Test Signals

Build with `CONFIG_SYNTH_EVENT_GEN_TEST`, insert the module, inspect the trace buffer for `create_synth_test`, `empty_synth_test`, and `gen_synth_test`, verify named/sequential/array emission, remove the module, and confirm synthetic events are deleted.
