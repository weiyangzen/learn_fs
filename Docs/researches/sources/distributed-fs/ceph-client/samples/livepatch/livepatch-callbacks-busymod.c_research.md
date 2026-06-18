# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-busymod.c

Purpose: support module for livepatch callback demonstrations; provides a delayed-work function that can be patched and can intentionally stall transitions.

Important APIs/functions: module parameter `sleep_secs`, `DECLARE_DELAYED_WORK`, `schedule_delayed_work`, `cancel_delayed_work_sync`, `msleep`, and `busymod_work_func`.

Control flow: init schedules work immediately. The work function logs, sleeps for the configured seconds, and exits. Exit cancels the delayed work synchronously.

State and persistence: global delayed work and parameter while loaded.

Dependencies and integration: livepatch callback demo targets `busymod_work_func` in this module.

Risks: long `sleep_secs` deliberately parks execution in a patch target and can stall livepatch transitions.

Test signals: load with `sleep_secs=30`, load `livepatch-callbacks-demo.ko`, and observe callback/transition behavior in logs.
