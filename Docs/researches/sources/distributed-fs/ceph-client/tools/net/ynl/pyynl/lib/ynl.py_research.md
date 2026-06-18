# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/ynl.py

Purpose: Implements the Python YNL runtime for generic and raw netlink: message encoding/decoding from YAML specs, socket setup, policy introspection, do/dump/multi operation execution, extack annotation, multicast subscription, and notification polling.

Important APIs and state: Public classes include `YnlFamily`, `Netlink`, `NlError`, `NlPolicy`, `YnlException`, and `ConfigError`. Message helpers include `NlAttr`, `NlAttrs`, `NlMsg`, `NlMsgs`, `GenlMsg`, `NetlinkProtocol`, `GenlProtocol`, and `SpaceAttrs`. `YnlFamily` subclasses `SpecFamily`, binds operation names as methods, owns a netlink socket, tracks async response ids, and queues decoded notifications.

Control flow: Initialization parses the spec, resolves protocol ids through generic-netlink controller or raw protocol config, creates a netlink socket, enables CAP_ACK, EXT_ACK, and strict checking, and binds convenience operation methods. `_encode_message()` builds netlink/genetlink headers, optional fixed headers, and attributes. `_ops()` batches one or more requests, sends them, receives replies until all sequences complete, decodes matching responses, queues async notifications, raises `NlError` on kernel errors, and returns normalized single/dump/multi results.

Dependencies and integration: Depends on Python `socket`, `struct`, `selectors`, `queue`, `ipaddress`, `uuid`, the spec model from `nlspec.py`, and kernel netlink/generic-netlink controller support.

State and persistence: Maintains a live socket, receive size/debug flags, async message id set, and `Queue` of decoded notifications. No disk persistence occurs.

Risks: Attribute encoding/decoding covers many spec forms, making selector scope and sub-message resolution high-risk areas. `_encode_struct()` mutates the `vals` dictionary via `pop()`, which can surprise callers when fixed headers are used. `NlMsgs` advances by `nl_len` without explicit alignment, so malformed multi-message buffers can desynchronize parsing. Receive buffer truncation is user-controllable through debug options but guarded to at least about one page.

Test signals: Generic and raw family initialization, do/dump/multi operations, fixed headers, nested attributes, indexed arrays, multi-attrs, enums/flags including unknowns, auto scalars, bitfield32, display hints for MAC/IP/hex/UUID, sub-messages, extack bad-attribute paths, policy queries, notification subscribe/check/poll, small receive debug mode, kernel errors, and malformed attribute buffers.
