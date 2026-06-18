# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1.h

Purpose: primary private header for the VSP1 driver. It defines hardware feature flags, per-SoC device metadata, global device state, maximum entity counts, register access wrappers, and core lifecycle prototypes.

Important APIs and types: `struct vsp1_device_info` describes model/version/generation/features/counts/uapi mode. `struct vsp1_device` owns MMIO, FCP/bus-master/reset resources, all entity pointers, media/V4L2 devices, entity/video lists, and DRM/VSPX private pointers. `vsp1_feature()`, `vsp1_read()`, `vsp1_write()`, `vsp1_device_get()`, `vsp1_device_put()`, and `vsp1_reset_wpf()` are the main cross-file helpers.

Control flow role: probe fills `struct vsp1_device`, looks up `info`, then entity constructors populate the typed pointers. Runtime paths acquire the device through runtime PM, write registers directly or through display lists, and use feature flags to select entity availability, extended display-list support, LIF quirks, flips, and VSPX/IIF paths.

State and persistence: persistent state includes hardware resources, active media graph objects, and pointers used by both UAPI and DRM modes. Feature flags persist as immutable capabilities after probe. Register access functions are thin MMIO wrappers with no locking, so callers own ordering and power state.

Dependencies and integration: includes Linux IO/list/mutex, media-device, V4L2 device/subdev, and `vsp1_regs.h`. It forward-declares all major internal entity types and integrates with R-Car FCP and reset controller support.

Risks and test signals: edits can affect almost every VSP1 object. Validate feature-bit additions against entity creation, route setup, Kbuild, and runtime PM. Compile-test all VSP1 objects, then test both media-controller UAPI devices and DRM display integration on variants with different `vsp1_device_info` entries.
