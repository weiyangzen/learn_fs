# sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.c

Purpose: generic PCI front-end for SOF DSP devices. It handles PCI enable/resource claiming, DMI topology/key quirks, firmware/topology override profiles, IPC-type selection, runtime PM completion, and delegation to the common SOF core.

Important APIs/functions: `sof_pci_probe()` validates `sof_dev_desc` and ops from the PCI ID table, enables the PCI device with managed helpers, requests BAR regions, stores subsystem IDs, selects IPC type from descriptor default or deprecated `ipc_type` module parameter, applies firmware/library/topology path overrides, applies community-key postfixed paths via DMI, applies DMI topology filename overrides, installs `sof_pci_probe_complete()`, and calls `snd_sof_device_probe()`. `sof_pci_remove()` removes the SOF core and restores PCI runtime PM usage count if probe completed. `sof_pci_shutdown()` forwards shutdown. `sof_pci_pm` exports common SOF PM callbacks.

Control flow/state: DMI callbacks update static globals `sof_dmi_override_tplg_name` and `sof_dmi_use_community_key`; these are process-global for the module. Runtime PM is forbidden by PCI initially and allowed only after successful probe completion unless `sof_pci_debug` disables runtime PM.

Dependencies/integration: depends on PCI managed resource APIs, DMI, Intel SOF ACPI matching helpers, common SOF device core, and `sof_dev_desc` instances supplied by per-platform PCI ID tables. Exports symbols in namespace `SND_SOC_SOF_PCI_DEV`.

Risks/test signals: static DMI state can persist across probes, so multi-device or reprobe scenarios need careful validation. Deprecated module parameters still affect path selection. Tests should cover DMI override matches, community key platforms, invalid IPC type, runtime PM disable flag, remove after partial probe failure, and subsystem ID propagation.
