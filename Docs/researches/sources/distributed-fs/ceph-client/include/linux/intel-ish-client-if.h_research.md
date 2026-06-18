<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel-ish-client-if.h -->
# sources/distributed-fs/ceph-client/include/linux/intel-ish-client-if.h

Purpose: Defines the client-driver interface for Intel Integrated Sensor Hub Transport Protocol devices.

Important APIs/types/functions: `enum cl_state` models client connection state. `struct ishtp_cl_driver` is the bus driver object with probe/remove/reset callbacks and id table. `struct ishtp_msg_data` and `ishtp_cl_rb` model messages and receive buffers. APIs register drivers, register event callbacks, allocate/link/connect/disconnect/destroy clients, send data, flush/recycle queues, get RX buffers, set client data, access ISHTP/PCI/workqueue devices, change ring sizes/state/FW client id, and reset hardware.

Control flow: Client drivers bind to firmware clients, allocate/link a client, establish connection, receive callbacks/RBs, send messages, and disconnect/unlink on remove/reset.

State/persistence: Connection state, rings, client data, receive buffers, and firmware-client ids persist per client connection.

Dependencies/integration: Depends on device model, mod_devicetable, GUID firmware clients, PCI parent devices, and workqueues.

Risks: Duplicate `ishtp_register_event_cb()` declarations hint at ABI sensitivity; queue ownership and recycle discipline are critical.

Test signals: Driver bind/unbind, connect/disconnect, send/receive loopback, reset recovery, ring size changes, and RB recycle leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel-ish-client-if.h -->
