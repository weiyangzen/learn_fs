<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gen_stats.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gen_stats.h

## Purpose
`gen_stats.h` defines the generic traffic-control statistics ABI used in netlink attributes for qdiscs, classes, actions, and estimators. It is a layout contract between kernel networking code and user tools such as `tc`.

## Important APIs, types, and functions
The exported attribute IDs are `TCA_STATS_UNSPEC`, `TCA_STATS_BASIC`, `TCA_STATS_RATE_EST`, `TCA_STATS_QUEUE`, `TCA_STATS_APP`, `TCA_STATS_RATE_EST64`, `TCA_STATS_PAD`, and `TCA_STATS_BASIC_HW`, bounded by `TCA_STATS_MAX`. Data layouts are `struct gnet_stats_basic`, `struct gnet_stats_rate_est`, `struct gnet_stats_rate_est64`, `struct gnet_stats_queue`, and `struct gnet_estimator`.

## Control flow
This header has no executable flow. The kernel fills nested `TCA_STATS_*` netlink attributes; user space selects known attributes and decodes the matching fixed-size structures.

## State and persistence behavior
State is sampled counter state, not persistent configuration. 64-bit byte and packet counters are used for basic stats, while queue counters and estimator settings reflect current qdisc/action state.

## Dependencies and integration points
It depends on `<linux/types.h>` and is included by traffic-control UAPI consumers. It integrates with rtnetlink dumps and rate estimator setup.

## Risks and test signals
Risks are ABI size changes, 32-bit rate estimator overflow, confusing software and hardware basic counters, and attribute alignment mistakes. Test signals include `tc -s` dumps, netlink policy validation, 32/64-bit userspace decoding, and qdisc/action tests that compare byte, packet, drop, requeue, and rate fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gen_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genetlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/genetlink.h

## Purpose
`genetlink.h` defines the generic netlink wire ABI: message header shape, static family ID ranges, operation flags, and the controller family used to discover families, operations, multicast groups, and policy dumps.

## Important APIs, types, and functions
The core message prefix is `struct genlmsghdr` with `cmd`, `version`, and `reserved`. Constants include `GENL_NAMSIZ`, `GENL_MIN_ID`, `GENL_MAX_ID`, `GENL_ID_CTRL`, `GENL_START_ALLOC`, and operation flags such as `GENL_ADMIN_PERM`, `GENL_CMD_CAP_DO`, `GENL_CMD_CAP_DUMP`, `GENL_CMD_CAP_HASPOL`, and `GENL_UNS_ADMIN_PERM`. Controller enums define `CTRL_CMD_*`, `CTRL_ATTR_*`, `CTRL_ATTR_OP_*`, `CTRL_ATTR_MCAST_GRP_*`, and `CTRL_ATTR_POLICY_*`.

## Control flow
Generic netlink messages travel as normal netlink messages whose payload starts with `genlmsghdr`, followed by family-specific attributes. User space queries the controller family with `CTRL_CMD_GETFAMILY` or policy commands before issuing family-specific commands.

## State and persistence behavior
The header declares no storage. Runtime state lives in registered kernel generic-netlink families, their dynamic IDs, multicast groups, and operation policies.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/netlink.h>`. It is the common discovery layer used by many headers in this subset, including GTP and handshake.

## Risks and test signals
Risks include treating dynamic family IDs as stable, missing admin-permission checks, policy nesting mismatches, and older tools not understanding newer controller attributes. Test signals are `genl-ctrl-list`, YNL policy dumps, strict attribute validation, multicast group discovery, and 32/64-bit header alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genwqe/genwqe_card.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/genwqe/genwqe_card.h

## Purpose
`genwqe_card.h` exposes the userspace ABI for IBM GenWQE accelerator cards. It covers device naming, card types, MMIO register offsets, DDCB command submission, bitstream update/read operations, memory pinning, and register access ioctls.

## Important APIs, types, and functions
The header exports `GENWQE_DEVNAME`, card type IDs, unit offset helpers, SLU/SLC/HSU/APP register offsets, DDCB return codes and command options, service layer commands, `enum genwqe_card_state`, `struct genwqe_reg_io`, `struct genwqe_bitstream`, `struct genwqe_debug_data`, `struct genwqe_ddcb_cmd`, and `struct genwqe_mem`. Ioctls use `GENWQE_IOC_CODE` and include `GENWQE_READ_REG*`, `GENWQE_WRITE_REG*`, `GENWQE_GET_CARD_STATE`, `GENWQE_PIN_MEM`, `GENWQE_UNPIN_MEM`, `GENWQE_EXECUTE_DDCB`, `GENWQE_EXECUTE_RAW_DDCB`, `GENWQE_SLU_UPDATE`, and `GENWQE_SLU_READ`.

## Control flow
User space opens the GenWQE character device, optionally reads or writes diagnostic registers, pins memory for DMA reuse, prepares a DDCB command with ASIV/ASV payload and ATS fixup descriptors, then executes it synchronously. Flash and bitstream flows use the service layer update/read ioctls and service commands.

## State and persistence behavior
Persistent state may exist on the accelerator, in flash bitstreams, and in pinned user memory mappings held until unpin or file close. The card state enum describes not-available, unconfigured, configured, and failure cases. DDCB completion fields and debug data are per-command.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/ioctl.h>`, and integrates with the GenWQE char driver, sysfs/debugfs naming, PCI PF/VF register windows, DMA mapping, and accelerator firmware.

## Risks and test signals
Risks include raw register access causing device recovery, stale pinned memory, ATS fixup offsets that do not match hardware expectations, struct packing changes, flash update corruption, and return-code confusion between driver errors and DDCB `retc`. Test signals include ioctl ABI size checks, DDCB echo commands, pin/unpin leak tests, PF/VF permission tests, illegal-MMIO-value handling, fault injection for DMA mapping, and flash read/update validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genwqe/genwqe_card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gfs2_ondisk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gfs2_ondisk.h

## Purpose
`gfs2_ondisk.h` defines the stable on-disk format for GFS2 metadata. It is consumed by the kernel filesystem, recovery paths, and userspace tools that inspect, create, repair, or upgrade GFS2 volumes.

## Important APIs, types, and functions
Key constants include `GFS2_MAGIC`, basic block size, non-disk lock numbers, format numbers, metatype IDs, `GFS2_SB_ADDR`, resource-group bitmap states, resource-group flags, dinode flags, directory limits, EA type/flag values, log header flags, log flush caller bits, log descriptor types, and quota flags. Fixed layouts include `struct gfs2_inum`, `gfs2_meta_header`, `gfs2_sb`, `gfs2_rindex`, `gfs2_inode_lvb`, `gfs2_rgrp_lvb`, `gfs2_rgrp`, `gfs2_quota`, `gfs2_dinode`, `gfs2_dirent`, `gfs2_leaf`, `gfs2_ea_header`, `gfs2_log_header`, `gfs2_log_descriptor`, `gfs2_inum_range`, `gfs2_statfs_change`, `gfs2_quota_change`, and `gfs2_quota_lvb`.

## Control flow
There is no code flow in the header. Runtime consumers read blocks, validate `mh_magic`, `mh_type`, and format fields, convert big-endian fields to CPU order, then dispatch to resource group, dinode, directory, extended attribute, log, statfs, quota, or lock-value-block handling. Journal recovery interprets log headers and descriptors before replaying or revoking metadata.

## State and persistence behavior
Almost every structure here is persistent disk or distributed-lock state. The ABI preserves historical padding for GFS1 compatibility, old superblock upgrades, and fixed journal formats. Resource group bitmaps persist allocation state, dinodes persist file metadata, log records persist recovery state, and LVBs mirror cluster-visible lock state.

## Dependencies and integration points
It depends on `<linux/types.h>` and POSIX mode bits used by `DT2IF()`/`IF2DT()`. It integrates with gfs2 kernel code, dlm lock state, gfs2-utils, fsck, mkfs, quota tooling, NFS generation handling, and journal recovery.

## Risks and test signals
Risks include endian mistakes, changing reserved fields, incorrect directory record alignment, resource bitmap state corruption, CRC/hash mismatches, log version confusion around `LH_V1_SIZE`, and cross-node compatibility breaks. Test signals are mkfs/fsck round trips, endian sparse checks, mount/recovery tests after forced shutdown, resource group allocation tests, xattr boundary tests, quota updates, statfs local/global reconciliation, and old-format volume compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gfs2_ondisk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gpib.h

## Purpose
`gpib.h` declares common userspace constants for Linux GPIB devices, including board/descriptor limits, status bits, end-of-string modes, bus-line status encoding, parallel-poll bits, service-request bits, and event IDs.

## Important APIs, types, and functions
The ABI defines `GPIB_MAX_NUM_BOARDS`, `GPIB_MAX_NUM_DESCRIPTORS`, `enum ibsta_bit_numbers`, `enum ibsta_bits`, `enum eos_flags`, `enum bus_control_line`, `enum ppe_bits`, `request_service_bit`, and `enum gpib_events`. `device_status_mask` and `board_status_mask` capture legal status aggregation for device and board APIs.

## Control flow
No functions are defined. GPIB ioctl handlers and libraries update `ibsta`-style status words after read, write, wait, poll, controller, and event operations. Userspace tests bits such as `ERR`, `TIMO`, `END`, `CMPL`, and `RQS` after each operation.

## State and persistence behavior
State is transient bus status and per-board/per-device configuration. EOS and parallel-poll settings may persist for an open descriptor or board until changed, but the header stores no state.

## Dependencies and integration points
This header is paired with `gpib_ioctl.h` and integrates with IEEE-488/GPIB controller drivers and compatibility libraries that emulate NI-488 style status semantics.

## Risks and test signals
Risks include mixing board-only and device-only status bits, missing `ERR`/`TIMO` completion checks, misinterpreting valid-line masks, and EOS mode bit conflicts. Test signals include loopback or instrument tests for read/write completion, serial and parallel poll, SRQ handling, IFC/device-clear events, line-status reads, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gpib_ioctl.h

## Purpose
`gpib_ioctl.h` defines the ioctl command ABI for Linux GPIB character devices. It describes the data structures used to configure boards, open logical devices, transfer data and command bytes, wait for status, serial/parallel poll, control bus lines, and select hardware.

