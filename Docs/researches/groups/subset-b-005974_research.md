# subset-b-005974 Research

Grouped source research for Linux UAPI networking, filesystem, exec, bitmask, block crypto, partitioning, tracing, and zoned block-device headers under `sources/distributed-fs/ceph-client/include/uapi/linux`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ax25.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ax25.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/ax25.h` exports the Linux userspace ABI for AX.25 amateur packet radio sockets and device control. The complete 117-line header was read. It defines socket address layouts, routing/control ioctl payloads, socket option numbers, and connection status structures shared by userspace AX.25 tools and the kernel AX.25 networking stack.

## Important APIs, Types, and Functions

There are no functions. Important constants include `AX25_MTU`, `AX25_MAX_DIGIS`, socket options such as `AX25_WINDOW`, `AX25_T1`, `AX25_N2`, `AX25_T3`, `AX25_T2`, `AX25_BACKOFF`, `AX25_EXTSEQ`, `AX25_PIDINCL`, `AX25_IDLE`, `AX25_PACLEN`, `AX25_IAMDIGI`, and `AX25_KILL`. Ioctls are allocated from `SIOCPROTOPRIVATE`, including UID mapping, route options, connection control, forwarding, device control, and old/new info queries. Main exported types are `ax25_address`, `sockaddr_ax25`, `full_sockaddr_ax25`, `ax25_routes_struct`, `ax25_route_opt_struct`, `ax25_ctl_struct`, `ax25_info_struct_deprecated`, `ax25_info_struct`, and `ax25_fwd_struct`.

## Control Flow

The file has no executable control flow. Runtime flow is ABI-driven: userspace opens an AX.25 socket, passes `sockaddr_ax25` or `full_sockaddr_ax25` to socket syscalls, sets options by the numeric option constants, and issues AX.25 ioctls with one of the exported payload structures. The kernel AX.25 implementation interprets the command, mutates socket/route/device state, and may return `ax25_info_struct` counters and protocol variables.

## State and Persistence Behavior

This header owns no storage. It describes transient kernel state: AX.25 socket timers, sequence variables, receive/send queue counters, UID policy, routes, digipeater chains, and forwarding mappings. Persistence, if any, is external to this header and handled by userspace configuration tools or kernel module/device lifetime.

## Dependencies and Integration Points

The header depends on `<linux/socket.h>` for `__kernel_sa_family_t` and `SIOCPROTOPRIVATE`. Integration points are the AX.25 socket family, netdevice-specific AX.25 controls, route/forwarding management, and compatibility with userspace tools that know the seven-byte shifted-call-sign `ax25_address` encoding.

## Risks and Edge Cases

The structures are UAPI ABI and must not be reordered casually. `sockaddr_ax25` is variable length because digipeater addresses follow `sax25_ndigis`; callers must size buffers for up to `AX25_MAX_DIGIS`. `sax25_uid` aliases `sax25_ndigis`, so old UID-oriented userspace can collide conceptually with address-count usage. The deprecated info struct remains ABI surface even though the comment warns against exporting it. Timer/window fields are plain `unsigned int`, so tooling must not assume kernel-internal units without checking the AX.25 implementation.

## Test Signals

Useful signals include UAPI header selftests or build coverage for userspace includes, ioctl smoke tests for UID/route/device operations, sockaddr round trips with zero and eight digipeaters, compatibility tests for `SIOCAX25GETINFOOLD` versus `SIOCAX25GETINFO`, and packet-radio integration tests that validate timer/window options affect live AX.25 sockets as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ax25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/batadv_packet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/batadv_packet.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/batadv_packet.h` is the public wire-format contract for the B.A.T.M.A.N. advanced mesh protocol. The complete 669-line header was read. It defines packet type numbers, protocol flags, ICMP/throughput-meter values, TVLV container types, and the packed packet structures consumed by kernel batman-adv code and userspace tools such as `batctl`.

## Important APIs, Types, and Functions

