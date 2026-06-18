# Group Research: group_1366_openbsd_src_sources_os_bsd_openbsd_src_sbin_ifconfig_brconfig_c_sou_34eefcf0cc6c

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/brconfig.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/brconfig.c

## Purpose
`brconfig.c` is the non-`SMALL` bridge-control companion for OpenBSD `ifconfig`. It implements bridge, TPMR-like bridge status, bridge-member flag changes, VLAN/PVLAN configuration, forwarding-table inspection, VXLAN-style endpoint address handling, and bridge packet-filter rule parsing. The public entry points are declared in `ifconfig.h` and are invoked from `ifconfig.c` command-table rows such as `add`, `del`, `tagged`, `pvlan`, `static`, `endpoint`, `rules`, and `rulefile`.

## Compilation and Integration
The entire file is guarded by `#ifndef SMALL`, so install-media or reduced builds omit these features. It depends on global state from `ifconfig.c`: `sock`, `ifname`, `aflag`, `ifaliases`, and `printb()`. It uses OpenBSD bridge kernel ABI structures and ioctls from `<net/if_bridge.h>`, Ethernet parsing from `<netinet/if_ether.h>`, `getnameinfo()` for endpoint display, and `clock_gettime(CLOCK_MONOTONIC)` for virtual address age output.

## Major Data and Formatting Helpers
- `VID_SEP` is `'@'`, used to encode a VLAN-scoped bridge address as `mac@vid`.
- `IFBAFBITS` and `IFBIFBITS` are `%b`-style bit-name strings passed to `printb()`.
- `PV2ID()` splits a bridge priority/vector ID into priority plus Ethernet address bytes.
- `stpstates`, `stpproto`, and `stproles` convert kernel STP/RSTP numeric fields into user-facing text.

## Bridge Member Flag Operations
Small setters like `setdiscover()`, `unsetdiscover()`, `setlearn()`, `unsetlearn()`, `setlocked()`, `unsetlocked()`, `setstp()`, `setedge()`, `setptp()`, and related auto variants delegate to:
- `bridge_ifsetflag()`: fetches member flags with `SIOCBRDGGIFFLGS`, ORs the requested writable flag after masking `IFBIF_RO_MASK`, and commits with `SIOCBRDGSIFFLGS`.
- `bridge_ifclrflag()`: fetches member flags, clears the requested bits and read-only mask bits, then commits.
- `addlocal()`: adds a local bridge port via `SIOCBRDGADDL`, but first enforces that the member name starts with `vether`.

## Bridge Membership and STP Status
- `bridge_add()`, `bridge_delete()`, `bridge_addspan()`, and `bridge_delspan()` wrap `SIOCBRDGADD`, `SIOCBRDGDEL`, `SIOCBRDGADDS`, and `SIOCBRDGDELS`.
- `bridge_cfg()` reads bridge parameters with `SIOCBRDGGPARAM`, prints priority, timers, hold count, and protocol, then prints designated/root bridge details unless `aflag` suppresses extra detail.
- `bridge_list()` grows an `SIOCBRDGIFS` buffer until large enough, prints each bridge member/span with flags, port number, priority, path cost, PVID/untagged state, protected domains, STP state/role, tagged VLAN map, and bridge rules for the member.
- `is_bridge()` probes `SIOCBRDGRTS`; `ENETDOWN` still counts as bridge-like.
- `is_tpmr()` identifies TPMR devices by `tpmr` prefix.
- `bridge_status()` is the status orchestrator called by `ifconfig.c`. It handles TPMR with only member listing, otherwise prints bridge parameters, PVLANs, members, and address cache unless global display flags suppress aliases.

## Timers, Priorities, and Bridge Parameters
The file validates numeric arguments with `strtonum()` before ioctl submission:
- `bridge_timeout()` -> `SIOCBRDGSTO`
- `bridge_maxage()` -> `SIOCBRDGSMA`
- `bridge_priority()` / `spanpriority` -> `SIOCBRDGSPRI`
- `bridge_fwddelay()` -> `SIOCBRDGSFD`
- `bridge_hellotime()` -> `SIOCBRDGSHT`
- `bridge_maxaddr()` -> `SIOCBRDGSCACHE`
- `bridge_holdcnt()` -> `SIOCBRDGSTXHC`
- `bridge_proto()` validates against `stpproto[]` and writes `SIOCBRDGSPROTO`.
- `bridge_ifprio()`, `bridge_ifcost()`, and `bridge_noifcost()` set per-member priority/path cost.

