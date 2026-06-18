# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.h

Purpose: declares the hotplug core interface used by i915 display initialization, interrupt handling, polling, encoder code, and debugfs setup.

Important APIs/types/functions: exposes HPD lifecycle (`intel_hpd_init_early()`, `intel_hpd_init()`, `intel_hpd_cancel_work()`), polling control (`intel_hpd_poll_enable()`, `intel_hpd_poll_disable()`, `intel_hpd_poll_fini()`), event entry points (`intel_hpd_irq_handler()`, `intel_hpd_trigger_irq()`, `intel_encoder_hotplug()`), pin mapping (`intel_hpd_pin_default()`), block/unblock APIs, detection work enable/disable/schedule, and `intel_hpd_debugfs_register()`.

Control flow: callers initialize work structures early, enable IRQ-backed HPD after interrupt hardware is ready, route decoded IRQ masks into `intel_hpd_irq_handler()`, and use polling or blocking helpers around runtime PM, Type-C mode changes, and sensitive AUX transactions.

State and persistence behavior: the header owns no state, but its APIs operate on `struct intel_display`, `struct intel_encoder`, `struct intel_connector`, and `struct intel_digital_port` hotplug fields.

Dependencies and integration points: provides the contract between `intel_hotplug.c`, `intel_hotplug_irq.c`, display bringup/teardown, DP/Type-C code, connector probing, and debugfs.

Risks: API callers must pair `intel_hpd_block()` with an unblock variant and must not assume `intel_hpd_schedule_detection()` succeeds when detection work is disabled. Incorrect initialization order can leave work items uninitialized or IRQs enabled before the generic state is ready.

Test signals: build coverage for all prototypes, driver load/unload, suspend/resume HPD polling, manual HPD trigger through DP helpers, and block/unblock paths.
