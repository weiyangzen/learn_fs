# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.h

## Purpose

`uvc_configfs.h` declares the private configfs data model used by the UVC gadget function. It defines wrapper structures that combine configfs items/groups with UVC descriptor state for control headers, streaming headers, formats, frames, color matching descriptors, and extension units.

## Important APIs, Types, and Functions

`to_f_uvc_opts()` maps a configfs item back to its owning `struct f_uvc_opts`. `UVCG_STREAMING_CONTROL_SIZE` defines the one-byte per-format streaming control field stored in input headers. `struct uvcg_control_header`, `struct uvcg_streaming_header`, `struct uvcg_format`, `struct uvcg_frame`, `struct uvcg_uncompressed`, `struct uvcg_mjpeg`, `struct uvcg_framebased`, `struct uvcg_color_matching`, and `struct uvcg_extension` are the core state carriers.

Inline conversion helpers such as `to_uvcg_control_header()`, `to_uvcg_streaming_header()`, `to_uvcg_format()`, `to_uvcg_frame()`, and format-specific `to_uvcg_*()` helpers provide type-safe container lookups for configfs callbacks. The one exported declaration is `uvcg_attach_configfs()`.

## Control Flow

The header has no independent execution path. `uvc_configfs.c` allocates these structures when users create configfs groups/items, initializes their embedded descriptors, links them into list heads, and later walks those lists to assemble runtime USB descriptors.

## State and Persistence Behavior

All structures are in-memory configfs state. `linked` counters prevent unsafe mutation after descriptors are selected. `refcnt` on color matching entries prevents edits while referenced by formats. Format and frame lists preserve ordering, which becomes the UVC format/frame index order. Extension units own dynamically allocated `baSourceID` and `bmControls` arrays. No persistent storage is represented.

## Dependencies and Integration Points

The header depends on `linux/configfs.h` and `u_uvc.h`, and indirectly on UVC descriptor declarations used by `f_uvc_opts`. It is private to the UVC function implementation but forms a key boundary between configfs callbacks, V4L2 format discovery, and descriptor materialization.

## Risks and Test Signals

Risks include packed internal frame layout assumptions, list lifetime errors, conversion-helper misuse, and descriptor structures with flexible-array semantics (`DECLARE_UVC_HEADER_DESCRIPTOR(1)` and `uvc_input_header_descriptor`) being copied with exact sizes. Compile coverage plus configfs create/link/drop tests for every declared type are the main signals.