There are no functions, but the macro `batadv_tp_is_error(n)` classifies throughput-meter status values over 127 as errors. Important enums include `batadv_packettype`, `batadv_subtype`, `batadv_iv_flags`, `batadv_icmp_packettype`, `batadv_mcast_flags`, `batadv_tt_data_flags`, `batadv_vlan_flags`, `batadv_bla_claimframe`, `batadv_tvlv_type`, and `batadv_icmp_tp_subtype`. Important structs include `batadv_bla_claim_dst`, OGM/OGM2/ELP headers, ICMP variants, unicast, unicast-4addr, fragment, broadcast, multicast, coded, unicast TVLV, `batadv_tvlv_hdr`, gateway, translation-table VLAN/data/change, roam advertisement, multicast data, and multicast tracker payloads.

## Control Flow

The file itself has no executable flow. Protocol flow is encoded in header layout and type fields: receivers classify packets by `packet_type`, then route to OGM, ELP, unicast, multicast, ICMP, network-coding, or TVLV parsers. TVLV-bearing packets use `tvlv_len` followed by one or more `batadv_tvlv_hdr` containers. Fragment flow depends on the endian-specific bitfield in `batadv_frag_packet`; ICMP route-record flow uses a bounded `BATADV_RR_LEN` array; throughput-meter flow sends `BATADV_TP_MSG` and expects `BATADV_TP_ACK`.

## State and Persistence Behavior

No persistent state is owned by the header. It describes transient mesh control and payload packets whose fields drive kernel tables for originators, neighbors, translation tables, multicast capabilities, bridge loop avoidance, distributed ARP table, roaming, and throughput-meter sessions. Packet sequence numbers, TTLs, TTVNs, checksums, and write-once timestamps are state carriers across the mesh, not local storage.

## Dependencies and Integration Points

Direct dependencies are `<asm/byteorder.h>`, `<linux/if_ether.h>`, `<linux/stddef.h>`, and `<linux/types.h>`. Integration points include the batman-adv kernel module, Ethernet frame handling, `batctl`, generic netlink status reporting in `batman_adv.h`, and mesh peers that must agree on `BATADV_COMPAT_VERSION`, packet type numbers, byte order, and structure packing.

## Risks and Edge Cases

This is a wire ABI. The `#pragma pack(2)` requirement is central because headers before Ethernet payloads must satisfy alignment constraints; accidental padding can break interoperability or leak uninitialized bytes. The fragment packet bitfield depends on `__BIG_ENDIAN_BITFIELD` or `__LITTLE_ENDIAN_BITFIELD`; unsupported byteorder intentionally fails compilation. Flexible arrays and counted TVLV data require length validation before parsing. Multicast, TT, and network-coding fields mix host-local and network-byte-order values, so tools must respect the declared `__be16`/`__be32` types.

## Test Signals

