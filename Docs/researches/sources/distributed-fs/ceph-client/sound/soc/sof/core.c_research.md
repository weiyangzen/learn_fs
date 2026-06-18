# sources/distributed-fs/ceph-client/sound/soc/sof/core.c

Purpose: main SOF core device lifecycle: module overrides, firmware state tracking, machine selection, IPC/path profile selection, ops validation, DSP probe/boot, client/machine/component registration, remove/shutdown, and panic stack printing.

Important APIs/types/functions: module params override firmware/topology/lib paths and IPC type. `sof_debug_check_flag()`, `sof_print_oops_and_stack()`, and `sof_set_fw_state()` are exported helpers. Key lifecycle functions are `snd_sof_device_probe()`, `sof_probe_continue()`, `snd_sof_device_remove()`, `snd_sof_device_shutdown()`, `sof_machine_register()`, and `sof_machine_unregister()`. Internal helpers include `sof_machine_check()`, `sof_select_ipc_and_paths()`, `validate_sof_ops()`, `sof_init_sof_ops()`, and `sof_init_environment()`.

Control flow: device probe allocates `snd_sof_dev`, initializes lists/locks/timeouts, applies module overrides, initializes ops for the selected IPC type, runs early probe, and either schedules or directly runs `sof_probe_continue()`. Continue probes hardware, selects machine, resolves firmware/topology profile, creates platform driver, initializes debug/IPC, loads firmware, runs firmware, optionally starts trace, registers ASoC component/DAIs, registers machine and clients, and marks probe complete. Error unwind frees trace, firmware, IPC, debug, hardware, late resources, ops, and resets boot state. Remove cancels work, unregisters clients and machine, releases retained-D3 prevention, powers down/notifies DSP when booted, frees resources, and unloads firmware.

State and persistence: `snd_sof_dev` owns firmware state, power state, lists for PCM/widgets/routes/clients, locks, IPC object, debugfs, firmware profile paths, first-boot/probe-complete flags, and PM/debug flags. Machine selection mutates `snd_sof_pdata`.

Dependencies and integration points: ALSA SoC, SOF IPC/loader/PM/debug/topology subsystems, PCI/OF/ACPI platform descriptors, runtime PM, tracepoints, client framework, and firmware profile logic in `fw-file-profile.c`.

Risks: probe has a long multi-stage unwind path. IPC fallback can require ops reinitialization after hardware probe. Forced nocodec and DSPless debug modes alter normal machine/DSP behavior. Workqueue probing cannot propagate errors except logs. State transitions must stay synchronized with client notifications.

Test signals: probe/remove/shutdown on all bus types, firmware boot failure paths, machine selection/nocodec fallback, IPC override/fallback, runtime PM, client registration, and panic/oops logging.
