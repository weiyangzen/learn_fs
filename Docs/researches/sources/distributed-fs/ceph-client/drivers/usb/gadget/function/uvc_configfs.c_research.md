# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.c

## Purpose

`uvc_configfs.c` builds the configfs interface for the UVC gadget function. It exposes the UVC control and streaming descriptor graph under the function instance, lets users create headers, formats, frames, color matching descriptors, and extension units, and materializes linked configfs items into descriptor arrays consumed by the runtime UVC function. It also exposes root UVC options such as streaming interval, max packet, max burst, and function name.

## Important APIs, Types, and Functions

The public entry point is `uvcg_attach_configfs(struct f_uvc_opts *opts)`, which initializes `opts->func_inst.group` and creates the default `control` and `streaming` child groups. Most implementation uses `struct uvcg_config_group_type`, `uvcg_config_create_group()`, `uvcg_config_create_children()`, and `uvcg_config_remove_children()` to build and tear down static configfs subtrees.

Attribute generation is macro-heavy. `UVC_ATTR()` and `UVC_ATTR_RO()` create configfs attributes. Control-side handlers cover `control/header/<name>`, default processing/camera/output terminal descriptors, extension units, and `control/class/{fs,ss}` symlink targets. Streaming-side handlers cover `streaming/header/<name>`, `uncompressed`, `mjpeg`, `framebased`, `color_matching`, and `streaming/class/{fs,hs,ss}`.

Descriptor assembly centers on `uvcg_streaming_header_allow_link()`, `uvcg_streaming_class_allow_link()`, `__uvcg_iter_strm_cls()`, `__uvcg_cnt_strm()`, and `__uvcg_fill_strm()`. Those functions walk linked headers, formats, frames, and color matching descriptors, size an array of `struct uvc_descriptor_header *`, allocate one contiguous descriptor block, and copy configfs state into USB descriptor layouts.

## Control Flow

On function-instance creation, `uvcg_attach_configfs()` initializes the top-level config group and recursively creates default children. Users then populate dynamic groups: control headers, extension units, streaming headers, format instances, frame entries, and color matching entries. Stores validate numeric ranges, parse newline-delimited arrays through `__uvcg_iter_item_entries()`, and usually reject changes with `-EBUSY` once a descriptor is linked or `opts->refcnt` shows the function is active.

Configfs symlinks commit descriptor relationships. Control class links accept only headers under the matching `control/header` group and install the selected header into `opts->uvc_fs_control_cls` or `opts->uvc_ss_control_cls`. Streaming header links accept only direct children of streaming format groups and append `struct uvcg_format_ptr` entries. Streaming class links accept only streaming headers, compute final descriptor arrays for full/high/super speed, and store them in the corresponding `f_uvc_opts` fields.

## State and Persistence Behavior

State is runtime configfs state held in `f_uvc_opts` and per-item allocations. Lists in `opts->extension_units`, `uvcg_streaming_header.formats`, and `uvcg_format.frames` preserve user-created topology. `linked`, `refcnt`, and class-array pointers freeze descriptor edits once configfs symlinks or active function users depend on them. No state is persisted by this file; userspace must recreate configfs layout after reboot or module reload.

## Dependencies and Integration Points

The file depends on configfs, libcomposite function instances, UVC and USB video descriptor definitions, `u_uvc.h`/`f_uvc_opts`, gadget strings, `uvc_format_by_guid()`, and core kernel helpers for sorting, allocation, hex parsing, and endian conversion. It is the bridge between configfs layout and `f_uvc.c` descriptor binding, and its output feeds the V4L2/video code through `uvc->header` and `opts` descriptor arrays.

## Risks and Test Signals

Risks are concentrated in configfs hierarchy navigation, symlink validation, descriptor sizing, and memory ownership. Many handlers climb fixed parent chains; tree changes or bad assumptions can target the wrong `f_uvc_opts`. Extension-unit arrays are reallocated on size writes, and streaming class arrays allocate a pointer array plus contiguous descriptor data that must be freed on link drop. The framebased copy path intentionally translates from the internal packed frame layout into `struct uvc_frame_framebased`; descriptor-length mistakes would break host enumeration.

Useful tests include creating and deleting all dynamic groups; writing invalid numeric values, oversized arrays, and malformed hex; changing attributes before and after links; linking control headers for FS/SS; linking multiple formats and frames into a streaming header; creating framebased H.264 descriptors; linking and dropping color matching descriptors; enabling interrupt endpoint; binding the UVC function after configfs setup; and unbinding while descriptors and strings are linked.
