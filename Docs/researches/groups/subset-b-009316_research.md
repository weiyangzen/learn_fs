# subset-b-009316 research

Grouped research report for Linux UAPI headers bundled under `sources/test-tools/strace/bundled/linux/include/uapi/linux`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs_tree.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs_tree.h

Purpose: defines the exported Btrfs on-disk tree constants and item layouts visible through userspace tooling, especially `BTRFS_IOC_SEARCH_TREE` consumers. In this repository it is a bundled UAPI source for strace-style decoding, so its stable numeric constants, packed structs, and helper macros are the important surface.

Important APIs/types/functions: includes `BTRFS_MAGIC`, tree object IDs, item key type constants, checksum types, file type and inode flag masks, `struct btrfs_disk_key`, `struct btrfs_key`, `struct btrfs_header`, leaf/node item layouts, device/chunk/superblock structures, extent/reference/inode/root/balance/file-extent/qgroup structures, and block-group/profile masks. Inline helpers are `btrfs_dir_flags_to_ftype`, `btrfs_legacy_root_item_size`, `chunk_to_extended`, `extended_to_chunk`, and `btrfs_qgroup_level`.

Control flow: there is no syscall implementation here. The only executable behavior is deterministic bit/offset transformation: directory flags are masked to remove encryption state, root-item legacy size is derived with `offsetof`, chunk profiles gain or drop the synthetic single-allocation bit, and qgroup level is extracted from the upper bits of an ID.

State and persistence behavior: this header describes persistent Btrfs metadata: superblocks, backup roots, btree headers, leaves/nodes, device items, chunks/stripes, free-space records, extent references, inode/root records, balance resume state, device replacement state, block groups, qgroup accounting, verity descriptors, and remap records. Fields are little-endian and packed; layout changes are ABI and disk-format sensitive.

Dependencies: depends on `<linux/btrfs.h>`, `<linux/types.h>`, and `<stddef.h>`. It also assumes Btrfs UUID/stat constants from the broader Btrfs UAPI and uses fixed-width Linux integer aliases plus `__DECLARE_FLEX_ARRAY`.

Integration points: strace and other decoders use the constants to print Btrfs search keys, ioctl payloads, tree item types, flags, and nested item structures. Kernel and btrfs-progs integration depends on preserving numeric key order, packed alignment, reserved values, and obsolete aliases that prevent accidental reuse.

Risks: high risk comes from enum/key drift, reused obsolete values, packed layout mistakes, endian confusion, and treating flexible item payloads as fixed size. `BTRFS_*_KEY` ordering is part of on-disk semantics, not just names. Superblock reserved fields and newer remap/qgroup fields must be decoded defensively because older kernels/filesystems may lack them.

Test signals: good signals are strace decoder tables matching these constants, compile-time size/offset checks against the bundled header, Btrfs ioctl decode tests with search-tree results, and samples containing mixed old/new metadata such as legacy root items, qgroups, free-space-tree entries, and remap items.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/cgroupstats.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/cgroupstats.h

Purpose: defines the taskstats-based cgroup statistics ABI. It lets userspace request and receive per-cgroup task state counts via generic netlink/taskstats.

Important APIs/types/functions: `struct cgroupstats` contains five 64-bit counters: sleeping, running, stopped, uninterruptible, and I/O wait. Command IDs start at `__TASKSTATS_CMD_MAX` and include `CGROUPSTATS_CMD_GET`, `CGROUPSTATS_CMD_NEW`, and max macros. Attribute/type enums define `CGROUPSTATS_TYPE_CGROUP_STATS` and `CGROUPSTATS_CMD_ATTR_FD`.

Control flow: no executable control flow exists. The ABI flow implied by the declarations is userspace sending a GET command with a cgroup file descriptor attribute and receiving a stats payload or kernel event.

State and persistence behavior: values are snapshots of live task state derived from `task->state`; there is no persistent storage in the header. Each member is documented as 8-byte aligned for cross-architecture ABI stability.

