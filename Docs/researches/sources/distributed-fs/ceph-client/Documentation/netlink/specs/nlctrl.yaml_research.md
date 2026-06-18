# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nlctrl.yaml

Purpose: describes the Generic Netlink controller meta-family, which lets userspace discover registered Generic Netlink families, operations, multicast groups, and policy information.

Important APIs/types/functions: family name is `nlctrl`, protocol `genetlink-legacy`, UAPI header `linux/genetlink.h`, operation prefix `ctrl-cmd-`. Definitions include `op-flags` and `attr-type`. Attribute sets include `ctrl-attrs`, `mcast-group-attrs`, `op-attrs`, `policy-attrs`, and `op-policy-attrs`. `ctrl-attrs` carries family id/name, version, header size, max attr, indexed arrays of ops and multicast groups, nested policy and op-policy data, and operation id.

Control flow: `getfamily` supports do lookup by family name and full dumps of registered families; replies include id, name, hdrsize, maxattr, groups, ops, and version. `getpolicy` dumps policy information for a family id/name and optional operation. Numeric values in request/reply entries align with legacy controller command ids.

State and persistence: the API exposes live kernel Generic Netlink registration state. Families, operations, groups, and policy data change as modules load/unload or register/unregister. No YAML-local state exists.

Dependencies and integration points: this is the discovery dependency for all Generic Netlink consumers, including many other specs in this group. It integrates with kernel genetlink registration and policy export code.

Risks: policy export can be incomplete or kernel-version-dependent. Indexed arrays and nest-type-value attributes require generator support beyond simple nested attributes. Family ids and multicast group ids are dynamic and should not be persisted by userspace without rediscovery.

Test signals: query known families by name and dump mode, validate operation and multicast group decoding, retrieve policies for operations, handle module load/unload races, and confirm generated command ids match `linux/genetlink.h`.
