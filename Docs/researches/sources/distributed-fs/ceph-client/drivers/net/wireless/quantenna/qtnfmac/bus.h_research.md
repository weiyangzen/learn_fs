<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/bus.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/bus.h

## Purpose
This header defines the Quantenna qtnfmac bus abstraction shared by the common FullMAC core and hardware transports such as PCIe. It describes firmware state, host bus operations, global bus state, bus-private storage, locking wrappers, and attach/detach APIs.

## Important APIs, Types, And Functions
Key types are `struct qtnf_frame_meta_info`, `enum qtnf_fw_state`, `struct qtnf_bus_ops`, and `struct qtnf_bus`. Inline helpers include `qtnf_fw_is_up()`, `qtnf_fw_is_attached()`, `get_bus_priv()`, `qtnf_bus_preinit()`, `qtnf_bus_stop()`, `qtnf_bus_data_tx()`, `qtnf_bus_data_tx_timeout()`, `qtnf_bus_control_tx()`, `qtnf_bus_data_rx_start()`, `qtnf_bus_data_rx_stop()`, `qtnf_bus_lock()`, and `qtnf_bus_unlock()`. External common-layer APIs are `qtnf_core_attach()` and `qtnf_core_detach()`.

## Control Flow
Transport drivers allocate a `struct qtnf_bus` with trailing private data, fill `bus_ops`, and call common attach. Common code calls inline wrappers to preinitialize transport, send control and data frames, start/stop RX, and stop the bus. The firmware state enum gates operations such as attach/running/dead checks. `bus_lock` serializes command and event processing.

## State And Persistence
`struct qtnf_bus` persists device pointer, firmware state, chip ids, MAC pointers, QLINK transport, hardware info, mux NAPI/netdev, workqueues, firmware/event work items, debugfs directory, netdev notifier, hardware id, and bus-private tail storage. Firmware state persists as a host-side state machine reflecting device lifecycle.

## Dependencies And Integration Points
Includes Linux netdevice/workqueue APIs and qtnfmac `trans.h`/`core.h`. It is included by common cfg80211/core/command paths and PCIe transport code. `qtnf_frame_meta_info` defines optional per-frame metadata for host bus multiplexing.

## Risks
`get_bus_priv()` returns `&bus->bus_priv`, whose type is a pointer to the flexible array member rather than `bus->bus_priv`; callers must treat it carefully. Operation wrappers assume required bus_ops callbacks are non-NULL except preinit/stop. Firmware state transitions must be consistent across asynchronous work and bus stop. Lock misuse can deadlock command/event handling.

## Test Signals
Validate attach/detach, firmware boot/running/dead transitions, control and data TX through PCIe ops, RX start/stop, NAPI mux behavior, bus lock contention under scan/connect/event load, and bus-private access in transport code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/bus.h -->