Dependencies: includes `<linux/types.h>` and `<linux/taskstats.h>`, and it relies on taskstats command numbering to avoid collisions.

Integration points: strace can decode taskstats generic netlink messages, command IDs, attributes, and the returned cgroup stats struct. Kernel integration is through taskstats, not a standalone syscall.

Risks: command numbering depends on `__TASKSTATS_CMD_MAX`, so stale bundled taskstats headers can mislabel messages. Because counters are snapshots, tests must not assume stable values across a running system.

Test signals: decode tests should cover `CGROUPSTATS_CMD_GET` with `CGROUPSTATS_CMD_ATTR_FD`, a response containing `CGROUPSTATS_TYPE_CGROUP_STATS`, and max-value rendering for unknown future attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/cgroupstats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/close_range.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/close_range.h

Purpose: declares the public flag bits for the `close_range(2)` system call.

Important APIs/types/functions: `CLOSE_RANGE_UNSHARE` requests unsharing the file descriptor table before closing or marking descriptors. `CLOSE_RANGE_CLOEXEC` requests setting `FD_CLOEXEC` instead of closing descriptors.

Control flow: the header has no functions. Runtime behavior is in the kernel syscall: callers pass a first descriptor, last descriptor, and ORed flags.

State and persistence behavior: the ABI affects process-local file descriptor table state. `CLOEXEC` persists only until the next exec boundary, while `UNSHARE` changes descriptor-table sharing before the range operation.

Dependencies: no external includes are required beyond the include guard.

Integration points: strace uses these constants to render `close_range` flags. Libraries and tests use them when constructing syscall arguments.

Risks: bit 0 is intentionally absent in this header; decoders must not infer a dense enum. Unknown future bits should remain printable as raw flag values.

Test signals: syscall decode tests should verify no flags, each individual flag, both flags combined, and an unknown bit mixed with known flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/close_range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/const.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/const.h

Purpose: provides kernel UAPI helper macros for defining constants that work in both C and assembly contexts, plus common alignment and division helpers.

Important APIs/types/functions: `_AC`, `_AT`, `_UL`, `_ULL`, `_BITUL`, `_BITULL`, `_BIT128`, `__ALIGN_KERNEL`, `__ALIGN_KERNEL_MASK`, `__KERNEL_DIV_ROUND_UP`, and `__KERNEL_DIV_ROUND_CLOSEST`.

Control flow: most behavior is macro expansion. In assembly mode constants are left untyped; in C mode suffixes/casts are applied. `__KERNEL_DIV_ROUND_CLOSEST` evaluates its operands into temporaries and chooses add-half or subtract-half rounding based on signedness and operand signs.

State and persistence behavior: there is no runtime state. The persistent effect is compile-time ABI constant shape and type width, especially for bit masks shared by many UAPI headers.

Dependencies: relies on compiler extensions such as `__typeof__`, statement expressions, token pasting, and `unsigned __int128` where `_BIT128` is available.

Integration points: headers such as `devlink.h` use `_BITUL` to define bit masks. Strace indirectly depends on these definitions when bundled UAPI headers generate decoder constants.

Risks: macro side effects are mostly controlled in `DIV_ROUND_CLOSEST`, but inputs to other macros can still be expression-sensitive. `_BIT128` is C-only and intentionally unavailable in assembly. Incorrect signedness assumptions can produce surprising rounding for unsigned negative-like values.

Test signals: compile tests should cover C and assembly preprocess paths, 32/64-bit builds, `_BITUL`/`_BITULL` width behavior, and signed versus unsigned `__KERNEL_DIV_ROUND_CLOSEST` cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/counter.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/counter.h

Purpose: defines the userspace ABI for Linux Counter character devices, including component identification, event watches, event records, and related ioctl numbers.