Strong signals include compile coverage on big- and little-endian targets, structure size/offset assertions for packet headers, packet parser fuzzing with malformed `tvlv_len` and fragment fields, interop tests between kernel batman-adv and `batctl`, mesh integration tests for OGM/ELP/unicast/multicast paths, and throughput-meter tests that validate success/error classification around value 127/128.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/batadv_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/batman_adv.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/batman_adv.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/batman_adv.h` exports the generic-netlink and rtnetlink userspace ABI for configuring and inspecting B.A.T.M.A.N. advanced mesh interfaces. The complete 704-line header was read. It names the netlink family and multicast groups, defines translation-table and multicast flags, gateway modes, netlink attributes, commands, throughput-meter reasons, and nested link attributes.

## Important APIs, Types, and Functions

There are no functions. Important symbols are `BATADV_NL_NAME`, multicast groups `BATADV_NL_MCAST_GROUP_CONFIG` and `BATADV_NL_MCAST_GROUP_TPMETER`, `enum batadv_tt_client_flags`, `enum batadv_mcast_flags_priv`, `enum batadv_gw_modes`, `enum batadv_nl_attrs`, `enum batadv_nl_commands`, `enum batadv_tp_meter_reason`, `enum batadv_ifla_attrs`, and `IFLA_BATADV_MAX`. The large `batadv_nl_attrs` enum covers mesh, hard-interface, originator, neighbor, TT, gateway, bridge-loop-avoidance, DAT, multicast, VLAN, and tunable configuration fields.

## Control Flow

The header has no runtime flow. Netlink flow is command/attribute driven: userspace sends a `BATADV_CMD_GET_*` request to dump mesh state, sends `BATADV_CMD_SET_MESH`, `BATADV_CMD_SET_HARDIF`, or `BATADV_CMD_SET_VLAN` to update tunables, or starts/cancels a throughput-meter session with the TP-meter commands. Kernel replies use the enumerated attributes and may emit multicast notifications on the config or throughput-meter groups.

## State and Persistence Behavior

This file defines runtime configuration and reporting state rather than owning storage. State described by attributes includes active hard interfaces, mesh addresses, routing algorithm, originator and neighbor metrics, translation-table state, multicast flags, VLAN IDs, bridge loop avoidance data, DAT cache entries, gateway mode/bandwidth/selection, hop penalty, log level, fragmentation, network coding, orig/ELP intervals, throughput override, and multicast fanout. Persistence is tied to kernel netdevice/module lifetime unless userspace reapplies configuration.

## Dependencies and Integration Points

This header is paired with the wire packet ABI in `batadv_packet.h` and with kernel policy tables in batman-adv netlink/rtnetlink implementation files. It integrates with libnl-style generic-netlink clients, rtnetlink creation of batadv netdevices through `IFLA_BATADV_ALGO_NAME`, and tooling such as `batctl` that uses stable enum values for dumps and configuration.

## Risks and Edge Cases

The comments explicitly require updating netlink policies when attributes or ifla values are added. Attribute and command numbering is ABI: reordering would break userspace. Some flags are local-only while others are remote or CRC-synchronized, so userspace must not treat all TT or multicast bits identically. TP-meter statuses deliberately reserve values below 128 for non-error completion/cancel and values at or above 128 for errors, matching `batadv_tp_is_error()` in the packet header. Alias commands such as `BATADV_CMD_GET_MESH_INFO` and `BATADV_CMD_GET_HARDIFS` must remain numerically identical to their base commands.

## Test Signals

Useful coverage includes generic-netlink policy tests, `batctl` dump/set smoke tests, netdevice creation through rtnetlink with `IFLA_BATADV_ALGO_NAME`, enum stability checks against userspace headers, multicast notification tests for config and TP-meter events, and integration tests that set every boolean/numeric mesh tunable and read it back through `BATADV_CMD_GET_MESH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/batman_adv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bcm933xx_hcs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bcm933xx_hcs.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/bcm933xx_hcs.h` exports the header structure for a Broadcom Cable Modem firmware format. The complete 25-line header was read. It is a compact UAPI description of metadata found around BCM933xx firmware images.

## Important APIs, Types, and Functions

There are no functions or ioctls. The single exported type is `struct bcm_hcs`, with fields for `magic`, `control`, major/minor revision, `build_date`, file length, load address, a 64-byte filename, `hcs`, an obscure `her_znaet_chto` 16-bit field, and a 32-bit `crc`. It depends on fixed-width Linux integer aliases from `<linux/types.h>`.

## Control Flow

The header has no executable control flow. Firmware tooling or kernel drivers read bytes from a firmware image, interpret them as `struct bcm_hcs`, validate magic/checksum fields, and then use metadata such as `filelen`, `ldaddress`, and `filename` to decide how to load or identify the payload.

## State and Persistence Behavior

The structure describes persistent state embedded in a firmware file or flash image. This header does not store or mutate anything itself; it defines the layout that persists outside the kernel until firmware tooling rewrites the image.

## Dependencies and Integration Points

The direct dependency is `<linux/types.h>`. Integration points are firmware loaders, image validators, and userspace tools that parse Broadcom cable modem firmware. Because this is UAPI, any parser outside the kernel may include the same header to avoid duplicated layout definitions.

## Risks and Edge Cases

The fields are fixed-width but not annotated as little- or big-endian, so consumers must know the firmware format's byte order from the driver or image specification. The filename is a raw fixed-size character array and may not be NUL-terminated. `filelen`, `ldaddress`, and `crc` must be bounds-checked against the actual image size. The oddly named unknown field is part of the layout and cannot be removed without changing ABI assumptions.

## Test Signals

Good tests parse known-good and corrupted BCM933xx images, verify structure size and field offsets, reject truncated headers and oversized `filelen` values, validate CRC/checksum behavior, and exercise filename handling with both NUL-terminated and fully occupied 64-byte names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bcm933xx_hcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bfs_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bfs_fs.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/bfs_fs.h` exports the on-disk BFS filesystem layout and helper macros. The complete 82-line header was read. It defines block sizing, magic values, inode and directory layouts, superblock layout, and arithmetic for translating between BFS inode numbers, offsets, file sizes, and dirty-state checks.

