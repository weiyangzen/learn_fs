<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/shim.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/shim.h

## Purpose
Shared Intel SOF shim and descriptor header for older Atom/Baytrail/Broadwell-style DSP register definitions plus the common Intel DSP hardware descriptor used by HDA and non-HDA platform code.

## Important APIs, Types, and Functions
Defines `enum sof_intel_hw_ip_version`, SHIM register offsets (`SHIM_CSR`, `SHIM_IMRX`, `SHIM_IPCX`, etc.), SHIM bit fields for CSR/interrupt/IPC/clock/HMDC registers, audio DSP PCI register offsets and power-management bits, `SOF_INTEL_PROCEN_FMT_QUIRK`, `struct sof_intel_dsp_desc`, `struct sof_intel_stream`, extern declarations for Tangier ops/chip info, and `get_chip_info()`.

## Control Flow, State, and Persistence
No executable control flow except inline `get_chip_info()`, which returns `pdata->desc->chip_info`. The header defines layout for persistent platform metadata consumed throughout Intel SOF probe, boot, IPC, SoundWire, power-management, and debug paths. Descriptor callbacks encode hardware-specific behavior such as IPC IRQ checks, SoundWire IRQ processing, DSP power-down, interrupt disable, and code-loader initialization.

## Dependencies and Integration
Included by Atom/Tangier and other Intel SOF files. It integrates platform descriptors with generic SOF device descriptors, SHIM MMIO accessors, PCI PM register programming, SoundWire handling, HDA boot paths, and per-platform hardware IP version selection.

## Risks and Test Signals
Risks are ABI-like: register offsets and bit meanings must match the platform generation, and `sof_intel_dsp_desc` fields must be filled consistently by each platform file. Test signals are compile coverage across Intel platform modules, successful SHIM IPC interrupt mask/unmask, correct PCI power bits on legacy platforms, and platform descriptors reporting the expected core count, IPC registers, SoundWire bases, and hardware IP version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/shim.h -->