## Important APIs, types, and functions
The ioctl namespace is `GPIB_CODE`. Important structures include `gpib_read_write_ioctl`, `gpib_open_dev_ioctl`, `gpib_close_dev_ioctl`, `gpib_serial_poll_ioctl`, `gpib_eos_ioctl`, `gpib_wait_ioctl`, `gpib_online_ioctl`, `gpib_spoll_bytes_ioctl`, `gpib_board_info_ioctl`, `gpib_select_pci_ioctl`, `gpib_ppoll_config_ioctl`, `gpib_pad_ioctl`, `gpib_sad_ioctl`, `gpib_select_device_path_ioctl`, and `gpib_request_service2`. `enum gpib_ioctl` names commands such as `IBRD`, `IBWRT`, `IBCMD`, `IBOPENDEV`, `IBWAIT`, `IBSIC`, `IBSRE`, `IBLINES`, `IBPAD`, `IBSAD`, `IBTMO`, `IBRSP`, `IBEOS`, `IBPPC`, `IBBOARD_INFO`, `IBSELECT_PCI`, `IBEVENT`, `IBAUTOSPOLL`, `IBONL`, and `IBRSV2`.

## Control flow
User space opens the board device, optionally selects hardware, opens a board or addressed device handle, configures addresses, EOS, timeout, controller state, autopolling, or online state, then uses read/write/command ioctls. `IBWAIT` blocks until status masks are satisfied or timeout expires.

## State and persistence behavior
Handles identify open board/device contexts. Board configuration such as PAD/SAD, EOS, timeout, controller mode, autopolling, request service reason, and selected PCI/sysfs device path persists in the driver until reset, close, or explicit ioctl changes.

## Dependencies and integration points
It depends on `<asm/ioctl.h>` and `<linux/types.h>`, and relies on status and mode definitions from `gpib.h`. It integrates with GPIB controller hardware, sysfs device identification, and userspace GPIB libraries.

## Risks and test signals
Risks include unsafe user pointers, 32/64-bit layout mismatches, partial transfer accounting errors, stale handles, bitfield ABI portability in board-info and ppoll config structs, and long blocking waits. Test signals include compat ioctl tests, transfer-count verification, invalid-handle rejection, timeout behavior, PCI/path selection, service-request updates, and board-info round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpib_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gpio.h

## Purpose
`gpio.h` defines the userspace ABI for GPIO character devices. It covers chip information, line information, line requests, event delivery, value get/set, reconfiguration, and the deprecated v1 ABI retained for compatibility.

## Important APIs, types, and functions
The v2 ABI centers on `struct gpiochip_info`, `enum gpio_v2_line_flag`, `struct gpio_v2_line_values`, `enum gpio_v2_line_attr_id`, `struct gpio_v2_line_attribute`, `struct gpio_v2_line_config_attribute`, `struct gpio_v2_line_config`, `struct gpio_v2_line_request`, `struct gpio_v2_line_info`, `struct gpio_v2_line_info_changed`, and `struct gpio_v2_line_event`. V2 ioctls include `GPIO_GET_CHIPINFO_IOCTL`, `GPIO_V2_GET_LINEINFO_IOCTL`, `GPIO_V2_GET_LINEINFO_WATCH_IOCTL`, `GPIO_V2_GET_LINE_IOCTL`, `GPIO_V2_LINE_SET_CONFIG_IOCTL`, `GPIO_V2_LINE_GET_VALUES_IOCTL`, `GPIO_V2_LINE_SET_VALUES_IOCTL`, and line-info unwatch. V1 exposes `gpioline_info`, `gpiohandle_request`, `gpiohandle_config`, `gpiohandle_data`, `gpioevent_request`, and `gpioevent_data`.

## Control flow
Users open a gpiochip device, fetch chip/line metadata, request one or more line offsets with a `gpio_v2_line_config`, receive an anonymous request fd, then read edge events or issue get/set/reconfigure ioctls on that fd. Line info watch produces change events when request, release, or config state changes.

## State and persistence behavior
Chip and line metadata is live kernel state. A successful line request persists ownership, consumer label, direction, bias, drive, active-low, edge, debounce, event clock, and event buffer state until the request fd closes or config changes. Events carry monotonic, realtime, or HTE timestamps and sequence counters.

## Dependencies and integration points
It depends on `<linux/const.h>`, `<linux/ioctl.h>`, and `<linux/types.h>`. It integrates with gpiolib, the `/dev/gpiochipN` and anonymous request fds, pinctrl/bias support, hardware timestamping, and libgpiod.

## Risks and test signals
Risks include nonzero reserved padding, duplicate attributes for one line, invalid masks, mixed v1/v2 semantics, event buffer overflow, confusing active with physical polarity, and unsupported bias/drive/timestamp flags. Test signals include libgpiod conformance, ioctl struct-size checks, multi-line get/set ordering, edge-event sequence validation, debounce tests, watch/unwatch events, v1 compatibility tests, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gsmmux.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gsmmux.h

## Purpose
`gsmmux.h` defines the userspace ioctl ABI for configuring the `n_gsm` line discipline used by GSM 07.10/TS 27.010 multiplexing. It covers basic mux parameters, raw-IP network mode, extended keepalive/wait settings, and per-DLCI configuration.

## Important APIs, types, and functions
The flag `GSM_FL_RESTART` can force a DLCI reset. `struct gsm_config` carries basic line discipline settings such as adaption, encapsulation, initiator mode, timers `t1`/`t2`/`t3`, retransmit count `n2`, MRU/MTU, window `k`, and frame type `i`. `struct gsm_netconfig` configures raw-IP network interfaces. `struct gsm_config_ext` adds keepalive, wait-config, and flags. `struct gsm_dlci_config` configures channel, adaption, MTU, priority, frame type, window, and flags. Ioctls include `GSMIOC_GETCONF`, `GSMIOC_SETCONF`, `GSMIOC_ENABLE_NET`, `GSMIOC_DISABLE_NET`, `GSMIOC_GETFIRST`, `GSMIOC_GETCONF_EXT`, `GSMIOC_SETCONF_EXT`, `GSMIOC_GETCONF_DLCI`, and `GSMIOC_SETCONF_DLCI`.

## Control flow
Users attach `n_gsm` to a tty, set mux configuration, optionally create virtual tty channels or a network interface, then tune global or DLCI-specific parameters. DLCI config uses the `channel` field to select which virtual channel is being read or updated.

## State and persistence behavior
Configuration is live per line discipline instance and per DLCI. Network mode creates kernel netdevice state. Restart flags are consumed by the kernel and cleared on retrieval.

## Dependencies and integration points
It depends on `<linux/const.h>`, `<linux/if.h>`, `<linux/ioctl.h>`, and `<linux/types.h>`. It integrates with tty line disciplines, GSM modem control channels, virtual ttys, and raw-IP cellular network interfaces.

## Risks and test signals
Risks include invalid timer units, stale DLCI settings, restart side effects, unsupported protocols beyond `ETH_P_IP`, uninitialized reserved fields, and interface-name truncation. Test signals include mux setup/teardown tests, DLCI open/close resets, raw-IP netdevice creation, keepalive timeout behavior, and ABI checks for zeroed reserved fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gsmmux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gtp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gtp.h

## Purpose
`gtp.h` defines the generic-netlink ABI for the kernel GPRS Tunneling Protocol implementation. It lets userspace create, delete, query, and monitor PDP contexts for GTP-U tunnels.

## Important APIs, types, and functions
The multicast group name is `GTP_GENL_MCGRP_NAME`. `enum gtp_genl_cmds` defines `GTP_CMD_NEWPDP`, `GTP_CMD_DELPDP`, `GTP_CMD_GETPDP`, and `GTP_CMD_ECHOREQ`. `enum gtp_version` distinguishes `GTP_V0` and `GTP_V1`. `enum gtp_attrs` defines attributes for link index, version, v0 TID, peer address, MS address, flow, network namespace fd, v1 input/output TEIDs, padding, IPv6 peer/MS addresses, and address family.

## Control flow
User space discovers the generic-netlink family, sends `NEWPDP` with link, version, tunnel identifiers, peer/MS addresses, and optional netns fd, then deletes or dumps contexts through `DELPDP`/`GETPDP`. Echo requests use the command channel to probe peers.

## State and persistence behavior
PDP context state lives in the kernel GTP device and is keyed by GTP version and tunnel IDs. It persists until deleted, the netdevice is removed, or the network namespace exits.

## Dependencies and integration points
It relies on generic netlink definitions and integrates with GTP netdevices, network namespaces, mobile-core control planes, and route/address management.

## Risks and test signals
Risks include mixing v0 TID and v1 TEID attributes, IPv4/IPv6 family mismatches, stale namespace fds, duplicate tunnel keys, and userspace assuming multicast group availability. Test signals include netlink policy tests, PDP add/delete/dump round trips, packet encapsulation/decapsulation tests, namespace teardown, echo request handling, and IPv6 attribute coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gtp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/handshake.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/handshake.h

## Purpose
`handshake.h` is an auto-generated YNL generic-netlink UAPI for the kernel handshake service. It lets kernel consumers delegate transport handshakes, currently TLS via `tlshd`, to userspace.

## Important APIs, types, and functions
The family is `HANDSHAKE_FAMILY_NAME` with version `HANDSHAKE_FAMILY_VERSION`. Enums define handler classes (`HANDSHAKE_HANDLER_CLASS_TLSHD`), message types (`CLIENTHELLO`, `SERVERHELLO`), auth modes (`UNAUTH`, `PSK`, `X509`), X.509 certificate/private-key attributes, accept attributes such as socket fd, handler class, message type, timeout, auth mode, peer identity, certificate, peer name, and keyring, done attributes such as status, socket fd, and remote auth, commands `HANDSHAKE_CMD_READY`, `HANDSHAKE_CMD_ACCEPT`, `HANDSHAKE_CMD_DONE`, and multicast groups `none` and `tlshd`.

## Control flow
Userspace announces readiness, receives or issues accept work for a socket and requested handler class, performs the negotiated handshake outside the kernel, then reports completion status and remote authentication details with `DONE`.

## State and persistence behavior
Handshake work is transient per socket. Certificate, keyring, timeout, peer identity, and remote-auth results are carried in netlink messages; durable TLS or transport state is associated with the socket by kernel and daemon code.

