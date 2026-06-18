# sources/distributed-fs/ceph-client/include/media/dvbdev.h

Purpose: Core DVB adapter and device-node infrastructure for registering `/dev/dvb/adapterX/*` devices, media-controller links, generic file operations, usercopy ioctls, and frontend module attachment.

Important APIs/types/functions: Defines `DVB_MAJOR`, adapter count defaults, `DVB_UNSET`, `enum dvb_device_type`, module-parameter helper `DVB_DEFINE_MOD_OPT_ADAPTER_NR`, `dvb_adapter`, `dvb_device`, and `dvbdevfops_node`. APIs get/put device refs, register/unregister adapters and devices, remove/unregister devices, create media graphs, generic open/release/ioctl, `dvb_usercopy`, I2C module probe/release, and legacy `dvb_attach`/`dvb_detach`.

Control flow: Drivers register an adapter, then register frontend/demux/DVR/CA/net devices from templates. Generic open/release checks device validity and reader/writer/user counts. Generic ioctl copies user arguments, calls `kernel_ioctl`, and copies results back. Optional media-controller code links DVB entities. I2C helpers bind submodules; legacy attach dynamically requests symbols when enabled.

State and persistence: `dvb_adapter` tracks adapter number, device list, private data, module/device, mutually exclusive frontend state, locks, and optional media-controller objects. `dvb_device` tracks kref, fops, type/minor/id, open counters, wait queue, ioctl callback, optional media entities, and private data.

Dependencies and integration: Depends on Linux fs/poll/list/types, media-device, optional I2C and media controller. It is used by all DVB frontend, demux, CA, DVR, and network layers.

Risks and test signals: Risks include reference/open races, counter underflow, media graph mismatches, unregister while filehandles exist, ioctl copy-size bugs, and legacy module attach leaks. Test adapter numbering, multiple device types, RO/RW open limits, hot-unplug with open files, media graph creation, usercopy directions, I2C probe/release, and CONFIG_MEDIA_ATTACH variants.
