# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-core.c

## Purpose
`rcar-core.c` is the platform, media-controller, async-subdevice, SoC-data, routing, controls, and PM core for the Renesas R-Car VIN capture driver. It groups all VIN instances in a system, discovers upstream CSI-2/ISP/parallel sources from DT, creates media links, and registers video nodes once the graph is complete.

## Important APIs, Types, And Functions
The file uses shared types from `rcar-vin.h`: `struct rvin_dev`, `struct rvin_group`, `struct rvin_info`, and `struct rvin_group_route`. Main functions are `rcar_vin_probe()`, `rcar_vin_remove()`, `rvin_group_get()`, `rvin_group_put()`, notifier callbacks, `rvin_csi2_link_notify()`, `rvin_csi2_setup_links()`, `rvin_isp_setup_links()`, `rvin_parallel_setup_links()`, `rvin_create_controls()`, `rvin_suspend()`, and `rvin_resume()`. Static match data describes H1/M1/Gen2/Gen3/Gen4 capabilities, max dimensions, NV12/RAW10 support, routes, and scaler callbacks.

## Control Flow
Probe allocates a VIN, maps registers, gets IRQ, initializes DMA/V4L2 device state through `rvin_dma_register()`, assigns an ID from `renesas,id` for Gen3/Gen4 or IDA for older models, initializes the video entity sink pad, creates alpha controls, and joins a singleton `rvin_group`. Depending on model it initializes ISP links, CSI-2 links, or parallel links, enables runtime PM, and returns. The group notifier waits until all enabled VINs are present, registers async fwnode matches, and on completion registers the media device, subdev nodes, all VIN video nodes, and the graph links.

CSI-2 link notification validates that link changes happen only when no entity is streaming, ensures VINs in a master group attach to one CSI-2 receiver, looks up the proper CHSEL route, writes channel routing via `rvin_set_channel_routing()`, and marks `vin->is_csi`. ISP setup creates immutable enabled links from ISP source pads to VIN nodes based on VIN id. Parallel setup creates direct source-to-VIN links and disables immutable auto-enable if CSI/ISP remotes also exist.

## State And Persistence
Global state is `rvin_group_data`, protected by `rvin_group_lock`, plus `rvin_ida` for legacy IDs. Per-group state includes media device, notifier, VIN array, remote subdev slots, platform info, lock, and refcount. Per-device state includes ID, group membership, controls, `is_csi`, scaler selection, and cached route `chsel` in the DMA file. State is not persistent across driver unload; routing is restored on resume from cached memory.

## Dependencies And Integration Points
This file depends on OF graph parsing, V4L2 async notifiers, media controller, runtime PM, V4L2 controls, and the DMA/V4L2 helper functions defined in sibling files. It integrates with `rcar-csi2`, `rcar-isp`, and parallel sensor/decoder subdevices. Its route tables encode SoC-specific CSI-to-VIN topology.

## Risks
The group allocator assumes only one system-wide VIN group. Link routing is sensitive to `renesas,id` uniqueness and complete DT coverage; duplicate or missing IDs fail probe. Link changes while streaming are blocked, but route state spans multiple VIN instances and master VINs. Error paths after partial notifier/media registration can affect all VIN nodes in the group. Suspend/resume depends on cached CHSEL and master VIN availability.

## Test Signals
Test complete and partial DT groups, duplicate IDs, CSI-2 and ISP graph creation, parallel-only operation, link enable/disable rejection while streaming, route programming for every SoC route table, media device registration only after async completion, alpha control creation, PM suspend/resume while streaming, and clean removal of group/notifier/video nodes.