## Dependencies and integration points
The file is generated from `Documentation/netlink/specs/handshake.yaml` and integrates with YNL tooling, generic netlink, `tlshd`, kernel TLS/RPC consumers, sockets, keyrings, and X.509 credential handling.

## Risks and test signals
Risks include generated header/spec drift, fd lifetime mistakes, missing timeout handling, wrong auth-mode interpretation, certificate/keyring lookup failures, and daemon/kernel version mismatch. Test signals include YNL schema validation, `tlshd` accept/done round trips, timeout and daemon-crash recovery, X.509/PSK cases, and multicast readiness tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/handshake.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hash_info.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hash_info.h

## Purpose
`hash_info.h` assigns stable numeric IDs and digest sizes for hash algorithms exposed through kernel/user ABI surfaces.

## Important APIs, types, and functions
`enum hash_algo` defines algorithm IDs such as `HASH_ALGO_MD4`, `MD5`, `SHA1`, `RIPE_MD_160`, `SHA256`, `SHA384`, `SHA512`, `SHA224`, `RIPE_MD_128`, `RIPE_MD_256`, `RIPE_MD_320`, `WP_256`, `WP_384`, `WP_512`, `TGR_128`, `TGR_160`, `TGR_192`, `SM3_256`, `STREEBOG_256`, `STREEBOG_512`, `SHA3_256`, `SHA3_384`, and `SHA3_512`, ending with `HASH_ALGO__LAST`.

## Control flow
There is no runtime flow. Kernel subsystems and tools pass or store the enum ID, then use subsystem-specific lookup tables to map it to crypto algorithm names and digest sizes.

## State and persistence behavior
Algorithm IDs may appear in persisted signatures, measurement logs, module metadata, integrity records, or policy formats. The enum ordering is therefore ABI-sensitive, and new algorithms must be appended rather than inserted.

## Dependencies and integration points
It is a small standalone UAPI header used by integrity, module-signing, key, and measurement code that needs stable hash IDs.

## Risks and test signals
Risks include reordering enum values, missing table entries for newly appended algorithms, digest-size assumptions made outside this header, and disagreement with crypto API names. Test signals include build-time table coverage for every enum, IMA/EVM/module-signing verification with each supported hash, unknown numeric ID rejection by consumers, and ABI regression tests for numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hash_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hdlc.h

## Purpose
`hdlc.h` defines common UAPI protocol identifiers for Linux generic HDLC network devices.

## Important APIs, types, and functions
`enum hdlc_proto` assigns values for `GENERIC`, `CISCO`, `FR`, `FR_ADD_PVC`, `FR_DEL_PVC`, `X25`, `HDLC_ETH`, `PPP`, `CHDLC`, and `RAW`. The maximum type is `PROTO_MAX`. `struct hdlc_proto_desc` pairs a protocol ID with a textual description.

## Control flow
No logic is present. Generic HDLC ioctl or netlink handlers use the protocol IDs to select encapsulation or management operations; user tools display or pass descriptors.

## State and persistence behavior
Selected protocol mode is device configuration state stored by the HDLC network driver. The header itself has no persistent state.

## Dependencies and integration points
It is paired with `linux/hdlc/ioctl.h` and generic HDLC drivers for synchronous serial, Frame Relay, Cisco HDLC, PPP, X.25, Ethernet-over-HDLC, and raw HDLC modes.

## Risks and test signals
Risks include protocol ID mismatch between tools and kernel, unsupported mode selection on a device, and stale descriptors for newer modes. Test signals include mode switch tests, device reopen persistence checks, protocol-specific ioctl validation, and packet encapsulation tests for each supported protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc/ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hdlc/ioctl.h

## Purpose
`hdlc/ioctl.h` defines ioctl data structures and constants for configuring generic HDLC network devices, including Cisco HDLC, Frame Relay, raw HDLC, raw Ethernet, PPP, and X.25 modes.

## Important APIs, types, and functions
Constants include `GENERIC_HDLC_VERSION`, encoding modes `ENCODING_*`, parity modes `PARITY_*`, clocking modes `CLOCK_*`, and Frame Relay link management constants `LMI_*`. Structures include `sync_serial_settings`, `te1_settings`, `raw_hdlc_proto`, `fr_proto`, `fr_proto_pvc`, `fr_proto_pvc_info`, `cisco_proto`, `raw_hdlc_proto`, `raw_eth_proto`, `ppp_proto`, and `x25_hdlc_proto` variants visible through protocol-specific configuration.

## Control flow
User tools query or set line settings and selected protocol through socket ioctl paths. For Frame Relay, tools add or delete PVCs and request PVC information using DLCI-related structures. Clocking, encoding, and parity choices are passed to lower-level hardware drivers.

## State and persistence behavior
Device settings such as clock rate, loopback, slot maps, encoding, parity, LMI type, DLCI values, and protocol mode persist in the netdevice/driver until changed or the device is removed. Runtime PVC status and LMI counters are live state.

## Dependencies and integration points
It integrates with generic HDLC network drivers, synchronous serial adapters, netdevice ioctls, and the protocol identifiers in `linux/hdlc.h`.

## Risks and test signals
Risks include invalid clock/encoding combinations, ABI differences in ioctl structures, deleting active PVCs, LMI mismatch with peers, and devices that only support a subset of settings. Test signals include ioctl round trips, line loopback tests, Frame Relay PVC add/delete/status, Cisco keepalive behavior, PPP/X.25 attach tests, and compat ioctl coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdreg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hdreg.h

## Purpose
`hdreg.h` defines the legacy ATA/IDE ioctl ABI, command constants, taskfile layouts, geometry data, drive identity layout, and driver tuning controls historically used by IDE block devices and tools such as `hdparm`.

## Important APIs, types, and functions
The header exports taskfile header sizes, `ide_reg_valid_t`, `ide_task_request_t`, `ide_ioctl_request_t`, `struct hd_drive_cmd_hdr`, userspace task/HOB headers, `TASKFILE_*` data phase flags, many ATA command opcodes (`WIN_READ`, `WIN_WRITE`, `WIN_SMART`, `WIN_IDENTIFY`, `WIN_SETFEATURES`, security and SMART subcommands), `struct hd_geometry`, ioctl numbers `HDIO_GET*`, `HDIO_SET*`, `HDIO_DRIVE_TASKFILE`, `HDIO_DRIVE_TASK`, `HDIO_DRIVE_CMD`, bus states, and the large userspace `struct hd_driveid` matching ATA identify words.

## Control flow
User space issues ioctl calls against a block device to read geometry/identity, query or set IDE driver options, reset devices, or submit raw ATA taskfiles. For identity data, the kernel returns a 512-byte word layout decoded by tools. For raw commands, userspace supplies register-valid masks, taskfile bytes, data-phase direction, and buffers.

## State and persistence behavior
Some ioctls only sample state, while others alter drive or controller state: DMA, write cache, acoustic management, address mode, bus state, transfer mode, keep-settings, reset behavior, and raw ATA side effects. `hd_driveid` is a snapshot of device firmware identify data.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with legacy IDE, libata compatibility paths, block device ioctls, ATA/ATAPI firmware, and disk management tools.

## Risks and test signals
Risks include destructive raw ATA commands, 28/48-bit taskfile mistakes, user pointer/compat layout problems, obsolete ioctls that no longer apply to libata, endianness and word-swapping in identify strings, and security/SMART command misuse. Test signals include `hdparm -I` identity decoding, ioctl permission tests, compat ioctl tests, non-destructive SMART reads, invalid taskfile rejection, reset paths, and checks that obsolete commands fail safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hid.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hid.h

## Purpose
`hid.h` defines common USB HID class constants exposed to userspace and shared by HID-related character-device APIs.

## Important APIs, types, and functions
Constants include `USB_INTERFACE_CLASS_HID`, boot subclass and keyboard/mouse protocol codes, descriptor type values `HID_DT_HID`, `HID_DT_REPORT`, and `HID_DT_PHYSICAL`, and `HID_MAX_DESCRIPTOR_SIZE`. `enum hid_report_type` names input, output, and feature reports in Linux's zero-based internal ordering. `enum hid_class_request` defines USB class requests such as `GET_REPORT`, `GET_IDLE`, `GET_PROTOCOL`, `SET_REPORT`, `SET_IDLE`, and `SET_PROTOCOL`.

## Control flow
The header has no executable flow. HID core, hidraw, and user tools use these constants when parsing report descriptors, issuing class requests, and bounding descriptor buffers.

## State and persistence behavior
HID protocol, idle, descriptors, and reports are device state managed by USB/HID drivers. The header only fixes numeric IDs and maximum descriptor size.

## Dependencies and integration points
It is included by `hidraw.h` and aligns with USB HID class definitions used by kernel HID core, hiddev, hidraw, and userspace HID libraries.

## Risks and test signals
Risks include confusion between Linux zero-based report type enum and HID specification report numbers, descriptor truncation at 4096 bytes, and missing USB type definitions in consumers. Test signals include hidraw descriptor reads, boot keyboard/mouse enumeration, class request handling, malformed descriptor rejection, and report type mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hiddev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hiddev.h

## Purpose
`hiddev.h` defines the older parsed-HID userspace ABI for `/dev/usb/hiddev*`. It exposes HID applications, collections, reports, fields, usages, string descriptors, and event reads at a higher level than raw HID reports.

## Important APIs, types, and functions
Structures include `hiddev_event`, `hiddev_devinfo`, `hiddev_collection_info`, `hiddev_string_descriptor`, `hiddev_report_info`, `hiddev_field_info`, `hiddev_usage_ref`, and `hiddev_usage_ref_multi`. Constants cover report IDs (`HID_REPORT_ID_UNKNOWN`, `FIRST`, `NEXT`, `MASK`, `MAX`), report types, field flags, `HID_MAX_MULTI_USAGES`, `HID_FIELD_INDEX_NONE`, `HID_VERSION`, and read flags `HIDDEV_FLAG_UREF`/`HIDDEV_FLAG_REPORT`. Ioctls include `HIDIOCGVERSION`, `HIDIOCAPPLICATION`, `HIDIOCGDEVINFO`, `HIDIOCGSTRING`, `HIDIOCINITREPORT`, `HIDIOCGNAME`, `HIDIOCGREPORT`, `HIDIOCSREPORT`, `HIDIOCGREPORTINFO`, `HIDIOCGFIELDINFO`, `HIDIOCGUSAGE`, `HIDIOCSUSAGE`, `HIDIOCGUCODE`, `HIDIOCGFLAG`, `HIDIOCSFLAG`, collection queries, `HIDIOCGPHYS`, and multi-usage gets/sets.