## Important APIs, Types, and Functions

There are no functions. Important constants include `BFS_BSIZE_BITS`, `BFS_BSIZE`, `BFS_MAGIC`, `BFS_ROOT_INO`, `BFS_INODES_PER_BLOCK`, `BFS_VDIR`, `BFS_VREG`, `BFS_NAMELEN`, `BFS_DIRENT_SIZE`, and `BFS_DIRS_PER_BLOCK`. Important structs are `struct bfs_inode`, `struct bfs_dirent`, and `struct bfs_super_block`. Macros include `BFS_OFF2INO`, `BFS_INO2OFF`, `BFS_NZFILESIZE`, `BFS_FILESIZE`, `BFS_FILEBLOCKS`, and `BFS_UNCLEAN`.

## Control Flow

The header has no executable flow, but it encodes filesystem traversal arithmetic. Mount and fsck-like code read `bfs_super_block`, confirm `BFS_MAGIC`, map inode numbers to disk offsets with `BFS_INO2OFF`, read `bfs_inode` entries, compute file size/block count from start/end fields, and iterate fixed-size directory entries containing a little-endian inode and 14-byte name.

## State and Persistence Behavior

The main state is persistent on disk. Inodes, directory entries, and the superblock are stored in little-endian form. Runtime callers convert fields with `le32_to_cpu()` before arithmetic. `BFS_UNCLEAN` describes mount-time dirty state by comparing `s_from` and `s_to` to `-1` and checking that the VFS superblock is not read-only.

## Dependencies and Integration Points

The only direct include is `<linux/types.h>`, but some macros assume conversion helpers such as `le32_to_cpu()` and VFS flag `SB_RDONLY` are visible from the including kernel context. Integration points are the BFS filesystem driver, filesystem check/repair utilities, and any tool that reads raw BFS images.

## Risks and Edge Cases

This is an on-disk ABI. Changing struct fields or padding would break existing images. `BFS_NZFILESIZE` subtracts a block-derived start offset from `i_eoffset + 1`; corrupted images can underflow or overflow if callers do not validate block ranges. Directory names are fixed 14-byte arrays and may not behave like C strings. `BFS_UNCLEAN` mixes little-endian superblock fields and VFS state, so it is not a pure UAPI helper for standalone userspace without equivalent constants.

## Test Signals

