# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.c

Purpose: platform driver and provider API for the Xilinx Video Timing Controller. It registers VTC instances globally so other Xilinx video blocks, notably TPG, can obtain them by `xlnx,vtc` phandle and start/stop timing generation.

Important APIs/types: `struct xvtc_device` embeds `xvip_device`, global list linkage, detector/generator flags, and generator config. Exported functions are `xvtc_of_get`, `xvtc_put`, `xvtc_generator_start`, and `xvtc_generator_stop`. Register definitions cover control, status, detector/generator timing blocks, polarity, active size, frame size, sync, blanking, and frame sync.

Control flow: probe parses `xlnx,detector`/`xlnx,generator`, initializes common Xilinx resources, prints version, and adds the device to a global mutex-protected list. `xvtc_of_get()` parses the consumer phandle and returns a matching registered VTC or `-EPROBE_DEFER`. Generator start enables the clock, writes active-high polarity, default encoding, active/frame/sync timing registers, then enables generator and register update. Stop clears control and disables the clock.

State and persistence: global `xvtc_list` is runtime registry state; per-device state includes capabilities and MMIO/clock. No persistent state. `xvtc_put()` is currently empty because lookup does not take references.

Dependencies and integration: uses common clock, OF phandles, Xilinx VIP MMIO helpers, and platform driver compatible `xlnx,v-tc-6.1`. Consumers must handle probe deferral.

Risks: `xvip_init_resources()` already enables the clock, and `xvtc_generator_start()` prepares/enables it again; reference balancing depends on matching stop/remove paths. No validation clamps `xvtc_config` fields against masks. Test signals include phandle lookup ordering, TPG-driven timing generation, detector/generator property combinations, and repeated start/stop/remove cycles.
