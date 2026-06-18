# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-of.c

## Purpose

`imx-media-of.c` parses the top-level i.MX capture subsystem device-tree node and adds CSI nodes referenced by its `ports` phandle array to the media device async notifier.

## Important APIs, Types, and Functions

The exported function is `imx_media_add_of_subdevs()`. Its helper `imx_media_of_add_csi()` validates availability and adds a fwnode async connection with `v4l2_async_nf_add_fwnode()`.

## Control Flow

`imx_media_add_of_subdevs()` iterates `of_parse_phandle(np, "ports", i)` until no phandle is found. Each CSI node is passed to `imx_media_of_add_csi()`, then released with `of_node_put()`. Disabled nodes and duplicates are treated as nonfatal and skipped; other errors abort parsing.

## State and Persistence Behavior

No local persistent state exists. The effect is to populate `imxmd->notifier.waiting_list` with fwnode matches. All node references obtained during parsing are released before returning.

## Dependencies and Integration Points

This file depends on Open Firmware graph/device APIs and V4L2 async notifier fwnode matching. The top-level platform driver calls it during probe before registering the notifier.

## Risks and Edge Cases

If all ports are disabled or duplicate, the later notifier registration path fails with "no subdevs". Device-tree schema mistakes in the `ports` phandle array directly prevent media graph discovery. The code only adds CSI nodes listed by phandle; it does not recursively discover arbitrary OF graph endpoints.

## Test Signals

Test no `ports`, disabled CSI nodes, duplicate phandles, valid one/two CSI phandles, malformed phandle references, and notifier registration after this parser returns an empty waiting list.
