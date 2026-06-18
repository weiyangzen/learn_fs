# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-debug.c

## Purpose
`imx8-isi-debug.c` provides debugfs register dumps for each ISI pipe when `CONFIG_DEBUG_FS` is enabled.

## Important APIs, Types, and Functions
`mxc_isi_debug_dump_regs_show()` is the seq_file show function. It lists a fixed table of channel registers such as `CHNL_CTRL`, `CHNL_IMG_CTRL`, buffer addresses, scaler, crop, CSC, ROI, memory-read, and flow-control registers. When platform data advertises 36-bit DMA, it also dumps the extended address registers. `mxc_isi_debug_init()` creates a debugfs directory named after the device and one read-only file per pipe. `mxc_isi_debug_cleanup()` removes the tree.

## Control Flow
Debugfs initialization runs from core probe after the pipes have been initialized. Reading a pipe file calls `pm_runtime_get_if_in_use()` and returns an empty dump if the device is powered down. If active, it prints register names, offsets, and values, then drops the runtime PM reference.

## State and Persistence
The only stored state is `isi->debugfs_root`. Register values are read live from MMIO. Debugfs files are ephemeral and removed on driver detach.

## Dependencies and Integration Points
The file depends on debugfs, seq_file, runtime PM, MMIO reads, `imx8-isi-core.h`, and `imx8-isi-regs.h`. It integrates with the core through `mxc_isi_debug_init()` and `mxc_isi_debug_cleanup()` declarations, which become inline no-ops when debugfs is disabled.

## Risks and Edge Cases
The dump intentionally avoids waking a suspended device, so absence of output can mean the device is inactive rather than broken. Register reads are unsynchronized with streaming hardware and may show transient state. `sprintf(name, "pipe%u", pipe->id)` uses an 8-byte buffer, which is fine for current small pipe IDs but would need review if channel counts grew dramatically.

## Test Signals
Validation includes debugfs directory creation, one file per pipe, correct register dumps while streaming or runtime-active, no runtime wakeup when idle, inclusion of extended address registers on 36-bit DMA platforms, and cleanup after module removal.
