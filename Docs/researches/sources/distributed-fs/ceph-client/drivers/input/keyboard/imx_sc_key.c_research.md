## sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_sc_key.c

Purpose: i.MX System Controller single-key driver. It maps an SCU wake/button interrupt to a firmware-polled Linux key configured by `linux,keycodes`.

Important APIs/types/functions: `struct imx_key_drv_data` stores keycode, cached state, delayed work, input device, SCU IPC handle, and notifier. `imx_sc_key_probe()` gets the SCU handle, reads firmware properties, registers input, enables the SC wake IRQ group, and registers a notifier. `imx_sc_key_notify()` schedules debounce work; `imx_sc_check_for_events()` sends `IMX_SC_MISC_FUNC_GET_BUTTON_STATUS`.

Control flow: notifier fires only for `SC_IRQ_BUTTON` in `SC_IRQ_GROUP_WAKE`; it wakes the parent and schedules work after 30 ms. The worker performs an SCU RPC, masks the first response byte as button state, reports a transition, relaxes wakeup on release, and reschedules every 60 ms while pressed.

State/dependencies/integration: no persistent storage is used. Dependencies are the NXP SCU firmware IPC API, `imx_scu_irq_*` notifier group, delayed work, input core, and firmware property parsing. Cleanup is a devm action that disables the SCU IRQ group, unregisters the notifier, and cancels work.

Risks and test signals: the RPC response contains dirty upper bytes, so only the low byte is valid. Missing `linux,keycodes` is fatal. Test notification filtering, press/release polling, wakeup reference release, cleanup order, and firmware errors from `imx_scu_call_rpc()`.
