# sources/distributed-fs/ceph-client/sound/soc/sof/amd/Kconfig

Purpose: AMD SOF platform configuration for Renoir, Vangogh, Rembrandt, ACP6.3, ACP7.0/7.1, common ACP support, probes, and SoundWire integration.

Important APIs/types/functions: `SND_SOC_SOF_AMD_COMMON` selects core SOF, IPC3, PCI device glue, AMD ACP config, Xtensa support, ACP probes, and ACPI match helpers. Per-platform symbols select the common layer. SoundWire baseline/support symbols select AMD SoundWire ACPI integration when available.

Control flow: `SND_SOC_SOF_AMD_TOPLEVEL` gates all AMD platform options and depends on X86 or compile-test. Per-platform PCI options depend on `SND_SOC_SOF_PCI` and `AMD_NODE`, then select common support. ACP63/ACP70 additionally select SoundWire link baseline.

State and persistence: build-time symbols only.

Dependencies and integration points: integrates with AMD ACP machine selection, PCI probing, ACPI machine tables, SoundWire, Xtensa DSP architecture support, and SOF debug probes.

Risks: the toplevel `depends on SOUNDWIRE_AMD || !SOUNDWIRE_AMD` keeps visibility independent of SoundWire but can hide missing runtime SoundWire coverage until specific symbols are selected. ACP probes are always selected by common support, so probe-client build dependencies must stay healthy.

Test signals: platform-specific module builds and PCI probe tests across revisions `ACP_RN_PCI_ID`, `ACP_VANGOGH_PCI_ID`, `ACP_RMB_PCI_ID`, `ACP63_PCI_ID`, and ACP70+.
