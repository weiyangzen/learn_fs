# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/clock.c

## Purpose
Implements the SCMI Clock protocol. It discovers platform-managed clocks, exposes clock rate/state/parent/OEM configuration operations to SCMI clients, and supports clock rate change notifications.

## APIs, Types, And Functions
Protocol state is `struct clock_info`, containing clock count, max async requests, notification command availability, current async request count, a devm-managed array of `struct scmi_clock_info`, and version-specific config get/set function pointers. The exported protocol ops are `count_get`, `info_get`, `rate_get`, `rate_set`, `enable`, `disable`, `state_get`, `config_oem_get`, `config_oem_set`, `parent_set`, and `parent_get`.

## Control Flow
Protocol init reads protocol attributes, allocates per-clock info, then loops over every clock to read attributes, extended names, notification support, parent support, permissions, extended config support, and rates. Rates are obtained through iterator helpers and can be either a sorted discrete list or min/max/step triplet; an SCMI quirk can repair known out-of-spec triplet replies.

At runtime, rate get/set use `CLOCK_RATE_GET` and `CLOCK_RATE_SET`; rate set optionally uses asynchronous completion when firmware advertises async capacity. Enable/disable and state/config queries dispatch to v1/v2 or v3 config formats depending on protocol version. Parent operations validate parent indexes against cached possible-parent arrays and then use firmware parent IDs.

Notifications map SCMI clock events to `CLOCK_RATE_NOTIFY` or `CLOCK_RATE_CHANGE_REQUESTED_NOTIFY`, validate per-clock support, enable/disable firmware notifications, and translate payloads into `struct scmi_clock_rate_notif_report`.

## State, Persistence, And Dependencies
Runtime state is a devm-managed cache of discovered clocks, names, rate descriptions, parent IDs, permissions, notification capabilities, and extended-config support. `atomic_t cur_async_req` tracks in-flight async rate requests. There is no persistent storage. Dependencies include SCMI protocol/transfer/iterator ops, SCMI notifier framework, quirks, sorting, and endian helpers.

## Integration Points
Registered as `SCMI_PROTOCOL_CLOCK` via `DEFINE_SCMI_PROTOCOL_REGISTER_UNREGISTER(clock, scmi_clock)`. Client clock providers consume `scmi_clk_proto_ops`; notifications feed the SCMI notifier framework for consumers interested in clock rate changes.

## Risks And Test Signals
Risks include firmware overreporting rates or parents, permissions not being enforced by older firmware, async request accounting edge cases, protocol-version field differences, invalid parent indexes, and malformed notification payloads. Signals are SCMI clock enumeration logs, common clock framework consumers using rates/parents, enable/disable/state tests, notification injection, and quirk-platform coverage for malformed rate triplets.
