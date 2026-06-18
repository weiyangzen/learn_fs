# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/reset.c

Purpose: This file implements the SCMI Reset protocol agent. It discovers reset domains, exposes reset/assert/deassert operations to SCMI clients, and wires reset-issued notifications into the SCMI notification framework.

Important APIs/types/functions: `struct reset_dom_info` caches per-domain async reset support, notification support, latency, and name. `struct scmi_reset_info` stores domain count, whether `RESET_NOTIFY` exists, and the domain array. Protocol ops include `scmi_reset_num_domains_get()`, `scmi_reset_name_get()`, `scmi_reset_latency_get()`, `scmi_reset_domain_reset()`, `scmi_reset_domain_assert()`, and `scmi_reset_domain_deassert()`. Notification ops include `scmi_reset_notify_supported()`, `scmi_reset_set_notify_enabled()`, and `scmi_reset_fill_custom_report()`.

Control flow: `scmi_reset_protocol_init()` allocates private state, calls `PROTOCOL_ATTRIBUTES`, allocates one descriptor per domain, and retrieves each domain's attributes/name/latency. Reset requests validate the domain, add the asynchronous flag for autonomous resets when supported, send `RESET`, and either wait for delayed response or synchronous completion. Notification enablement sends `RESET_NOTIFY` per domain and report filling decodes agent, domain, and reset state.

State and persistence: Domain metadata is cached in devm-managed memory for the protocol instance. Notification enablement state is managed by the generic notification core and firmware. No persistent storage is used.

Dependencies and integration points: It depends on `protocols.h`, `notify.h`, Linux module support, and public `linux/scmi_protocol.h` reset types. It registers as `SCMI_PROTOCOL_RESET` with ops and `reset_protocol_events`, so reset controller drivers can consume it.

Risks and edge cases: Domain lookup returns `-EINVAL` for out-of-range IDs. Per-domain attribute failures during init are ignored by the loop, leaving default zeroed entries, so missing firmware data can surface later as empty names or unsupported flags. Extended name lookup failures are intentionally nonfatal. Async reset delayed-response validation is delegated to core transport behavior.

Test signals: Firmware test cases should cover zero/multiple domains, extended names, latency `U32_MAX` normalization to zero, sync and async reset commands, assert/deassert, invalid domain IDs, `RESET_NOTIFY` absence, and decoding of reset-issued reports.
