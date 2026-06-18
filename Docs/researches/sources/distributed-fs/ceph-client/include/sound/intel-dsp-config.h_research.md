# sources/distributed-fs/ceph-client/include/sound/intel-dsp-config.h

Source read summary: 42 lines, Intel audio DSP driver selection interface.

Purpose: declares the policy API that selects between legacy HDA, SST, SOF, and AVS drivers for Intel PCI or ACPI audio devices.

Important APIs, types, and functions: enum values are `SND_INTEL_DSP_DRIVER_ANY`, `LEGACY`, `SST`, `SOF`, `AVS`, and `LAST`. Enabled builds expose `snd_intel_dsp_driver_probe()` for PCI and `snd_intel_acpi_dsp_driver_probe()` for ACPI HID devices. Disabled builds return `ANY`.

Control flow: Intel audio probe code asks this helper which driver family should bind before committing to a legacy or DSP stack.

State and persistence behavior: no state is stored in this header; implementation policy may inspect DMI, PCI IDs, ACPI, NHLT, and module parameters at runtime.

Dependencies and integration points: forward declares `pci_dev` and uses ACPI ID length via included environment. It gates HDA/SST/SOF/AVS driver integration.

Risks and edge cases: wrong selection can bind the wrong audio stack and break topology firmware loading or DMIC support; disabled config returns permissive `ANY`.

Test signals: platform matrix across Intel generations, ACPI HID matching, module override behavior, SOF/SST/AVS/legacy fallback, and compile without `CONFIG_SND_INTEL_DSP_CONFIG`.
