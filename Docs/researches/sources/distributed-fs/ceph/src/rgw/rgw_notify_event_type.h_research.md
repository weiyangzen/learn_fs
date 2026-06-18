## sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.h

Purpose: declares notification event bitmask values and conversion helpers.

Important APIs/types: `enum EventType` assigns bit ranges to object-created, object-removed, lifecycle expiration/transition, object sync, replication, restore, and unknown events. `EventTypeList` is a vector of event types. Helpers include `operator==`, `to_string()`, `to_event_string()`, `from_string()`, and `from_string_list()`.

Control flow: event filtering can compare configured categories with concrete events via bit intersection rather than strict equality.

State and persistence: enum numeric bit values are part of configuration/runtime semantics. String conversions provide external API representation.

Dependencies/integration: lightweight `<string>`/`<vector>` header consumed by notification configuration and event dispatch code.

Risks and test signals: values exceed 32 bits, so storage must use a wide enough type. Tests should verify category masks include intended subtypes and no accidental overlap exists between event families.