## VLAN and Private VLAN Handling
- `bridge_pvid()` maps `default`, `none`, `passthrough`/`passthru`, or a numeric VID into `ifbr_pvid` and applies `SIOCBRDGSPVID`.
- `bridge_unpvid()` sets `IFBR_PVID_NONE`.
- `bridge_set_vidmap()` parses `all`, `none`, or comma/range lists, with optional `+`, `-`, or `=` operation prefixes. It fills `ifbrvidmap.ifbrvm_map` and uses `SIOCBRDGSVMAP`.
- `bridge_unset_vidmap()` resets the tagged map to all zero bits.
- `bridge_vidmap()` reads `SIOCBRDGGVMAP` and compresses set VID bits into ranges for display.
- `bridge_pvlan_primary_op()` and `bridge_pvlan_secondary_op()` implement PVLAN primary, isolated, and community add/delete through `SIOCBRDGADDPV` and `SIOCBRDGDELPV`.
- `bridge_pvlans()` iterates PVLAN primary and community mappings with `SIOCBRDGNFINDPV`.

## Forwarding Address Cache and Endpoints
- `bridge_addaddr()` accepts either a plain Ethernet address or `mac@vid`. Plain entries use `ifbareq` and `SIOCBRDGSADDR`; VLAN-scoped entries use `ifbvareq` and `SIOCBRDGSVADDR`.
- `bridge_deladdr()` deletes plain or VLAN-scoped entries via `SIOCBRDGDADDR` or `SIOCBRDGDVADDR`.
- `bridge_addendpoint()` resolves an endpoint host with `getaddrinfo()`, stores the resolved sockaddr in `ifba_dstsa`, and adds a static bridge address.
- `bridge_delendpoint()` removes a static endpoint by Ethernet address.
- `bridge_vaddrs_try()` reads newer virtual address records with `SIOCBRDGVRTS`, prints optional VID, member name, age since last use, flags, and tunnel endpoint.
- `bridge_addrs()` is the older address-table path using `SIOCBRDGRTS`.

## Rule Handling
- `bridge_rules()` grows an `SIOCBRDGGRL` buffer, then prints each `ifbrlreq` via `bridge_showrule()`.
- `bridge_rule()` parses one bridge rule of the shape `block|pass [in|out|in/out] on ifs [src mac] [dst mac] [tag name] [arp|rarp ...]`, fills an `ifbrlreq`, and installs it with `SIOCBRDGARL`.
- `bridge_arprule()` parses ARP/RARP predicates such as request/reply, SHA/THA Ethernet addresses, and SPA/TPA IPv4 addresses.
- `bridge_rulefile()` reads whitespace-tokenized rules from a file, ignores comments and blank lines, limits each rule to `MAXRULEWORDS`, and passes each rule to `bridge_rule()`.
- `bridge_badrule()` prints a normalized parse error including file line number when available.
- `bridge_flushrule()` clears rules for a member with `SIOCBRDGFRL`.

## Error Handling and Risks
The file consistently fails fast with `err()`/`errx()` for invalid user input and ioctl failures that indicate command failure. Display paths tolerate some unsupported ioctls (`ENOTTY`, `ENOENT`, `ENETDOWN`) to keep status output useful across bridge feature versions. Notable risks are ABI coupling to `if_bridge.h`, manual variable-length ioctl buffer growth, and rule parser ambiguity if new bridge-rule grammar is added without preserving current token ordering.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/brconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.c

## Purpose
`ifconfig.c` is OpenBSD `ifconfig`'s main implementation. It parses command-line options, dispatches interface commands through a large command table, reads and writes interface state through network ioctls, prints interface status, and hosts support for address families, media selection, 802.11, bridges, trunks, CARP, pfsync, tunnels, MPLS/PWE3, PPPoE/SPPP, pflow, WireGuard, UMB mobile broadband, link-layer addresses, groups, rdomains, descriptions, and hardware capabilities.