Useful signals include mounting known BFS images, fsck parsing of clean and unclean superblocks, endian/offset tests for `BFS_OFF2INO` and `BFS_INO2OFF`, corrupt-image tests with invalid block ranges and names, and structure size/offset checks against historical BFS disk images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/binfmts.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/binfmts.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/binfmts.h` exports exec/binfmt limits and auxiliary flag definitions shared with userspace. The complete 25-line header was read. It documents maximum argument string sizing, maximum argument count, the initial binary-prm buffer size, and an interpreter flag for preserving `argv[0]`.

## Important APIs, Types, and Functions

There are no functions. Exported values are `MAX_ARG_STRLEN`, `MAX_ARG_STRINGS`, `BINPRM_BUF_SIZE`, `AT_FLAGS_PRESERVE_ARGV0_BIT`, and `AT_FLAGS_PRESERVE_ARGV0`. It also includes `<linux/capability.h>` and forward declares `struct pt_regs`.

## Control Flow

The header has no executable flow. It participates in the exec path by giving kernel binfmt loaders and userspace-aware code the same limits: argument-copy logic rejects strings beyond `MAX_ARG_STRLEN`, aggregate argument handling is bounded by `MAX_ARG_STRINGS`, and binary format probing uses a buffer of `BINPRM_BUF_SIZE` bytes. Interpreter setup may consult `AT_FLAGS_PRESERVE_ARGV0` to decide whether to preserve the original `argv[0]`.

## State and Persistence Behavior

No state is owned by the file. The constants affect transient `execve()` argument copying and binary format selection. They do not persist beyond the exec operation except as process argument state once a new image starts.

## Dependencies and Integration Points

`MAX_ARG_STRLEN` depends on `PAGE_SIZE` being available through the broader UAPI include environment. Integration points include kernel binary format loaders, script/interpreter execution, auxiliary vector flag handling, and userspace that wants to mirror Linux exec argument limits.

## Risks and Edge Cases

`MAX_ARG_STRLEN` is intentionally a guard against bad pointers, not a promise that all large argument vectors succeed; aggregate memory and `RLIMIT_STACK` style checks can fail earlier. `MAX_ARG_STRINGS` fits a signed 32-bit integer but is not a practical allocation guarantee. Changing `BINPRM_BUF_SIZE` can affect format probes that expect enough initial bytes for magic/shebang parsing. Consumers must include headers in an order that defines `PAGE_SIZE`.

## Test Signals

Useful tests include exec boundary tests around `MAX_ARG_STRLEN`, shebang/interpreter tests that need `BINPRM_BUF_SIZE` bytes, checks that `AT_FLAGS_PRESERVE_ARGV0` preserves interpreter `argv[0]` where supported, and userspace header compile tests across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/binfmts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bits.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bits.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/bits.h` exports low-level bitmask construction macros for UAPI consumers. The complete 14-line header was read. It provides generic mask builders for unsigned long, unsigned long long, and 128-bit values.

## Important APIs, Types, and Functions

There are no functions or types. Exported macros are `__GENMASK(h, l)`, `__GENMASK_ULL(h, l)`, and `__GENMASK_U128(h, l)`. They depend on helper macros such as `_UL`, `_ULL`, `_BIT128`, `__BITS_PER_LONG`, and `__BITS_PER_LONG_LONG` that are expected from the surrounding Linux UAPI constant infrastructure.

## Control Flow

The header has no runtime flow. Compile-time expressions call the macros to generate contiguous masks from high bit `h` down to low bit `l`. The U128 variant forms a mask by subtracting the low-bit power from one past the high-bit power; the long and long-long variants use paired shifts against all-ones constants.

## State and Persistence Behavior

No state is stored or persisted. The macros influence compile-time constants and inline expressions in drivers, protocol headers, and userspace programs.

## Dependencies and Integration Points

This header integrates with Linux UAPI bit operations and constant macros, typically via includes that provide the `_UL`/`_ULL` wrappers and architecture bit widths. It is used by headers that need stable bit-field masks without manually writing architecture-width-dependent constants.

## Risks and Edge Cases

Callers must pass valid bit indexes where `h >= l` and both indexes fit the target width. Invalid shifts at or beyond the type width are undefined in C and can produce compiler warnings or wrong masks. The macros are prefixed with double underscores, so they are low-level building blocks rather than policy-checked public helpers. The U128 macro relies on `_BIT128()` support and should only be used where 128-bit constant handling is available.

## Test Signals

