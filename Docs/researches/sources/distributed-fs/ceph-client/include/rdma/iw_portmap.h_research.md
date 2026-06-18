# sources/distributed-fs/ceph-client/include/rdma/iw_portmap.h

Purpose: Kernel iWARP port mapper interface for coordinating real and mapped socket addresses with the userspace port mapping daemon/library.

Important APIs/types/functions: Name-size constants, IWPM error enum, `struct iwpm_dev_data`, `struct iwpm_sa_data`, and functions for init/exit, PID registration/validation, add/query/remove mapping, remote info lookup, mapinfo creation/removal, and netlink callbacks including `iwpm_register_pid_cb`, `iwpm_add_mapping_cb`, `iwpm_remote_info_cb`, and `iwpm_hello_cb`.

Control flow: iWARP CM initializes a netlink client, registers the userspace daemon PID and device/interface info, creates or queries mappings during connection/listen setup, and removes mappings on teardown. Netlink callbacks update mapping tables or report daemon errors.

State and persistence behavior: Runtime-only mapping state is keyed by sockaddr tuples, daemon PID validity, netlink client, and flags.

Dependencies and integration points: Depends on Linux socket and netlink structures. Integrates with `iw_cm.h` mapped address fields and iWARP CM setup.

Risks: PID validation, duplicate add, unknown remove, and daemon absence are failure points. IPv4/IPv6 sockaddr handling must be strict. No-port-map mode changes reservation semantics.

Test signals: Daemon register/unregister, duplicate mapping, unknown mapping, remote query success/reject, IPv4/IPv6 round trips, stale PID handling, concurrent updates, and no-port-map behavior.