## Control flow
Users enumerate applications and reports, walk fields and usages by repeatedly using `HID_REPORT_ID_FIRST` and `HID_REPORT_ID_NEXT`, get or set usage values, then optionally send output/feature reports. Reads return either events or usage/report records depending on configured flags.

## State and persistence behavior
Report values, flag mode, and initialized report state are per open HID device. Device descriptors and collections are discovered state from the HID parser; output/feature writes can alter device state.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with the HID parser, USB/input devices, hiddev char devices, and legacy tools that need parsed usages rather than raw reports.

## Risks and test signals
Risks include report ID traversal loops, wrong report type numbering, oversized multi-usage arrays, stale field indexes after device reconnect, and using hiddev for devices better served by hidraw. Test signals include descriptor traversal tests, get/set usage round trips, feature report writes, collection lookup, read-flag behavior, disconnect handling, and compat ioctl coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hiddev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hidraw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hidraw.h

## Purpose
`hidraw.h` defines the raw HID character-device ABI. It lets userspace read and write reports with minimal kernel parsing and query device metadata and report descriptors.

## Important APIs, types, and functions
`struct hidraw_report_descriptor` contains descriptor size and up to `HID_MAX_DESCRIPTOR_SIZE` bytes. `struct hidraw_devinfo` contains bus type, vendor, and product IDs. Ioctls include `HIDIOCGRDESCSIZE`, `HIDIOCGRDESC`, `HIDIOCGRAWINFO`, `HIDIOCGRAWNAME`, `HIDIOCGRAWPHYS`, `HIDIOCSFEATURE`, `HIDIOCGFEATURE`, `HIDIOCGRAWUNIQ`, `HIDIOCSINPUT`, `HIDIOCGINPUT`, `HIDIOCSOUTPUT`, `HIDIOCGOUTPUT`, and `HIDIOCREVOKE`. Limits include `HIDRAW_FIRST_MINOR`, `HIDRAW_MAX_DEVICES`, and `HIDRAW_BUFFER_SIZE`.

## Control flow
Users open `/dev/hidrawN`, query descriptor size and descriptor bytes, then read input reports and write output or feature reports. For feature/input/output ioctls, the first byte of the buffer is the report number.

## State and persistence behavior
The char device has per-open buffering and access state. `HIDIOCREVOKE` can revoke further access. Report effects persist according to device firmware.

## Dependencies and integration points
It depends on `linux/hid.h` and `<linux/types.h>`. It integrates with HID core, udev permissions, USB/Bluetooth/I2C-HID devices, and userspace HID libraries.

## Risks and test signals
Risks include descriptor truncation, missing report-number byte, buffer length mismatches, concurrent access surprises, revoked fds, and device-specific report side effects. Test signals include descriptor round trips, raw report echo tests, feature get/set, disconnect/revoke behavior, minor allocation limits, and fuzzing malformed descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hidraw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hpet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hpet.h

## Purpose
`hpet.h` defines the userspace ioctl ABI for High Precision Event Timer devices exposed through `/dev/hpet`.

## Important APIs, types, and functions
`struct hpet_info` returns interrupt frequency, feature flags, HPET block number, and timer number. `HPET_INFO_PERIODIC` indicates periodic-capable comparator support. Ioctls are `HPET_IE_ON`, `HPET_IE_OFF`, `HPET_INFO`, `HPET_EPI`, `HPET_DPI`, and `HPET_IRQFREQ`. `MAX_HPET_TBS` bounds timer blocks.

## Control flow
Users open an HPET timer, query its capabilities, set interrupt frequency, optionally enable periodic mode, then turn interrupts on or off and read timer events from the device.

## State and persistence behavior
Timer interrupt enablement, periodic mode, and requested frequency are live device/open-file state. No configuration is persisted by the header.

## Dependencies and integration points
It depends on `<linux/compiler.h>` for ioctl macro availability in included environments. It integrates with HPET hardware, the misc/char driver, timer interrupt delivery, and legacy timing applications.

## Risks and test signals
Risks include unsupported periodic mode, invalid frequency requests, timer resource conflicts, architecture availability differences, and unexpected interrupt rates. Test signals include ioctl round trips, periodic and one-shot interrupt counts, invalid-frequency rejection, open/close cleanup, and `HPET_INFO` capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hpet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/cs-protocol.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hsi/cs-protocol.h

## Purpose
`cs-protocol.h` defines message, command, and control constants for the cellular modem control protocol carried over HSI character devices.

## Important APIs, types, and functions
The header defines `CS_DEV_FILE_NAME`, `CS_IF_VERSION`, command-domain bit packing helpers (`CS_CMD_SHIFT`, `CS_DOMAIN_SHIFT`, `CS_CMD_MASK`, `CS_PARAM_MASK`, `CS_CMD()`), indications `CS_ERROR`, `CS_RX_DATA_RECEIVED`, `CS_TX_DATA_READY`, and `CS_TX_DATA_SENT`, error parameter `CS_ERR_PEER_RESET`, buffer feature flags `CS_FEAT_TSTAMP_RX_CTRL` and `CS_FEAT_ROLLING_RX_COUNTER`, states `CS_STATE_CLOSED`, `CS_STATE_OPENED`, and `CS_STATE_CONFIGURED`, `CS_MAX_BUFFERS`, `struct cs_buffer_config`, `struct cs_timestamp`, `struct cs_mmap_config_block`, and ioctls `CS_GET_STATE`, `CS_SET_WAKELINE`, `CS_GET_IF_VERSION`, and `CS_CONFIG_BUFS`.

## Control flow
User space opens `/dev/cmt_speech`, queries the interface version and state, configures mmap buffer counts/sizes/features, controls the wake line, and receives command indications for RX data availability, TX readiness, TX completion, or peer reset. The shared mmap config block tells applications where RX/TX buffers and counters live.