Important APIs/types/functions: core enums are `counter_component_type`, `counter_scope`, `counter_event_type`, count direction/mode/function enums, signal level/polarity, and synapse action. `struct counter_component` identifies a device/signal/count/function/extension component; `struct counter_watch` binds a component to an event/channel; `struct counter_event` is read back with timestamp, value, watch, and status. Ioctls are `COUNTER_ADD_WATCH_IOCTL`, `COUNTER_ENABLE_EVENTS_IOCTL`, and `COUNTER_DISABLE_EVENTS_IOCTL`.

Control flow: implied userspace flow is queue one or more watches, enable event monitoring, read `counter_event` records, and disable or replace watches. The header itself only defines ioctl encoding and payload layouts.

State and persistence behavior: watch queues and enabled event sets are per character-device file instance. Events are transient runtime records with aligned 64-bit timestamp/value fields; no durable persistence is specified.

Dependencies: includes `<linux/ioctl.h>` for `_IO`/`_IOW` encoding and `<linux/types.h>` for fixed-width ABI types.

Integration points: strace decodes counter ioctl commands and can print event/watch payload structures. The ABI references sysfs component IDs documented under `Documentation/ABI/testing/sysfs-bus-counter`.

Risks: component `parent` and `id` are compact 8-bit values tied to sysfs suffixes, so tools must not assume global uniqueness. Event replacement semantics on enable are easy to miss. `status` stores system error numbers, not boolean success.

Test signals: ioctl decode tests should cover watch addition with nested component fields, enable/disable commands, and a read event with nonzero status. ABI tests should confirm ioctl numbers stay stable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/cryptouser.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/cryptouser.h

Purpose: declares the crypto userspace configuration and reporting netlink ABI for algorithm management and introspection.

Important APIs/types/functions: message IDs are `CRYPTO_MSG_NEWALG`, `DELALG`, `UPDATEALG`, `GETALG`, `DELRNG`, and the deprecated `GETSTAT`. Attribute enum `crypto_attr_type_t` maps report/stat payload types. `struct crypto_user_alg` carries algorithm, driver, module, type, mask, refcount, and flags. Report structs describe larval, hash, cipher, block cipher, AEAD, compression, RNG, akcipher, KPP, acomp, and signature algorithms. Deprecated stat structs remain for ABI numbering.

Control flow: no local code executes. The implied flow is netlink request/response against the kernel crypto subsystem: create/update/delete algorithms, query algorithm metadata, or delete RNG state. Stat messages are explicitly marked unsupported.

State and persistence behavior: algorithm registry state is kernel-global and module-backed; this header only fixes message layouts. Report data is a snapshot of registered crypto algorithms. Deprecated stats remain layout-compatible but should not be used.

Dependencies: includes `<linux/types.h>` for fixed-width fields and depends on generic netlink framing outside this file.

Integration points: strace can decode crypto netlink message types, attributes, `crypto_user_alg`, and report payloads. Crypto tools depend on `CRYPTO_MAX_NAME` fixed-size strings.

Risks: `CRYPTOCFGA_MAX` is defined inside the enum block after `__CRYPTOCFGA_MAX`, an unusual but valid style to preserve UAPI. Deprecated stat attributes still occupy IDs; removing them from decoders would shift labels. `CRYPTO_REPORT_MAXSIZE` is based on the largest legacy report and can become stale if new report structs grow.

Test signals: netlink decode tests should include GETALG replies for hash/cipher/AEAD/RNG, deprecated stat attributes rendered as unsupported, and unknown future attributes beyond `CRYPTOCFGA_MAX`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/cryptouser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/dcbnl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/dcbnl.h

Purpose: defines the Data Center Bridging generic netlink ABI for IEEE 802.1Qaz, QCN, PFC, CEE DCBX, application priority mappings, feature flags, and capability negotiation.

Important APIs/types/functions: structs include `ieee_ets`, `ieee_maxrate`, `ieee_qcn`, `ieee_qcn_stats`, `ieee_pfc`, `dcbnl_buffer`, `cee_pg`, `cee_pfc`, `dcb_app`, `dcb_peer_app_info`, and `dcbmsg`. Command enum `dcbnl_commands` covers get/set state, priority groups, PFC, capabilities, traffic class counts, BCN, APP, IEEE set/get/delete, DCBX, feature config, and CEE aggregate get. Many nested attr enums define IEEE, CEE, PFC, PG, TC, capability, number-of-TCs, BCN, APP, and feature-config attributes.

