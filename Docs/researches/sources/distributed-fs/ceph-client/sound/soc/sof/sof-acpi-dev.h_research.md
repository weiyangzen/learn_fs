# sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.h

Purpose: Declares the shared SOF ACPI PM/probe/remove interface.

Important APIs: `extern const struct dev_pm_ops sof_acpi_pm`, `sof_acpi_probe(struct platform_device *, const struct sof_dev_desc *)`, and `sof_acpi_remove(struct platform_device *)`.

Control flow and integration: ACPI platform drivers include this header to delegate common SOF setup/teardown and to attach the shared PM ops table.

State and persistence: No state. The implementation stores runtime state in `snd_sof_pdata` and SOF device data.

Risks: Header depends on callers having platform device and descriptor types visible through other includes. Namespace export in the C file means module users must import `SND_SOC_SOF_ACPI_DEV`.

Test signals: Compile/link of ACPI platform drivers and module namespace import checks.