## State and persistence behavior
Protocol state is transient device state: closed/opened/configured state, wake-line state, configured RX/TX buffer rings, optional RX-control timestamp, RX pointer boundary, and rolling counters. No persistent storage is described in the header.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/ioctl.h>`. It integrates with the Nokia CMT speech character driver, lower-level HSI transport, modem firmware, and userspace telephony/audio daemons using mmap rings.

## Risks and test signals
Risks include command-number drift with firmware, wrong mmap offset handling, buffer count/size validation bugs, wake-line races, timestamp feature mismatches, and unsupported interface versions. Test signals include version/state ioctls, buffer config boundary tests up to `CS_MAX_BUFFERS`, mmap ring RX/TX flow, peer-reset indication handling, wake-line toggling, and ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/cs-protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/hsi_char.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hsi/hsi_char.h

## Purpose
`hsi_char.h` defines the userspace ioctl ABI for HSI character devices, allowing clients to configure transmission parameters, query modem/channel state, and issue break or wake operations.

## Important APIs, types, and functions
The header exports ioctl helpers under `HSI_CHAR_MAGIC` and commands `HSC_RESET`, `HSC_SET_PM`, `HSC_SEND_BREAK`, `HSC_SET_RX`, `HSC_GET_RX`, `HSC_SET_TX`, and `HSC_GET_TX`. Power-management values are `HSC_PM_DISABLE` and `HSC_PM_ENABLE`. Mode and arbitration constants include `HSC_MODE_STREAM`, `HSC_MODE_FRAME`, `HSC_FLOW_SYNC`, `HSC_ARB_RR`, and `HSC_ARB_PRIO`. `struct hsc_rx_config` carries RX mode, flow, and channel count; `struct hsc_tx_config` carries TX mode, channels, speed, and arbitration mode.

## Control flow
Users open an HSI char device, set RX/TX configuration with the config ioctls, optionally enable power management, send break or reset commands, then read/write HSI payloads through the character device.

## State and persistence behavior
Configuration is per HSI char instance and persists while the device is active. Runtime state includes PM enablement, reset/break effects, RX/TX mode, channel count, TX speed, arbitration mode, and transfer queues; payload data is transient.

## Dependencies and integration points
It depends on `<linux/types.h>` and ioctl macros available to users. It integrates with the kernel HSI framework, modem protocol headers such as `cs-protocol.h`, and userspace cellular stacks.

## Risks and test signals
Risks include unsupported speed/mode combinations, racing configuration changes with active transfers, PM state mismatches, reset/break side effects, and ABI layout drift for ioctl structs. Test signals include ioctl set/get symmetry, loopback transfers, break handling, suspend/resume, PM enable/disable tests, invalid parameter rejection, and 32/64-bit compat tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/hsi_char.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsr_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hsr_netlink.h

## Purpose
`hsr_netlink.h` defines netlink attributes for High-availability Seamless Redundancy and Parallel Redundancy Protocol network devices.

## Important APIs, types, and functions
The header exports generic-netlink node attributes `HSR_A_NODE_ADDR`, `HSR_A_IFINDEX`, `HSR_A_IF1_AGE`, `HSR_A_IF2_AGE`, `HSR_A_NODE_ADDR_B`, `HSR_A_IF1_SEQ`, `HSR_A_IF2_SEQ`, `HSR_A_IF1_IFINDEX`, `HSR_A_IF2_IFINDEX`, and `HSR_A_ADDR_B_IFINDEX`, bounded by `HSR_A_MAX`. Commands are `HSR_C_RING_ERROR`, `HSR_C_NODE_DOWN`, `HSR_C_GET_NODE_STATUS`, `HSR_C_SET_NODE_STATUS`, `HSR_C_GET_NODE_LIST`, and `HSR_C_SET_NODE_LIST`, bounded by `HSR_C_MAX`.

## Control flow
User space and the kernel exchange generic-netlink notifications and requests about HSR/PRP node status. Tools can request node status or node lists; the kernel can report ring errors or node-down events with node addresses, interface indexes, ages, and sequence numbers.

## State and persistence behavior
Runtime state lives in HSR/PRP node databases: node addresses, redundant-port ifindexes, per-port ages, and per-port sequence numbers. It persists until aged out, reconfigured, or the device/namespace is removed.

## Dependencies and integration points
It integrates with generic netlink, HSR/PRP network drivers, redundant Ethernet topologies, and network management tools that inspect node lists or receive topology events.

## Risks and test signals
Risks include wrong port ifindex attribution, node-table races, sequence number wrap handling, stale node ages, and netlink policy drift. Test signals include HSR/PRP device creation, dual-port failover, supervision frame observation, node-status/list dumps, sequence number validation, ring-error/node-down notifications, and invalid attribute rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsr_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hw_breakpoint.h

## Purpose
`hw_breakpoint.h` exposes userspace constants for configuring hardware breakpoints and watchpoints through perf events.

## Important APIs, types, and functions
The header defines breakpoint length constants `HW_BREAKPOINT_LEN_1` through `HW_BREAKPOINT_LEN_8` and type bits `HW_BREAKPOINT_EMPTY`, `HW_BREAKPOINT_R`, `HW_BREAKPOINT_W`, `HW_BREAKPOINT_RW`, `HW_BREAKPOINT_X`, and `HW_BREAKPOINT_INVALID`. These values are used in `perf_event_attr.bp_type` and `bp_len`.

## Control flow
User space configures a perf event with a breakpoint address, type mask, and length. The perf and architecture-specific breakpoint code programs hardware debug registers and reports events when the access condition matches.

## State and persistence behavior
Breakpoint state is per perf event and per task or CPU depending on how the event is opened. It persists until the event fd is closed, disabled, or reconfigured.

## Dependencies and integration points
It integrates with `perf_event_open`, architecture debug-register backends, ptrace/debugger tooling, and kernel breakpoint reservation.

## Risks and test signals
Risks include unsupported lengths on some architectures despite the generic 1-8 constants, limited hardware slots, alignment constraints, confusing read/write/execute semantics, and privilege restrictions. Test signals include perf breakpoint selftests, invalid length/type rejection, signal/event delivery tests, per-task versus per-CPU coverage, and architecture-specific slot exhaustion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hyperv.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hyperv.h

## Purpose
`hyperv.h` defines the userspace/kernel message ABI for Hyper-V integration services on Linux: VSS backup coordination, host-to-guest file copy, and key-value-pair exchange including IP injection.

## Important APIs, types, and functions
Version and registration constants include `UTIL_*`, `VSS_OP_REGISTER`, `VSS_OP_REGISTER1`, `FCOPY_CURRENT_VERSION`, `KVP_OP_REGISTER`, and `KVP_OP_REGISTER1`. VSS types include `enum hv_vss_op`, `struct hv_vss_hdr`, `hv_vss_check_feature`, `hv_vss_check_dm_info`, and `hv_vss_msg`. File copy types include `enum hv_fcopy_op`, `struct hv_fcopy_hdr`, `hv_start_fcopy`, and `hv_do_fcopy`. KVP definitions include registry value types, `enum hv_kvp_exchg_op`, `enum hv_kvp_exchg_pool`, Hyper-V status codes, address-family constants, `hv_kvp_ipaddr_value`, `hv_kvp_hdr`, `hv_kvp_exchg_msg_value`, `hv_kvp_msg_*`, `hv_kvp_msg`, and `hv_kvp_ip_msg`.

## Control flow
Userspace daemons register with kernel Hyper-V utility drivers. The kernel relays host requests to daemons: VSS create/freeze/thaw/checks, fcopy start/write/complete/cancel chunks, or KVP get/set/delete/enumerate/IP operations. Daemons respond with data or error status, and the kernel forwards completion to the host.

## State and persistence behavior
VSS state is transaction-scoped but affects filesystem freeze/thaw. Fcopy state persists for the duration of a host file transfer and writes guest files. KVP pools can persist host/guest key-value data and network configuration. The fixed message sizes and packed UTF-16 fields are ABI-critical.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with Hyper-V VMBus/hv_utils, connector or netlink daemon channels, filesystem freeze code, guest file I/O, registry-compatible KVP exchange, and IP configuration tooling.

## Risks and test signals
Risks include daemon/kernel version mismatch, undersized VSS buffers for large host messages, UTF-16 length mistakes, file copy path traversal or overwrite behavior, stale KVP pool data, and incomplete thaw after failures. Test signals include daemon registration compatibility, VSS freeze/thaw under I/O, fcopy chunk sequencing and cancel paths, KVP enumerate invalid-index behavior, IP injection validation, and Hyper-V status-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c-dev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i2c-dev.h

## Purpose
`i2c-dev.h` defines the ioctl ABI for `/dev/i2c-X` adapter character devices, exposing adapter configuration, direct I2C combined transfers, and SMBus transactions to userspace.

## Important APIs, types, and functions
Ioctls include `I2C_RETRIES`, `I2C_TIMEOUT`, `I2C_SLAVE`, `I2C_SLAVE_FORCE`, `I2C_TENBIT`, `I2C_FUNCS`, `I2C_RDWR`, `I2C_PEC`, and `I2C_SMBUS`. `struct i2c_smbus_ioctl_data` carries read/write direction, command, transaction size, and `union i2c_smbus_data` pointer. `struct i2c_rdwr_ioctl_data` carries an array of `struct i2c_msg` and count. `I2C_RDWR_IOCTL_MAX_MSGS` caps combined messages, with misspelled `I2C_RDRW_IOCTL_MAX_MSGS` retained.

## Control flow
User space opens an adapter, selects a slave address and options, queries supported functions, then performs `I2C_RDWR` for combined messages or `I2C_SMBUS` for SMBus operations. `I2C_SLAVE_FORCE` bypasses normal driver ownership checks and should be rare.

## State and persistence behavior
Retries, timeout, selected slave address, ten-bit mode, and PEC mode are per open adapter fd. Transfer buffers are transient and copied/validated by i2c-dev.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/compiler.h>` and uses structures from `linux/i2c.h`. It integrates with I2C adapter drivers, SMBus emulation, sensor/EEPROM tooling, and board-management utilities.

## Risks and test signals
Risks include using unsupported functions, overlong message arrays, unsafe `I2C_SLAVE_FORCE`, ten-bit limitations, pointer compat issues, and devices with side-effectful register writes. Test signals include `i2cdetect`/`i2ctransfer` behavior, function-mask checks, invalid message rejection, SMBus block transfers, PEC toggling, and 32/64-bit compat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i2c.h

## Purpose
`i2c.h` defines the low-level I2C and SMBus transaction ABI shared by kernel and userspace. It describes I2C message segments, adapter functionality masks, SMBus data containers, and SMBus transaction type IDs.

## Important APIs, types, and functions
`struct i2c_msg` contains slave address, flags, length, and buffer pointer. Flags include `I2C_M_RD`, `I2C_M_TEN`, `I2C_M_DMA_SAFE`, `I2C_M_RECV_LEN`, `I2C_M_NO_RD_ACK`, `I2C_M_IGNORE_NAK`, `I2C_M_REV_DIR_ADDR`, `I2C_M_NOSTART`, and `I2C_M_STOP`. Function masks include raw I2C, 10-bit addressing, protocol mangling, PEC, no-start, slave mode, SMBus operation bits, and aggregate masks such as `I2C_FUNC_SMBUS_EMUL`. `union i2c_smbus_data`, `I2C_SMBUS_READ/WRITE`, and `I2C_SMBUS_*` size IDs define SMBus payloads.

## Control flow
An I2C transaction is a sequence of `i2c_msg` segments, each beginning with START and ending with STOP or repeated START unless special protocol-mangling flags apply. SMBus helpers encode common command/data flows with explicit transaction size IDs.

## State and persistence behavior
The header carries no state. Message buffers are transient transfer data; function masks reflect current adapter capabilities.

## Dependencies and integration points
It depends on `<linux/types.h>` and is used by i2c-dev, kernel adapter drivers, SMBus emulation, and userspace tools.

## Risks and test signals
Risks include using protocol-mangling flags without capability bits, `I2C_M_RECV_LEN` buffer underallocation, ten-bit address misuse, DMA-safe flag misuse in userspace, and SMBus block length off-by-one errors. Test signals include adapter functionality tests, combined transfer traces, SMBus block/proc-call validation, NACK behavior, and fuzzing message counts/lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2o-dev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i2o-dev.h

## Purpose
`i2o-dev.h` defines the legacy Intelligent I/O userspace ABI for controller discovery, hardware/resource table reads, parameter set/get, software download/upload/delete, event registration, HTML queries, and raw passthrough messages.

## Important APIs, types, and functions
The ioctl namespace is `I2O_MAGIC_NUMBER`. Ioctls include `I2OGETIOPS`, `I2OHRTGET`, `I2OLCTGET`, `I2OPARMSET`, `I2OPARMGET`, `I2OSWDL`, `I2OSWUL`, `I2OSWDEL`, `I2OVALIDATE`, `I2OHTML`, `I2OEVTREG`, `I2OEVTGET`, `I2OPASSTHRU`, and `I2OPASSTHRU32`. Structures cover passthrough, HRT/LCT commands, parameter set/get, software transfer, HTML, event IDs/info, S/G flags, bus entries (`i2o_pci_bus`, local, ISA, EISA, MCA, other), `i2o_hrt`, `i2o_lct`, `i2o_status_block`, event masks, class/subclass IDs, parameter operations, serial-number formats, adapter states, software module types, and DPT/Adaptec flash constants.

## Control flow
User space opens an I2O control device, enumerates controllers, obtains HRT/LCT topology, reads status, registers for events, manipulates parameter groups, downloads or uploads firmware/software fragments, or sends raw passthrough messages to an IOP.

## State and persistence behavior
Controller topology, LCT change indicators, adapter state, event registrations, software modules, flash fragments, and parameter tables are persistent or semi-persistent IOP/device state. Event queues are bounded by `I2O_EVT_Q_LEN`.

## Dependencies and integration points
It depends on `<linux/ioctl.h>` and `<linux/types.h>`. It integrates with legacy I2O controllers, storage/network class drivers, DPT/Adaptec firmware update tools, and kernel compat ioctl paths.

## Risks and test signals
Risks include obsolete hardware assumptions, raw passthrough privilege hazards, 32-bit pointer compatibility, bitfield layout sensitivity, firmware update failures, bounded event loss, and table-size trust issues. Test signals include ioctl size/compat tests, HRT/LCT dump validation, event queue overflow tests, parameter set/get round trips, safe passthrough rejection, and flash fragment boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i2o-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i8k.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/i8k.h

