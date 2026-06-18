# subset-b-006581

Grouped research report for Linux UAPI headers under `sources/distributed-fs/ceph-client/tools/include/uapi/linux`. Each section is source-tree-aligned and is intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_common.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_common.h

Purpose: common classic BPF instruction encoding constants shared by socket filters and eBPF-adjacent userspace tooling. The header is a pure UAPI contract: it defines how to decode the low-level `code` byte of BPF instructions and the maximum instruction count accepted when `BPF_MAXINSNS` is not provided elsewhere.

Important APIs/types: there are no functions or structs. The API is the macro set `BPF_CLASS`, `BPF_SIZE`, `BPF_MODE`, `BPF_OP`, and `BPF_SRC`, plus opcode/class constants such as `BPF_LD`, `BPF_LDX`, `BPF_ST`, `BPF_ALU`, `BPF_JMP`, `BPF_RET`, sizes `BPF_W/H/B`, modes `BPF_IMM/ABS/IND/MEM/LEN/MSH`, ALU ops, jump ops, and sources `BPF_K` and `BPF_X`.

Control flow, state, and persistence: all behavior is compile-time bit masking. Runtime control flow lives in kernel BPF interpreters/JITs and consumers such as `filter.h`, which use these masks to classify instructions. The only state-like value is `BPF_MAXINSNS`, an ABI limit macro rather than persistent state.

Dependencies and integration points: used by Linux socket-filter definitions and by userspace assemblers/disassemblers that build `struct sock_filter` arrays. Integration risk is semantic drift: changing bit values or masks would break compiled filters and tools that share BSD-compatible BPF encodings.