## Global State and Dispatch Model
The file keeps process-wide command state in globals: `ifr`, `ifr6`, `in_addreq`, `in6_addreq`, `ifname`, `flags`, `xflags`, `metric`, `mtu`, `llprio`, `sock`, selected address family `af`, `afp`, and deferred-action flags. The `cmds[]` table maps user tokens to:
- a parameter model: immediate integer, `NEXTARG`, `NEXTARG0`, or `NEXTARG2`;
- a deferred action flag such as media, join, or WireGuard;
- either one-argument or two-argument handler functions.

Bridge functions come from `brconfig.c`; transceiver SFF parsing comes from `sff.c`; shared prototypes are in `ifconfig.h`.

## Main Control Flow
`main()` handles these primary modes:
- no arguments: unveil no filesystem visibility, set `aflag`, and print all interfaces;
- option parsing: `-a`, `-A`, `-g`, `-C`, and `-M lladdr`;
- optional address-family selection (`inet`, `inet6`);
- cloner listing (`-C`);
- group attribute read/write (`-g`);
- special early `create`, because normal `getinfo()` would fail before the interface exists;
- interface probing via `getinfo()`;
- command-table dispatch, including bridge `rule` special handling;
- deferred processing for WireGuard, 802.11 join, and media commands;
- final address deletion/addition via address-family-specific ioctls.

The program uses `unveil()` to restrict filesystem access. Unless `rulefile` is present, it unveils only resolver, hosts, and services files for address/name resolution.

## Address Families
`afs[]` defines `inet` and `inet6` behavior:
- `in_status()`, `in_getaddr()`, and `in_getprefix()` handle IPv4 display and parsing.
- `in6_status()`, `in6_alias()`, `in6_getaddr()`, and `in6_getprefix()` handle IPv6 display, scoped link-local fixups, prefix lengths, lifetimes, and flags.
- `setifaddr()`, `setifdstaddr()`, `setifnetmask()`, `setifprefixlen()`, and `notealias()` stage address changes in global request structs; actual ioctl submission is delayed until flags and prefixes are settled.
- IPv6 defaults unspecified prefix length to `/64`, or `/128` for point-to-point destination addresses.

## Interface Discovery and Printing
- `getsock()` caches a datagram socket by address family.
- `getinfo()` reads flags, extended flags, metric, MTU, rdomain, and link-layer priority; it can create the interface if requested.
- `printif()` walks `getifaddrs()`, supports group-name expansion, exact interface matching for names ending in digits, prefix matching for group-like names, and prints link-layer status before protocol addresses.
- `status()` is the main per-interface status printer. It prints flags, rdomain, metric, MTU, link-layer address, description, index, priority, llprio, keepalive, patch peer, encapsulation, protocol-specific status blocks, media, link status, optional transceiver data, wireless state, address-family status, tunnel state, and bridge status.

## Command Families
Core setters use ioctls directly:
- flags and xflags: `setifflags()`, `setifxflags()`, `addaf()`, `removeaf()`;
- MTU, metric, llprio, priority, rdomain, description, patch pair, random/static lladdr;
- group membership and group CARP demotion;
- interface cloning via `SIOCIFCREATE`, `SIOCIFDESTROY`, and `SIOCIFGCLONERS`;
- `findmac()` finds a physical non-cloned interface by MAC address.

## Media Handling
Media commands are deferred so multiple options can be combined safely:
- `init_current_media()` fetches current media with `SIOCGIFMEDIA`.
- `setmedia()`, `setmediamode()`, `unsetmediamode()`, `setmediaopt()`, `unsetmediaopt()`, and `setmediainst()` validate command ordering and update `media_current`, `mediaopt_set`, and `mediaopt_clear`.
- `process_media_commands()` commits with `SIOCSIFMEDIA`.
- `print_media_word()` renders media in status or command syntax.
- Lookup helpers use `IFM_*_DESCRIPTIONS` tables.

