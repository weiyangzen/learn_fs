# sources/distributed-fs/ceph-client/include/media/dvb_net.h

Purpose: DVB network interface wrapper for IP-over-DVB/MPE style data paths.

Important APIs/types/functions: `DVB_NET_DEVICES_MAX` is 10. With `CONFIG_DVB_NET`, `struct dvb_net` stores a DVB device, net_device array, per-device state, exit flag, demux pointer, ioctl mutex, and remove mutex. APIs are `dvb_net_init` and `dvb_net_release`. Without the config, a minimal stub struct and no-op/init-success functions are provided.

Control flow: The DVB adapter initializes DVB net with a demux. Userspace creates/removes network interfaces through DVB net ioctls; the implementation uses demux section/TS filters to feed network packets into Linux net devices. Release unregisters interfaces and the DVB device.

State and persistence: Runtime state includes registered net devices, in-use flags, exit/removal synchronization, and demux binding. No disk persistence.

Dependencies and integration: Depends on DVB device core, module infrastructure, net_device, and demux APIs. Integrates DVB adapters with Linux networking when enabled.

Risks and test signals: Risks include remove/ioctl races, exceeding device slots, stale demux filters, and disabled-config assumptions. Test interface create/delete, concurrent unplug and ioctl, max device count, packet receive path, and builds with and without `CONFIG_DVB_NET`.
