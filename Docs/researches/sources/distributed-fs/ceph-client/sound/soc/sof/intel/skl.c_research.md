<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/skl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/skl.c

## Purpose
Skylake/Kabylake HDA DSP ops initializer and chip descriptor for IPC4-capable CAVS 1.5 platforms. It adapts common HDA ops to SKL SRAM mailbox/window placement, boot method, IPC4 interrupt handling, and debug mapping.

## Important APIs, Types, and Functions
`skl_dsp_ipc_get_window_offset()` maps window IDs to `0x8000 + 0x2000 * id`; `skl_dsp_ipc_get_mailbox_offset()` returns `0x9000`. `sof_skl_ops_init()` copies `sof_hda_common_ops`, allocates `struct sof_ipc4_fw_data`, sets manifest offset and mtrace type, installs IPC4 send/IRQ callbacks, DAI driver ops, debug maps, IPC dump, CL boot, and post-fw-run hooks. `sof_skl_ops` and `skl_chip_info` are exported in the HDA common namespace.

## Control Flow, State, and Persistence
Ops init mutates the global `sof_skl_ops` template and stores IPC4 private data in `sdev->private`. That private data persists for the device lifetime and informs IPC4 manifest parsing and tracing. Chip descriptor state is static and supplies IPC register offsets/masks, ROM status register, core masks, and power/interrupt callbacks to the HDA core.

## Dependencies and Integration
Depends on common HDA SOF ops, IPC4 private data, HDA IPC4 send/IRQ/dump helpers, SKL CL firmware boot, and SOF topology/audio code. It is selected by PCI descriptors for SKL-family devices and integrates with CAVS 1.5 firmware manifests (`SOF_MAN4_FW_HDR_OFFSET_CAVS_1_5`) and mtrace type.

## Risks and Test Signals
Risks include global ops mutation if multiple SKL-like devices were initialized concurrently, wrong SRAM window offsets breaking mailbox/debug windows, and CAVS 1.5 manifest offset drift. Test signals are IPC4 firmware boot, mailbox discovery at the expected SRAM offsets, HDA IPC4 IRQ traffic, debugfs `hda`/`pp`/`dsp` region reads, and clean power-down/interrupt-disable callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/skl.c -->
