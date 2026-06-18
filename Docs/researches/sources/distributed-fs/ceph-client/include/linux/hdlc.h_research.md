<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdlc.h -->
# sources/distributed-fs/ceph-client/include/linux/hdlc.h

Purpose: This header defines the generic HDLC network-device support interface between HDLC hardware drivers and protocol modules.

Important APIs/types/functions: `struct hdlc_proto` defines protocol callbacks for open/close, carrier start/stop, detach, ioctl, type translation, RX, transmit, module owner, and linked-list membership. `hdlc_device` is stored in `netdev_priv()` and contains hardware `attach` and `xmit` callbacks plus internal protocol pointer, carrier/open flags, state lock, protocol state, and hardware private pointer. APIs include `hdlc_ioctl()`, `register_hdlc_device()`, `unregister_hdlc_device()`, protocol register/unregister, `alloc_hdlcdev()`, `dev_to_hdlc()`, `debug_frame()`, `hdlc_open()`, `hdlc_close()`, `hdlc_start_xmit()`, `attach_hdlc_protocol()`, `detach_hdlc_protocol()`, and `hdlc_type_trans()`.

Control flow, state, and persistence: Hardware drivers allocate/register an HDLC netdev and route `ndo_start_xmit` to `hdlc_start_xmit()`. User ioctls attach protocol modules. Open/close and carrier changes call protocol start/stop hooks while state is protected by `state_lock`. `hdlc_type_trans()` lets protocol override packet type or defaults to `ETH_P_HDLC`.

Dependencies/integration: It integrates Linux netdevice, skbuff, HDLC ioctl/uapi definitions, modules, spinlocks, and protocol plugins.

Risks and test signals: Protocol attach/detach must respect module lifetime and open/carrier state. `debug_frame()` prints up to 100 bytes and should not be used on hot paths. Tests should cover protocol registration, ioctl attach, open/close, carrier transitions, TX/RX delegation, detach while open, and default/custom type translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdlc.h -->