## 802.11 Wireless Support
The file manages SSID/join state, WEP/WPA settings, scanning, and status:
- `get_string()`, `len_string()`, and `print_string()` parse/format ASCII or hex network IDs and keys.
- `setifnwid()` and `setifjoin()` are mutually exclusive; `process_join_commands()` submits deferred `SIOCS80211JOIN`.
- WEP/WPA handlers configure nwkey, WPA protocol sets, AKMs, ciphers, group cipher, and WPA PSK. WPA passphrases are converted with `pkcs5_pbkdf2()`.
- `ieee80211_status()` reads many wireless ioctls and prints nwid/join, channel, BSSID, RSSI, nwkey, WPA settings, power-save, flags, and association failures.
- `join_status()`, `ieee80211_listchans()`, and `ieee80211_listnodes()` display join lists, available channels, and scan results.

## Encapsulation, VLAN, Tunnels, MPLS, and PWE3
Encapsulation state is grouped in `struct ifencap`:
- `getencap()` prints `vnetid`, `parent`, optional flow ID, TX priority, and RX priority.
- `setvnetid()`, `delvnetid()`, `setifparent()`, `delifparent()`, `setvnetflowid()`, and priority setters use the corresponding `SIOC*` ioctls.
- `phys_status()` and tunnel setters manage local/remote physical tunnel addresses, TTL, DF, ECN, and tunnel rdomain.
- MPLS and PWE3 support prints labels, PWE3 neighbor labels, control word, FAT state, and sets/unsets labels/neighbors/options.

## Aggregation and Redundancy Protocols
- Trunk support sets ports, protocol, LACP mode/timeout, and prints aggregate/port LACP state.
- CARP support prints one or many VHIDs and sets password, VHID, advbase, advskew, peer, state, device, node list, and balancing mode.
- pfsync support sets syncdev, syncpeer, max updates, defer flag, and prints active sync settings.
- pflow support parses IPv4/IPv6 sender/receiver endpoints, sets protocol version, and prints sender/receiver/version status.
- PPPoE support prints discovery/session state and sets device, service, and access concentrator.
- SPPP support reads/writes auth/peer auth protocol, names, secrets, peer flags, DNS info, and phase state.

## WireGuard Support
WireGuard configuration is built in a growable `wg_data_io` buffer:
- `WG_LOAD_KEY` validates base64 key length and decodes keys.
- `ensurewginterface()` and `growwgdata()` allocate and resize the packed interface/peer/AIP request layout while preserving offsets.
- Peer commands add/remove peers, descriptions, endpoints, allowed IPs, PSKs, persistent keepalive, listen port, private key, and routing table.
- `process_wg_commands()` submits `SIOCSWG`.
- `wg_status()` reads variable-sized `SIOCGWG` output, prints interface port/rtable/public key, and with aliases enabled prints peers, descriptions, PSK presence, endpoints, counters, last handshake age, and allowed IPs.

## UMB Mobile Broadband Support
Non-`SMALL` UMB support uses MBIM value-description tables:
- `umb_status()` prints network errors, roaming/registration, supported classes, internal state, cell class, RSSI, speed, SIM/PIN state, subscriber identifiers, device/firmware info, phone/APN/provider info, and DNS servers.
- `umb_setpin()`, `umb_chgpin()`, `umb_puk()`, `umb_apn()`, `umb_setclass()`, and `umb_roaming()` read/update `umb_parameter`.
- `utf16_to_char()` and `char_to_utf16()` convert ASCII-compatible strings to/from UTF-16LE fields used by UMB ioctls.

## Formatting Helpers
- `printb()` and `printb_status()` render kernel `%b` bit descriptions.
- `prefix()` computes a contiguous prefix length and rejects non-contiguous masks by returning zero in invalid cases.
- `sec2str()` currently returns decimal seconds.
- `usage()` prints the concise command syntax.

## Error Handling and Risks
The implementation is intentionally ioctl-centric and exits on command failure with `err()`/`errx()` while status paths often tolerate unsupported ioctls. Risk areas include heavy reliance on global mutable structs, command ordering subtleties in deferred media/join/WireGuard paths, variable-size ioctl buffer resizing, packed WireGuard offset arithmetic, ambiguous parsing of `host:port` versus IPv6 literals in some tunnel/pflow paths, and broad ABI coupling to OpenBSD kernel networking headers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.h