Control flow: no implementation exists here. The ABI flow is generic-netlink request/reply using `dcbmsg.cmd` and nested attributes. Some commands configure pending state and `DCB_CMD_SET_ALL` applies changes to hardware.

State and persistence behavior: represents live NIC/LLDP/DCBX negotiation state and driver configuration, not disk persistence. Struct fields encode traffic-class arrays with fixed maxima of eight priorities/classes and persistent-in-device settings only insofar as a driver/firmware stores them.

Dependencies: includes `<linux/types.h>` and relies on generic netlink/nested-attribute conventions outside the file.

Integration points: strace decodes DCB netlink commands and nested attributes. Network configuration tools use these IDs for configuring ETS/PFC/APP behavior and reading peer-advertised CEE/IEEE state.

Risks: several enums use dense priority-specific ranges plus `*_ALL` pseudo-attributes, so decoders must preserve order. IEEE and CEE selectors use overlapping but different semantic values. Comments for BCN get/set are historically confusing, so tests should check numeric IDs rather than prose assumptions.

Test signals: decode samples should include `DCB_CMD_IEEE_GET` with ETS/PFC/APP nested payloads, `DCB_CMD_CEE_GET`, capability flags, feature flags, and APP selector cases including DSCP and nonstandard PCP.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/dcbnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/devlink.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/devlink.h

Purpose: defines the devlink generic netlink ABI for managing and observing physical/network devices, ports, shared buffers, eswitches, resources, regions, health reporters, flash updates, traps, rates, linecards, selftests, and function capabilities.

Important APIs/types/functions: exported constants include `DEVLINK_GENL_NAME`, version, multicast group names, and index bus name. `enum devlink_command` is the command ABI. Supporting enums cover port type/flavour/function state, shared-buffer pool/threshold types, eswitch modes, rate types, parameter config modes, firmware-load/reset policies, flash overwrite bit masks, selftest IDs/results, trap action/type, reload action/limit, linecard state, variable attr types, dpipe fields, resources, and port-function caps. `enum devlink_attr` is the large typed attribute namespace with explicit comments for payload type.

Control flow: no implementation is present. The implied flow is generic-netlink command dispatch with nested attributes, dumps for get commands, notifications for new/del/status events, and command-specific validation in the kernel.

State and persistence behavior: devlink exposes live driver/device state plus persistent-ish firmware/device configuration such as parameters, flash components, resources, and port functions. Reload, health, and flash status attributes model long-running state transitions, while traps/statistics are runtime counters and policies.

Dependencies: includes `<linux/const.h>` for `_BITUL` masks. Generic netlink types and nested attribute parsing are external.

Integration points: strace decodes devlink netlink commands/attributes and bitfields. The header is coordinated with kernel devlink YAML/spec generation comments for newer attributes and with network drivers that expose devlink instances.

Risks: command and attribute order is explicitly ABI; inserting values in the middle breaks decoders. Obsolete eswitch command aliases intentionally map to current IDs. Attribute comments are the main local type metadata, so stale comments can cause wrong pretty-printers. Future YAML-generated changes must keep `DEVLINK_ATTR_MAX` and masks aligned.

Test signals: decoder tests should cover representative GET dump commands, port function capability bitfields, reload action/limit masks, flash overwrite masks, trap policer attrs, health reporter attrs, linecard attrs, and unknown attributes beyond `DEVLINK_ATTR_MAX`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/dm-ioctl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/dm-ioctl.h

Purpose: defines the traditional device-mapper ioctl ABI for `/dev/mapper/control` and related block-device operations.

