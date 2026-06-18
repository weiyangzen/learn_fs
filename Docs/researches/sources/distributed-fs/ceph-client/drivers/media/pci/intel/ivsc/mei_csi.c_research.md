# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_csi.c

## Purpose
`mei_csi.c` is the Intel IVSC CSI MEI client and V4L2 bridge driver. It exposes a two-pad V4L2 subdevice between a sensor and the host IPU pipeline, sends MEI commands to assign CSI-2 link ownership and configure lane/frequency parameters, forwards stream-on/off to the remote sensor, and reports privacy state through a read-only V4L2 control.

## Important APIs, Types, And Functions
Important structures include `struct csi_link_cfg`, `struct csi_cmd`, `struct csi_notif`, and `struct mei_csi`. Key functions are `mei_csi_send()`, `csi_set_link_owner()`, `csi_set_link_cfg()`, `mei_csi_rx()`, `mei_csi_set_stream()`, `mei_csi_set_fmt()`, `mei_csi_get_mbus_config()`, async notifier bound/unbind callbacks, `mei_csi_init_controls()`, `mei_csi_parse_firmware()`, probe, and remove.

## Control Flow
Probe first finds any IPU6 PCI device and initializes IPU bridge sensor fwnodes, requires the MEI device to have fwnode data, enables MEI, registers RX, parses firmware graph endpoints, then initializes and registers the V4L2 subdev. Firmware parsing reads sink/source endpoints, requires matching CSI-2 lane counts, and registers an async notifier for the remote sensor. The bound callback links the remote sensor source pad to the IVSC CSI sink pad.

On stream-on from V4L2, the driver obtains the remote link frequency, switches CSI link ownership to host, sends lane/frequency configuration, waits an empirical 100 ms, then starts the remote sensor. Stream-off stops the remote sensor and switches link ownership back to IVSC. RX handles privacy notifications by updating `V4L2_CID_PRIVACY` and command responses by completing the command wait.

## State And Persistence
The driver stores current streaming state, lane count, link frequency, remote pad pointer, command response/completion, V4L2 controls, and active subdev state. No file persistence exists. Privacy state is cached in the V4L2 control.

## Dependencies And Integration Points
It depends on MEI, IPU bridge, IPU6 PCI ID table, V4L2 async/subdev/fwnode/control frameworks, media-controller links, and the remote sensor's link-frequency control and `s_stream` op.

## Risks And Test Signals
Probe calls `mei_csi_parse_firmware()` before `v4l2_subdev_init()`, but `v4l2_async_subdev_nf_init()` receives `&csi->subdev`; this ordering is worth verifying against V4L2 notifier expectations. `mei_csi_set_stream()` assumes `csi->remote` is bound before streaming. Command status `-1` is translated to privacy-on success, which should be documented in tests. Test invalid lane mismatch, missing endpoints, remote sensor unbind, link-frequency absence, command timeout, privacy notifications, stream-on error unwinding to IVSC ownership, and format propagation across both pads.
