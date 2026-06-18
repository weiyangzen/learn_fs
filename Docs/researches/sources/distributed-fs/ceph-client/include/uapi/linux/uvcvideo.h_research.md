# sources/distributed-fs/ceph-client/include/uapi/linux/uvcvideo.h

## Purpose
Defines userspace controls for USB Video Class devices, especially dynamic extension unit controls and UVC metadata buffers.

## Important APIs, Types, And Constants
Control data type constants classify raw, signed, unsigned, boolean, enum, bitmask, and rectangle payloads. `UVC_CTRL_FLAG_*` describes supported GET/SET operations, suspend/resume restore, device auto-update, and asynchronous reporting; `UVC_CTRL_FLAG_GET_RANGE` combines the standard range queries. UVC-specific V4L2 controls define region-of-interest rectangle and automation bitmasks under `V4L2_CID_USER_UVC_BASE`. `struct uvc_menu_info` stores menu entries. `struct uvc_xu_control_mapping` maps a UVC extension unit selector to a V4L2 control id/type/data type and optional userspace menu array. `struct uvc_xu_control_query` describes raw UVC class-specific control requests. `UVCIOC_CTRL_MAP` and `UVCIOC_CTRL_QUERY` are the ioctl entry points. `struct uvc_meta_buf` is a packed variable-length metadata record with driver timestamp, USB SOF, payload length/flags, and copied UVC header bytes.

## Control Flow, State, And Persistence
Userspace maps extension-unit controls through `UVCIOC_CTRL_MAP`, then issues queries through `UVCIOC_CTRL_QUERY` or normal V4L2 control paths. Driver state includes registered mappings, current camera control values, and metadata queue buffers. Some control values are explicitly marked restorable across suspend/resume, but persistent storage belongs to the driver/device, not this header.

## Dependencies And Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`, plus V4L2 control IDs from the broader media API. Integrates with UVC USB descriptors, V4L2 control handling, video node metadata queues, and applications such as camera control tools.

## Risks And Test Signals
Pointer fields marked `__user` and variable metadata records require careful size and bounds validation. Extension-unit mappings can expose vendor controls incorrectly if `size`, `offset`, `selector`, or data type are wrong. Tests should cover ioctl ABI sizes, mapping invalid selectors, menu-count bounds, GET/SET request paths, suspend restore behavior, and metadata buffer parsing with multiple complete records.