Important APIs/types/functions: constants define mapper/control names, type/name/UUID lengths, ioctl base `DM_IOCTL`, interface version `4.50.0`, command enum IDs, ioctl macros such as `DM_VERSION`, `DM_DEV_CREATE`, `DM_DEV_SUSPEND`, `DM_TABLE_LOAD`, `DM_TABLE_STATUS`, `DM_TARGET_MSG`, and `DM_MPATH_PROBE_PATHS`. Main payloads are `struct dm_ioctl`, `dm_target_spec`, `dm_target_deps`, `dm_name_list`, `dm_target_versions`, and `dm_target_msg`. Flag bits cover readonly, suspend, persistent dev, status-table query, active/inactive table presence, buffer full, noflush, query inactive, uevent/cookie behavior, UUID rename, secure data wiping, deferred remove, internal suspend, and IMA measurement.

Control flow: userspace sends one memory block beginning with `struct dm_ioctl`; `data_start`, `data_size`, and command-specific variable records describe appended table specs, dependency arrays, device lists, versions, messages, or geometry strings. Device-mapper has active and inactive table slots, and suspend/resume/table-load commands move state between them.

State and persistence behavior: device-mapper state is kernel runtime block-device state: mapped devices, active/inactive target tables, open counts, event numbers, udev cookies, deferred removal, and optional geometry. Some target tables may reference persistent backing devices, but this header itself describes ioctl exchange state.

Dependencies: includes `<linux/types.h>` and uses Linux ioctl encoding macros expected from userspace build context.

Integration points: strace decodes device-mapper ioctls, version triplets, flags, names/UUIDs, table specs, and variable-length lists. Device-mapper tools use this ABI for all legacy control operations.

Risks: variable-length records rely on offsets with two different `next` interpretations for load versus status paths. `struct dm_ioctl.data[7]` is padding/data start space, not a normal C string. Sensitive-data flag has security implications for buffers. Version extra string indicates this bundled header is recent and decoder tables should not assume older command ceilings.

Test signals: ioctl decode tests should cover version query, device create/remove/rename, table load/status with multiple target specs, list devices with UUID flags, buffer-full return, uevent cookie/event number fields, and secure-data/noflush/deferred-remove flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/dm-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/dqblk_xfs.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/dqblk_xfs.h

Purpose: defines XFS-specific quota `quotactl(2)` command values, quota record layouts, field masks, and quota subsystem status structures.

Important APIs/types/functions: command macros include `XQM_CMD`, `XQM_COMMAND`, quota type IDs, and `Q_XQUOTAON`, `Q_XQUOTAOFF`, `Q_XGETQUOTA`, `Q_XSETQLIM`, `Q_XGETQSTAT`, `Q_XQUOTARM`, `Q_XQUOTASYNC`, `Q_XGETQSTATV`, and `Q_XGETNEXTQUOTA`. Main types are `fs_disk_quota_t`, `fs_qfilestat_t`, `fs_quota_stat_t`, `struct fs_qfilestatv`, and `struct fs_quota_statv`. Field masks cover limits, timers, warning counts, accounting values, and `FS_DQ_BIGTIME`. Flags distinguish user/group/project quota accounting and enforcement.

Control flow: no implementation exists. The ABI flow is callers issuing XFS quota commands through `quotactl`, passing or receiving the relevant struct; `Q_XSETQLIM` uses `d_fieldmask` to select which fields mutate.

State and persistence behavior: quota limits, counters, grace timers, warning counters, and accounting/enforcement flags are persistent filesystem quota state. Status structs are snapshots of quota files and incore dquot counts. Bigtime timer support stores 40-bit signed expiration timestamps split between base timer and high-byte fields.

Dependencies: includes `<linux/types.h>`.

Integration points: strace decodes XFS quota commands, quota types, field masks, and payload structures. XFS quota tools depend on command encodings forming the first `QCMD` argument.

Risks: units are 512-byte basic blocks, not filesystem blocks. Timer semantics differ for superuser dquots versus ordinary dquots. Versioned `fs_quota_statv` requires retrying lower versions on `EINVAL`; decoders should show requested and returned versions clearly.

