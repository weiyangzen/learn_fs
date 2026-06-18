# sources/distributed-fs/ceph-client/drivers/input/apm-power.c

## Purpose

`apm-power.c` is a small input handler that bridges input power events to APM emulation. It listens for `EV_PWR` events and converts `KEY_SUSPEND` key-down events into `APM_USER_SUSPEND` requests.

## Important APIs, Types, and Functions

`system_power_event()` maps keycodes to APM actions. `apmpower_event()` filters input events to key-down power events. `apmpower_connect()` allocates and registers an `input_handle` and opens matching devices. `apmpower_disconnect()` closes and frees the handle. `apmpower_ids` matches devices advertising `EV_PWR`. `apmpower_handler` registers the handler with input core through `input_register_handler()` and `input_unregister_handler()`.

## Control Flow

On module load, `apmpower_init()` registers the input handler. Input core calls `apmpower_connect()` for matching devices, which registers a handle and opens the device. During event delivery, only value `1` key-down events are processed; `EV_PWR` plus `KEY_SUSPEND` queues an APM user suspend event and logs the request. On disconnect or module exit, handles are closed/unregistered and the handler is removed.

## State and Persistence Behavior

The module has no global mutable driver state beyond the registered `input_handler`. Per-device state is a heap `input_handle` owned from connect until disconnect. Suspend requests are queued into the APM emulation subsystem; this file does not persist policy state.

## Dependencies and Integration Points

It depends on input core, APM emulation, PM headers, and module infrastructure. It is selected by `CONFIG_INPUT_APMPOWER`, which depends on `INPUT` and `APM_EMULATION`, and is built by `drivers/input/Makefile` as `apm-power.o`.

## Risks and Edge Cases

The driver intentionally bypasses userspace policy for suspend key events, so enabling it can surprise systems that expect desktop/session-manager handling. It only handles `KEY_SUSPEND`; other power keys are ignored. It only reacts to key-down value `1`, not repeats or releases. Connect error paths must unregister and free the handle correctly, which the code does.

## Test Signals

Tests should cover module load/unload, matching an input device with `EV_PWR`, connect/open failure paths, synthetic `KEY_SUSPEND` down/repeat/up events, verification that exactly key-down queues `APM_USER_SUSPEND`, non-suspend power keys being ignored, and disconnect cleanup under input device removal.
