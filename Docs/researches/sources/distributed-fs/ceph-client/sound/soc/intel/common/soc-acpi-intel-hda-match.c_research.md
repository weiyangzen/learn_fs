<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hda-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hda-match.c

## Purpose
Generic HDA DSP machine-match table for Intel platforms using the `skl_hda_dsp_generic` machine driver.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_hda_machines[]` with a wildcard-style entry using `drv_name = "skl_hda_dsp_generic"` and topology prefix `sof-hda-generic`; `SND_SOC_ACPI_TPLG_INTEL_DMIC_NUMBER` controls runtime topology suffix generation.

## Control Flow, State, and Persistence
No runtime state exists. The entry provides generic machine data when platform selection chooses HDA DSP instead of a codec-specific SSP/SoundWire machine.

## Dependencies and Integration
Depends on ASoC ACPI Intel match helpers. Consumed by Intel DSP configuration paths that fall back to HDA generic SOF topology selection.

## Risks and Test Signals
Risks include overly broad matching when a board-specific topology is required, incorrect DMIC-count suffix generation, and topology mismatch for systems with unusual HDMI/DMIC arrangements. Test signals are generic HDA SOF probe, topology filename selection for 0/2/4 DMIC variants, and HDMI/analog/DMIC stream validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hda-match.c -->