## Purpose
`ifconfig.h` is the shared local header for OpenBSD `sbin/ifconfig`. It exposes globals owned by `ifconfig.c` plus function prototypes implemented by `ifconfig.c`, `brconfig.c`, and `sff.c`.

## Exported Globals
- `aflag`: global "all interfaces" status mode.
- `ifaliases`: controls whether alias/extra details are printed.
- `sock`: current ioctl socket shared by helper files.
- `ifname[IFNAMSIZ]`: selected interface name used by nearly every ioctl helper.

## Shared Formatting
- `printb(char *, unsigned int, unsigned char *)` is exported so bridge code can print bridge flag bitfields using the same `%b`-style formatter as `ifconfig.c`.

## Bridge API Surface
Most declarations are bridge control/status functions implemented in `brconfig.c`. They cover:
- member flags: discover, block non-IP, learn, locked, private VLAN port tags, STP, edge, autoedge, point-to-point, autoptp;
- membership: add/delete member, add/delete span, add local;
- forwarding database: flush, flushall, static address add/delete, endpoint add/delete, address display, virtual address display, max address count;
- timers and STP settings: hello time, forward delay, max age, protocol, priority, hold count, timeout;
- per-port settings: protected domains, PVID/untagged behavior, tagged VID map, interface priority, interface cost;
- PVLAN settings: primary, isolated, and community add/delete;
- rules: display, rulefile, flushrule, and direct `bridge_rule()` parsing;
- bridge detection and status.

## SFF API Surface
- `if_sff_info(int)` is implemented by `sff.c` and used by `ifconfig.c` for `transceiver`, `sff`, and `sffdump` output.

## Integration Notes
This header intentionally contains declarations only. It relies on included translation units already having the required system types visible, especially `IFNAMSIZ`. The separation keeps `ifconfig.c` as the command dispatcher while allowing bridge and transceiver logic to live in separate files without duplicating global declarations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/sff.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/sff.c

## Purpose
`sff.c` implements non-`SMALL` transceiver EEPROM/DDM reporting for OpenBSD `ifconfig`. It reads SFF/QSFP/XFP pages via `SIOCGIFSFFPAGE`, decodes module identity, connector/media distances, vendor strings, serial/date fields, voltage, temperature, optical power, bias current, thresholds, warnings, and optional raw hex dumps. `ifconfig.c` calls `if_sff_info(0)` for `transceiver`/`sff` status and `if_sff_info(1)` for `sffdump`.

## Standards and Module Types
The file contains constants and register offsets for:
- SFF-8024 identifiers/connectors;
- SFF-8472 SFP/GBIC EEPROM and DDM page `0xa2`;
- SFF-8436/SFF-8636 QSFP/QSFP+/QSFP28 lower and upper pages;
- INF-8077 XFP page layout.

It maps known transceiver identifiers and connector types to readable names and falls back to `Reserved` or `Vendor Specific`.

## Data Structures
- `struct sff_thresholds` stores high alarm, low alarm, high warning, and low warning thresholds.
- `struct sff_media_map` abstracts media-printing offsets/scales for connector, wavelength, SMF/OM distances, and copper distance across SFF-8472 and upper-page layouts.
- `sff8472_media_map` and `upper_media_map` configure those offsets.

## Page Access Flow
- `if_sffpage_init()` fills `struct if_sffpage` with `ifname`, I2C address, and page.
- `if_sff_info()` reads EEPROM page 0. If page 0 fails with `ENXIO`, it tries page 1 for XFP devices that cannot switch pages.
- Optional `dump` mode prints page address/page number and calls `hexdump()`.
- It inspects byte 0 for SFF-8024 identifier, prints the transceiver type, and dispatches:
  - SFP/GBIC -> `if_sff8472()`;
  - XFP -> `if_inf8077()`, ensuring page 1 is loaded;
  - QSFP/QSFP+/QSFP28 -> `if_sff8636()`;
  - unknown types -> type line only.

