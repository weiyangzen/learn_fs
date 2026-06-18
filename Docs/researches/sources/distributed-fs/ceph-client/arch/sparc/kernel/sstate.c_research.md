# sources/distributed-fs/ceph-client/arch/sparc/kernel/sstate.c

Purpose: reports Linux soft-state transitions to sun4v hypervisors that support the soft-state API.

Important APIs/types/functions: `do_set_sstate()`, `sstate_reboot_call()`, `sstate_panic_event()`, `sstate_init()`, and `sstate_running()` use `sun4v_hvapi_register()`, `sun4v_mach_set_soft_state()`, `prom_sun4v_guest_soft_state()`, reboot notifiers, and the panic notifier chain.

Control flow: `core_initcall` verifies `tlb_type == hypervisor`, registers HV group `HV_GRP_SOFT_STATE` v1.0, marks support, tells PROM the guest participates, sets "Linux booting", and registers panic/reboot hooks. `late_initcall` moves to normal/running state. Reboot and panic paths set transition state with aligned static message strings.

State and persistence: `hv_supports_soft_state` gates calls; messages are static 32-byte aligned constants. State is externally visible to firmware/hypervisor but not persisted by Linux.

Dependencies and integration points: integrates with sun4v hypervisor APIs, reboot/panic notifier ordering, image virtual-to-real address conversion, and PROM soft-state awareness.

Risks: notifier paths can run during failure; calls must tolerate hypervisor errors. Message buffers must remain static and real-address convertible. Non-sun4v systems must be no-ops.

Test signals: sun4v boot should show hypervisor soft state progressing through booting/running; reboot, halt, poweroff, and panic should set transition messages; non-hypervisor boot should not call the API.