## Purpose
`i8k.h` defines the userspace ABI for the Dell laptop SMM BIOS access driver historically exposed through `/proc/i8k` and ioctl commands.

## Important APIs, types, and functions
Constants include `I8K_PROC`, `I8K_PROC_FMT`, ioctls `I8K_BIOS_VERSION`, `I8K_MACHINE_ID`, `I8K_POWER_STATUS`, `I8K_FN_STATUS`, `I8K_GET_TEMP`, `I8K_GET_SPEED`, `I8K_GET_FAN`, and `I8K_SET_FAN`, fan IDs (`I8K_FAN_LEFT`, `I8K_FAN_RIGHT`), fan levels (`OFF`, `LOW`, `HIGH`, `TURBO`, `AUTO`, `MAX`), volume/Fn status bits, and AC/battery values.

## Control flow
User tools query BIOS and machine identity, read power/Fn/temp/fan state, and optionally set fan speed by issuing ioctls or reading the proc file. The kernel driver translates these calls into SMM BIOS operations.

## State and persistence behavior
Temperature, fan RPM, power, and Fn status are sampled live state. Fan mode changes persist in firmware/platform control until changed by the driver, BIOS, or thermal policy.

## Dependencies and integration points
It integrates with Dell SMM BIOS calls, the i8k driver, procfs compatibility, hwmon/thermal userspace, and fan-control tools.

## Risks and test signals
Risks include broken ioctl sizes noted in comments, machine-specific SMM behavior, unsafe manual fan control, treating `TURBO` and `AUTO` as distinct on all machines, and non-Dell platform probing. Test signals include supported-model detection, read-only telemetry checks, fan set/get round trips under thermal guardrails, proc output format validation, and invalid fan/value rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/i8k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/icmp.h

## Purpose
`icmp.h` defines the IPv4 ICMP wire-format constants and structures used by raw sockets, packet parsers, and kernel networking code.

## Important APIs, types, and functions
Constants define ICMP message types such as echo reply/request, destination unreachable, source quench, redirect, time exceeded, parameter problem, timestamp, info request/reply, address mask, and extended echo. Code constants cover unreachable reasons, redirect variants, time-exceeded reasons, extended echo reply codes/flags, c-types, and address family identifiers. `struct icmphdr` defines type, code, checksum, and a union for echo ID/sequence, gateway, fragment MTU, or reserved bytes. `ICMP_FILTER` and `struct icmp_filter` define the raw-socket filter option. RFC 4884 and RFC 8335 extension layouts include `struct icmp_ext_hdr`, `struct icmp_extobj_hdr`, `struct icmp_ext_echo_ctype3_hdr`, and `struct icmp_ext_echo_iio`.

## Control flow
ICMP packets are parsed by inspecting type and code, validating checksum, and interpreting the union based on type. Raw-socket users can install an ICMP type filter. Extended echo and RFC 4884 messages append extension headers and objects after the base ICMP payload.

## State and persistence behavior
ICMP state is packet-local, except that applications may correlate echo ID/sequence or extended echo identifiers. The header stores no state.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with IPv4 raw sockets, ping, traceroute, network diagnostics, firewall/NAT code, and packet analyzers.

## Risks and test signals
Risks include wrong union member for type, byte-order mistakes, accepting invalid type/code pairs, ICMP filter bit mistakes, extension object length errors, extended echo compatibility, and unchecked MTU or gateway fields. Test signals include ping/traceroute tests, checksum validation, unreachable/code parsing, socket filter behavior, extended echo cases, raw-socket send/receive, and packet-fuzzer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmpv6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/icmpv6.h

## Purpose
`icmpv6.h` defines ICMPv6 wire-format constants, the base ICMPv6 header, raw-socket filters, and multicast listener constants used by IPv6 networking.

## Important APIs, types, and functions
`struct icmp6hdr` contains type, code, checksum, and unions for identifier/sequence, MTU/pointer/unused words, neighbor advertisement flags, and router advertisement fields. Constants cover router preference values, destination unreachable, packet-too-big, time exceeded, parameter problem, echo, multicast listener discovery, node information, MLDv2 reports, mobile IPv6 discovery, multicast router discovery, and extended echo. Macros map union members to names such as `icmp6_identifier`, `icmp6_sequence`, `icmp6_mtu`, `icmp6_router_pref`, and ND flags. `ICMPV6_FILTER` and `struct icmp6_filter` define raw-socket filtering; MLDv2 record type constants and `MLD2_ALL_MCR_INIT` support multicast listener reports.

## Control flow
IPv6 receivers parse the common header, dispatch by type/code, and interpret the union for echo, errors, neighbor discovery, router advertisement, MLD, and extended echo. Raw ICMPv6 sockets can set filters over the 256 possible message types.

