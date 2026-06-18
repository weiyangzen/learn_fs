# sources/distributed-fs/ceph-client/net/ceph/ceph_common.c

## Purpose
Provides libceph module initialization, client lifecycle management, mount/session option parsing and printing, fsid handling, compatibility reporting, and common helpers exported to CephFS/RBD.

## Important APIs, Types, and Functions
Important exported APIs include `libceph_compatible()`, `ceph_msg_type_name()`, `ceph_check_fsid()`, `ceph_compare_options()`, `ceph_parse_fsid()`, `ceph_alloc_options()`, `ceph_destroy_options()`, `ceph_parse_mon_ips()`, `ceph_parse_param()`, `ceph_print_client_options()`, `ceph_client_addr()`, `ceph_client_gid()`, `ceph_create_client()`, `ceph_destroy_client()`, `ceph_reset_client_addr()`, `__ceph_open_session()`, `ceph_open_session()`, and `ceph_wait_for_latest_osdmap()`. Module hooks are `init_ceph_lib()` and `exit_ceph_lib()`.

## Control Flow
Options are allocated with defaults, parsed through `fs_parameter_spec` tables, and destroyed by freeing names, keys, monitor addresses, and CRUSH location trees. Secret options either unarmor inline key material or request a `ceph` key from the kernel keyring. Client creation waits for randomness, allocates `struct ceph_client`, sets feature masks, initializes messenger, monitor client, and OSD client. Opening a session starts the monitor session, waits for auth, monmap, and osdmap using `auth_wq` and configured timeout, then initializes debugfs. Destroying a client stops OSD and monitor clients, finalizes messenger, cleans debugfs, destroys options, and frees memory.

Module init sets up debugfs, crypto key type, messenger, and OSD client support in that order; exit reverses those layers after checking Ceph string-table cleanup.

## State and Persistence
Runtime state is held in `struct ceph_options` and `struct ceph_client`. Options contain flags, timeouts in jiffies, monitor addresses, optional key, client name, connection modes, and CRUSH locations. Client state includes messenger instance, monc, osdc, feature bits, auth waitqueue, mount mutex, and fsid. No persistent storage is written.

## Dependencies and Integration Points
Depends on fs parser, keyrings, Ceph crypto, messenger, monitor client, OSD client, debugfs, CRUSH location parsing, IP parsing, namespaces, and feature constants. It is the main libceph module boundary consumed by CephFS and RBD.

## Risks
Option comparison uses a raw memcmp up to `mon_addr`, so struct layout changes must keep comparable fields before that offset. Secret parsing must avoid leaking keys; `secret=<hidden>` is printed. Session opening depends on waitqueue wakeups from monitor/OSD paths and can time out or be interrupted. Init/exit ordering must match dependencies. `ceph_check_fsid()` returns `-1` rather than a conventional negative errno.

## Test Signals
Parse every mount option including negated flags, invalid ranges, fsid strings, monitor IPs, keyring failures, and CRUSH locations. Compare shared versus non-shared client options across namespaces. Create/destroy clients under failure injection at monc/osdc init. Open sessions with successful maps, auth errors, timeout, and signal interruption. Build/load/unload libceph with debugfs, crypto, messenger, and osdc cleanup checks.
