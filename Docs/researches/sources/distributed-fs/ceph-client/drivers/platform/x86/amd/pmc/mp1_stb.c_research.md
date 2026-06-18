# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp1_stb.c

Purpose: `mp1_stb.c` implements AMD MP1 Smart Trace Buffer support for PMC S2Idle debugging. It can write PM event markers to STB, dump legacy FIFO STB data, and on newer systems map firmware spill-to-DRAM telemetry for debugfs reads.

Important APIs, types, and functions: module parameters `enable_stb` and `dump_custom_stb` control STB debug setup. Exported helpers to PMC are `amd_stb_write()`, `amd_stb_read()`, and `amd_stb_s2d_init()`. Legacy debugfs uses `amd_stb_debugfs_fops`; enhanced spill-to-DRAM uses `amd_stb_debugfs_fops_v2` and `struct amd_stb_v2_data`. `amd_is_stb_supported()` selects S2D message IDs by CPU/root device; `amd_stb_update_args()` selects message/argument/response register offsets, with Zen5 model 0x44 special handling.

Control flow: PMC probe calls `amd_stb_s2d_init()`. If `enable_stb` is false, no debugfs file is added. Unsupported systems get a legacy `stb_read` file backed by repeated SMN reads from `AMD_STB_PMI_0`. Supported systems set S2D message-port offsets, query telemetry size and DRAM address through `amd_pmc_send_cmd()` while temporarily setting `dev->msg_port = MSG_PORT_S2D`, map the DRAM buffer, and create enhanced `stb_read`. Opening enhanced debugfs writes a dummy postcode, optionally flushes firmware data, reads either the full custom buffer or a ring-ordered slice based on sample count, and serves it through `simple_read_from_buffer()`.

State and persistence: state lives in `amd_pmc_dev` fields `stb_virt_addr`, `dram_size`, `msg_port`, and `stb_arg`. Debugfs open allocates per-file buffers. Firmware STB contents persist across the relevant firmware runtime window but are not stored by the driver.

Dependencies and integration points: depends on AMD SMN read/write helpers, PMC SMU command transport, debugfs, and CPU feature/model detection. PMC S2Idle paths call `amd_stb_write()` for prepare/check/restore breadcrumbs.

Risks: `dev->msg_port` is shared with normal PMC command paths; failures in `amd_stb_s2d_init()` before resetting it could leave subsequent SMU commands using S2D offsets. Enhanced open sets S2D mode, calls a flush command, and only resets after the sample-count command; early custom STB path bypasses the reset. Firmware-reported sizes and DRAM addresses are trusted after basic checks. Debugfs can allocate large buffers up to firmware DRAM size.

Test signals: `enable_stb=1` creates `amd_pmc/stb_read`, legacy FIFO reads produce 4096 u32 entries, enhanced systems map S2D DRAM and produce ring-ordered data, prepare/check/restore STB writes succeed during S2Idle, and `msg_port` returns to PMC after debugfs reads.