Test signals: quotactl decode tests should cover `Q_XGETQUOTA`, `Q_XSETQLIM` with mixed field masks, `Q_XGETQSTATV` including project quota fields, bigtime flags, and user/group/project quota type flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/dqblk_xfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/elf-em.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/elf-em.h

Purpose: defines Linux-visible ELF `e_machine` constants for architectures and legacy/interim machine IDs.

Important APIs/types/functions: constants include common IDs such as `EM_386`, `EM_MIPS`, `EM_S390`, `EM_ARM`, `EM_X86_64`, `EM_AARCH64`, `EM_RISCV`, `EM_BPF`, `EM_LOONGARCH`, plus legacy/interim values like `EM_ALPHA`, `EM_CYGNUS_M32R`, `EM_S390_OLD`, and `EM_CYGNUS_MN10300`.

Control flow: no control flow; these are numeric identifiers used in ELF headers.

State and persistence behavior: values are persisted in ELF binaries, kernel modules, core files, and object files. The header also documents historical IDs that Linux rejects or keeps for compatibility.

Dependencies: no includes beyond the guard.

Integration points: strace and related tooling can decode ELF machine fields when inspecting exec/module-related data. Kernel ELF loaders and user tools use the same numeric IDs.

Risks: some IDs alias or document history: `EM_MIPS_RS3_LE` and `EM_MIPS_RS4_BE` both use 10, and some old/interim IDs remain nonstandard. Decoders should print exact names where possible without assuming one-to-one architecture mapping for obsolete values.

Test signals: tests should cover modern architectures, `EM_BPF`, `EM_LOONGARCH`, duplicate MIPS legacy value handling, and fallback rendering for unknown `e_machine` numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/elf-em.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool.h

Purpose: declares the legacy ioctl-based ethtool ABI and shared constants for link settings, driver info, wake-on-LAN, tunables, EEPROM/register access, coalescing, rings, channels, pause, EEE, strings/statistics, RX classification, RSS, firmware flashing/dumps, features, timestamping, per-queue ops, FEC, speeds, ports, wake flags, flow hash fields, module EEPROM IDs, reset flags, and link settings.

Important APIs/types/functions: major payload structs include `ethtool_cmd`, `ethtool_drvinfo`, `ethtool_wolinfo`, `ethtool_value`, `ethtool_tunable`, `ethtool_regs`, `ethtool_eeprom`, `ethtool_eee`, `ethtool_modinfo`, `ethtool_coalesce`, `ethtool_ringparam`, `ethtool_channels`, `ethtool_pauseparam`, string/stat/test structs, RX flow/classification structs, `ethtool_rxfh`, firmware/dump structs, feature block structs, `ethtool_ts_info`, `ethtool_per_queue_op`, `ethtool_fecparam`, and `ethtool_link_settings`. Command macros range from deprecated `ETHTOOL_GSET`/`SSET` through modern feature, channel, linksettings, PHY tunable, and FEC commands.

Control flow: no local implementation. Userspace normally passes an `ifreq` with an ethtool command struct pointer to `SIOCETHTOOL`; the first field is `cmd`, and the kernel interprets the remaining payload by command. Variable-length structs use trailing arrays sized by companion fields.

State and persistence behavior: exposes live NIC/PHY state, driver and firmware metadata, device settings, offload feature wishes/active states, RSS tables/keys, classification filters, module EEPROM pages, and firmware update/dump state. Some settings persist in device/driver configuration; many are runtime-only.

Dependencies: includes Linux networking, types, if_ether, and related UAPI dependencies earlier in the file. Shared constants are also consumed by ethtool netlink headers.

Integration points: strace decodes `SIOCETHTOOL` ioctl command IDs, nested payload structures, bitsets, speed/duplex/port/autoneg values, reset masks, flow specs, and feature/FEC flags. Modern netlink ethtool still reuses many constants from this header.

Risks: very large ABI surface with legacy and modern variants. Many structures are variable length; decoder bounds must honor `len`, `n_stats`, `rule_cnt`, `indir_size`, `hkey_size`, and feature block counts. Deprecated commands remain valid ABI names. Link mode bit indices grow over time, so old masks and `SUPPORTED_`/`ADVERTISED_` compatibility macros cover only legacy ranges.

