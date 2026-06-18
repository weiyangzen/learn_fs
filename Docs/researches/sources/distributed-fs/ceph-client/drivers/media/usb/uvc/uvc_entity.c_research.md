# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_entity.c

Purpose: implements media-controller entity registration for UVC devices when `CONFIG_MEDIA_CONTROLLER` is enabled. It turns parsed UVC entities into media entities/subdevices and creates immutable pad links that mirror the UVC topology.

Important APIs and functions: exported functions are `uvc_mc_register_entities` and `uvc_mc_cleanup_entity`. Internal helpers are `uvc_mc_init_entity` and `uvc_mc_create_links`. The file uses an empty `v4l2_subdev_ops` table because entities are represented for topology rather than active subdevice operations.

Control flow: registration first iterates chain entities and initializes each media entity. Non-streaming UVC units become V4L2 subdevices with functions selected from entity type, such as mux, processing formatter, composite/S-Video connector, or camera sensor. Streaming terminals initialize pads on the already registered video node and can be marked default. A second pass creates enabled immutable pad links from each sink pad to the source entity referenced by `baSourceID`. Cleanup tears down either subdevice media entities or video-node media entities.

State and persistence: media entity state is attached to `struct uvc_entity` subdevices or video device entities and lasts until device cleanup. Link topology is runtime-only and regenerated on probe.

Dependencies and integration points: depends on media controller core, V4L2 subdev registration, parsed UVC chain/entity data from `uvc_driver.c`, and video-node pointers filled during stream registration. It is called from `uvc_register_chains` and `uvc_delete`.

Risks: link creation depends on valid `baSourceID` and pad counts; malformed topology returns errors after some entities may already be initialized. Function classification is approximate for processing and extension units. Conditional build means declarations and call sites must remain guarded by `CONFIG_MEDIA_CONTROLLER`.

Test signals: enable media controller and inspect `media-ctl -p` output for cameras with camera, processing, selector, extension, streaming, and GPIO entities; verify immutable links, default video entity flag, cleanup on probe failure/disconnect, and behavior for missing or invalid source references.