Useful signals include UAPI compile tests on 32-bit and 64-bit architectures, static assertions for representative masks such as single-bit, full-width, and subrange masks, compiler warning scans for invalid shift expressions, and build coverage for headers that consume `__GENMASK_U128`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blk-crypto.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/blk-crypto.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blk-crypto.h` exports block-layer crypto key management ioctls. The complete 44-line header was read. It defines userspace argument structures for importing raw keys, generating wrapped keys, preparing ephemeral wrapped keys, and the ioctl numbers allocated in the block device ioctl space.

## Important APIs, Types, and Functions

There are no functions. Exported types are `struct blk_crypto_import_key_arg`, `struct blk_crypto_generate_key_arg`, and `struct blk_crypto_prepare_key_arg`. Exported ioctls are `BLKCRYPTOIMPORTKEY`, `BLKCRYPTOGENERATEKEY`, and `BLKCRYPTOPREPAREKEY`, all using command type `0x12` and numbers 137 through 139. The header notes that numbers 140 and 141 are reserved for future blk-crypto use.

## Control Flow

The header has no executable flow. Userspace opens a block device and issues an ioctl with one of the argument structures. Import flow passes a raw key pointer/size and receives a long-term wrapped key blob. Generate flow requests a newly generated long-term wrapped key. Prepare flow passes a long-term wrapped key and receives an ephemerally wrapped key suitable for immediate use by hardware or the block layer.

## State and Persistence Behavior

The header owns no key storage. It describes transient ioctl arguments and caller-provided buffers. The long-term wrapped key blob may be persisted by userspace or higher-level storage software, while ephemeral keys are intended for shorter-lived operational use. The reserved fields provide ABI extension space and should be zeroed by callers.

## Dependencies and Integration Points

Direct dependencies are `<linux/ioctl.h>` and `<linux/types.h>`. Integration points are the block device ioctl namespace, blk-crypto kernel support, hardware inline encryption engines, filesystem/storage encryption stacks, and userspace key-management utilities that pass pointers as `__u64` for ABI-stable 32/64-bit handling.

## Risks and Edge Cases

Pointer fields are numeric `__u64` values, so compat handling and address validation must be correct in the kernel. Callers must supply valid buffer sizes and expect the kernel to reject unsupported sizes or algorithms. Reserved fields must remain zero for forward compatibility. The shared block ioctl number space is scarce; accidental command collisions would break unrelated block-device ioctls. Raw keys and wrapped blobs are sensitive data and require memory lifetime/scrubbing discipline outside this header.

## Test Signals

Useful tests include ioctl ABI size checks on 32- and 64-bit builds, invalid pointer and short-buffer tests, reserved-field rejection or ignore behavior as implemented by the kernel, successful import/generate/prepare sequences on supported devices, unsupported-device error-path tests, and key-material leak scans in tracing/logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blk-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blkdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/blkdev.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blkdev.h` exports a small io_uring block command identifier. The complete 14-line header was read. It defines the block-layer uring command for discard operations, separate from normal ioctl numbering while reusing the block ioctl command type value.

## Important APIs, Types, and Functions

There are no functions or structs. The exported macro is `BLOCK_URING_CMD_DISCARD`, defined with `_IO(0x12, 0)`. The comment ties the command to `IORING_OP_URING_CMD` and states that this command number space is different from `ioctl()`.

## Control Flow

The header has no executable flow. Runtime flow is through io_uring: userspace submits `IORING_OP_URING_CMD` against a block file and identifies the operation with `BLOCK_URING_CMD_DISCARD`; the block layer dispatches the command to discard handling rather than treating it as a traditional ioctl.

## State and Persistence Behavior

No state is owned by this header. Discard commands can affect persistent media allocation state by informing the device/filesystem that sectors are unused, but the header only names the command.

## Dependencies and Integration Points

Direct dependencies are `<linux/ioctl.h>` and `<linux/types.h>`. Integration points are io_uring command submission, block-device file operations, discard/TRIM handling, and userspace libraries that need the stable command value.

## Risks and Edge Cases

The most important distinction is namespace: although `_IO(0x12, 0)` is used, this is for uring commands, not `ioctl()`. Userspace that issues it through the wrong syscall path will not exercise the intended interface. Runtime discard behavior depends on block-device support, alignment, range validation, permissions, and filesystem/device policy outside this header.

## Test Signals

