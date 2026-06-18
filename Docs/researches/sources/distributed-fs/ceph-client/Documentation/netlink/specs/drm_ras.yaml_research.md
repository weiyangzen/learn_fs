# sources/distributed-fs/ceph-client/Documentation/netlink/specs/drm_ras.yaml

Purpose: specifies the DRM RAS Generic Netlink family, exposing reliability, availability, and serviceability counters from DRM drivers to userspace.

Important APIs/types/functions: the family is `drm-ras`, protocol `genetlink`, with generated UAPI header `drm/drm_ras.h`. The `node-type` enum identifies hardware/software component classes. Attribute set `node-attrs` describes registered RAS nodes with `node-id`, `device-name`, `node-name`, and `node-type`. Attribute set `error-counter-attrs` describes counters with `node-id`, `error-id`, `error-name`, and `error-value`.

Control flow: userspace first dumps `list-nodes` to discover dynamic node ids. It then calls or dumps `get-error-counter`: a do request can target `node-id` plus `error-id`, while a dump request uses `node-id` to enumerate counters for that node. Both operations require `admin-perm`, so the API is intended for privileged diagnostics rather than unprivileged telemetry.

State and persistence: the YAML stores no state. It describes kernel-maintained, dynamically registered DRM RAS nodes and live error counter values. Node ids are explicitly dynamic, so userspace should not persist them across driver reloads or reboot without rediscovery.

Dependencies and integration points: integrates DRM drivers with Generic Netlink and code generation for `drm/drm_ras.h`. Monitoring tools can build a discovery-then-counter query workflow from the two operations.

Risks: dynamic ids are easy to misuse if applications cache them. Error counter values are `u32`, which may be too small for long-running devices unless kernel drivers reset or expose counters consistently. The spec has no notification operation, so userspace must poll for changes.

Test signals: tests should verify that node dumps include all registered nodes, counter dumps require a valid node, invalid stale node ids fail predictably, generated headers match the YAML enum/attributes, and privilege checks are enforced.
