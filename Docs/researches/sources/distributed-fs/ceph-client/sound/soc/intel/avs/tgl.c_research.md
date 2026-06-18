# sources/distributed-fs/ceph-client/sound/soc/intel/avs/tgl.c

Purpose: Defines Tiger Lake platform DSP operations, limiting generic core controls to the main core and configuring base firmware with crystal frequency and bus hardware ID.

Important APIs/functions: Main-core wrappers `avs_tgl_dsp_core_power()`, `avs_tgl_dsp_core_reset()`, `avs_tgl_dsp_core_stall()`, firmware config helpers `avs_tgl_set_xtal_freq()` and `avs_tgl_config_basefw()`, and `avs_tgl_dsp_ops`.

Control flow: Core wrappers mask to `AVS_MAIN_CORE_MASK` before calling generic operations. Base firmware config reads CPUID leaf 0x15 ECX when available and sends `AVS_FW_CFG_XTAL_FREQ_HZ`; then sends PCI device/subsystem/revision as `AVS_FW_CFG_BUS_HARDWARE_ID`.

State and persistence: Writes firmware runtime configuration; reads PCI IDs and CPU CPUID. No long-lived local state.

Dependencies and integration: Uses PCI device data from `adev->base.pci`, CPUID helpers, firmware config IPC, CNL interrupt handling, ICL firmware loading/logging/D0ix helpers, and HDA library/module transfer helpers.

Risks: CPUID frequency may be absent; code intentionally treats that as success. Hardware ID packing combines subsystem vendor/device into one word and is firmware ABI-sensitive. Only main core operations are forwarded.

Test signals: TGL boot firmware config IPCs, CPUID-present and CPUID-absent systems, PCI ID correctness, D0ix behavior, and firmware load/library/module transfer.
