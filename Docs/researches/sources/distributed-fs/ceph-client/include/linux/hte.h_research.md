# sources/distributed-fs/ceph-client/include/linux/hte.h

## Purpose
`hte.h` defines the Hardware Timestamp Engine provider/consumer API. It lets providers register timestamp-capable chips and consumers request timestamping for logical lines, receive primary non-sleeping callbacks, optionally run secondary sleepable callbacks, enable/disable timestamps, and query clock source information.

## Important APIs, Types, And Functions
Important types are `enum hte_edge`, `enum hte_return`, `struct hte_ts_data`, `struct hte_clk_info`, callback typedefs `hte_ts_cb_t` and `hte_ts_sec_cb_t`, `struct hte_line_attr`, `struct hte_ts_desc`, `struct hte_ops`, and `struct hte_chip`. Enabled APIs include `devm_hte_register_chip()`, `hte_push_ts_ns()`, `hte_init_line_attr()`, `hte_ts_get()`, `hte_ts_put()`, `hte_request_ts_ns()`, `devm_hte_request_ts_ns()`, `of_hte_req_count()`, `hte_enable_ts()`, `hte_disable_ts()`, and `hte_get_clk_src_info()`. Disabled builds return `-EOPNOTSUPP`.

## Control Flow And State
Providers populate `hte_chip` with operations, line count, translation callbacks, and private data, then register it. Consumers initialize a descriptor, acquire a timestamp line from DT or platform data, request callbacks, and enable timestamping. Providers push timestamp data with translated line IDs. The HTE core invokes primary callbacks in non-sleeping context and runs secondary callbacks when requested. State persists in descriptors' subsystem private data, provider chip registration, line attributes, callback bindings, and clock metadata.

## Dependencies And Integration Points
It depends on errno, device model types, OF phandle arguments, clock IDs, and optional `CONFIG_HTE`. It integrates with GPIO/IRQ-like timestamp providers and consumers that need accurate edge timestamps.

## Risks
Risks include invalid line translation, edge flag mismatch with consumer IRQ setup, sleeping in primary callbacks, stale descriptor `hte_data` after put, provider pushing timestamps after unregister, sequence counter wrap assumptions, and disabled-config API signature mismatch: the stub for `hte_push_ts_ns()` takes `const struct hte_ts_data *` while the enabled declaration takes non-const.

## Test Signals
Test provider registration/unregistration, DT and platform line translation, request/put lifecycle, primary and secondary callback paths, enable/disable, rising/falling/no-setup edge modes, clock source query, timestamp sequence ordering, provider push after disable, and disabled-config builds.
