# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp.h

Purpose: shared AMD ACP SOF definitions: constants, register-related masks, data structures, exported prototypes, and per-platform ops symbols.

Important APIs/types/functions: defines stream limits, BAR index, poll/timeouts, reset/power masks, SRAM/PTE/base addresses, PCI/revision IDs, PSP mailbox constants, scratch box sizes, SoundWire IRQ/wake constants, `enum clock_source`, DMA descriptor structures, `scratch_ipc_conf`, `scratch_reg_conf`, `acp_dsp_stream`, `sof_amd_acp_desc`, `acp_quirk_entry`, and `acp_dev_data`. It declares all common ACP callbacks for probe, loader, IPC, stream, PCM, trace, PM, debug dumps, probes, and machine selection.

Control flow: no direct flow. Inline `get_chip_info()` retrieves `sof_amd_acp_desc` from `snd_sof_pdata->desc->chip_info`.

State and persistence: `acp_dev_data` is the main persistent platform state for an ACP SOF device. `scratch_reg_conf` defines the firmware/host-shared SRAM layout for IPC flags, PTEs, DMA descriptors, per-stream offsets/sizes, and FIFOs.

Dependencies and integration points: includes SOF private/audio headers and Linux SoundWire AMD definitions. Provides the ABI between common ACP files and per-platform PCI/ops files.

Risks: host and firmware must agree exactly on scratch layout and constants. Revision IDs are used in switch statements throughout the implementation, so adding a new ACP revision requires updating both descriptors and branch conditions.

Test signals: compile coverage across all AMD modules, firmware boot using scratch layout, stream mapping, and namespace symbol resolution.
