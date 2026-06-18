# sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_chassis.c

Purpose: integrates PA-RISC firmware chassis-code reporting with boot, panic, reboot, warning, and optional LCD/LED status paths.

Important state and functions include boot parameter `pdcchassis=`, `pdc_chassis_enabled`, panic and reboot notifier blocks, `parisc_pdc_chassis_init`, `pdc_chassis_send_status`, optional `pdc_chassis_warn_show`, and `pdc_chassis_create_procfs`. The firmware-facing calls are `pdc_pat_chassis_send_log`, `pdc_chassis_disp`, and `pdc_chassis_warn`.

Control flow during boot registers panic and reboot notifiers when `CONFIG_PDC_CHASSIS` is enabled and the boot parameter has not disabled support. `pdc_chassis_send_status` maps generic direct messages such as boot start, boot complete, shutdown, panic, LPMC, and HPMC to either 64-bit PDC PAT message/state pairs or 32-bit legacy chassis display codes. After a successful status update it refreshes LCD text when LCD/LED support is enabled. With chassis warnings enabled, init probes firmware warning support and creates `/proc/chassis`; reads decode component, battery, and temperature warning bits.

State persists mostly in firmware-visible chassis logs, front-panel display/LED state, registered notifier chains, and procfs. Dependencies include PDC/PDC_PAT firmware APIs, panic and reboot notifier infrastructure, processor/PAT detection, procfs seq files, and LCD/LED integration.

Risks include firmware support variability, returning `-1` for unsupported messages or platform mode, making firmware calls in panic context, config-dependent behavior divergence between 32-bit and 64-bit kernels, and warning-bit interpretation across machine families. Test signals are boot logs enabling chassis support, visible front-panel state changes for boot and shutdown, panic/reboot notifier invocation, `/proc/chassis` contents on supported systems, and graceful "not supported" behavior on machines without the firmware option.
