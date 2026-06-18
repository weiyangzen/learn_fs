# sources/distributed-fs/ceph-client/drivers/media/mc/Makefile

Purpose: builds the media-controller core object `mc.o` from device, devnode, entity, and request components, with optional USB media-device allocator support.

Important APIs/types/functions: `mc-objs` includes `mc-device.o`, `mc-devnode.o`, `mc-entity.o`, and `mc-request.o`; `mc-dev-allocator.o` is added when `CONFIG_USB` is non-empty. `obj-$(CONFIG_MEDIA_SUPPORT) += mc.o` links the aggregate into the media support build.

Control flow: Kbuild composes a single `mc.o` module/built-in object based on configuration. USB-specific allocator APIs are compiled only when USB is configured.

State/persistence: no runtime state; build output reflects configuration.

Dependencies/integration: integrates with Kbuild and the media subsystem. Exported symbols from the object are used by V4L2, DVB, USB, PCI, and media graph drivers.

Risks/test signals: the `ifneq ($(CONFIG_USB),)` check includes the allocator for either built-in or module USB configurations. Build tests should cover `MEDIA_SUPPORT=y/m`, `CONFIG_USB=n/y/m`, and users of `media_device_usb_allocate()` to ensure symbol availability matches callers.
