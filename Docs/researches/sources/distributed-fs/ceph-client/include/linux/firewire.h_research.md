# sources/distributed-fs/ceph-client/include/linux/firewire.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firewire.h` defines the Linux FireWire core interface, including CSR constants, card/device/unit structures, transactions, address handlers, descriptors, and isochronous transfer contexts. The source was read as a complete 625-line file for this report.

## Important APIs, Types, and Functions

Important exports include CSR register/key constants, `struct fw_csr_iterator`, `fw_csr_iterator_init`, `fw_csr_iterator_next`, `fw_csr_string`, `fw_bus_type`, `struct fw_card`, `fw_card_get`, `fw_card_put`, `fw_card_read_cycle_time`, `struct fw_attribute_group`, device quirks/state enums, `struct fw_device`, `struct fw_unit`, `struct fw_driver`, transaction callback types, `struct fw_packet`, `struct fw_transaction`, `struct fw_address_handler`, `struct fw_address_region`, address-handler APIs, `fw_send_response`, `fw_send_request`, `fw_send_request_with_tstamp`, `fw_cancel_transaction`, `fw_run_transaction`, descriptor APIs, `struct fw_iso_packet`, `struct fw_iso_buffer`, `struct fw_iso_context`, iso context create/queue/start/stop/destroy APIs, and `fw_iso_resource_manage`.

## Control Flow

FireWire cards register core state and workqueues. Devices and units are discovered from CSR config ROMs; drivers probe `fw_unit` instances. Outbound transactions are built as `fw_transaction`/`fw_packet`, sent through the card driver, and completed through callbacks, sometimes synchronously for local/error cases. Inbound address handlers run in RCU read-side context and must respond. Isochronous contexts queue packet descriptors and DMA buffers, then schedule work to flush completions.

## State and Persistence Behavior

State includes card generation/node IDs, transaction label allocation, split timeout tracking, bus manager work, topology and speed maps, device state/config ROMs, unit directories, pending transactions/timers, address handler refs, and DMA-mapped iso buffers. This is runtime bus state reset by topology changes.

## Dependencies and Integration Points

The header depends on device model, DMA mapping, krefs, workqueues, timers, completions, sysfs, atomics, and byte order helpers. It integrates with FireWire host controller drivers, device/unit drivers, sysfs, CSR/config ROM parsing, asynchronous request/response transactions, and isochronous audio/video streaming.

## Risks and Edge Cases

Generation must be read before node ID to avoid sending to stale nodes after bus reset. Address callbacks run in RCU context and cannot sleep or recursively initiate outbound requests. Iso DMA buffers are not normally kernel-mapped. Transaction callbacks may run in current or workqueue context.

## Test Signals

FireWire bus reset/device discovery tests, config ROM parsing tests, async transaction timeout/cancel tests, generation/node-id race tests, address handler response tests, and isochronous transmit/receive DMA tests.
