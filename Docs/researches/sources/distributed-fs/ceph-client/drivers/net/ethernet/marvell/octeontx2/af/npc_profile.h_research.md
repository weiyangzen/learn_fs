# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/npc_profile.h

## Purpose

`npc_profile.h` is the built-in default NPC parser and MCAM key-extraction profile for the Marvell OcteonTX2/CN9K/CN10K RVU Admin Function driver. It is not normal executable logic; it is a large static hardware-profile data set that the AF driver copies into NPC KPU, PKIND, and MCAM KEX CSRs during NPC initialization.

The profile defines:

- protocol constants for Ethernet, VLAN, PPP, IP, IPv6 extension headers, TCP/UDP ports, GRE, VXLAN/VXLAN-GPE, Geneve, GTP, MPLS, NSH, DSA, and parser validation masks;
- parser states, layer flags, error codes, and error levels used by the NPC KPU state machine;
- initial PKIND actions in `ikpu_action_entries`;
- 16 per-KPU CAM tables, `kpu1_cam_entries` through `kpu16_cam_entries`;
- 16 matching per-KPU action tables, `kpu1_action_entries` through `kpu16_action_entries`;
- the `npc_kpu_profiles` table that binds each CAM/action pair into a loadable KPU profile array;
- `npc_lt_defaults`, the default LID/LTYPE contract used by flow steering, NIX offloads, RSS/flow tag logic, VLAN insertion/stripping, packet color, and ethertype helpers;
- `npc_mkex_default`, the default MCAM key extraction layout for RX and TX.

## Important APIs, Types, And Data

This header depends on type definitions from `npc.h`, notably:

- `struct npc_kpu_profile_cam`: one KPU CAM match row containing parser state plus three 16-bit data/mask pairs.
- `struct npc_kpu_profile_action`: the action paired with a CAM row, including error level/code, data-pointer offsets, next state, parse-done bit, LID/LTYPE capture, flags, pointer advance, and variable-length pointer arithmetic fields.
- `struct npc_kpu_profile`: array wrapper containing CAM count, action count, and pointers.
- `struct npc_mcam_kex`: MCAM key extraction profile containing `keyx_cfg`, per-LDATA flag extraction, and per-interface/per-LID/per-LTYPE/per-LD extraction rules.
- `struct npc_lt_def_cfg`: named defaults for common outer/inner L2/L3/L4 and IPsec protocol locations.

The header's central exported data objects are declared `static` and `__maybe_unused`, because inclusion into `rvu_npc.c` makes them translation-unit-local defaults:

- `NPC_KPU_PROFILE_VER` is `1.7.0` encoded as `0x0000000100070000`; loader code compares major/minor compatibility for custom profiles against this version.
- `NPC_KPU_NOP_CAM` and `NPC_KPU_NOP_ACTION` fill unused early slots. Built-in profiles reserve the first `KPU_MAX_CST_ENT` entries for possible custom entries; `npc_program_kpu_profile()` disables them unless a custom profile is active.
- `ikpu_action_entries` configures PKIND startup actions for packet origins such as default RX/TX, loopback, CPT header, custom pre-L2, HiGig, EDSA, and VLAN/DSA variants.
- `kpu*_cam_entries` and `kpu*_action_entries` form the parser state transition table.
- `npc_kpu_profiles` lists all 16 KPU stages in hardware programming order.
- `npc_lt_defaults` maps common offload concepts to LID/LTYPE/mask triplets, for example outer IPv4 at LC/IP, inner IPv4 at LG/TU_IP, outer TCP at LD/TCP, inner TCP at LH/TU_TCP, and IPsec ESP SPI offsets.
- `npc_mkex_default` names the default MKEX profile, carries `MKEX_SIGN`, references `NPC_KPU_PROFILE_VER`, enables RX and TX parse nibbles, and programs selected byte ranges into MCAM key words.

The header also includes CN20K-related parser flag enumerants, but the non-CN20K runtime path uses this file's `npc_mkex_default` directly; CN20K code adapts or replaces several action entries and uses CN20K-specific MKEX extraction structures.

## Parser Control Flow

The KPU pipeline is a table-driven state machine. The first stage receives a parser state from the PKIND action table, then each KPU stage compares the current state and extracted packet data against its CAM rows. The selected row's action can capture a layer, set a layer type and flags, advance the parser pointer, compute variable length skips, raise parse errors, transition to a next state, or mark parsing complete.

At a high level, the stages are arranged as follows:

