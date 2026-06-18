## sources/distributed-fs/ceph-client/sound/hda/core/intel-dsp-config.c

Purpose: central policy engine that chooses the Intel audio DSP driver family for PCI and ACPI devices: legacy HDA, SST, SOF, AVS, or any available implementation. The decision combines module override, PCI class, platform IDs, build-time Kconfig, DMI quirks, ACPI codec HIDs, NHLT, DMIC, and SoundWire discovery.

Important APIs, types, and functions: `dsp_driver` module parameter, `struct config_entry`, `config_table[]`, `acpi_config_table[]`, `snd_intel_dsp_driver_probe()`, `snd_intel_acpi_dsp_driver_probe()`, `snd_intel_dsp_find_config()`, `snd_intel_dsp_check_dmic()`, and `snd_intel_dsp_check_soundwire()`.

Control flow: PCI probing rejects non-Intel devices and old devices without PCI DSP selection. A valid positive module override wins. Otherwise PCI class identifies legacy-only or DSP-capable hardware. The ordered config table then applies first-match semantics, including DMI and codec-HID checks. Conditional flags require DMIC or SoundWire evidence before SOF/SST is returned. ACPI probing uses a smaller HID table and disallows forcing legacy for ACPI DSP devices.

State and persistence: there is no persistent runtime state beyond the read-only module parameter. The large static tables encode policy and depend heavily on compile-time `IS_ENABLED()` branches.

Dependencies and integration points: depends on ACPI, DMI, PCI IDs, SoundWire ACPI scanning, `intel-nhlt` helpers, and ASoC ACPI codec matching. It imports the `SND_INTEL_SOUNDWIRE_ACPI` namespace.

Risks: order-sensitive tables can shadow later quirks. Missing or malformed NHLT/SoundWire firmware can fall back to legacy even when digital mics or codecs require DSP. Module override can force unsupported selections. New platforms require table updates in both PCI IDs and Kconfig guards.

Test signals: matrix boots across SKL/KBL/APL/GLK/CNL/CML/ICL/TGL/ADL/RPL/MTL/LNL/PTL/NVL classes; compare selected driver with `dmesg`; test `dsp_driver=` overrides; verify ES83xx codec HID plus valid SSP endpoint; test DMIC-only and SoundWire-only firmware.
