<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c` implements Ice Lake style NHI operations used by integrated Thunderbolt/USB4 controllers. Its main job is force-power sequencing, link-controller mailbox handshakes, LTR programming, and PM/shutdown hooks. The source was read as a complete 185-line file.

## Important APIs, Types, and Functions

The exported object is `icl_nhi_ops`. Internal helpers include `icl_nhi_is_device_connected()`, `icl_nhi_force_power()`, `icl_nhi_lc_mailbox_cmd()`, `icl_nhi_lc_mailbox_cmd_complete()`, `icl_nhi_set_ltr()`, `icl_nhi_suspend()`, `icl_nhi_suspend_noirq()`, `icl_nhi_resume()`, and `icl_nhi_shutdown()`. `ICL_LC_MAILBOX_TIMEOUT` bounds link-controller mailbox waits.

## Control Flow

Initialization and resume call `icl_nhi_resume()`: assert force power via PCI VSEC `VS_CAP_22`, wait for firmware-ready in `VS_CAP_9`, then program snoop/no-snoop LTR from `VS_CAP_16` into `VS_CAP_15`. Runtime suspend checks for connected devices; if none are present and the root switch is ICM-controlled, it sends `ICL_LC_PREPARE_FOR_RESET` through the LC mailbox, waits for `VS_CAP_18_DONE`, then clears force power. System suspend-noirq either follows normal suspend when not firmware-assisted, or sends `GO2SX`/`GO2SX_NO_WAKE` depending on wake requirements. Shutdown clears force power.

## State and Persistence Behavior

State is held in PCI config/VSEC registers, not in heap objects. Force-power and LC mailbox bits persist in controller config space until cleared or reset. The device-connected predicate reads current children under `tb->root_switch->dev`, so behavior changes with the live topology.

## Dependencies and Integration Points

The file depends on PCI config-space accessors, sleep timing, Linux suspend helpers, `nhi.h`, `nhi_regs.h`, and `tb.h`. It is selected from the NHI PCI ID table through `driver_data`, and called by `nhi.c` around domain PM transitions. It also depends on `tb_switch_is_icm()` because the LC mailbox sequence differs for firmware-managed controllers.

## Risks and Edge Cases

Timeouts waiting for `VS_CAP_9_FW_READY` or `VS_CAP_18_DONE` can block probe/resume. The suspend path intentionally skips force power down when devices are connected, so false device detection affects power use. Firmware-assisted suspend only sends LC commands for ICM roots. Misprogramming force-power or DMA-delay fields can leave integrated controllers inaccessible until another power transition.

## Test Signals

Probe and runtime PM on Ice Lake/Tiger Lake/Alder Lake and newer integrated controllers; suspend-to-idle and firmware-assisted sleep with and without connected devices; timeout injection on VSEC ready/done bits; LTR register readback; and shutdown/poweroff tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c -->
