# `sources/distributed-fs/ceph-client/include/linux/if_hsr.h`

Purpose: shared definitions for High-availability Seamless Redundancy and PRP devices, including protocol versions, port roles, HSR tag layout, and optional helper entry points.

Important APIs/types/functions: `enum hsr_version`, `enum hsr_port_type`, packed `struct hsr_tag`, `HSR_HLEN`, `is_hsr_master`, `hsr_get_version`, `hsr_get_port_ndev`, and `hsr_get_port_type`.

Control flow and state: helpers are real only with `CONFIG_HSR`; otherwise stubs return false or `-EINVAL`/`ERR_PTR(-EINVAL)`. Actual state is in HSR netdevices and port mappings outside the header.

Dependencies/integration: depends on kernel types and `struct net_device`; integrated with Ethernet redundancy drivers and consumers checking HSR/PRP topology.

Risks: callers must handle disabled-config stubs; HSR tag fields are packed network order and easy to misalign/mis-endian; port enum ordering is semantically constrained.

Test signals: build with and without HSR, packet tag encode/decode, master/port lookup error handling, and PRP/HSR version detection.