Useful signals include io_uring block discard smoke tests, unsupported-device and permission error tests, namespace tests that confirm the command is not treated as a regular ioctl contract, and end-to-end discard verification with devices that expose deterministic trim behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blkdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blkpg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/blkpg.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blkpg.h` exports the block partition table manipulation ioctl ABI. The complete 36-line header was read. It defines the `BLKPG` ioctl, operation codes for adding, deleting, and resizing partitions, and the argument structures passed from userspace to the block layer.

## Important APIs, Types, and Functions

There are no functions. `BLKPG` is `_IO(0x12,105)`. `struct blkpg_ioctl_arg` carries `op`, `flags`, `datalen`, and a `void __user *data` pointer. Operation codes are `BLKPG_ADD_PARTITION`, `BLKPG_DEL_PARTITION`, and `BLKPG_RESIZE_PARTITION`. `struct blkpg_partition` provides byte `start`, byte `length`, partition number `pno`, and fixed-size `devname`/`volname` arrays that the comments say are unused or ignored.

## Control Flow

The header has no executable flow. Userspace populates `blkpg_ioctl_arg`, points `data` at a `blkpg_partition`, chooses an op, and issues `BLKPG` to a block device. Kernel block partition code copies the data from userspace, validates the operation, and updates the in-kernel partition representation.

## State and Persistence Behavior

This ABI primarily mutates kernel runtime partition state. It does not by itself rewrite the on-disk partition table; persistence requires separate tooling to update partition metadata on media. The effects last until rescans, removal, reboot, or later partition-management operations.

## Dependencies and Integration Points

Direct dependencies are `<linux/compiler.h>` for `__user` and `<linux/ioctl.h>`. Integration points include block device ioctl handling, partition scanning, partition-management tools, udev-style consumers observing partition changes, and disk utilities that coordinate on-disk table edits with kernel table updates.

## Risks and Edge Cases

`data` is a userspace pointer and must be validated through copy-from-user logic. `datalen` must match the expected structure for the selected op. `start` and `length` are byte offsets, not sectors, so tools must avoid unit confusion. The name fields are fixed 64-byte arrays but ignored, so relying on them for naming behavior is wrong. Partition numbers, overlap checks, open partitions, and resize constraints are enforced outside this header and are common failure points.

## Test Signals

Useful tests include add/delete/resize ioctl smoke tests on loop devices, invalid `datalen` and bad pointer tests, byte-versus-sector unit tests, partition overlap and busy-device error tests, and verification that on-disk partition tables are unchanged unless a separate writer updates them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blkpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blktrace_api.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/blktrace_api.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blktrace_api.h` exports the block I/O tracing event ABI. The complete 197-line header was read. It defines trace category masks, action codes, notify events, trace record layouts, remap payloads, setup states, and setup structures for the original and extended blktrace interfaces.

## Important APIs, Types, and Functions

There are no functions. Important enums are `blktrace_cat`, `blktrace_act`, and `blktrace_notify`. Important action macros combine base actions with category masks through `BLK_TC_ACT`, including queue, merge, request allocation, requeue, issue, complete, plug/unplug, insert, split, remap, abort, driver data, zone append/plug/unplug, and notify actions. Important structs are `blk_io_trace`, `blk_io_trace2`, `blk_io_trace_remap`, `blk_user_trace_setup`, and `blk_user_trace_setup2`.

## Control Flow

The header has no executable flow. Trace control flow is driven by setup ioctls in the block layer: userspace configures action masks, buffers, LBA ranges, and PID filters, starts tracing, reads event records, and stops tracing. Event consumers parse `magic` to distinguish `BLK_IO_TRACE_VERSION` and `BLK_IO_TRACE2_VERSION`, then decode action/category bits and any post-record PDU such as cgroup IDs, messages, driver data, or remap payloads.

## State and Persistence Behavior

The file owns no storage. It describes transient tracing sessions with states `Blktrace_setup`, `Blktrace_running`, and `Blktrace_stopped`. Trace records are runtime observations of block I/O, carrying sequence number, timestamp, sector, byte count, action, PID, device, CPU, error, and PDU length. Persistence occurs only if userspace records the trace stream.

## Dependencies and Integration Points

