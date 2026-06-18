# sources/distributed-fs/ceph-client/sound/soc/intel/Kconfig

Purpose: top-level Kconfig for Intel ASoC platform, DSP, ACPI match, codec, and board-driver support.

Important APIs/types/functions: exposes `SND_SOC_INTEL_SST_TOPLEVEL`, `SND_SOC_INTEL_CATPT`, `SND_SOC_INTEL_HASWELL`, `SND_SST_ATOM_HIFI2_PLATFORM`, PCI/ACPI Atom variants, `SND_SOC_ACPI_INTEL_MATCH`, `SND_SOC_ACPI_INTEL_SDCA_QUIRKS`, `SND_SOC_INTEL_KEEMBAY`, and `SND_SOC_INTEL_AVS`. It sources AVS boards and generic Intel boards Kconfig files.

Control flow: the SST toplevel boolean gates legacy SST/CATPT/Atom options. ACPI match helpers are available when either SST or SOF Intel toplevel is enabled. Keembay and AVS are independent platform options. Selected symbols pull in dependencies such as ACPI match helpers, DSP config, DMA, topology, HDA, and coredump support.

State and persistence: kernel configuration only; no runtime code.

Dependencies/integration: tightly integrated with the broader Intel ASoC tree, SOF top-level option, ACPI, PCI, X86, Keembay architecture, DMA, HDA, and board Kconfig files.

Risks: option interactions are subtle, especially Atom ACPI being mutually exclusive with SOF support as documented in help. Hidden symbols are selected by visible options and can affect build closure. `default y` on `SND_SOC_INTEL_SST_TOPLEVEL` changes menu exposure on X86/compile-test.

Test signals: kconfig dependency tests for X86, ACPI, PCI, SOF coexistence, Atom PCI/ACPI variants, AVS, Keembay, and sourced board menus.