Test signals: ioctl decode tests should include representative get/set commands, variable-length strings/stats/features, RX NFC rules, RSS contexts, link settings with high-speed modes, FEC masks, reset flags, module EEPROM, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink.h

Purpose: supplements the generated ethtool generic-netlink UAPI with manually maintained constants for flags, cable-test notifications, TDR payloads, and standardized Ethernet statistics groups.

Important APIs/types/functions: includes `ETHTOOL_FLAG_ALL`, cable result codes, cable pairs, cable information sources, cable test notification statuses, TDR amplitude/pulse/step/nest attribute enums, stats group IDs (`ETH_PHY`, `ETH_MAC`, `ETH_CTRL`, `RMON`, `PHY`), and detailed per-group statistic attribute IDs.

Control flow: no implementation. The implied netlink flow is a cable test or TDR action emitting started/completed notifications with nested result/fault/amplitude data, and stats requests returning nested standardized counters.

State and persistence behavior: cable-test/TDR values are transient diagnostic results; stats are live counters. The header does not define persistent configuration.

Dependencies: includes `<linux/ethtool.h>` for shared ethtool constants and `<linux/ethtool_netlink_generated.h>` for the generated family schema.

Integration points: strace decodes ethtool netlink notifications and stats attributes using these IDs in combination with the generated command/attribute tables.

Risks: this file and the generated header are coupled; mismatched bundled versions can decode command IDs but miss manual stat/cable nested IDs. The comments contain standard references that should not be collapsed into generic counter names.

Test signals: netlink decode tests should cover cable test started/completed notifications, TDR amplitude/pulse/step nesting, all stats group IDs, and at least one counter from each standardized stats group.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink_generated.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink_generated.h

Purpose: auto-generated UAPI schema for the ethtool generic netlink family, generated from `Documentation/netlink/specs/ethtool.yaml`.

Important APIs/types/functions: defines `ETHTOOL_GENL_NAME`, version, UDP tunnel types, common header flags, TCP data split values, hardware timestamp source, PSE event bits, common header/bitset/string/string-set attributes, and per-operation attribute namespaces for rings, MM, linkinfo, linkmodes, linkstate, debug, WOL, features, channels, IRQ moderation/profile, coalesce, pause, EEE, timestamp info/config, cable tests, tunnel info, FEC, module EEPROM/module power, stats, PHC vclocks, PSE, RSS, PLCA, module firmware flash, PHY, MSE, plus user and kernel message enums and monitor multicast group.

Control flow: no executable implementation. The generated enums define generic-netlink request, reply, action, notification, and nested attribute IDs. The user message enum drives userspace requests/actions; kernel message enum drives replies and notifications.

State and persistence behavior: models live ethtool netlink state and configuration for NIC/PHY properties. Some operations mutate driver/device settings, while notifications report asynchronous changes such as link mode, rings, channels, pause, EEE, FEC, module, PSE, PLCA, MM, PHY, RSS, and firmware flash progress.

Dependencies: generated as a standalone UAPI header but included by `ethtool_netlink.h`. It must stay synchronized with kernel YAML specs and ethtool core implementation.

Integration points: strace uses it as the authoritative source for ethtool netlink message and attribute names. Network tooling uses the same IDs for modern ethtool operations instead of `SIOCETHTOOL`.

Risks: generated order is ABI; manual edits are forbidden by the header. Many namespaces begin at zero, but some begin at one for padding/reserved conventions, so decoders must not normalize them. User and kernel message enums are related but not identical; set replies and notifications have separate IDs.

Test signals: decode tests should cover at least one request/reply pair, one notification, common header flags, nested bitsets/strings, RSS create/delete actions, module firmware flash notifications, PSE events, timestamp config, MSE attributes, and unknown future attributes beyond each `*_MAX`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ethtool_netlink_generated.h -->
