<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/Makefile

## Purpose
Kbuild recipe for Intel ASoC ACPI machine-match support objects and the separate SDCA quirk helper module.

## APIs, Types, and Functions
Builds `snd-soc-acpi-intel-match-y` from per-generation match tables (`byt`, `cht`, `hsw-bdw`, `skl`, `kbl`, `bxt`, `glk`, `cnl`, `cfl`, `cml`, `icl`, `tgl`, `ehl`, `jsl`, `adl`, `rpl`, `mtl`, `arl`, `lnl`, `ptl`, `nvl`, `hda`), SoundWire mockup tables, SSP common helpers, and `sof-function-topology-lib.o`. Builds `snd-soc-acpi-intel-sdca-quirks-y` from `soc-acpi-intel-sdca-quirks.o`.

## Control Flow, State, and Persistence
No runtime state is held here. Object inclusion controls which exported match arrays and helper symbols are available when `CONFIG_SND_SOC_ACPI_INTEL_MATCH` or `CONFIG_SND_SOC_ACPI_INTEL_SDCA_QUIRKS` is enabled.

## Dependencies and Integration
Integrated by the Linux ASoC Intel common Kbuild. The match object is consumed by Intel SOF/SST/HDA selection code via exported `snd_soc_acpi_intel_*` arrays; the SDCA quirk object exports a namespaced helper used by newer SoundWire match tables.

## Risks and Test Signals
Risks include omitting a generation object from the aggregate, building tables that reference helper symbols not included in the same object, or enabling SDCA machine checks without the quirk module. Test signals are allmodconfig/allyesconfig builds, modpost exported-symbol validation, and probe-time availability of expected generation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/Makefile -->
