<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp.h

Purpose: defines an auto-generated generic netlink UAPI for a `psp` networking family with device, association, key, and statistics attributes.

Important APIs and types: family constants are `PSP_FAMILY_NAME` and version. `enum psp_version` lists supported PSP header/security modes. Attribute sets define device ID/ifindex and enabled/capable versions, association device/version/RX/TX keys/socket fd, key material/SPI, and stats such as key rotations, stale events, RX/TX packets/bytes/errors/auth failures. Commands cover device get/set/add/delete/change notifications, key rotation and notification, RX/TX association, and stats retrieval. Multicast groups are `mgmt` and `use`.

Control flow: userspace speaks generic netlink to enumerate/configure PSP-capable devices, rotate keys, bind associations, and query stats. Kernel networking code validates nested attributes and emits notifications on management/use groups.

State and persistence: runtime state includes per-device PSP capabilities, enabled versions, associations, key material, SPI, socket binding, and counters. Persistence depends on device/driver; the netlink ABI itself is runtime.

Dependencies and integration points: generated from a YNL spec, integrates with generic netlink/YNL tooling, network devices, PSP-aware offload or protocol code, and management agents.

Risks and test signals: risks include generated spec/header drift, key material exposure, attribute policy mistakes, multicast notification loss, and stats width/ordering compatibility. Test YNL schema validation, dev get/set, association add/remove, key rotation, notification delivery, and malformed netlink attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp.h -->
