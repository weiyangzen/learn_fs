# sources/distributed-fs/ceph-client/include/linux/seg6_genl.h

Purpose: `seg6_genl.h` is a kernel wrapper for SRv6 generic netlink UAPI definitions.

Important APIs/types/functions: It includes `<uapi/linux/seg6_genl.h>` and adds no local declarations.

Control flow: There is no local control flow. Generic netlink handlers use the UAPI attributes and command IDs through this wrapper.

State and persistence behavior: No state is stored here; netlink families and SRv6 configuration objects live in networking implementation files.

Dependencies and integration points: It integrates with generic netlink, iproute2-facing SRv6 configuration, and IPv6 segment-routing control paths.

Risks: Attribute numbering and command IDs must remain UAPI-compatible. Kernel-only changes should be made carefully to avoid userspace mismatch.

Test signals: Generic netlink policy validation, SRv6 command parsing, netlink dump compatibility, and builds of networking modules including this wrapper.