Risks and test signals: verify by compiling userspace filter programs, decoding known filter bytecode, and running socket filter attach tests. Tests should include instruction class/mode/op round-trips and boundary handling around `BPF_MAXINSNS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_perf_event.h

Purpose: defines the perf-event context structure exposed to BPF programs/userspace tooling for perf event attachments. It is a minimal wrapper around architecture-specific register state plus event sample metadata.

Important APIs/types: `struct bpf_perf_event_data` contains `bpf_user_pt_regs_t regs`, `__u64 sample_period`, and `__u64 addr`. `regs` is imported from `<asm/bpf_perf_event.h>`, so its concrete layout is architecture-specific.

Control flow, state, and persistence: the header has no executable control flow. The runtime flow is kernel perf infrastructure populating the structure before invoking a BPF program or exposing metadata through helper-facing ABI. The structure is transient per event and does not describe persistent storage.

Dependencies and integration points: depends on the architecture UAPI header for register layout. It integrates perf events, BPF program contexts, and tracing tools that inspect sampled instruction/address data. The type is consumed by libbpf-like tooling and BPF C programs through generated or copied UAPI headers.

Risks and test signals: the main risk is arch layout mismatch or assuming register fields are portable. Tests should compile BPF perf-event programs on target architectures, validate sample period/address population, and verify CO-RE or generated bindings do not hard-code an incompatible `regs` shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/btf.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/btf.h

Purpose: defines the on-wire/on-disk BPF Type Format metadata ABI used by the kernel, BPF loaders, debuggers, and CO-RE tooling. It describes BTF headers, type records, string offsets, kind encodings, and trailing records for complex type kinds.

Important APIs/types: key structures are `btf_header`, `btf_layout`, `btf_type`, `btf_enum`, `btf_array`, `btf_member`, `btf_param`, `btf_var`, `btf_var_secinfo`, `btf_decl_tag`, and `btf_enum64`. Macros extract packed fields from `btf_type.info` (`BTF_INFO_KIND`, `BTF_INFO_VLEN`, `BTF_INFO_KFLAG`) and integer/member encodings. `enum` values define BTF kinds from `BTF_KIND_INT` through `BTF_KIND_ENUM64`, plus variable and function linkage constants.

Control flow, state, and persistence: this header defines a serialized format. Parsers first validate `BTF_MAGIC`, `BTF_VERSION`, and section offsets in `btf_header`, then walk type records and use `kind` and `vlen` to determine which trailing records follow. Persistent state is the BTF blob embedded in ELF sections, kernel BTF, or BPF object metadata.

Dependencies and integration points: depends on `<linux/types.h>`. It integrates clang/pahole-generated BTF, kernel BPF verifier type checks, CO-RE relocations, bpftool inspection, and BPF map/program metadata.

Risks and test signals: risks include integer overflow in offset/length walking, invalid `vlen`, string table out-of-range references, enum64 sign handling, and bitfield interpretation through `kind_flag`. Tests should parse malformed BTF, verify round-trip encoding, exercise every kind, and load BPF objects that use structs, datasecs, decl/type tags, and 64-bit enums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/btf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/const.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/const.h

Purpose: provides constant-construction and alignment macros that work in both C and assembler UAPI contexts. It prevents C suffixes/casts from leaking into assembly while still giving C code typed constants.

Important APIs/types: macros include `_AC`, `_AT`, `_UL`, `_ULL`, `_BITUL`, `_BITULL`, optional `_BIT128`, `__ALIGN_KERNEL`, `__ALIGN_KERNEL_MASK`, and `__KERNEL_DIV_ROUND_UP`. There are no structs or functions.

Control flow, state, and persistence: all behavior is preprocessor-time. The header branches on `__ASSEMBLY__`; C builds concatenate suffixes and cast expressions, while assembler builds leave constants unannotated. No runtime or persistent state is defined.

Dependencies and integration points: widely included by UAPI headers that need bit masks, alignment, or typed constants, such as `kvm.h`. It interacts with compiler support for `typeof` and `unsigned __int128` in C-only paths.

Risks and test signals: macro changes can break assembly preprocessing, constant width, or ABI bit positions. `_BIT128` is explicitly C-only and can fail if used in assembler-facing macros. Tests should preprocess representative C and assembly users, validate generated constants on 32-bit and 64-bit builds, and check alignment/division macros for side effects and overflow-prone inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/coredump.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/coredump.h

Purpose: defines a userspace coredump-server negotiation ABI. It lets the kernel request a coredump handling decision, lets userspace acknowledge selected behavior, and defines marker bytes for request/ack validation results.

Important APIs/types: feature flags include `COREDUMP_KERNEL`, `COREDUMP_USERSPACE`, `COREDUMP_REJECT`, and `COREDUMP_WAIT`. `struct coredump_req` carries request size, maximum known ack size, and supported feature mask. `struct coredump_ack` returns ack size and selected mask. `enum coredump_mark` reports success or failures such as min size, max size, unsupported mask, or conflicting options.

Control flow, state, and persistence: runtime flow is kernel sends `coredump_req` on a coredump socket, userspace reads/peeks the versioned size, sends a bounded `coredump_ack`, and kernel emits one marker byte. State is transient per crash; persistence is in the generated core or userspace coredump service policy, not in this header.

Dependencies and integration points: depends on `<linux/types.h>`. It integrates kernel coredump generation with external coredump daemons and versioned UAPI negotiation.

Risks and test signals: risks are size negotiation bugs, accepting unsupported mask bits, conflicting kernel/userspace decisions, and old userspace reading only v0 structure sizes. Tests should cover short/long ack sizes, invalid masks, conflicting flags, successful kernel/userspace/reject flows, and forward-compatible larger request structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/elf.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/elf.h

Purpose: exposes Linux ELF base types, constants, and structures for 32-bit and 64-bit ELF parsing. It covers executable/shared-object/core-file metadata used by loaders, debuggers, coredump readers, and kernel/userspace tooling.

Important APIs/types: defines `Elf32_*` and `Elf64_*` scalar types; program, file, dynamic, symbol, relocation, section, note, and auxiliary-vector constants; macros such as `ELF_ST_BIND`, `ELF_ST_TYPE`, `ELF32_R_SYM`, `ELF32_R_TYPE`, `ELF64_R_SYM`, and `ELF64_R_TYPE`; structures including `Elf32/64_Dyn`, `Rel`, `Rela`, `Sym`, `Ehdr`, `Phdr`, `Shdr`, `Nhdr`, `Move`, `Lib`, and symbol version records.

Control flow, state, and persistence: the file defines serialized ELF layout. Readers validate `e_ident`, then traverse headers, sections, program headers, dynamic entries, symbol tables, relocation tables, notes, and version tables. Persistent state is the ELF file or core image.

Dependencies and integration points: depends on `<linux/types.h>` and `<linux/elf-em.h>`. It integrates Linux binfmt loaders, core dumps, perf/debug tools, dynamic linkers, crash analyzers, and architecture-specific ELF constants.

Risks and test signals: risks include endian/word-size confusion, extended numbering (`PN_XNUM`) mishandling, malformed offsets/sizes, GNU/processor-specific constant interpretation, and ABI incompatibility if structures change. Tests should parse 32/64-bit relocatable, executable, shared, and core ELF files; validate symbol and relocation macros; and fuzz malformed header/section length combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/erspan.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/erspan.h

Purpose: defines userspace metadata structures for ERSPAN tunnel metadata mode, covering ERSPAN version 1/type II and version 2/type III metadata passed between tunnel configuration/control paths and kernel networking.

Important APIs/types: `struct erspan_md2` represents version 2 metadata with big-endian timestamp and security group tag plus endian-sensitive bitfields for hardware ID, frame type, platform, overflow, granularity, and direction. `struct erspan_metadata` contains an integer `version` and a union of version 1 `index` or version 2 `md2`.

Control flow, state, and persistence: no executable flow. Userspace selects the union member by `version` and passes metadata to netlink/tunnel code; kernel tunnel code interprets it while encapsulating/decapsulating packets. State is per tunnel or per metadata-mode packet path, depending on the tunnel configuration.

Dependencies and integration points: depends on `<linux/types.h>` and `<asm/byteorder.h>`. Integration is with GRE/ERSPAN tunnel setup, metadata-mode tunnel devices, and tooling that configures mirrored traffic sessions.

Risks and test signals: risks are bitfield endian mistakes, selecting the wrong union member, and treating network-order fields as host-order. Tests should build on big- and little-endian targets, configure ERSPAN v1/v2 tunnels, inspect netlink payloads, and validate captured ERSPAN headers against expected metadata fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/erspan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/fanotify.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/fanotify.h

Purpose: defines the fanotify userspace ABI for filesystem event monitoring and permission decisions. It includes event masks, initialization/mark flags, variable-length event records, permission response records, and iteration helpers.

Important APIs/types: event bits include access, modify, open, close, move, create/delete, exec, overflow, filesystem error, permission events, pre-access, mount attach/detach, child events, rename, and directory events. Init flags define notification/content classes and report formats (`FAN_REPORT_FID`, `FAN_REPORT_NAME`, `FAN_REPORT_PIDFD`, `FAN_REPORT_MNT`). Mark flags target inodes, mounts, filesystems, and mount namespaces. Structures include `fanotify_event_metadata`, `fanotify_event_info_header`, FID/pidfd/error/range/mount info records, `fanotify_response`, and audit-rule response info. Macros `FAN_EVENT_NEXT` and `FAN_EVENT_OK` walk event buffers.

Control flow, state, and persistence: userspace calls `fanotify_init`, adds marks, reads event buffers containing metadata plus optional info records, and writes `fanotify_response` for permission events. Kernel state persists in fanotify groups and marks until removed or the fd closes.

Dependencies and integration points: depends on Linux integer/fsid types and integrates with VFS, mount notifications, audit, file handles, pidfds, and permission mediation services.

Risks and test signals: risks include buffer-walk bugs, unsupported flag combinations, stale deprecated `FAN_ALL_*` masks, missing permission replies, and variable-length FID/name parsing errors. Tests should exercise each report mode, permission allow/deny including `FAN_DENY_ERRNO`, queue overflow, mount events, rename old/new FIDs, and mixed metadata records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/fanotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/filter.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/filter.h

Purpose: defines classic Linux socket filter program structures and helper macros used with `SO_ATTACH_FILTER` and TUN/TAP filtering. It extends the common BPF instruction constants with socket-filter-specific return, misc, scratch-memory, and ancillary-data definitions.

Important APIs/types: `struct sock_filter` is one BPF instruction (`code`, true/false jumps, `k`). `struct sock_fprog` carries a program length and pointer to the instruction array. Macros include `BPF_STMT`, `BPF_JUMP`, `BPF_RVAL`, `BPF_A`, `BPF_MISCOP`, `BPF_TAX`, `BPF_TXA`, `BPF_MEMWORDS`, and `SKF_AD_*` negative-offset ancillary fields such as protocol, ifindex, mark, queue, CPU, VLAN tag, and random.

Control flow, state, and persistence: userspace builds an instruction array, passes it to the kernel, and the kernel validates and attaches it to a socket or TAP filter. The filter then runs per packet. Attached program state persists with the socket/device until detached or closed; scratch memory is per execution.

Dependencies and integration points: depends on `<linux/types.h>` and `bpf_common.h`. It integrates sockets, seccomp-like classic BPF infrastructure, packet capture, TUN/TAP, and network filtering tools.

Risks and test signals: risks are invalid jump offsets, negative ancillary offset misuse, program length limits, and pointer lifetime during attach. Tests should attach valid/invalid filters, validate ancillary loads, verify packet accept/drop behavior, and compile macros into known instruction arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/fs.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/fs.h

Purpose: central filesystem UAPI header for generic file, inode, block-device, cloning, dedupe, trimming, flags, async I/O, pagemap scanning, and `/proc` map query interfaces. It is a broad ABI surface consumed by libc, filesystem tools, storage tools, and io_uring.

Important APIs/types: structures include `file_clone_range`, `fstrim_range`, `fsuuid2`, `fs_sysfs_path`, `file_dedupe_range_info`, `file_dedupe_range`, `files_stat_struct`, `inodes_stat_t`, `fsxattr`, `page_region`, `pm_scan_arg`, and `procmap_query`. It defines seek modes, rename flags, integrity flags, block ioctls (`BLK*`), filesystem ioctls (`FICLONE`, `FIDEDUPERANGE`, `FS_IOC_*`), inode flags (`FS_*_FL`), xflags (`FS_XFLAG_*`), `__kernel_rwf_t` and `RWF_*` per-I/O flags, `PAGEMAP_SCAN`, and `PROCMAP_QUERY`.

Control flow, state, and persistence: flow is syscall/ioctl driven. Userspace issues file/block/procfs ioctls with these structures; kernel filesystem, block, or mm code reads input fields, performs operations, and fills output fields. Persistent effects include inode flags, labels, encryption/verity indicators, clone/dedupe extents, block-device state, and write-protection changes from pagemap scanning.

Dependencies and integration points: includes limits, ioctl, types, fscrypt for userspace, and mount flags. It integrates VFS, block layer, filesystems such as ext4/xfs/btrfs, procfs memory inspection, and io_uring read/write flags.

Risks and test signals: risks include ioctl number compatibility, 32/64-bit structure size issues, reserved fields not zeroed, dangerous persistent flags such as immutable/append/DAX, and partial clone/dedupe results. Tests should cover ioctl ABI sizes, compat ioctls, clone/dedupe/trim, fs labels/UUIDs, RWF flag validation, pagemap scans, and proc map queries with short buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/fscrypt.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/fscrypt.h

Purpose: defines the userspace ioctl ABI for filesystem encryption policies and key management on fscrypt-capable filesystems. It supports legacy v1 policies and recommended v2 policies with HKDF and key verification.

Important APIs/types: policy flags cover filename padding, direct keys, and IV inode/logical-block modes. Encryption modes include AES-XTS/CTS/CBC, SM4, Adiantum, and AES-HCTR2. Types include `fscrypt_policy_v1`, legacy `fscrypt_key`, `fscrypt_policy_v2`, `fscrypt_get_policy_ex_arg`, `fscrypt_key_specifier`, `fscrypt_provisioning_key_payload`, `fscrypt_add_key_arg`, `fscrypt_remove_key_arg`, and `fscrypt_get_key_status_arg`. Ioctls include `FS_IOC_SET/GET_ENCRYPTION_POLICY`, `FS_IOC_GET_ENCRYPTION_POLICY_EX`, add/remove key, get key status, and get nonce.

Control flow, state, and persistence: userspace sets an encryption policy on an empty directory, provisions keys by descriptor or identifier, checks/removes keys, and then file creation/open paths enforce encryption. Persistent state is on-disk policy metadata and per-filesystem key availability; raw keys are transient and should not be persisted by this ABI.

Dependencies and integration points: depends on ioctl and types headers and is included by `fs.h` for non-kernel users. It integrates ext4/f2fs/ubifs encryption, Linux keyrings, hardware-wrapped keys, and provisioning services.

Risks and test signals: risks include using deprecated v1 descriptors, leaking raw keys, unsupported mode/flag combinations, nonzero reserved fields, and removal while files remain busy. Tests should set/get v1 and v2 policies, add/remove keys for all specifier types, verify status flags, reject invalid reserved fields, and perform encrypted file I/O across mount/remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/fscrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/genetlink.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/genetlink.h

Purpose: defines the Generic Netlink message header and controller ABI used to discover and manage netlink families, operations, multicast groups, and policy metadata.

Important APIs/types: `struct genlmsghdr` carries command, version, and reserved fields after a netlink header. Macros define family name length, ID ranges, header length, command capability flags, and reserved static family IDs. Controller enums define commands (`CTRL_CMD_NEWFAMILY`, `GETFAMILY`, `GETOPS`, `GETPOLICY`), family attributes, operation attributes, multicast-group attributes, and policy dump attributes.

Control flow, state, and persistence: userspace sends `NETLINK_GENERIC` messages with an `nlmsghdr`, `genlmsghdr`, and TLV attributes. The controller reports dynamic family IDs and capabilities that userspace caches for later requests. Persistent state is kernel-registered generic netlink families, not in this header.

Dependencies and integration points: depends on `<linux/types.h>` and `netlink.h`. It integrates with all Generic Netlink families, including generated YNL families such as `netdev`, and with libnl/iproute2-style discovery.

Risks and test signals: risks include stale cached family IDs, incorrect `GENL_HDRLEN` alignment, unknown controller attributes, and privilege flag handling. Tests should query `GENL_ID_CTRL`, dump families/ops/groups/policies, validate nested attributes, and check permission failures for admin-only operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/genetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/hw_breakpoint.h

Purpose: exposes generic hardware breakpoint/watchpoint length and access-type constants for perf events and ptrace/debug tooling.

Important APIs/types: length enum values define byte lengths 1 through 8. Type enum values define empty, read, write, read/write, execute, and invalid combinations. There are no structs or functions.

Control flow, state, and persistence: the header is compile-time constants only. Runtime flow is consumers passing these values in breakpoint attributes to kernel perf/debug APIs; kernel and architecture code validate whether the requested type and length can be represented by hardware debug registers.

Dependencies and integration points: standalone UAPI header. It integrates perf hardware breakpoints, debuggers, tracing tools, and architecture-specific breakpoint backends.

Risks and test signals: risks are assuming every architecture supports all lengths/types, using `HW_BREAKPOINT_INVALID`, and confusing execute breakpoints with read/write watchpoints. Tests should create perf breakpoint events for supported and unsupported lengths, verify read/write/execute triggers, and validate rejection of invalid combinations on each target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_addr.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_addr.h

Purpose: defines rtnetlink address message structures and attributes for adding, deleting, and dumping interface addresses.

Important APIs/types: `struct ifaddrmsg` carries family, prefix length, flags, scope, and interface index. Attributes include `IFA_ADDRESS`, `IFA_LOCAL`, label, broadcast/anycast/multicast, `IFA_CACHEINFO`, extended `IFA_FLAGS`, route priority, target netns ID, and address protocol. Address flags include secondary/temporary, DAD state, optimistic, deprecated, tentative, permanent, no-prefix-route, multicast auto-join, and stable privacy. `struct ifa_cacheinfo` carries preferred/valid lifetimes and timestamps. Compatibility macros `IFA_RTA` and `IFA_PAYLOAD` locate attributes.

Control flow, state, and persistence: userspace sends `RTM_NEWADDR`, `RTM_DELADDR`, or dump requests with `ifaddrmsg` plus attributes. Kernel updates per-interface address state and returns notifications. Persistent state is network namespace address configuration until removed or namespace/device teardown.

Dependencies and integration points: depends on `types.h` and `netlink.h`; integrates iproute2, NetworkManager/systemd-networkd, IPv4/IPv6 address management, DAD, router advertisements, and netns operations.

Risks and test signals: risks include confusing point-to-point `IFA_ADDRESS` with `IFA_LOCAL`, relying on the 8-bit `ifa_flags` when `IFA_FLAGS` is present, and lifetime/protocol mismatches. Tests should add/dump/delete IPv4 and IPv6 addresses, point-to-point addresses, temporary/deprecated addresses, and route-priority/protocol attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_link.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_link.h

Purpose: large rtnetlink link-configuration ABI for network device attributes, statistics, link kinds, virtual devices, bridge/bond/VLAN/tunnel/SR-IOV settings, XDP attachment, and link stats queries.

Important APIs/types: core stats structures are `rtnl_link_stats`, `rtnl_link_stats64`, `rtnl_hw_stats64`, `rtnl_link_ifmap`, and `if_stats_msg`. Top-level `IFLA_*` attributes cover addresses, name, MTU, qdisc, master, netns, stats, carrier, phys port/switch IDs, alt names, parent device, offload sizes, devlink port, DPLL, and pacing horizon. Nested families cover IPv4/IPv6 `AF_SPEC`, bridge and bridge-port options, `IFLA_INFO_*` link-kind data, VLAN, MACVLAN, VRF, MACsec, XFRM, IPVLAN, netkit, VXLAN/VNI filters, Geneve, bareudp, PPP, GTP, bonding and bond slaves, SR-IOV VF config/stats, VF ports, IPoIB, HSR/PRP, offload stats, XDP, TUN, rmnet, MCTP, and DSA.

Control flow, state, and persistence: userspace sends rtnetlink `RTM_NEWLINK`, `DELLINK`, `GETLINK`, and stats requests with nested attributes. Kernel validates link-kind-specific payloads, mutates netdev/bridge/bond/tunnel state, and emits notifications. Most settings persist for the life of the netdev or network namespace; stats are counters.

Dependencies and integration points: depends on `types.h` and `netlink.h`. It is central to iproute2, network managers, container runtimes, virtual networking, XDP loaders, SR-IOV tooling, switchdev/offload drivers, and tunnel configuration.

Risks and test signals: risks include nested attribute misalignment, wrong attribute family for a link kind, enum value drift, 32-bit stats overflow if `STATS64` is ignored, destructive bridge/bond changes, and unsupported XDP mode combinations. Tests should create/dump/change representative links for each major kind, verify netns moves, stats filters, XDP attach/replace semantics, SR-IOV VF attributes, and unknown-attribute compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_tun.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_tun.h

Purpose: defines the userspace ioctl and packet-header ABI for `/dev/net/tun` TUN/TAP virtual network devices.

Important APIs/types: ioctl constants configure device creation, persistence, ownership/group, link type, offloads, filters, queue attach/detach, ifindex, virtio-net header size/endian, steering/filter eBPF programs, carrier, and device netns fd. `TUNSETIFF` flags include `IFF_TUN`, `IFF_TAP`, `IFF_NO_PI`, `IFF_VNET_HDR`, `IFF_TUN_EXCL`, `IFF_MULTI_QUEUE`, and read-only persistence state. Feature flags include checksum, TSO4/6, ECN, and UFO. `struct tun_pi` is the optional per-packet protocol header, and `struct tun_filter` configures TAP multicast filtering.

Control flow, state, and persistence: userspace opens the tun device, issues `TUNSETIFF`, optionally sets queues/offloads/filters/persistence, then reads/writes packets. Device and queue state persists while file descriptors are open; `TUNSETPERSIST` can keep the netdev beyond fd lifetime.

Dependencies and integration points: depends on Ethernet and socket-filter headers. It integrates VPNs, containers, emulators, virtual switches, eBPF steering, and virtio-net compatible packet paths.

Risks and test signals: risks include flag aliasing (`IFF_NO_PI` and `IFF_NOFILTER` share a value in different contexts), multi-queue attach/detach races, wrong virtio header size/endian, and unsupported offload claims. Tests should create TUN and TAP devices, send/receive packets with and without PI/VNET headers, attach filters/eBPF, exercise multi-queue, and verify persistence/ownership permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_tun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_xdp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_xdp.h

Purpose: defines the AF_XDP socket ABI for high-performance packet I/O between userspace rings and XDP-capable network drivers.

Important APIs/types: `sockaddr_xdp` binds a socket to interface/queue and optional shared UMEM. Ring and mmap types include `xdp_ring_offset` and `xdp_mmap_offsets`. `xdp_umem_reg` registers packet memory with chunk size, headroom, flags, and optional Tx metadata length. `xdp_statistics` and `xdp_options` report drops, invalid descriptors, ring starvation, and zero-copy. Socket options configure ring sizes, UMEM, statistics, options, and Tx budget. Descriptor-related definitions cover mmap offsets, unaligned chunk address masks, and Tx metadata requests/completion flags.

Control flow, state, and persistence: userspace creates an AF_XDP socket, configures Rx/Tx/fill/completion rings and UMEM, mmaps rings, binds to a queue, then advances producer/consumer indices. Kernel/driver and userspace share ring state until socket/UMEM teardown.

Dependencies and integration points: depends on Linux types. It integrates XDP programs, netdev queue configuration, zero-copy driver support, libxdp/libbpf, and high-throughput packet processors.

Risks and test signals: risks include producer/consumer ordering bugs, invalid descriptors, UMEM alignment/chunk masking mistakes, zero-copy fallback assumptions, need-wakeup handling, and multi-buffer packet drops if `XDP_USE_SG` is absent. Tests should run copy and zero-copy modes, shared UMEM, unaligned chunks, need-wakeup polling, multi-buffer Rx, Tx metadata, and statistics validation under packet loss/backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/if_xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/in.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/in.h

Purpose: defines Linux IPv4 protocol numbers, socket address structures, multicast request structures, socket options, IP packet option constants, and special address helpers for userspace networking.

Important APIs/types: types include `struct in_addr`, `sockaddr_in`, `ip_mreq`, `ip_mreqn`, `ip_mreq_source`, `group_req`, `group_source_req`, `in_pktinfo`, `ip_msfilter`, and timestamp/original-destination helpers where present. Constants cover `IPPROTO_*` values, IPv4 address classes and specials, `INADDR_*`, IP socket options such as `IP_TOS`, `IP_TTL`, `IP_HDRINCL`, multicast membership/source filters, `IP_PKTINFO`, `IP_RECVERR`, `IP_TRANSPARENT`, `IP_FREEBIND`, and PMTU/security options.

Control flow, state, and persistence: userspace passes these structures to `socket`, `bind`, `connect`, `setsockopt`, `getsockopt`, `sendmsg`, and `recvmsg`. Kernel stores per-socket options and multicast memberships until socket close or explicit drop.

Dependencies and integration points: depends on Linux/socket integer types and integrates TCP/IP sockets, multicast routing, raw sockets, transparent proxying, network namespaces, and netfilter/NAT helpers.

Risks and test signals: risks include byte-order mistakes in addresses/ports, obsolete classful address assumptions, option availability differences, multicast source-filter size handling, and privilege requirements for raw/transparent options. Tests should set/get representative IPv4 options, join/drop multicast and source-specific multicast, verify ancillary `IP_PKTINFO`, test PMTU/error queue behavior, and bind special addresses in namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/io_uring.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/io_uring.h

Purpose: defines the complete io_uring userspace ABI: submission/completion entries, setup flags, operation codes, mmap ring offsets, enter/register flags, registered resource structures, probes, restrictions, provided buffers, and ancillary result formats.

Important APIs/types: `io_uring_sqe` encodes per-operation input through unions for fd, offsets, buffers, flags, fixed-file slots, socket/xattr/splice/msg-ring/uring-cmd fields, and optional 128-byte command data. `enum io_uring_op` covers reads/writes, fsync, poll, timeouts, sockets, open/close/statx, splice/tee, filesystem operations, xattrs, msg ring, uring command, zero-copy send, multishot read/recv, waitid, and futex operations. `io_uring_cqe` returns `user_data`, result, and flags. Ring layout types are `io_sqring_offsets`, `io_cqring_offsets`, and `io_uring_params`. Register APIs use resource update/register structures, probe structures, restrictions, buffer rings, getevents args, sync cancel, file index ranges, and recvmsg output.

Control flow, state, and persistence: userspace calls `io_uring_setup`, mmaps SQ/CQ/SQE regions, fills SQEs, advances ring indices, calls `io_uring_enter`, and consumes CQEs. Registered files/buffers/personalities/rings and provided-buffer groups persist until unregistered or ring close.

Dependencies and integration points: depends on `fs.h`, types, and time types. It integrates VFS, block, networking, futex, eventfd, io-wq workers, fixed resources, and liburing.

Risks and test signals: risks include ABI union field misuse per opcode, memory-ordering bugs in shared rings, feature-flag assumptions, CQ overflow, multishot lifetime handling, fixed-resource index errors, and setup flag incompatibilities. Tests should run opcode probes, setup variants, fixed files/buffers, linked operations, cancellation, buffer selection, multishot operations, ring fd registration, and 32-byte CQE/128-byte SQE modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/kcmp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/kcmp.h

Purpose: defines comparison selector constants for the `kcmp(2)` syscall, which lets privileged userspace compare selected kernel resources between two processes.

Important APIs/types: `enum kcmp_type` values cover file table, VM, files, fs, sighand, IO context, System V semundo, individual file descriptors, epoll target-file checks, and named type maximum. `struct kcmp_epoll_slot` identifies an epoll fd, target fd, and target offset for `KCMP_EPOLL_TFD`.

Control flow, state, and persistence: userspace calls `kcmp(pid1, pid2, type, idx1, idx2)`. Kernel compares references or selected objects and returns ordering/equality information. No state is mutated or persisted by the ABI.

Dependencies and integration points: depends on `<linux/types.h>`. It integrates checkpoint/restore tooling, process inspection, and debugging utilities that need to infer resource sharing.

Risks and test signals: risks include permission failures, racing process exit or fd reuse, misinterpreting ordering as more than equality, and using wrong indices for epoll slots. Tests should compare cloned processes with shared/unshared VM/files/fs/sighand resources, compare duplicated fds, verify epoll target checks, and cover permission-denied and stale-pid cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/kcmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/kvm.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/kvm.h

Purpose: defines the main `/dev/kvm`, VM fd, vCPU fd, and device fd ABI for Kernel-based Virtual Machine userspace VMMs. It covers VM creation, memory slots, vCPU run exits, interrupts, dirty logging, capabilities, devices, registers, stats, private guest memory, and architecture hooks.

Important APIs/types: foundational structures include `kvm_userspace_memory_region`, `kvm_userspace_memory_region2`, `kvm_irq_level`, `kvm_irqchip`, `kvm_run`, `kvm_dirty_log`, `kvm_clear_dirty_log`, `kvm_guest_debug`, `kvm_ioeventfd`, `kvm_enable_cap`, IRQ routing entries, `kvm_irqfd`, clock data, one-reg types, device attributes, stats headers/descriptors, memory attributes, guest memfd creation, and pre-fault requests. Exit reasons range from IO/MMIO/hypercall/debug/system events through Hyper-V/Xen/RISC-V/TDX/SNP/ARM exits. Ioctls are grouped for system fd, VM fd, vCPU fd, and device fd. Capability constants enumerate feature discovery up to memory attributes, guest memfd, VM types, and architecture-specific features.

Control flow, state, and persistence: VMMs query API/capabilities, create a VM, configure memory/irq/devices, create vCPUs, mmap `struct kvm_run`, and loop on `KVM_RUN`, handling exit-specific union payloads before re-entering. VM/vCPU/device/memory-slot state persists in kernel objects until fds close; dirty logs, stats fds, and guest private memory expose ongoing state.

Dependencies and integration points: depends on const/types/compiler/ioctl and `<asm/kvm.h>` for architecture-specific register/device layouts. It integrates QEMU, crosvm, cloud hypervisors, VFIO, irqfd/ioeventfd, guest memory backends, confidential-computing flows, and live migration.

Risks and test signals: risks include TOCTOU on `kvm_run`, architecture-specific struct assumptions, capability-gated ioctl misuse, dirty-log state-machine mistakes, guest_memfd/private-memory alignment, and ABI breakage from changing ioctl numbers or struct layout. Tests should boot smoke VMs, exercise all enabled caps, IO/MMIO exits, irqfd/ioeventfd, dirty logging/rings, migration save/restore paths, stats fds, memory attributes, and private-memory flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/memfd.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/memfd.h

Purpose: defines flags for `memfd_create(2)`, controlling close-on-exec, sealing, hugetlb backing, executable policy, and huge-page size selection.

Important APIs/types: flags include `MFD_CLOEXEC`, `MFD_ALLOW_SEALING`, `MFD_HUGETLB`, `MFD_NOEXEC_SEAL`, and `MFD_EXEC`. Huge-page selectors are aliases to `HUGETLB_FLAG_ENCODE_*` values for 64KB through 16GB pages. There are no structs or functions.

Control flow, state, and persistence: userspace calls `memfd_create(name, flags)`. Kernel creates an anonymous file descriptor with the requested sealing/exec/hugetlb behavior. State persists in the anonymous file and seals until all fds are closed; hugetlb allocation consumes persistent kernel memory resources while live.

Dependencies and integration points: depends on `<asm-generic/hugetlb_encode.h>`. Integrates shared-memory IPC, sealed blobs, executable loaders, sandboxing, guest-memory backends, and hugetlbfs.

Risks and test signals: risks include incompatible exec flags, missing `MFD_ALLOW_SEALING` before adding seals, hugetlb privilege/resource failures, and huge page size unsupported by the host. Tests should create memfds with sealing and exec variants, add seals, mmap/exec where permitted, allocate hugetlb sizes, and validate error returns for unsupported flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/memfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/mman.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/mman.h

Purpose: defines Linux memory-mapping and memory-advice UAPI flags layered on architecture-generic mmap constants.

Important APIs/types: includes architecture generic mman definitions and adds/normalizes flags for shared mappings, validation, fixed mappings, locked mappings, huge pages, sync mappings, stack growth, populate/nonblock, noreserve, denywrite/executable/file placeholders, and huge-page size encodings. It also defines `MREMAP_*`, `MLOCK_ONFAULT`, `MADV_*` advice values, `MAP_HUGE_SHIFT/MASK`, and related constants where present.

Control flow, state, and persistence: userspace passes flags to `mmap`, `mprotect`, `mremap`, `mlock2`, and `madvise`. Kernel creates or mutates VMA state, page fault behavior, locking, huge page selection, and advisory memory policy. Mapping state persists until munmap, process exit, or further VMA changes.

Dependencies and integration points: depends on architecture generic mman and hugetlb encoding headers. It integrates mm/VMA management, hugetlbfs, tmpfs, device mappings, DAX, allocators, runtimes, and databases.

Risks and test signals: risks include architecture-specific flag differences, `MAP_FIXED` replacement hazards, `MAP_SHARED_VALIDATE` feature rejection, huge page size mismatch, lock-limit failures, and advice values being advisory rather than guaranteed. Tests should mmap shared/private/fixed/huge mappings, validate unknown flag rejection with shared-validate, exercise mremap growth/move, mlock-on-fault, and key madvise modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/module_signature.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/module_signature.h

Purpose: defines the trailer format and algorithm identifiers for signed Linux kernel modules. It is used by tooling that appends or inspects module signatures and by kernel module signature verification.

Important APIs/types: enums list public-key algorithm (`PKEY_ALGO_RSA`, `PKEY_ALGO_ECDSA`) and hash algorithms (`PKEY_HASH_MD4` through SHA variants and SM3). `struct module_signature` records algorithm, hash, signer/key ID lengths, reserved fields, and big-endian signature length. `MODULE_SIG_STRING` is the magic trailer marker.

Control flow, state, and persistence: signing tools append signature data, signer/key identifiers, a `module_signature` record, and the magic string to a module. Kernel module loading parses the trailer from EOF backward, validates the signature against trusted keys, then accepts or rejects loading. Signature data persists in the module file.

Dependencies and integration points: depends on Linux integer types. Integrates module build/signing tools, kernel keyrings, crypto/public-key verification, secure boot policies, and module loader enforcement.

Risks and test signals: risks include endian mistakes in signature length, unsupported hash/pubkey algorithms, malformed trailer lengths, and trusting unsigned or appended data incorrectly. Tests should sign modules with supported algorithms, reject corrupted signatures/trailers, validate absent signatures under permissive and enforcing modes, and inspect signer/key ID lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/module_signature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/mount.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/mount.h

Purpose: defines mount API flags and structures for legacy `mount(2)` flags and the newer file-descriptor-based mount API (`fsopen`, `fsconfig`, `fsmount`, `move_mount`, `open_tree`, `mount_setattr`, and mount ID queries).

Important APIs/types: legacy `MS_*` flags cover read-only, nosuid, nodev, noexec, sync, remount, mandlock, dirsync, noatime, nodiratime, bind, move, recursive, silent, POSIX ACL, unbindable/private/slave/shared propagation, relatime, strictatime, lazytime, and active/no-user internal bits. New API flags include `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSMOUNT_*`, `FSCONFIG_*`, `MOUNT_ATTR_*`, and lookup flags. Structures include `mount_attr`, `mnt_id_req`, and `statmount` with masks for mount attributes, propagation, IDs, fs type, root, point, options, and namespace ID.

Control flow, state, and persistence: userspace opens/configures a filesystem context, creates a detached mount, moves/attaches it, or changes attributes recursively. Kernel mutates namespace mount topology and per-mount attributes; state persists in the mount namespace until unmounted or namespace teardown.

Dependencies and integration points: depends on Linux types. Integrates VFS, containers, namespace setup, systemd-style mount management, idmapped mounts, and filesystem configuration.

Risks and test signals: risks include confusing superblock flags with per-mount attributes, recursive propagation mistakes, mount namespace races, incompatible lookup/empty-path semantics, and structure size extension handling. Tests should cover legacy and new mount flows, bind/move/recursive attributes, idmapped mount userns fds, statmount queries with variable string buffers, and permission failures in user namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/neighbour.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/neighbour.h

Purpose: defines rtnetlink neighbor/ARP/NDP table ABI for neighbor entries, proxy entries, neighbor table parameters, statistics, and FDB activity extensions.

Important APIs/types: `struct ndmsg` identifies neighbor family, interface, state, flags, and type. Neighbor attributes include destination, link-layer address, cache info, probes, VLAN, port, VNI, ifindex, master, protocol, nexthop ID, FDB extended attributes, flags extension, and NDM state masks. Flags/states cover permanent, noarp, stale, reachable, delay, probe, failed, router/proxy, externally learned, offloaded, sticky, managed, locked, and extended state validity. `struct nda_cacheinfo`, `ndt_stats`, `ndtmsg`, and `ndt_config` support timing and table introspection. `NDTPA_*`, `NDTA_*`, and `NFEA_*` enums define tunable table parameters and FDB activity notification attributes.

Control flow, state, and persistence: userspace sends `RTM_NEWNEIGH`, `DELNEIGH`, `GETNEIGH`, and table requests. Kernel updates neighbor/FDB cache entries and table parameters; entries persist until timeout, deletion, device teardown, or namespace teardown.

Dependencies and integration points: depends on netlink/types. Integrates iproute2 `ip neigh`, bridge FDB, ARP/NDP, switchdev/offload, VXLAN/bridge learning, and network managers.

Risks and test signals: risks include stale cache semantics, offload/extern-learned mismatch, hardware FDB sync races, incorrect lifetime units, and nested FDB extension parsing. Tests should add/delete/dump IPv4/IPv6 neighbors, proxy entries, bridge FDB entries, table parameter changes, stale/reachable transitions, and offload/activity notification attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/neighbour.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netdev.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netdev.h

Purpose: generated Generic Netlink UAPI for the `netdev` family, exposing modern network-device capability, page-pool, NAPI, queue, queue-stats, DMA-buf, lease, and XDP/AF_XDP metadata queries and operations.

Important APIs/types: constants define family name/version and multicast groups. Enums describe XDP action features, XDP Rx metadata capabilities, XSK Tx feature flags, queue type, qstats scope, and NAPI threaded mode. Attribute enums cover device capabilities, page pool identity/stats, NAPI settings, queue identity/binding/leases, queue stats counters, DMA-buf binding, and leases. Commands include device/page-pool get and notifications, page-pool stats, queue get/create, NAPI get/set, qstats get, and bind Rx/Tx.

Control flow, state, and persistence: userspace discovers the `netdev` Generic Netlink family, sends command messages with typed attributes, and receives replies or multicast notifications. Operations can read capabilities/counters or mutate NAPI/queue/binding state depending on command. State belongs to netdev queues, page pools, NAPI instances, and namespace-scoped devices.

Dependencies and integration points: generated from `Documentation/netlink/specs/netdev.yaml`; integrates Generic Netlink/YNL tooling, AF_XDP, io_uring networking providers, page-pool recycling, DMA-buf networking, and driver capability reporting.

Risks and test signals: risks include generated-header/spec drift, assuming optional attributes are always present, counter width/availability differences by driver, and admin-permission failures for mutating commands. Tests should validate YNL schema conformance, dump devices/page pools/NAPI/queues, compare qstats to driver counters, subscribe to multicast groups, and exercise bind/create/set commands on supported drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter.h

Purpose: defines core netfilter verdicts, hook numbers, protocol-family identifiers, and address union used by userspace netfilter APIs and kernel-facing UAPI structures.

Important APIs/types: verdict constants include `NF_DROP`, `NF_ACCEPT`, `NF_STOLEN`, `NF_QUEUE`, `NF_REPEAT`, and deprecated `NF_STOP`. Macros encode queue numbers and drop errno values into verdict high bits (`NF_QUEUE_NR`, `NF_DROP_ERR`). Hook enums define IPv4/IPv6/inet pre-routing, local-in, forward, local-out, post-routing, ingress, and netdev ingress/egress. Protocol IDs include inet, IPv4, ARP, netdev, bridge, IPv6, and legacy DECnet for userspace. `union nf_inet_addr` stores IPv4/IPv6 addresses.

Control flow, state, and persistence: netfilter hooks return encoded verdicts that direct packet traversal, queueing, dropping, repeating, or accepting. Userspace APIs such as nfnetlink/nftables use these constants to define rules and verdict expressions. Rulesets persist in kernel tables until replaced/deleted; verdicts are per packet.

Dependencies and integration points: depends on types, compiler, IPv4, and IPv6 headers. Integrates nftables/iptables, nfqueue, conntrack/NAT, bridge and netdev packet paths.

Risks and test signals: risks include errno encoding mistakes, queue-number truncation to 16 bits, relying on deprecated `NF_STOP`, and hook-family mismatch. Tests should install nftables/iptables rules for accept/drop/queue/repeat-like behavior, verify NFQUEUE numbers and drop errors, and exercise inet/bridge/netdev hook families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter_arp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter_arp.h

Purpose: defines ARP-specific netfilter protocol and hook constants for userspace compatibility with ARP filtering.

Important APIs/types: `NF_ARP` is the pseudo protocol family value because there is no `PF_ARP`. Hook constants are `NF_ARP_IN`, `NF_ARP_OUT`, and `NF_ARP_FORWARD`; userspace also sees `NF_ARP_NUMHOOKS`.

Control flow, state, and persistence: ARP packets traverse the ARP netfilter hooks and rules return core netfilter verdicts from `netfilter.h`. Persistent state is the configured ARP filtering ruleset, not this header.

Dependencies and integration points: includes `netfilter.h`. Integrates arptables/nftables ARP-family rules, bridge/ARP filtering paths, and legacy tooling that expects these hook numbers.

Risks and test signals: risks are assuming ARP has a normal socket protocol family, mixing ARP hook numbers with IPv4/inet hooks, and relying on legacy arptables behavior without nftables compatibility testing. Tests should install ARP input/output/forward rules, verify ARP request/reply filtering, and compare legacy arptables and nftables ARP-family behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter_arp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netlink.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netlink.h

Purpose: defines the core Netlink socket ABI: protocol numbers, socket/message headers, request flags, alignment helpers, error/extended-ack attributes, socket options, mmap ring structs, generic attribute headers, and bitfield attributes.

Important APIs/types: `sockaddr_nl` identifies netlink family, port ID, and multicast groups. `nlmsghdr` is the common message header with length/type/flags/sequence/pid. Macros handle request/dump/create/delete flags, ACK flags, `NLMSG_ALIGN`, `NLMSG_LENGTH`, `NLMSG_SPACE`, `NLMSG_DATA`, `NLMSG_NEXT`, `NLMSG_OK`, and `NLMSG_PAYLOAD`. `nlmsgerr` and `nlmsgerr_attrs` support ACK/error reporting. Socket options include memberships, packet info, broadcast errors, no-ENOBUFS, mmap rings, namespace listening, capped ACK, extended ACK, and strict checking. `nlattr` plus `NLA_*` flags/macros define nested/network-order TLVs; `nla_bitfield32` carries masked bit updates.

Control flow, state, and persistence: userspace sends datagrams containing one or more aligned `nlmsghdr` messages and nested attributes; kernel replies with ACKs, dumps, multicast notifications, or errors. Socket membership and mmap ring state persist for the socket lifetime; subsystem state is managed by protocol-specific families.

Dependencies and integration points: depends on kernel/socket/types headers and underpins rtnetlink, Generic Netlink, netfilter netlink, audit, uevent, crypto, RDMA, and many management tools.

Risks and test signals: risks include length/alignment bugs, infinite/unsafe message iteration on malformed lengths, lost multicast notifications, stale sequence handling, strict-check incompatibilities, and nested attribute flag misuse. Tests should parse malformed messages, validate multi-part dumps and ACK TLVs, join/drop multicast groups, use strict checking, and fuzz nested attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/netlink.h -->