- KPU1 begins L2 parsing from Ethernet, NIX-injected TX headers, CPT headers, HiGig2, ExDSA, and custom pre-L2 states.
- KPU2-KPU4 handle VLAN tag stacks, QinQ, ETAG/ITAG/BTAG, DSA/EDSA/EXDSA/FDSA, PPPoE, MPLS, and NSH before L3.
- KPU5 recognizes outer IPv4, IPv6, ARP/RARP, PTP, FCoE, MPLS payloads, NSH, NGIO, and CPT variants.
- KPU6-KPU7 walk outer IPv6 extension headers and route/fragment/hop/destination variants.
- KPU8 recognizes outer transport or tunnel protocols such as TCP, UDP, SCTP, ICMP/ICMPv6, IGMP, GRE, AH, ESP, and custom protocols.
- KPU9-KPU11 parse tunnel encapsulations and tunnel L2/MPLS/NSH forms such as VXLAN, VXLAN-GPE, Geneve, GTP, GRE/MPLS, NSH, PPP, and tunnel Ethernet.
- KPU12-KPU14 parse inner L3 and inner IPv6 extension headers.
- KPU15 parses inner transport and IPsec/AH/ESP.
- KPU16 captures final inner L4/application distinctions such as HTTP, HTTPS, PPTP, generic TCP data, UDP data, and PTP-over-UDP.

The CAM tables are protocol recognizers: for example KPU1 checks ethertypes for IPv4, IPv6, ARP, RARP, PTP, FCoE, VLAN, MPLS, NSH, PPPoE, and DSA-related forms. KPU5 validates IPv4 version/header length/fragment/TLL and next-header fields. Later stages check MPLS bottom-of-stack, tunnel ports, GRE flags and versions, VXLAN/Geneve/GTP validity bits, TCP flags, and UDP/TCP port-specific classifications.

## Runtime Integration

The runtime consumer is `rvu_npc.c`:

- `npc_prepare_default_kpu()` binds `rvu->kpu` to this header's default objects: `ikpu_action_entries`, `npc_kpu_profiles`, `npc_lt_defaults`, `npc_mkex_default`, and `npc_mkex_hash_default`.
- `npc_load_kpu_profile()` starts from the default and optionally overlays a custom firmware profile from the filesystem or firmware database. If loading or validation fails, it reverts to this header.
- `npc_parser_profile_init()` disables all KPUs, calls `npc_load_kpu_profile()`, writes PKIND actions with `npc_config_kpuaction()`, then programs each KPU stage with `npc_program_kpu_profile()`.
- `npc_config_kpucam()` converts `struct npc_kpu_profile_cam` rows into the hardware's positive/negative CAM register pair at `NPC_AF_KPUX_ENTRYX_CAMX`.
- `npc_config_kpuaction()` converts `struct npc_kpu_profile_action` rows into `ACTION0`/`ACTION1` register formats.
- `npc_load_mkex_profile()` either keeps this header's `npc_mkex_default` or replaces it with a selected MKEX profile image, then `npc_program_mkex_profile()` writes the extraction layout into `NPC_AF_INTFX_KEX_CFG`, `NPC_AF_INTFX_LIDX_LTX_LDX_CFG`, `NPC_AF_KEX_LDATAX_FLAGS_CFG`, and related LD flags registers.

Other integration points include:

- `rvu_npc_fs.c`, which uses the active MKEX layout and LID/LTYPE defaults to map high-level flow fields to MCAM key offsets and to validate whether fields like ethertype, VLAN TCI, DMAC, IP addresses, L4 ports, IPsec SPI, MPLS labels, and TCP flags are extractable.
- `rvu_npc_hash.c`, which consults `rvu->kpu.mkex_hash` and active LID/LTYPE mappings for RSS/hash behavior.
- `rvu_nix.c`, which reads `rvu->kpu.lt_def` when configuring NIX features that depend on parser layer classification.
- module parameters `kpu_profile` and `mkex_profile` in `rvu.c`, which select profile names at driver load.

## State And Persistence Behavior

The header itself has no persistent state, allocation, locking, or I/O. Its arrays are static kernel data compiled into the driver. Runtime state is persisted only in the driver instance and hardware registers:

- `rvu->kpu` stores pointers to the active profile data and records whether the active profile is built-in or custom.
- The default built-in profile's first custom-entry slots are disabled when `rvu->kpu.custom` is false.
- Custom KPU profile data may be allocated with `kzalloc()` from firmware contents or mapped with `ioremap_wc()` from firmware database memory. The loader frees or unmaps failed images and falls back to the default.
- Once programmed, parser behavior persists in NPC hardware registers until reinitialization, reset, or reprogramming.

