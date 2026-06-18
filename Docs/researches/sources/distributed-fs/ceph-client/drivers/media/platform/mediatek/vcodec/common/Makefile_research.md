# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/Makefile

## Purpose
This Makefile builds the shared MediaTek vcodec support module and optional debugfs support.

## Important APIs, Types, And Functions
`mtk-vcodec-common.o` includes interrupt, utility, and firmware-dispatch code. It conditionally adds `mtk_vcodec_fw_vpu.o` when the VPU backend is enabled and `mtk_vcodec_fw_scp.o` when the SCP backend is enabled. With `CONFIG_DEBUG_FS`, it also builds `mtk-vcodec-dbgfs.o` from `mtk_vcodec_dbgfs.o`.

## Control Flow
Kbuild evaluates backend booleans derived from Kconfig and assembles the common object list. Decoder/encoder code then links against exported symbols from these objects.

## State, Persistence, And Dependencies
No runtime state is defined here. Build-time state depends on `CONFIG_VIDEO_MEDIATEK_VCODEC`, backend symbols, and debugfs.

## Integration Points
Provides shared symbols for decoder and encoder firmware IPC, memory allocation, interrupts, register access, current-context tracking, and debugfs controls.

## Risks
Missing backend objects make `mtk_vcodec_fw_select()` return `-ENODEV` through stub initializers. Debugfs object is only built when debugfs is enabled, so header stubs must remain complete.

## Test Signals
Builds with VPU, SCP, both, neither backend stubs under compile-test, and debugfs enabled/disabled validate this file.