The direct dependency is `<linux/types.h>`. Integration points are kernel block tracepoints, relay/per-CPU trace buffers, legacy blktrace tooling, parsers that understand v1/v2 records, cgroup-aware tracing, zoned block tracing categories, and block driver-specific data PDUs.

## Risks and Edge Cases

Version handling matters: v1 has a 32-bit `action` and `__u16 act_mask`, while v2 extends action/masks to 64 bits for newer categories. Old tooling can miss zone or write-zeroes categories above bit 15. `pdu_len` requires bounds checking before reading trailing payload. `blk_io_trace_remap` uses big-endian fields. Setup names have different fixed lengths in v1 and v2. Trace streams are high volume, so buffer sizing and loss accounting need runtime validation outside this header.

## Test Signals

Useful tests include v1/v2 parser tests using `magic` and version fields, category mask tests above and below bit 16, remap payload endian tests, trace setup validation for LBA/PID filters, stress tests under high I/O to detect dropped events, and compatibility tests with existing blktrace/blkparse tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blktrace_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blkzoned.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/blkzoned.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blkzoned.h` exports the zoned block device ioctl ABI. The complete 211-line header was read. It defines zone types, zone conditions, report flags, zone descriptor and request structures, and ioctls for reporting, resetting, opening, closing, finishing, and querying zoned block-device geometry.

## Important APIs, Types, and Functions

There are no functions. Important enums are `blk_zone_type`, `blk_zone_cond`, and `blk_zone_report_flags`. Important structures are `struct blk_zone`, `struct blk_zone_report`, and `struct blk_zone_range`. Exported ioctls are `BLKREPORTZONE`, `BLKREPORTZONEV2`, `BLKRESETZONE`, `BLKGETZONESZ`, `BLKGETNRZONES`, `BLKOPENZONE`, `BLKCLOSEZONE`, and `BLKFINISHZONE`.

## Control Flow

The header has no executable flow. Userspace asks for zone descriptors with `BLKREPORTZONE` or `BLKREPORTZONEV2`, then uses the reported `start`, `len`, `capacity`, `wp`, `type`, and `cond` fields to plan sequential writes. Management operations pass `blk_zone_range` to reset write pointers, explicitly open zones, close zones, or mark zones full. Geometry queries return zone size and total zone count.

## State and Persistence Behavior

This ABI exposes and mutates persistent or device-managed zone state: write pointer position, open/closed/full/read-only/offline conditions, non-sequential resource usage, and reset recommendations. Cached reports can collapse implicit-open, explicit-open, and closed states into `BLK_ZONE_COND_ACTIVE`; regular reports should not use that synthetic condition. All sector fields use 512-byte units regardless of logical block size.

## Dependencies and Integration Points

Direct dependencies are `<linux/types.h>` and `<linux/ioctl.h>`. Integration points include the block layer zoned-device core, SCSI ZBC, ATA ZAC, NVMe ZNS, filesystems and databases that write sequentially to zones, and userspace management tools that choose between deprecated `BLKREPORTZONE` and flag-aware `BLKREPORTZONEV2`.

## Risks and Edge Cases

`struct blk_zone` is deliberately 64 bytes to match device standards; layout changes are ABI-sensitive. `struct blk_zone_report` uses a flexible array, so callers must allocate enough room for `nr_zones` descriptors and handle the output count. `BLKREPORTZONE` ignores input flags, while V2 uses flags as input and output; mixing those semantics can hide cached-report behavior. Range operations must be zone aligned. The `BLK_ZONE_COND_ACTIVE` and `BLK_ZONE_REP_CACHED` symbols are newer additions noted as Linux 6.19, so compatibility with older headers/kernels needs probing.

## Test Signals

Useful tests include zone report parsing with multiple descriptor counts, `BLKREPORTZONE` versus `BLKREPORTZONEV2` flag behavior, reset/open/close/finish operations on zoned loop or hardware devices, alignment and out-of-range error tests, verification that sector units are always 512 bytes, and compatibility tests against kernels that lack cached-report support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/blkzoned.h -->
