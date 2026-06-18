# sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.c

Purpose: Provides common ACPI platform-device probe/remove and PM ops for SOF ACPI drivers.

Important APIs/state: Exports namespace PM ops `sof_acpi_pm` with SOF system and runtime PM callbacks. Module params `fw_path` and `tplg_path` are deprecated overrides forwarded into `ipc_file_profile_base`; `sof_acpi_debug` can disable runtime PM with `SOF_ACPI_DISABLE_PM_RUNTIME`. `sof_acpi_probe()` allocates `snd_sof_pdata`, validates descriptor ops, sets descriptor/device/default IPC profile paths, installs a probe-complete callback, and calls `snd_sof_device_probe()`. `sof_acpi_remove()` disables runtime PM unless debug-disabled and removes the SOF device.

Control flow: Successful core probe calls `sof_acpi_probe_complete()`, which configures autosuspend delay, enables autosuspend, and enables runtime PM unless disabled by debug flag.

Dependencies and integration: Used by ACPI-specific SOF platform modules with matching descriptors. Depends on SOF core device probe/remove, ACPI PM, runtime PM, Intel ACPI matching headers, and platform descriptors.

Risks: Deprecated module params still affect firmware/topology path selection. Runtime PM disable debug flag changes power behavior and can mask suspend bugs. Probe fails if descriptor lacks ops before reaching SOF core validation.

Test signals: ACPI probe with valid/invalid desc, runtime PM enable/disable flag, deprecated path overrides, remove after partial probe, and system/runtime PM callback invocation.
