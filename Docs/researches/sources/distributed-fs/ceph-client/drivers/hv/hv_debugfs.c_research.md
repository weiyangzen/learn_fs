<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_debugfs.c

## Purpose

`hv_debugfs.c` creates a Hyper-V debugfs hierarchy used to inject artificial delays into VMBus channel interrupt and message paths for fuzzing and timing tests. It also exposes a per-device boolean that enables or disables these delay injections.

## Important APIs, Types, and Functions

- `hv_debug_init()` creates the top-level `hyperv` debugfs directory.
- `hv_debug_add_dev_dir()` creates a per-device directory plus `fuzz_test_state` and `delay/` files.
- `hv_debug_rm_dev_dir()` and `hv_debug_rm_all_dir()` remove per-device or all Hyper-V debugfs entries.
- `hv_debug_delay_test()` is the runtime hook called from event/message paths to apply configured microsecond delays.
- `hv_debugfs_delay_get/set()` and `hv_debugfs_state_get/set()` implement bounded debugfs accessors.

## Control Flow

When a VMBus device is added, `hv_debug_add_dev_dir()` creates `hyperv/<device>/`, adds `fuzz_test_state`, creates a `delay` child directory, and adds `fuzz_test_buffer_interrupt_delay` and `fuzz_test_message_delay`. Delay writes are accepted only up to 1000 microseconds; state writes accept only 0 or 1. Runtime code calls `hv_debug_delay_test(channel, delay_type)`, which maps a sub-channel back to its primary channel, checks `fuzz_testing_state`, and applies the interrupt or message `udelay()`.

## State and Persistence Behavior

The global `hv_debug_root` dentry persists until `hv_debug_rm_all_dir()`. Each `hv_device` stores its debugfs directory in `dev->debug_dir`. The actual delay and enable state live in `struct vmbus_channel` fields, so settings follow channel lifetime. There is no persistent storage beyond debugfs runtime state.

## Dependencies and Integration Points

This file depends on debugfs, VMBus channel structures from `hyperv_vmbus.h`, and delay hooks in the VMBus event/message path. It is optional test infrastructure and has no direct host protocol role.

## Risks and Edge Cases

The code relies on debugfs helpers and generally treats `IS_ERR()` as the failure check. If debugfs is disabled or unavailable, callers must tolerate missing entries. Artificial delays run in sensitive interrupt/tasklet-related paths and can perturb timing significantly, though they are capped at 1000 microseconds. Sub-channels share primary-channel fuzz settings.

## Test Signals

Check debugfs directory creation/removal for device add/remove, input validation for delay and state files, sub-channel inheritance of primary settings, no delay when disabled, and expected latency when interrupt or message delay is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_debugfs.c -->