## State and persistence behavior
ICMPv6 packets are transient, but ND/RA/MLD messages update neighbor cache, router state, multicast membership, and MTU state in the IPv6 stack. Socket filters are per-socket state.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<asm/byteorder.h>`. It integrates with IPv6, Neighbor Discovery, multicast listener discovery, router advertisement daemons, ping6, traceroute6, and firewalling.

## Risks and test signals
Risks include invalid type/code acceptance, endian mistakes in flags and MTU, router preference bit misuse, ICMPv6 filter mask errors, and incompatible handling of newer message types. Test signals include IPv6 ping/traceroute, ND conformance tests, RA/MLD daemon tests, packet-too-big PMTU behavior, raw-socket filter tests, MLDv2 report parsing, and raw-socket checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmpv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/idxd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/idxd.h

## Purpose
`idxd.h` defines the userspace descriptor and completion ABI for Intel Data Streaming Accelerator and In-Memory Analytics Accelerator devices exposed through the idxd driver.

## Important APIs, types, and functions
The header defines software command status codes in `enum idxd_scmd_stat`, descriptor flags `IDXD_OP_FLAG_*`, DSA opcodes in `enum dsa_opcode`, IAX opcodes in `enum iax_opcode`, completion status enums for DSA and IAX, status mask helpers, and packed descriptor/completion structures. `struct dsa_hw_desc` encodes PASID/privilege, flags, opcode, completion address, source/destination/pattern/list/translation operands, transfer size or descriptor count, interrupt handle, and operation-specific fields for compare, delta, CRC, DIF/DIX, fill, and translation fetch. `struct iax_hw_desc` encodes compression/analytics operands. Raw descriptor and completion record wrappers expose fixed 64-bit field arrays.

## Control flow
User space configures a work queue through sysfs/driver control, maps or opens a portal, writes a DSA or IAX descriptor, waits for completion record status to change, then decodes result, bytes completed, fault address, invalid flags, CRC/DIF/analytics fields, or page-fault status.

## State and persistence behavior
Descriptor and completion records are shared memory ABI. Completion status is written by hardware and marked volatile. Work queue configuration, PASID, interrupt handle, and device/workqueue enablement are persistent driver/device state outside this header.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with idxd character devices, sysfs workqueue setup, IOMMU/SVA/PASID, DSA/IAX hardware portals, DMA memory, and accelerator libraries.

## Risks and test signals
Risks include packed bitfield layout portability, missing memory barriers around volatile completion status, invalid PASID or privilege, page fault handling, descriptor alignment, overlapping buffers, unsupported opcodes/flags, and IOMMU-disabled user queues. Test signals include DSA/IAX user tests, opcode success/error coverage, page-fault injection, invalid flag reporting, workqueue enable failure codes, completion polling barriers, and descriptor size/static assert checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/idxd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if.h

## Purpose
`if.h` defines core Linux network-interface UAPI constants, names, flags, maps, request structures, and interface setting containers used by sockets, ioctl paths, rtnetlink-adjacent code, and network tools.

## Important APIs, types, and functions
The header defines `IFNAMSIZ`, `IFALIASZ`, `ALTIFNAMSIZ`, interface flag values such as `IFF_UP`, `IFF_BROADCAST`, `IFF_DEBUG`, `IFF_LOOPBACK`, `IFF_POINTOPOINT`, `IFF_NOARP`, `IFF_PROMISC`, `IFF_ALLMULTI`, `IFF_MULTICAST`, `IFF_LOWER_UP`, `IFF_DORMANT`, and `IFF_ECHO`, plus `IFF_VOLATILE`. It defines HDLC interface/protocol selectors (`IF_IFACE_*`, `IF_PROTO_*`), RFC 2863 operational states, link modes, `struct ifmap`, `struct if_settings`, and `struct ifreq`/`ifconf` style ioctl carriers with unions for addresses, flags, MTU, metric, map, data, slave/newname, and settings.

## Control flow
User space passes `ifreq` objects to socket ioctls to query or set interface attributes. The kernel dispatches by ioctl number and interprets the matching union member. Operational state is exposed through netdevice/rtnetlink/sysfs flows.

## State and persistence behavior
Interface flags, MTU, addresses, hardware map, master/slave naming, queue state, and operational state are live netdevice state. Some values persist through configuration managers until device teardown.

## Dependencies and integration points
It depends on libc coordination macros and socket address types through included kernel headers. It is central to net-tools, iproute2 compatibility, drivers, rtnetlink, sysfs, and protocol-specific interface headers.

## Risks and test signals
Risks include union member misuse, interface-name truncation, flag mask drift, ioctl/rtnetlink disagreement, and 32/64-bit pointer compatibility for `ifr_data`. Test signals include SIOCGIF* ioctl tests, name-length boundary tests, flag toggling, MTU and address round trips, compat ioctl checks, and cross-validation with rtnetlink dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_addr.h

## Purpose
`if_addr.h` defines rtnetlink address message and attribute constants for IPv4/IPv6 interface address configuration and dumps.

## Important APIs, types, and functions
`struct ifaddrmsg` contains address family, prefix length, flags, scope, and interface index. Address flags include `IFA_F_SECONDARY`, `IFA_F_TEMPORARY`, `IFA_F_NODAD`, `IFA_F_OPTIMISTIC`, `IFA_F_DADFAILED`, `IFA_F_HOMEADDRESS`, `IFA_F_DEPRECATED`, `IFA_F_TENTATIVE`, `IFA_F_PERMANENT`, `IFA_F_MANAGETEMPADDR`, `IFA_F_NOPREFIXROUTE`, `IFA_F_MCAUTOJOIN`, and `IFA_F_STABLE_PRIVACY`. Attribute enums include `IFA_ADDRESS`, `IFA_LOCAL`, `IFA_LABEL`, `IFA_BROADCAST`, `IFA_ANYCAST`, `IFA_CACHEINFO`, `IFA_MULTICAST`, `IFA_FLAGS`, `IFA_RT_PRIORITY`, `IFA_TARGET_NETNSID`, and `IFA_PROTO`. `struct ifa_cacheinfo` carries preferred/valid lifetimes, creation time, and update time. Compatibility macros `IFA_RTA()` and `IFA_PAYLOAD()` are exposed outside the kernel, and `IFAPROT_*` values identify kernel-originated address protocols.

## Control flow
Address add/delete/get rtnetlink messages carry `ifaddrmsg` plus attributes. The kernel validates family/prefix/interface and updates address lists; dumps return current addresses and lifetimes.

## State and persistence behavior
Address entries, labels, flags, lifetimes, route priorities, and namespace target references are live network-namespace state. Cacheinfo lifetimes age with time and can drive deprecation/removal.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with rtnetlink, IPv4/IPv6 address management, DAD, privacy addressing, prefix route creation, and iproute2.

## Risks and test signals
Risks include incorrect flag width when `IFA_FLAGS` is absent, lifetime overflow, missing DAD state transitions, label truncation, and namespace-ID confusion. Test signals include `ip addr` add/delete/dump, temporary/deprecated/tentative address tests, lifetime expiry, prefix-route behavior, and strict netlink policy validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addrlabel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_addrlabel.h

## Purpose
`if_addrlabel.h` defines rtnetlink attributes for IPv6 address label policy management used by source/destination address selection.

## Important APIs, types, and functions
`struct ifaddrlblmsg` carries address family, reserved byte, prefix length, flags, interface index, and sequence number. The attribute enum defines `IFAL_ADDRESS` and `IFAL_LABEL`, bounded by `IFAL_MAX`. Message command transport is handled by rtnetlink address-label operations.

## Control flow
User space sends address-label add/delete/list requests with prefix address and numeric label. The kernel updates or dumps the per-network-namespace address label table used by IPv6 address selection.

## State and persistence behavior
Address label rules are live namespace configuration. They persist until deleted or namespace teardown; policy managers may reload them from configuration.

## Dependencies and integration points
It integrates with IPv6 RFC 6724 source address selection, rtnetlink, and tools such as `ip addrlabel`.

## Risks and test signals
Risks include overlapping prefix ambiguity, wrong label values changing source selection, missing namespace isolation, and netlink attribute-policy drift. Test signals include `ip addrlabel` add/delete/list, source-address selection tests, namespace isolation tests, duplicate prefix handling, and invalid attribute rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_addrlabel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_alg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_alg.h

## Purpose
`if_alg.h` defines the AF_ALG userspace socket ABI for accessing kernel crypto algorithms.

## Important APIs, types, and functions
`struct sockaddr_alg` selects algorithm type, feature/mask values, and the legacy 64-byte algorithm name field. `struct sockaddr_alg_new` keeps the same prefix but exposes a flexible algorithm name for long names. `struct af_alg_iv` carries IV length and flexible IV bytes. Socket operation constants include `ALG_SET_KEY`, `ALG_SET_IV`, `ALG_SET_OP`, `ALG_SET_AEAD_ASSOCLEN`, `ALG_SET_AEAD_AUTHSIZE`, `ALG_SET_DRBG_ENTROPY`, and `ALG_SET_KEY_BY_KEY_SERIAL`. Operation values include `ALG_OP_DECRYPT` and `ALG_OP_ENCRYPT`.

## Control flow
User space creates an `AF_ALG` socket, binds it to an algorithm type/name, sets key material or a key-serial reference and per-operation controls, accepts an operation socket, then sends data and receives transformed output. AEAD and skcipher operations use control messages for IV, operation direction, associated data length, and auth tag size; DRBG users can provide entropy through the dedicated option.

## State and persistence behavior
The parent socket stores algorithm and key state. Accepted operation sockets carry per-request IV, direction, associated-data length, and buffered data until completion or close.

## Dependencies and integration points
It depends on UAPI socket types and integrates with the kernel crypto API, skcipher, hash, RNG, AEAD, kTLS/userspace crypto tooling, and test suites.

## Risks and test signals
Risks include leaking key material, missing auth tag size, incorrect associated-data length, IV reuse, partial send/recv handling, long algorithm-name compatibility, invalid key serials, and unsupported algorithm names. Test signals include `algif_*` selftests, known-answer crypto vectors, AEAD failure tests, zero-length messages, splice/sendmsg paths, DRBG entropy tests, and key/IV length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_alg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arcnet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_arcnet.h

## Purpose
`if_arcnet.h` defines ARCnet packet header formats, protocol IDs, and constants used by ARCnet network drivers and packet tools.

## Important APIs, types, and functions
The header defines ARCnet address/header lengths, MTU-related constants, protocol IDs for IP, ARP, RARP, Ethernet-encapsulated, diagnostics, and RFC1201/RFC1051 variants, plus structs for ARCnet hard headers, RFC1201 soft headers, RFC1051 headers, Ethernet-encapsulation headers, and cap-mode framing.

## Control flow
Drivers prepend ARCnet hard headers and protocol-specific soft headers, fragment/reassemble payloads according to ARCnet framing rules, and dispatch based on protocol ID. User space sees these layouts through packet sockets and captures.

## State and persistence behavior
Header fields are packet-local. Driver state such as node ID, fragmentation queues, and protocol mode lives in ARCnet netdevices.

## Dependencies and integration points
It depends on fixed-width UAPI types and integrates with legacy ARCnet drivers, packet sockets, ARP/IP support over ARCnet, and diagnostic tooling.

## Risks and test signals
Risks include incorrect fragmentation flags, soft-header variant confusion, MTU mismatch, legacy protocol ID handling, and struct packing assumptions. Test signals include ARCnet packet capture decoding, ARP/IP round trips, fragmentation/reassembly tests, unsupported protocol rejection, and header-size compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arcnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_arp.h

## Purpose
`if_arp.h` defines ARP hardware type constants, ARP operation codes, flags, and request structures used by neighbor/ARP ioctls and packet parsers.

## Important APIs, types, and functions
It exports many `ARPHRD_*` link-layer identifiers, including Ethernet, loopback, tunnel, IEEE 802 variants, CAN, Infiniband, Phonet, MCTP, and special `ARPHRD_NONE`/`VOID`. Operation codes include `ARPOP_REQUEST`, `REPLY`, `RREQUEST`, `RREPLY`, `InREQUEST`, `InREPLY`, and `NAK`. `struct arphdr` defines wire ARP header fields. `struct arpreq` and `struct arpreq_old` carry ioctl requests for protocol address, hardware address, flags, netmask, and device name. Flags include `ATF_COM`, `ATF_PERM`, `ATF_PUBL`, `ATF_USETRAILERS`, `ATF_NETMASK`, and `ATF_DONTPUB`.

## Control flow
ARP packets use `arphdr` followed by variable address fields. User space manages ARP cache entries through socket ioctls using `arpreq`; the kernel resolves, inserts, updates, deletes, or exposes entries based on flags.

## State and persistence behavior
Neighbor table entries, permanent/public flags, netmask proxy entries, and device-scoped ARP state are live network-namespace state. Wire headers are transient packets.

## Dependencies and integration points
It depends on `<linux/netdevice.h>`-compatible sizes and socket address types. It integrates with Ethernet/IP ARP, neighbor tables, netdevice hardware types, packet sockets, and legacy net-tools.

## Risks and test signals
Risks include hardware-type mismatches, ioctl struct compatibility, proxy ARP netmask misuse, stale permanent entries, and new link types requiring stable IDs. Test signals include ARP request/reply captures, `arp`/`ip neigh` interoperability, add/delete/proxy entries, namespace isolation, and packet parser tests for hardware lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bonding.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_bonding.h

## Purpose
`if_bonding.h` defines userspace constants and structures for Linux bonding driver modes, link states, MII monitor results, LACP state, and legacy bonding ioctls.

## Important APIs, types, and functions
The header exports `BOND_ABI_VERSION`, old private ioctl numbers for enslave/release/sethwaddr/info/change-active, `BOND_CHECK_MII_STATUS`, bond modes such as round-robin, active-backup, XOR, broadcast, 802.3ad, TLB, and ALB, link and slave states, default max bonds/tx queues/resend IGMP values, transmit hash policy constants, and LACP state bits. Structures include `ifbond` for aggregate mode/miimon/slave count, `ifslave` for slave id/name/link/state/failure count, and `struct ad_info` for 802.3ad aggregator details. Xstats enums expose bond and 802.3ad statistic attributes.

## Control flow
User space creates/configures a bond, enslaves or releases lower devices, queries bond/slave state, and sets hardware address through legacy ioctls or newer netlink/sysfs paths. The bonding driver then applies mode-specific transmit selection, failover control, and optional 802.3ad aggregation.

## State and persistence behavior
Bond mode, hash policy, slave list, LACP state, link monitoring, active slave, 802.3ad aggregator information, xstats, and failure counters are live bond-device state and often persisted by network configuration tools.

## Dependencies and integration points
It integrates with netdevice ioctls, rtnetlink bonding attributes, sysfs bonding controls, switch LACP peers, and network managers.

## Risks and test signals
Risks include legacy ioctl/netlink divergence, invalid mode/slave combinations, MAC address changes during enslave/release, LACP state mismatch, xstats schema drift, and failover races. Test signals include bond mode creation, enslave/release cycles, link-down failover, LACP partner tests, hash policy packet distribution, ioctl query compatibility, 802.3ad xstats dumps, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bonding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bridge.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_bridge.h

## Purpose
`if_bridge.h` defines the Linux bridge userspace ABI: legacy bridge ioctl constants, sysfs names, STP state structures, bridge netlink attributes for VLANs, MRP, CFM, MST, multicast database management, xstats, boolean options, and multicast querier state.

## Important APIs, types, and functions
Legacy pieces include `BRCTL_*`, bridge state constants, `struct __bridge_info`, `__port_info`, and `__fdb_entry`. Netlink definitions include `IFLA_BRIDGE_*`, `struct bridge_vlan_info`, VLAN tunnel and xstats attrs, extensive MRP attrs and structs (`br_mrp_instance`, `br_mrp_ring_state`, `br_mrp_ring_role`, `br_mrp_start_test`, `br_mrp_in_state`, `br_mrp_in_role`, `br_mrp_start_in_test`), CFM attrs, MST attrs, `struct bridge_stp_xstats`, VLAN database message/attrs, MDB/router attrs, `struct br_port_msg`, `struct br_mdb_entry`, MDB set/get/source attrs, `struct br_mcast_stats`, `enum br_boolopt_id`, `struct br_boolopt_multi`, and querier attrs.

## Control flow
User space configures bridges and ports through rtnetlink attributes under `IFLA_AF_SPEC`, manages VLAN and tunnel entries through VLAN database messages, controls MRP/CFM/MST features with nested attributes, manipulates MDB entries, and reads FDB/MDB/VLAN/STP/multicast stats. Legacy brctl ioctls provide older bridge and port management paths.

## State and persistence behavior
Bridge state includes STP timers and port states, FDB entries, VLAN membership and per-VLAN options, multicast snooping/querier/MDB/router state, MRP ring/interconnect roles, CFM maintenance points, MST states, boolean options, and per-VLAN/multicast/STP counters. These are live netdevice state until changed or removed.

## Dependencies and integration points
It depends on `<linux/types.h>`, `<linux/if_ether.h>`, and `<linux/in6.h>`. It integrates with rtnetlink, bridge driver, switchdev/offload drivers, iproute2 `bridge`, sysfs bridge files, multicast snooping, MRP/CFM protocols, and xstats.

## Risks and test signals
Risks include nested attribute policy drift, range VLAN semantics errors, offload failure notification handling, stale legacy ioctl behavior, CFM/MRP role mismatch, MDB source-list ambiguity, and boolean option updates missing sysfs handlers. Test signals include bridge/VLAN/MDB iproute2 tests, switchdev offload tests, multicast snooping/querier cases, STP transition counters, MRP ring failover, CFM peer status, MST state dumps, and strict netlink validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_eql.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_eql.h

## Purpose
`if_eql.h` defines the ioctl ABI for the legacy equalizer load-balancer for serial network interfaces.

## Important APIs, types, and functions
Defaults include `EQL_DEFAULT_SLAVE_PRIORITY`, `EQL_DEFAULT_MAX_SLAVES`, `EQL_DEFAULT_MTU`, and `EQL_DEFAULT_RESCHED_IVAL`. Private ioctls include `EQL_ENSLAVE`, `EQL_EMANCIPATE`, `EQL_GETSLAVECFG`, `EQL_SETSLAVECFG`, `EQL_GETMASTRCFG`, and `EQL_SETMASTRCFG`. Structures are `master_config`, `slave_config`, and `slaving_request`, carrying max slaves, min/max/slave priority, and slave/master names.

## Control flow
User space configures an eql master interface, enslaves serial interfaces, adjusts master/slave priority parameters, and removes slaves through private netdevice ioctls. The driver schedules traffic across slaves according to priority and reschedule interval.

## State and persistence behavior
Master configuration, slave list, slave priorities, and MTU are live netdevice state. They persist only while the eql device exists unless restored by external configuration.

## Dependencies and integration points
It relies on private `SIOCDEVPRIVATE` ioctl numbering and integrates with netdevice ioctl paths and legacy serial/PPP-style network interfaces.

## Risks and test signals
Risks include obsolete driver coverage, private ioctl conflicts, name truncation, invalid priority ranges, and behavior under slave link failure. Test signals include ioctl get/set round trips, enslave/emancipate cycles, packet distribution tests, slave failure handling, and private ioctl compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_eql.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ether.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_ether.h

## Purpose
`if_ether.h` defines Ethernet frame sizes, MTU limits, EtherType/protocol constants, pseudo protocol IDs used by packet sockets, and the Ethernet header layout.

## Important APIs, types, and functions
Constants include `ETH_ALEN`, `ETH_TLEN`, `ETH_HLEN`, `ETH_ZLEN`, `ETH_DATA_LEN`, `ETH_FRAME_LEN`, `ETH_FCS_LEN`, `ETH_MIN_MTU`, `ETH_MAX_MTU`, many `ETH_P_*` protocol identifiers for IP, ARP, VLANs, IPv6, MPLS, PPPoE, LLDP, MACsec, FCoE, HSR, MCTP, DSA tags, and internal pseudo types, plus `ETH_P_802_3_MIN`. `struct ethhdr` contains destination/source MAC addresses and big-endian protocol field, guarded by `__UAPI_DEF_ETHHDR`.

## Control flow
Network drivers and packet sockets classify Ethernet frames by the protocol field when it is at least `ETH_P_802_3_MIN`, or by 802.3/LLC logic for length-coded frames. User space uses the constants for socket protocol selection and packet decoding.

## State and persistence behavior
The header defines packet-local frame layout and stable numeric protocol IDs. Interface MTU/MAC state is managed elsewhere.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with almost all Ethernet netdevices, AF_PACKET, bridge/VLAN/DSA/tunnel code, BPF programs, and packet analyzers.

## Risks and test signals
Risks include using host byte order for EtherTypes, frame-size off-by-FCS errors, non-official protocol collisions, DSA tag confusion, and libc header guard conflicts. Test signals include packet socket bind tests, Ethernet header parsing, VLAN/MPLS/IPv6 captures, MTU validation, BPF protocol matching, and compile tests with glibc/musl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_fc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_fc.h

## Purpose
`if_fc.h` defines Linux UAPI constants and simplified headers for Fibre Channel network encapsulation.

## Important APIs, types, and functions
It exports `FC_ALEN`, `FC_HLEN`, `FC_ID_LEN`, LLC/SNAP constants `EXTENDED_SAP` and `UI_CMD`, `struct fch_hdr` for destination/source FC addresses, and `struct fcllc` for LLC/SNAP fields.

## Control flow
Drivers construct Fibre Channel frame headers internally, while this header describes the Linux-visible header pieces used for networking over FC-style links. Packet consumers interpret the address and LLC/SNAP portions.

## State and persistence behavior
Header fields are packet-local. FC port identity, link state, and topology are managed by lower-level drivers and not stored here.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with legacy FC network drivers, LLC/SNAP encapsulation handling, and packet capture tools.

## Risks and test signals
Risks include assuming this is the full hardware FC frame header, address length mismatches, and LLC/SNAP decoding errors. Test signals include header-size compile checks, packet capture decoding, FC network interface send/receive, and protocol classification tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_fddi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_fddi.h

## Purpose
`if_fddi.h` defines constants and header layouts for ANSI FDDI network interfaces, including frame sizing, frame-control values, LLC/SNAP headers, and a combined FDDI header.

## Important APIs, types, and functions
Constants include FDDI address length, 802.2 and SNAP header lengths, min/max payload lengths, OUI length, frame-control class/address/format/control masks, frame-control values for tokens, SMT, MAC, LLC, implementor, and reserved ranges, plus LLC/SNAP values. Structures include `fddi_8022_1_hdr`, `fddi_8022_2_hdr`, `fddi_snap_hdr`, and `struct fddihdr` containing frame control, destination/source addresses, and a union of LLC header variants.

## Control flow
Drivers and packet tools inspect the frame-control byte to classify FDDI frames and then interpret the matching LLC/SNAP header. Payload length and MTU checks use the exported size constants.

## State and persistence behavior
FDDI header contents are packet-local. Ring state and station management are driver/device state outside this header.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with legacy FDDI netdevices, LLC/SNAP protocol handling, ARP/IP over FDDI, and packet capture decoders.

## Risks and test signals
Risks include frame-control mask mistakes, SNAP versus 802.2 header confusion, payload length boundary errors, and rare-driver bitrot. Test signals include header-size checks, packet decode vectors, MTU validation, LLC/SNAP classification, and legacy driver send/receive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_fddi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_hippi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_hippi.h

## Purpose
`if_hippi.h` defines HIPPI network-interface constants, statistics, and packet header layouts for Linux HIPPI devices.

## Important APIs, types, and functions
Constants include `HIPPI_ALEN`, `HIPPI_HLEN`, `HIPPI_ZLEN`, `HIPPI_DATA_LEN`, `HIPPI_FRAME_LEN`, LLC/SNAP values, and `HIPPI_OUI_LEN`. `struct hipnet_statistics` exposes receive/transmit packet, byte, error, dropped, multicast, and detailed error counters. Header structs include `hippi_fp_hdr`, `hippi_le_hdr`, `hippi_snap_hdr`, and combined `struct hippi_hdr`.

## Control flow
Drivers build HIPPI FP, LE, and SNAP headers around network payloads and update statistics as packets are sent, received, or dropped. Packet parsers decode the combined header to identify payload protocol.

## State and persistence behavior
Headers are packet-local. `hipnet_statistics` is live per-device counter state. Link, address, and error state are maintained by HIPPI drivers.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<asm/byteorder.h>`. It integrates with legacy HIPPI netdevices, socket/pkt capture paths, and RFC 2067 IP-over-HIPPI handling.

