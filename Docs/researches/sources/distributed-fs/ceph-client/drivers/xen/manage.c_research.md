# sources/distributed-fs/ceph-client/drivers/xen/manage.c

Purpose: handles Xen toolstack control requests for shutdown, reboot, suspend/resume, and sysrq through xenstore watches and reboot notifiers.

Important APIs/functions: exports `xen_resume_notifier_register` and `xen_setup_shutdown_event`. Main helpers are `shutdown_handler`, `setup_shutdown_watcher`, `do_poweroff`, `do_reboot`, and, with hibernate callbacks, `do_suspend` and `xen_suspend`.

Control flow: setup registers xenstore watches for `control/shutdown` and optionally `control/sysrq`, advertises supported features, and registers a reboot notifier. Shutdown watch reads the requested command in a xenbus transaction, acknowledges recognized commands by clearing the xenstore node, and dispatches to poweroff, reboot, or suspend handlers. Suspend freezes userspace and kernel threads, suspends devices and xenstore, runs a stop-machine section that suspends syscore, grant tables, runstate accounting, architecture state, and the hypervisor domain, then resumes grant tables, IRQs, timers, console, devices, xenstore, and processes.

State and persistence: global `shutting_down` suppresses duplicate requests. A raw notifier chain lets other Xen subsystems observe resume. Xenstore feature nodes persist while the guest runs.

Dependencies and integration: depends on xenbus, grant table suspend/resume, Xen event IRQ resume, Xen timers, hvc console, architecture suspend/resume hooks, freezer, device PM, syscore ops, stop_machine, reboot notifiers, and sysrq.

Risks: suspend requires strict ordering and CPU0 stop-machine execution; failed freeze/device/syscore steps must thaw and resume correctly; xenstore transaction retries can race toolstack updates; duplicate shutdowns are ignored while a transition is active; sysrq accepts single-byte commands from xenstore.

Test signals: issue xenstore poweroff, halt, reboot, suspend, and sysrq requests; test suspend cancellation and successful restore; inject failures in freeze/device suspend; verify resume notifier ordering, IRQ/timer restoration, and xenstore feature advertisement.
