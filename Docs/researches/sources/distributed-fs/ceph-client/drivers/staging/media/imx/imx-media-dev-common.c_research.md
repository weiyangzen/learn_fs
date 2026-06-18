# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev-common.c

## Purpose

`imx-media-dev-common.c` contains shared media-device orchestration for i.MX5/6/7 media drivers. It initializes the `media_device` and `v4l2_device`, completes async probe, creates late CSI-2 links, builds source-pad-to-video-device reachability lists, forwards subdevice events to reachable video nodes, and refreshes inherited controls when media links change.

## Important APIs, Types, and Functions

Exported functions are `imx_media_probe_complete()`, `imx_media_dev_init()`, and `imx_media_dev_notifier_register()`. Internal helpers include `imx_media_create_csi2_links()`, `imx_media_alloc_pad_vdev_lists()`, `imx_media_create_pad_vdev_lists()`, `imx_media_add_vdev_to_pad()`, `imx_media_inherit_controls()`, `imx_media_link_notify()`, and `imx_media_notify()`.

## Control Flow

Device initialization allocates `struct imx_media_dev`, sets model and bus info, installs media ops, initializes the media device and mutex, registers a V4L2 device, initializes the video-device list, and prepares the async notifier. Notifier registration fails if no async subdevices were queued, otherwise it installs supplied or default notifier ops.

Probe completion runs under `imxmd->mutex`: it creates missing fwnode links from the CSI-2 receiver to CSI or CSI mux subdevices, allocates per-pad video-device lists for all subdevices, walks each registered video node upstream to populate reachability lists, and registers subdevice nodes. After releasing the mutex it registers the media device.

## State and Persistence Behavior

There is no file persistence. Persistent runtime state is the `imx_media_dev` object, the master video-device list, per-subdevice `host_priv` arrays of `list_head`, and devm-managed `imx_media_pad_vdev` entries. Link notifications mutate video-device control handlers based on the active graph.

## Dependencies and Integration Points

This file ties together the media-controller graph, V4L2 async notifier, V4L2 controls, V4L2 subdev nodes, and `imx-media` event forwarding. It is called by the i.MX6 platform driver and can be reused by related SoC variants.

## Risks and Edge Cases

Reachability list construction assumes each capture video device has at least one entity link and uses the first one. `sd->host_priv` is repurposed for pad vdev lists, so other users must not rely on it. Control inheritance is recursively rebuilt on link changes; failures can leave video nodes without expected upstream controls. CSI-2 link creation is broad and relies on group ids being set correctly.

## Test Signals

Verify async completion with CSI, CSI mux, and CSI-2 graphs; subdev node registration; media device registration; control inheritance before/after link enable and disable; event forwarding from subdevs to video nodes; no-subdev notifier failure; and duplicate traversal avoidance in pad vdev lists.