## Risks and test signals
Risks include bitfield/endian layout assumptions, RFC 2067 DSAP/SSAP swap compatibility, large MTU handling, and low test coverage for obsolete hardware. Test signals include header encode/decode checks, stats counter updates, MTU boundary tests, packet capture vectors, and driver loopback tests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_hippi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_infiniband.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_infiniband.h

## Purpose
`if_infiniband.h` defines the Linux UAPI hardware address length for IP over InfiniBand interfaces.

## Important APIs, types, and functions
The single exported constant is `INFINIBAND_ALEN`, set to 20 octets for IPoIB hardware addresses.

## Control flow
There is no control flow. Network code and userspace tools use the constant when sizing link-layer address buffers for ARPHRD_INFINIBAND/IPoIB devices.

## State and persistence behavior
The header carries no state. IPoIB hardware addresses are per-interface/per-neighbor live network state managed by the InfiniBand and netdevice stacks.

## Dependencies and integration points
It integrates with IPoIB netdevices, ARP/neighbor tables, rtnetlink address dumps, packet sockets, and tools displaying link-layer addresses.

## Risks and test signals
Risks include assuming Ethernet-length addresses for IPoIB, truncating rtnetlink or neighbor addresses, and inconsistent libc/kernel header use. Test signals include IPoIB link dumps, neighbor entry formatting, address buffer size tests, and packet socket sockaddr_ll handling for 20-byte addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_infiniband.h -->