One notable mutation exists on the CN20K path: `npc_prepare_default_kpu()` adjusts the CPT header PKIND action fields in `ikpu_action_entries` and then delegates more CN20K-specific updates. That means these `static` defaults are not purely immutable when compiled into a driver that uses the CN20K path.

## Dependencies

Compile-time dependencies include:

- kernel integer types, `ARRAY_SIZE`, `BIT_ULL`, `GENMASK_ULL`, packed layout macros, and `__maybe_unused`;
- `npc.h` for LID/LTYPE constants, parser data structures, parse nibble definitions, KPU firmware image layout, and MCAM KEX structures;
- `rvu_reg.h` and RVU/NPC register definitions indirectly through the programming code;
- NIX interface constants such as `NIX_INTF_RX` and `NIX_INTF_TX`;
- hardware limits such as `NPC_MAX_INTF`, `NPC_MAX_LID`, `NPC_MAX_LT`, `NPC_MAX_LD`, `NPC_MAX_LFL`, `KPU_MAX_CST_ENT`, `KPU_NAME_LEN`, and `MKEX_NAME_LEN`.

Semantic dependencies are tighter than the C compiler can check:

- LTYPE numeric values in `npc.h` must stay aligned with this profile. Comments in `npc.h` warn that changing early LC IPv4/IPv6 LTYPEs can break length/checksum logic and that changing early LD/LH transport LTYPEs can break RSS/flow tag calculations.
- `npc_lt_defaults` must match what the CAM/action pipeline actually captures, or flow installation and offload code will program keys for the wrong layer.
- `npc_mkex_default` must extract every field that higher-level flow steering promises to support.
- `NPC_KPU_PROFILE_VER` must remain synchronized with any external KPU profile format accepted by `npc_apply_custom_kpu()`.

## Risks

- Table drift is the main risk: CAM and action arrays must have matching entry counts and matching semantics. The runtime logs an error if counts differ, but it still programs the minimum effective entries.
- Numeric parser-state, LID, LTYPE, flag, and error-code values are ABI-like hardware contracts. Renumbering can silently misclassify packets or break RSS, checksum, VLAN, and flow rules.
- The profile is large and generated-looking, so manual edits are error-prone. A single mask, pointer advance, next state, or variable-length expression can affect broad packet classes.
- Built-in custom slots are intentionally disabled unless a custom profile is active. If an expected entry lands in the reserved area, it will not match in the default path.
- The MKEX profile must agree with the KPU profile. If parser captures change but KEX offsets do not, flow steering may accept rules that never match or reject valid rules as unsupported.
- Fallback behavior can hide profile loading failures by reverting to the default; logs are the primary signal.
- CN20K code mutates default action entries, so shared static table assumptions should be reviewed when adding cross-silicon behavior.

## Test Signals

Useful validation signals for changes touching this header or its generated profile include:

- Build coverage for the AF driver, catching initializer/type/count issues in `npc_profile.h` and the register programming paths.
- Boot/load logs containing `Using default mkex profile`, `Using custom profile`, or fallback warnings from `npc_load_kpu_profile()` and `npc_load_mkex_profile()`.
- Absence of `KPU%d: CAM and action entries ... not equal` from `npc_program_kpu_profile()`.
- Flow-rule tests for fields covered by `npc_mkex_default`: DMAC/SMAC, ethertype, VLAN tags, IPv4/IPv6 addresses, TOS, TCP/UDP/SCTP ports, ICMP type/code, TCP flags, IPsec SPI, and MPLS labels.
- Packet parser tests or hardware traffic tests for nested encapsulations: VLAN/QinQ, DSA/EDSA/EXDSA/FDSA, MPLS stacks, NSH, GRE/NVGRE, VXLAN, VXLAN-GPE, Geneve, GTP-C/GTP-U, IP-in-IP, IPv6 extension headers, and inner transport parsing.
- Negative tests for parser errors represented here, such as TTL/hop-limit zero, invalid IP versions, IPv4 fragment offset one, invalid TCP flag combinations, invalid VXLAN/GRE/NVGRE/GTP, and too many MPLS labels.
- RSS/flow-tag tests for TCP/UDP/SCTP and inner tunnel variants, because LD/LH LTYPE values are consumed by hash logic.
- Custom profile loading tests with unsupported major version, too-low minor version, too many KPUs, oversized custom entries, bad `KPU_SIGN`, and bad size/offsets, verifying fallback to the built-in profile.
