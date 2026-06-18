# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.h

Purpose: forwarding data model and helper declarations for usNIC.

Important APIs/types: defines `struct usnic_fwd_dev`, `struct usnic_fwd_flow`, `struct usnic_filter_action`, lifecycle/update APIs, flow allocation/free APIs, QP enable/disable APIs, and inline initializers for custom usNIC and UDP filters.

Control flow: QP group code uses inline filter initializers, then calls `usnic_fwd_alloc_flow()` and QP enable/disable helpers as state changes. Main netdev notifier code updates cached forwarding-device state through setters.

State and persistence: makes explicit the cached PF forwarding state and firmware flow identity that persists across a QP group's lifetime.

Dependencies and integration: includes Linux netdev/PCI/IP headers, usNIC ABI/packet constants, and ENIC `vnic_devcmd` filter/action types.

Risks: header comments require callers to monitor netdev reset/down events and free flows immediately; failure to honor that contract leaves stale firmware steering. Inline filter construction must stay aligned with ENIC firmware expectations.

Test signals: compile coverage, filter field inspection in ENIC devcmd traces, QP traffic steering, and flow cleanup on netdev events.