## String and Numeric Decoding
- `if_sff_ascii_print()` trims whitespace/NULs from fixed-width fields and uses `vis()` to safely print control characters.
- `if_sff_date_print()` formats six-digit `YYMMDD` as `20YY-MM-DD`, falling back to raw ASCII if non-digits appear.
- `if_sff_int()` and `if_sff_uint()` decode big-endian 16-bit signed/unsigned values.
- `if_sff_power2dbm()` converts 0.1 uW style power fields to dBm using `log10f()`.
- `if_sff_printalarm()` prints actual readings and optional threshold ranges, marking `[ALARM]` or `[WARNING]`.

## Media and Distance Output
`if_sff_printmedia()` prints connector name, wavelength when meaningful, and distances:
- SFF-8472 uses separate SMF meters/km fields and OM1/OM2/OM3 scale factors.
- Upper-page formats use a shared map with wavelength factor 20.0 and OM/copper offsets.
- Zero values are omitted; large distances are formatted in kilometers.

## SFF-8472 SFP/GBIC Path
`if_sff8472()` prints media, vendor/product/revision, serial, and date. It checks compliance and DDM-implemented bits before reading DDM page `IFSFF_ADDR_DDM`. It prints external-calibration warning if needed, then displays:
- voltage;
- TX bias current;
- temperature;
- TX optical power;
- RX optical power.
Each metric is compared to alarm/warning thresholds.

## XFP Path
`if_inf8077()` currently calls `if_upper_strings()` only, so it reports media plus vendor/product/revision/serial/date/lot fields, without DDM metrics.

## QSFP Path
`if_sff8636()` prints upper-page strings, checks `Data_Not_Ready`, max case temperature, and base temperature/voltage/channel fields. If paged memory is available, `if_sff8636_thresh()` reads page 3, validates page select, decodes alarm/warning thresholds, and prints threshold-aware:
- module temperature;
- voltage;
- per-channel TX bias;
- per-channel TX power;
- per-channel RX power.
If threshold page is not available or readings look unset, dump mode still prints fallback raw/current values.

## Hex Dump Support
`hexdump()` prints 16 bytes per line with hex bytes plus printable ASCII. `printable()` maps NUL to `_` and non-printable bytes to `~`.

## Error Handling and Risks
The file returns `-1` for page read failures so callers can decide whether to warn or fail. Most formatting assumes EEPROM data has standard-sized fields but guards output with fixed buffer lengths. Risk areas include unsupported external calibration, potentially `log10f(0)` on zero optical-power fields, and specification drift for newer SFF-8024 module identifiers not present in the static name tables.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/sff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/Makefile

## Purpose
This Makefile builds OpenBSD `iked`, the IKEv2 daemon, using the BSD make `bsd.prog.mk` infrastructure.

## Build Definition
- `PROG=iked` declares the output program.
- `SRCS` includes core daemon, configuration, crypto, IKEv2 message/payload handling, policy, PF_KEY, logging, process, timer, utility, RADIUS, vroute, and cryptographic support files.
- Generated map sources `eap_map.c` and `ikev2_map.c` are included in `SRCS`.
- `crypto_hash.c` and `sntrup761.c` are included for crypto support.
- `parse.y` is included for yacc-based configuration parsing.
- Manual pages are `iked.conf.5` and `iked.8`.

## Libraries and Compiler Flags
- Links against `libutil`, `libevent`, `libcrypto`, and `libradius` via `LDADD`.
- Mirrors dependencies in `DPADD`.
- Adds `-Wall`, local include path, strict prototypes, missing prototypes/declarations, shadow, pointer arithmetic, cast-qual, and sign-compare warnings.

## Generated Files
- `CLEANFILES` and `GENERATED` include `ikev2_map.c` and `eap_map.c`.
- `ikev2_map.c` is generated by running `genmap.sh ikev2.h ikev2`.
- `eap_map.c` is generated by running `genmap.sh eap.h eap`.
- Each generation target touches the output after redirecting script output.

## Link Mode
After including `<bsd.prog.mk>`, the file sets `LDSTATIC=` with a comment stating `iked` should not be compiled as a static binary by default.

## Integration Notes
This file is build metadata only; it does not implement runtime behavior. Its main maintenance risks are keeping `SRCS` synchronized with daemon source changes and ensuring generated map targets track header/script changes correctly.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/Makefile -->