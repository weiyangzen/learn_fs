# subset-b-009317 research

Grouped research report for Linux UAPI headers bundled with strace under `sources/test-tools/strace/bundled/linux/include/uapi/linux`. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/eventpoll.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/eventpoll.h

Purpose: defines the userspace ABI constants and structs for epoll control, event masks, and epoll-specific ioctls. Important APIs/types/functions: `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, event bits such as `EPOLLIN`, `EPOLLOUT`, `EPOLLET`, `EPOLLONESHOT`, `EPOLLWAKEUP`, `EPOLLEXCLUSIVE`, `struct epoll_event`, `struct epoll_params`, `EPIOCSPARAMS`, and `EPIOCGPARAMS`.

Control flow: the header has no executable flow; it describes values passed to `epoll_create1`, `epoll_ctl`, `epoll_wait`, and `ioctl` on epoll file descriptors. State/persistence behavior: epoll interest-list state lives in the kernel; `data` is userspace payload copied through readiness events, while `epoll_params` configures busy-poll behavior. Dependencies/integration: includes `linux/fcntl.h` for `O_CLOEXEC`, `linux/types.h`, and ioctl encoding macros transitively. Strace consumes these constants to decode epoll syscalls and ioctls. Risks/test signals: ABI alignment is critical, especially packed `struct epoll_event` on x86-64 for 32-bit compatibility. Tests should check decoded opcodes, flag bitmasks, busy-poll ioctls, and architecture-specific struct size/alignment.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/eventpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/falloc.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/falloc.h

Purpose: defines `fallocate(2)` mode bits for preallocation, hole punching, range transforms, copy-on-write unsharing, and zeroing. Important APIs/types/functions: `FALLOC_FL_KEEP_SIZE`, `FALLOC_FL_PUNCH_HOLE`, `FALLOC_FL_COLLAPSE_RANGE`, `FALLOC_FL_ZERO_RANGE`, `FALLOC_FL_INSERT_RANGE`, `FALLOC_FL_UNSHARE_RANGE`, and `FALLOC_FL_WRITE_ZEROES`.

Control flow: behavior is selected by userspace through the `mode` argument to `fallocate`; the kernel/filesystem validates combinations and translates them into allocation, deallocation, or layout mutation. State/persistence behavior: operations may allocate extents, convert ranges to unwritten extents, remove or insert byte ranges changing file size, unshare shared CoW blocks, or prepare zeroed ranges for future overwrite. Dependencies/integration: no includes are needed; values are shared by libc, filesystems, strace decoders, and tests issuing `fallocate`. Risks/test signals: invalid flag combinations and EOF-crossing collapse/insert cases are common failure points. Tests should verify bitmask decoding, filesystem-specific `EINVAL` behavior, `KEEP_SIZE` interactions, and that layout-changing flags report size and extent effects correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/falloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fcntl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/fcntl.h

Purpose: extends architecture `fcntl` definitions with Linux-specific commands, file seals, directory notifications, `*at` flags, pidfd/root pseudo-fds, delegation structs, and write lifetime hints. Important APIs/types/functions: `F_SETLEASE`, `F_NOTIFY`, `F_DUPFD_QUERY`, `F_CREATED_QUERY`, `F_DUPFD_CLOEXEC`, pipe size commands, `F_ADD_SEALS`, `F_GET_SEALS`, `F_SEAL_*`, `F_GET/SET_RW_HINT`, `struct delegation`, `DN_*`, `AT_*`, `PIDFD_SELF_THREAD`, `FD_PIDFS_ROOT`, and `FD_INVALID`.

Control flow: userspace supplies command constants to `fcntl(2)` or flag constants to path-based syscalls; the kernel dispatches by command number or interprets per-syscall flag bits. State/persistence behavior: leases, notifications, pipe capacities, seals, delegations, and write hints alter kernel object or inode state; `AT_*` flags affect one syscall traversal/check without persistent state. Dependencies/integration: includes `asm/fcntl.h`, `linux/openat2.h`, and `linux/types.h`. Strace must decode overlapping `AT_*` values according to syscall context. Risks/test signals: overlapping per-syscall flags such as `AT_EACCESS`/`AT_REMOVEDIR`, signed negative pseudo-fd ranges, and newly added commands are decode risks. Tests should cover contextual flag rendering, seal bitmasks, and command numbers relative to `F_LINUX_SPECIFIC_BASE`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fib_rules.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/fib_rules.h

Purpose: defines rtnetlink ABI for policy routing rules, including rule headers, selector attributes, action codes, and range structs. Important APIs/types/functions: `struct fib_rule_hdr`, `struct fib_rule_uid_range`, `struct fib_rule_port_range`, `FIB_RULE_*`, `FRA_*`, and `FR_ACT_*`.

Control flow: userspace sends rtnetlink rule messages with a `fib_rule_hdr` and nested `FRA_*` attributes; the kernel evaluates selectors such as source/destination prefixes, marks, interfaces, UID ranges, IP protocol, ports, DSCP, and flow label before applying an `FR_ACT_*` action. State/persistence behavior: successful netlink operations add, replace, list, or delete routing-policy database entries in a network namespace. Dependencies/integration: includes `linux/types.h` and `linux/rtnetlink.h`; integrates with `ip rule`, routing table lookup, l3mdev, and netfilter marks. Risks/test signals: extended table IDs, detached interface flags, inverted matches, `FRA_*_MASK` attributes, and goto targets are easy to mis-decode. Tests should validate netlink attribute names, range payload sizes, and action rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fib_rules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fiemap.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/fiemap.h

Purpose: defines the `FS_IOC_FIEMAP` extent-mapping ABI used to query logical-to-physical file extents. Important APIs/types/functions: `struct fiemap`, `struct fiemap_extent`, `FIEMAP_FLAG_SYNC`, `FIEMAP_FLAG_XATTR`, `FIEMAP_FLAG_CACHE`, `FIEMAP_FLAGS_COMPAT`, `FIEMAP_MAX_OFFSET`, and `FIEMAP_EXTENT_*` flags.

Control flow: userspace initializes `fm_start`, `fm_length`, `fm_flags`, and `fm_extent_count`, then the filesystem fills `fm_mapped_extents` and the flexible `fm_extents` array. State/persistence behavior: normally observational, except `FIEMAP_FLAG_SYNC` can force dirty data to disk before mapping; returned flags describe delayed allocation, unwritten, encrypted, inline, tail-packed, shared, merged, or final extents. Dependencies/integration: includes `linux/types.h`; `FS_IOC_FIEMAP` is declared in `fs.h`. Strace must decode nested extent arrays only up to the mapped count and userspace buffer limit. Risks/test signals: flexible arrays, reserved fields, unsupported flags, and partial results are common ABI pitfalls. Tests should cover zero extent count probes, `LAST` termination, and flag combinations such as `DELALLOC` implying unknown location.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fiemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fs.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/fs.h

Purpose: central generic filesystem/block/procfs UAPI header for file limits, seek constants, clone/dedupe/trim structs, filesystem attributes, block and filesystem ioctls, inode flags, per-IO `RWF_*` bits, pagemap scanning, proc maps querying, and filesystem shutdown. Important APIs/types/functions: `struct file_clone_range`, `struct fstrim_range`, `struct fsuuid2`, `struct fs_sysfs_path`, `struct logical_block_metadata_cap`, `struct file_dedupe_range(_info)`, `struct fsxattr`, `struct file_attr`, block `BLK*` ioctls, `FICLONE`, `FIDEDUPERANGE`, `FS_IOC_*`, `FS_*_FL`, `RWF_*`, `struct pm_scan_arg`, `struct page_region`, `struct procmap_query`, and `FS_IOC_SHUTDOWN`.

Control flow: userspace calls ioctl or read/write-vector syscalls with these constants and structs; the kernel dispatches to block, filesystem, procfs, or VFS handlers. State/persistence behavior: some interfaces mutate persistent state, including clone/dedupe extent sharing, trims/discards, labels, UUID exposure, inode flags, xattrs-like attributes, fscrypt policy ioctls included via `fscrypt.h`, and shutdown. Others are queries or per-operation flags. Dependencies/integration: includes `linux/limits.h`, `linux/ioctl.h`, `linux/types.h`, `linux/fscrypt.h`, and `linux/mount.h`. Risks/test signals: large ABI surface, 32/64-bit ioctl argument differences, flexible arrays, versioned `size` fields, and newly added procfs ioctls require precise decoding. Tests should cover representative ioctl numbers, inode flag masks, `RWF_SUPPORTED`, pagemap category masks, and procmap buffer-size error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fscrypt.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/fscrypt.h

Purpose: defines the fscrypt userspace ioctl ABI for encryption policies, keys, key status, nonce queries, and legacy compatibility aliases. Important APIs/types/functions: `FSCRYPT_POLICY_FLAGS_*`, encryption modes such as `FSCRYPT_MODE_AES_256_XTS`, `FSCRYPT_MODE_ADIANTUM`, `FSCRYPT_MODE_AES_256_HCTR2`, `struct fscrypt_policy_v1`, `struct fscrypt_policy_v2`, `struct fscrypt_get_policy_ex_arg`, `struct fscrypt_key_specifier`, `struct fscrypt_add_key_arg`, `struct fscrypt_remove_key_arg`, `struct fscrypt_get_key_status_arg`, and `FS_IOC_*ENCRYPTION*`.

Control flow: userspace sets or queries directory encryption policy, adds raw or keyring-backed keys, removes keys for one or all users, and queries key status via ioctls. State/persistence behavior: policies persist in filesystem metadata; keys are runtime kernel key state with user counts and incomplete-removal status; v1 descriptor and v2 identifier semantics differ. Dependencies/integration: includes `linux/ioctl.h` and `linux/types.h`, and is included by `fs.h`. Risks/test signals: flexible raw key payloads, `policy_size` version negotiation, deprecated v1 names, reserved fields, and hardware-wrapped key flags must be decoded carefully. Tests should cover v1/v2 policy structs, add/remove/status ioctls, absent/present/incompletely removed statuses, and legacy alias rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/fscrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/futex.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/futex.h

Purpose: defines futex syscall command numbers, private/realtime modifiers, futex2 wait flags, vector-wait structs, robust-list ABI structs, owner/waiter bits, and `FUTEX_WAKE_OP` encoding. Important APIs/types/functions: `FUTEX_WAIT`, `FUTEX_WAKE`, PI operations, `FUTEX_WAIT_BITSET`, `FUTEX_LOCK_PI2`, `FUTEX_PRIVATE_FLAG`, `FUTEX_CLOCK_REALTIME`, `FUTEX2_*`, `FUTEX_WAITV_MAX`, `struct futex_waitv`, `struct robust_list`, `struct robust_list_head`, `FUTEX_WAITERS`, `FUTEX_OWNER_DIED`, `FUTEX_TID_MASK`, `FUTEX_OP_*`, and `FUTEX_OP()`.

Control flow: userspace synchronization libraries manipulate user memory, then invoke futex operations when blocking, waking, requeueing, or handling priority inheritance. Robust lists are registered per thread so the kernel can repair owned futexes at thread exit. State/persistence behavior: futex state lives mostly in userspace words; kernel wait queues and robust-list registration are runtime-only. Dependencies/integration: includes `linux/types.h`; integrates deeply with pthread mutexes, PI locking, and strace syscall argument decoding. Risks/test signals: command masks, bitset matching, futex2 size/private bit layout, robust-list pointer walking, and `FUTEX_WAKE_OP` packed fields are easy to misinterpret. Tests should cover private variants, realtime modifier, vector wait element decoding, and owner-died bit display.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/gen_stats.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/gen_stats.h

Purpose: defines generic netlink traffic-control statistics attributes and payload structs shared by qdisc/class/action reporting. Important APIs/types/functions: `TCA_STATS_*`, `struct gnet_stats_basic`, `struct gnet_stats_rate_est`, `struct gnet_stats_rate_est64`, `struct gnet_stats_queue`, and `struct gnet_estimator`.

Control flow: kernel traffic-control components nest these attributes in netlink dumps or responses; userspace decodes byte/packet counters, rate estimates, queue depth, drops, requeues, overlimits, and estimator configuration. State/persistence behavior: statistics are runtime counters maintained by network subsystems; estimator configuration affects sampling behavior but the header has no storage logic. Dependencies/integration: includes `linux/types.h`; integrates with rtnetlink `tc` tooling and strace netlink decoders. Risks/test signals: 32-bit versus 64-bit packet/rate attributes, hardware-specific `TCA_STATS_BASIC_HW`, and padding attributes can cause decode drift. Tests should validate attribute names, struct sizes, and both `RATE_EST` and `RATE_EST64` output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/gen_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/genetlink.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/genetlink.h

Purpose: defines the generic netlink header, family ID ranges, capability flags, reserved IDs, and controller command/attribute namespace. Important APIs/types/functions: `GENL_NAMSIZ`, `GENL_MIN_ID`, `GENL_MAX_ID`, `struct genlmsghdr`, `GENL_HDRLEN`, `GENL_ADMIN_PERM`, `GENL_CMD_CAP_*`, `GENL_ID_CTRL`, `CTRL_CMD_*`, `CTRL_ATTR_*`, `CTRL_ATTR_OP_*`, `CTRL_ATTR_MCAST_GRP_*`, and `CTRL_ATTR_POLICY_*`.

Control flow: generic netlink messages carry an nlmsghdr followed by `genlmsghdr`; the controller family creates, deletes, dumps, and describes families, ops, multicast groups, and policies. State/persistence behavior: family registration state is maintained in the kernel and exposed dynamically; this header only pins message formats and reserved ranges. Dependencies/integration: includes `linux/types.h` and `linux/netlink.h`; consumed by all generic-netlink families and strace netlink decoding. Risks/test signals: nested policy attributes, command capability flags, static versus dynamically allocated family IDs, and header alignment must be stable. Tests should decode controller dumps, multicast-group entries, op flags, and policy dumps.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/genetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/gpio.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/gpio.h

Purpose: defines the GPIO character-device userspace ABI, including current v2 line configuration/events and deprecated v1 handle/event ioctls. Important APIs/types/functions: `GPIO_MAX_NAME_SIZE`, `struct gpiochip_info`, `GPIO_V2_LINES_MAX`, `enum gpio_v2_line_flag`, `struct gpio_v2_line_values`, `struct gpio_v2_line_attribute`, `struct gpio_v2_line_config`, `struct gpio_v2_line_request`, `struct gpio_v2_line_info`, `struct gpio_v2_line_info_changed`, `struct gpio_v2_line_event`, v1 `struct gpioline_info`, `struct gpiohandle_request`, `struct gpioevent_request`, and `GPIO_*_IOCTL`.

Control flow: userspace opens a gpiochip character device, queries chip/line info, requests one or more lines, then uses the returned anonymous request fd to get/set values, reconfigure lines, or read edge events. State/persistence behavior: line ownership, direction, bias, debounce, output value, event clock, and event buffering are runtime kernel state tied to request fds; no persistent configuration is defined here. Dependencies/integration: includes `linux/const.h`, `linux/ioctl.h`, and `linux/types.h`. Risks/test signals: v1/v2 struct differences, bitmap masks, reserved padding, event sequence numbers, and ioctl direction/size encodings must stay exact. Tests should cover v2 multi-line requests, line-info watch/unwatch, event decoding, and deprecated v1 ioctl compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/hiddev.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/hiddev.h

Purpose: defines the legacy HID device character-interface ABI for reading HID events and querying or setting report, field, collection, string, and usage data. Important APIs/types/functions: `struct hiddev_event`, `struct hiddev_devinfo`, `struct hiddev_collection_info`, `struct hiddev_string_descriptor`, `struct hiddev_report_info`, `struct hiddev_field_info`, `struct hiddev_usage_ref`, `struct hiddev_usage_ref_multi`, `HID_REPORT_ID_*`, `HID_REPORT_TYPE_*`, `HID_FIELD_*`, `HIDIOCG*`, `HIDIOCS*`, and `HIDDEV_FLAG_*`.

Control flow: userspace enumerates reports with `HIDIOCGREPORTINFO`, fields with `HIDIOCGFIELDINFO`, usage codes/values with `HIDIOCGUCODE` and `HIDIOCGUSAGE`, optionally sets usages and sends reports. Reads return event or usage-reference oriented records depending on flags. State/persistence behavior: report values and flags are runtime device/interface state; `SUSAGE` followed by `SREPORT` can change device output/feature state. Dependencies/integration: includes `linux/types.h`; integrates with USB/HID drivers and strace ioctl decoders. Risks/test signals: variable-length name/phys ioctls, `HID_REPORT_ID_FIRST/NEXT` iteration, multi-usage arrays up to 1024 values, and flag-dependent read formats are decode risks. Tests should exercise descriptor traversal and representative get/set ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/hiddev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_addr.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_addr.h

Purpose: defines rtnetlink address-message ABI for interface IP addresses, cache lifetimes, flags, and address-origin protocol values. Important APIs/types/functions: `struct ifaddrmsg`, `IFA_*`, `IFA_F_*`, `struct ifa_cacheinfo`, `IFA_RTA`, `IFA_PAYLOAD`, and `IFAPROT_*`.

Control flow: userspace sends or receives `RTM_NEWADDR`, `RTM_DELADDR`, and dump messages with `ifaddrmsg` followed by `IFA_*` attributes. `IFA_FLAGS` extends the u8 `ifa_flags` field and takes precedence when present. State/persistence behavior: address entries persist in the network namespace until removed or expired; cache info tracks preferred/valid lifetimes and timestamps. Dependencies/integration: includes `linux/types.h` and `linux/netlink.h`; integrates with IPv4/IPv6 address configuration, router advertisements, and `ip addr`. Risks/test signals: point-to-point semantics where `IFA_ADDRESS` is peer/destination and `IFA_LOCAL` is local address, extended flags, and lifetime units can be misdecoded. Tests should cover secondary/temporary aliases, stable privacy, no-prefix-route, proto values, and cacheinfo payloads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_addrlabel.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_addrlabel.h

Purpose: defines the netlink ABI for IPv6 address-label configuration used by source/destination address selection policy. Important APIs/types/functions: `struct ifaddrlblmsg`, `IFAL_ADDRESS`, `IFAL_LABEL`, and `IFAL_MAX`.

Control flow: userspace exchanges rtnetlink messages containing `ifaddrlblmsg` and attributes for prefix address and label; the kernel applies label rules by family, prefix length, interface index, and sequence. State/persistence behavior: address-label rules are network-namespace routing/address-selection state and remain until changed or namespace teardown. Dependencies/integration: includes `linux/types.h`; integrates with IPv6 policy routing/address selection and tools such as `ip addrlabel`. Risks/test signals: the header is small, but reserved fields, prefix lengths, sequence values, and attribute IDs must be decoded accurately. Tests should verify netlink message rendering for add/delete/dump address-label entries and unknown future flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_addrlabel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_alg.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_alg.h

Purpose: defines the AF_ALG socket address and options used by userspace to access kernel crypto algorithms. Important APIs/types/functions: `struct sockaddr_alg`, `struct sockaddr_alg_new`, `struct af_alg_iv`, `ALG_SET_KEY`, `ALG_SET_IV`, `ALG_SET_OP`, `ALG_SET_AEAD_ASSOCLEN`, `ALG_SET_AEAD_AUTHSIZE`, `ALG_SET_DRBG_ENTROPY`, `ALG_SET_KEY_BY_KEY_SERIAL`, `ALG_OP_DECRYPT`, and `ALG_OP_ENCRYPT`.

Control flow: userspace creates an AF_ALG socket, binds with an algorithm type/name, sets keys/options with `setsockopt`, accepts operation sockets, and sends/receives crypto data. State/persistence behavior: algorithm binding, keys, IVs, operation mode, AEAD sizes, and DRBG entropy are runtime socket state. Dependencies/integration: includes `linux/types.h`; integrates with kernel crypto API and strace socket/setsockopt decoders. Risks/test signals: `sockaddr_alg_new` uses a flexible algorithm-name field because names can exceed the legacy 64-byte array, and `af_alg_iv` is variable length. Tests should cover bind decoding for legacy/new sockaddr forms, option payloads, encrypt/decrypt operation display, and key-by-serial values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_alg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_bonding.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_bonding.h

Purpose: defines bonding driver userspace ABI constants, legacy ioctl numbers, modes, link/slave states, transmit hash policies, 802.3ad state bits, query structs, and xstats attributes. Important APIs/types/functions: `BOND_ABI_VERSION`, `BOND_*_OLD`, `BOND_MODE_*`, `BOND_LINK_*`, `BOND_STATE_*`, `BOND_XMIT_POLICY_*`, `LACP_STATE_*`, `ifbond`, `ifslave`, `struct ad_info`, `BOND_XSTATS_*`, and `BOND_3AD_STAT_*`.

Control flow: older tools use private ioctls to enslave/release/query interfaces, while newer bonding configuration also appears through rtnetlink attributes in `if_link.h`. The kernel reports bond mode, number of slaves, MII monitor, slave state, and LACP/3AD details. State/persistence behavior: bond membership, active/backup state, mode, hash policy, and LACP counters are network-device state in a namespace and may persist as long as the bond exists. Dependencies/integration: includes `linux/if.h`, `linux/types.h`, and `linux/if_ether.h`. Risks/test signals: old ioctl compatibility, ABI versioning, signed small fields, and xstats nesting are risk points. Tests should decode modes, link states, LACP state bits, old private commands, and 3AD statistics.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_bonding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_bridge.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_bridge.h

Purpose: defines Linux bridge ABI for legacy bridge ioctls, STP state structs, bridge/port flags, VLAN filtering, MRP, CFM, MST, VLAN database, multicast database, multicast stats, boolean options, and querier state attributes. Important APIs/types/functions: `BRCTL_*`, `BR_STATE_*`, `struct __bridge_info`, `struct __port_info`, `struct __fdb_entry`, `IFLA_BRIDGE_*`, `struct bridge_vlan_info`, `struct bridge_vlan_xstats`, MRP structs, CFM enums, `struct bridge_stp_xstats`, `struct br_vlan_msg`, `BRIDGE_VLANDB_*`, `MDBA_*`, `struct br_port_msg`, `struct br_mdb_entry`, `struct br_mcast_stats`, `enum br_boolopt_id`, and `struct br_boolopt_multi`.

Control flow: bridge state is configured and dumped through rtnetlink nested attributes, with old ioctl constants retained for compatibility. VLAN/MDB operations use dedicated RTM headers and nested attribute sets. State/persistence behavior: bridge device configuration, FDB/MDB entries, VLANs, MRP/CFM/MST state, multicast querier behavior, and boolean options are runtime network namespace state. Dependencies/integration: includes `linux/types.h`, `linux/if_ether.h`, and `linux/in6.h`. Risks/test signals: deep nested attributes, union address fields, timer units, deprecated ioctl paths, source-specific multicast entries, and offload flags are high-risk decoders. Tests should cover bridge VLAN dumps, MDB set/get, MRP/CFM payloads, boolean option masks, and xstats.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_ether.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_ether.h

Purpose: defines Ethernet frame constants, MTU bounds, EtherType/protocol IDs, Linux internal pseudo-protocol IDs, and the packed Ethernet header struct. Important APIs/types/functions: `ETH_ALEN`, `ETH_HLEN`, `ETH_ZLEN`, `ETH_DATA_LEN`, `ETH_FRAME_LEN`, `ETH_MIN_MTU`, `ETH_MAX_MTU`, many `ETH_P_*` values, `ETH_P_802_3_MIN`, `__UAPI_DEF_ETHHDR`, and `struct ethhdr`.

Control flow: packet sockets, network drivers, filters, and protocol decoders use `h_proto`/protocol values to classify frame payloads; no executable flow exists in the header. State/persistence behavior: no persistent state; constants define wire-format sizes and packet protocol identifiers. Dependencies/integration: includes `linux/types.h`; used by bonding, bridge, raw packet sockets, eBPF filters, and strace packet/protocol decoding. Risks/test signals: byte order for `h_proto`, unofficial/reserved protocol values, libc compatibility around `struct ethhdr`, and max/min MTU constants can drift. Tests should validate protocol-name decoding, packed struct layout, and use of host versus network byte order in syscall traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_ether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_link.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_link.h

Purpose: defines rtnetlink link-management ABI for generic netdevice stats, top-level link attributes, AF-specific data, bridge attributes, many virtual device kinds, SR-IOV VF management, stats filtering, XDP attachment, and tunnel/device-specific nested attributes. Important APIs/types/functions: `struct rtnl_link_stats`, `struct rtnl_link_stats64`, `struct rtnl_hw_stats64`, `struct rtnl_link_ifmap`, top-level `IFLA_*`, `IFLA_INET*`, `IFLA_BR*`, `IFLA_BRPORT*`, `IFLA_INFO_*`, VLAN/MACVLAN/VRF/MACsec/XFRM/IPVLAN/netkit/VXLAN/GENEVE/GTP/BOND/VF/IPoIB/HSR/TUN/RMNET/MCTP/DSA/OVPN enums and structs, `struct if_stats_msg`, `IFLA_STATS_*`, `LINK_XSTATS_TYPE_*`, `XDP_FLAGS_*`, and `IFLA_XDP_*`.

Control flow: userspace sends `RTM_NEWLINK`, `RTM_DELLINK`, `RTM_GETLINK`, and stats messages containing `ifinfomsg` plus nested `IFLA_*` attributes. Link-kind-specific payloads hang under `IFLA_LINKINFO`/`IFLA_INFO_DATA`; stats and offload data use separate nested filters. State/persistence behavior: link attributes create, configure, move, or query network devices and their namespace-local state; counters are runtime, while settings such as MTU, qdisc, bridge parameters, XDP program attachments, VF parameters, and tunnel options persist while the device exists. Dependencies/integration: includes `linux/types.h` and `linux/netlink.h`, with related bridge/bond constants in sibling headers. Risks/test signals: this is a large, rapidly growing ABI. Decode risks include nested kind-specific namespaces, 32/64-bit stats, aliases, deprecated names, mask/value flag pairs, and variable hardware support. Tests should exercise top-level link dumps, linkinfo kinds, bridge ports, VXLAN/GENEVE, VF lists, XDP attach flags, stats filters, and unknown future attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_xdp.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/if_xdp.h

Purpose: defines AF_XDP socket ABI for high-performance packet I/O through shared UMEM rings, mmap offsets, socket options, descriptors, statistics, and TX metadata. Important APIs/types/functions: `XDP_SHARED_UMEM`, `XDP_COPY`, `XDP_ZEROCOPY`, `XDP_USE_NEED_WAKEUP`, `XDP_USE_SG`, `struct sockaddr_xdp`, `XDP_RING_NEED_WAKEUP`, `struct xdp_ring_offset`, `struct xdp_mmap_offsets`, `XDP_*` socket options, `struct xdp_umem_reg`, `struct xdp_statistics`, `struct xdp_options`, mmap pgoff constants, `struct xsk_tx_metadata`, `struct xdp_desc`, `XDP_PKT_CONTD`, and `XDP_TX_METADATA`.

Control flow: userspace creates an AF_XDP socket, binds to interface/queue, registers UMEM, configures rings, mmaps producer/consumer queues, then exchanges descriptors with kernel or driver. State/persistence behavior: UMEM registration, ring sizes, wakeup mode, zero-copy/copy selection, stats, and shared-UMEM fd relationships are runtime socket state. Dependencies/integration: includes `linux/types.h`; integrates with XDP programs, network drivers, poll/sendto wakeups, and strace socket/setsockopt/mmap decoding. Risks/test signals: ring mmap offsets exceed 32 bits, unaligned chunk address packing, multi-buffer descriptor continuation, and TX metadata unions need careful decoding. Tests should cover bind flags, UMEM registration flags, statistics/options getsockopt, and descriptor option bits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/if_xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/in.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/in.h

Purpose: defines IPv4 socket ABI constants, protocol numbers, address structs, socket options, multicast request/filter structs, packet-info structs, socket address layout, classful address macros, and special IPv4 addresses. Important APIs/types/functions: `IPPROTO_*`, `struct in_addr`, `IP_*` socket options, `IP_PMTUDISC_*`, multicast `MCAST_*`, `struct ip_mreq`, `struct ip_mreqn`, `struct ip_mreq_source`, `struct ip_msfilter`, `IP_MSFILTER_SIZE`, `struct group_req`, `struct group_source_req`, `struct group_filter`, `GROUP_FILTER_SIZE`, `struct in_pktinfo`, `struct sockaddr_in`, `IN_CLASS*`, `INADDR_*`, and `IN_LOOPBACK`.

Control flow: applications use these constants with `socket`, `bind`, `connect`, `setsockopt`, `getsockopt`, `sendmsg`, and multicast membership calls. State/persistence behavior: socket options and multicast memberships are runtime socket state; addresses and protocol constants define wire/API interpretation. Dependencies/integration: includes `linux/types.h`, `linux/stddef.h`, `linux/libc-compat.h`, `linux/socket.h`, and `asm/byteorder.h`. Risks/test signals: libc compatibility gates, flexible multicast filters, option-number collisions, byte-order assumptions, and newer protocols above 255 such as SMC/MPTCP are decode risks. Tests should cover socket option names, multicast structs with variable source counts, `sockaddr_in`, and protocol enum rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/in6.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/in6.h

Purpose: defines IPv6 address/socket ABI types, multicast request struct, flow-label management, flowinfo masks, extension-header protocol constants, TLV option codes, IPv6 socket options, PMTU modes, and source address preferences. Important APIs/types/functions: `struct in6_addr`, `struct sockaddr_in6`, `struct ipv6_mreq`, `struct in6_flowlabel_req`, `IPV6_FL_*`, `IPV6_FLOWINFO_*`, `IPPROTO_HOPOPTS`, `IPPROTO_ICMPV6`, `IPV6_TLV_*`, `IPV6_*` socket options, `IPV6_PMTUDISC_*`, and `IPV6_PREFER_SRC_*`.

Control flow: userspace passes these constants and structs through IPv6 sockets, ancillary data, flow-label management, multicast membership, and path-MTU/source-selection options. State/persistence behavior: most options are runtime socket state; flow-label requests can allocate/renew/release kernel flow-label state with expiration/linger controls. Dependencies/integration: includes `linux/types.h` and `linux/libc-compat.h`; multicast group operation numbers intentionally share values with IPv4 definitions from `in.h`. Risks/test signals: libc compatibility gates, host-order flowinfo masks versus network-order fields, obsolete priority definitions, shared multicast options, and flow-label lifecycle values can be misdecoded. Tests should cover `sockaddr_in6`, flowlabel request actions, PMTU options, source preference bitmasks, and extension-header constants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/in6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/inet_diag.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/inet_diag.h

Purpose: defines inet socket diagnostic netlink ABI for querying TCP/DCCP/raw sockets, bytecode filters, diagnostic responses, timer states, extension attributes, socket options, memory info, and congestion-control info. Important APIs/types/functions: `TCPDIAG_GETSOCK`, `DCCPDIAG_GETSOCK`, `struct inet_diag_sockid`, `struct inet_diag_req`, `struct inet_diag_req_v2`, `struct inet_diag_req_raw`, `INET_DIAG_REQ_*`, `struct inet_diag_bc_op`, `INET_DIAG_BC_*`, `struct inet_diag_hostcond`, `struct inet_diag_markcond`, `struct inet_diag_msg`, `IDIAG_TIMER_*`, `INET_DIAG_*`, `struct inet_diag_meminfo`, `struct inet_diag_sockopt`, `struct tcpvegas_info`, `struct tcp_dctcp_info`, `struct tcp_bbr_info`, and `union tcp_cc_info`.

Control flow: userspace sends sock-diag netlink requests selecting family/protocol/states and optional bytecode filters; the kernel dumps matching sockets with base messages and requested extensions. State/persistence behavior: queries are observational, exposing live socket identity, queues, timers, uid/inode, socket options, memory, congestion-control, cgroup, mark, ULP, and BPF-storage metadata. Dependencies/integration: includes `linux/types.h`; integrates with `ss`, socket diagnostic netlink, TCP congestion modules, and strace netlink decoding. Risks/test signals: v1/v2/raw request aliases, 8-bit extension limits, bytecode variable arguments, IPv4/IPv6 addresses in fixed arrays, and bitfield socket options are risks. Tests should cover state masks, bytecode filters, extension attributes, and congestion-info unions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/inet_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/input-event-codes.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/input-event-codes.h

Purpose: defines the Linux input subsystem numeric event-code registry for device properties, event types, synchronization events, keys/buttons, relative and absolute axes, switches, misc events, LEDs, autorepeat, sounds, and sound profiles. Important APIs/types/functions: only `#define` constants are permitted because the file is also included by devicetree sources. Key groups include `INPUT_PROP_*`, `EV_*`, `SYN_*`, `KEY_*`, `BTN_*`, `REL_*`, `ABS_*`, `SW_*`, `MSC_*`, `LED_*`, `REP_*`, `SND_*`, `*_MAX`, and `*_CNT`.

Control flow: input drivers emit `struct input_event` records using these type/code values; userspace decodes them by event type and code namespace. The header itself deliberately has no structs, enums, or executable logic. State/persistence behavior: no persistent state; constants define capability bitmaps, event streams, and input device identity exposed through evdev/ioctls and sysfs. Dependencies/integration: no includes; used by C code, devicetree, HID mappings, libinput, udev, evtest, and strace input ioctl/event decoding. Risks/test signals: numeric stability is critical, aliases such as `KEY_HANGUEL`, reserved holes, `KEY_MIN_INTERESTING`, device-tree restrictions, and expanding `MAX/CNT` bounds can break consumers. Tests should validate representative key/button/axis/switch decodes, aliases, reserved values, and capability bitmap sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/input-event-codes.h -->
