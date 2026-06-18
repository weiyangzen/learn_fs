# sources/distributed-fs/ceph-client/include/net/rsi_91x.h

Purpose: declares shared Redpine/RSI 91x coexistence queue IDs, host-interface IDs, and WLAN/BT module operation tables.

Important APIs and types: queue constants identify coexistence, BT, WLAN, Wi-Fi management/data, and BT management/data queues. `enum rsi_coex_queues` classifies common/BT/WLAN coex queues. `enum rsi_host_intf` identifies SDIO or USB transport. `struct rsi_proto_ops` lets protocol modules send packets, query host interface, and set BT context. `struct rsi_mod_ops` defines attach/detach/receive callbacks. `rsi_bt_ops` is the exported Bluetooth module ops table.

Control flow: the core RSI driver attaches a module with protocol ops, module receive paths process messages, and coexistence send paths choose HAL queues.

State and persistence: state is private to the RSI core and modules; this header only defines callbacks and IDs.

Dependencies and integration points: depends on skbuffs and integrates RSI WLAN/BT coexistence modules over SDIO/USB transports.

Risks and test signals: risks include wrong queue selection, attach/detach ordering, BT context lifetime, and host-interface-specific behavior. Test module attach/detach, packet send queue IDs, receive callbacks, SDIO/USB variants, and coexistence traffic.
