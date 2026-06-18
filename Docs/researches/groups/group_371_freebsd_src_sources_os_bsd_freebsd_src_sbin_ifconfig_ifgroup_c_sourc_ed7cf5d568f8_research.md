# Group Research: group_371_freebsd_src_sources_os_bsd_freebsd_src_sbin_ifconfig_ifgroup_c_sourc_ed7cf5d568f8

Scope verified against `Docs/research_subset_a.md`: all files are within `sources/os/bsd/freebsd-src`. I read every listed file completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgroup.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgroup.c

`ifgroup.c` adds ifconfig support for interface groups. It registers `group` and `-group` commands, an `af_group` status callback, and the global `-g groupname` option for listing group members.

Core behavior is ioctl driven: `setifgroup()` uses `SIOCAIFGROUP`, `unsetifgroup()` uses `SIOCDIFGROUP`, and `printgroup()` uses `SIOCGIFGMEMB`. Group names are rejected if they end in a digit and are bounded by `IFNAMSIZ`.

Status output uses `ifconfig_get_groups(lifh, ctx->ifname, &ifgr)` and prints all groups except the implicit `all` group. `printgroup()` opens an `AF_LOCAL` datagram socket, first queries required buffer length, then allocates and fetches membership.

Dependencies include `<net/if.h>`, `libifconfig`, and the shared `ifconfig.h` command registration system. Memory ownership is straightforward: `ifgr.ifgr_groups` is freed after status/list use.

Notable edge behavior: duplicate group add is not fatal (`EEXIST` ignored), missing group removal is not fatal (`ENOENT` ignored), and `printgroup()` exits the process after printing because it is a top-level option callback.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifieee80211.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifieee80211.c

`ifieee80211.c` is the full ifconfig module for net80211 wireless devices. It registers a large `ieee80211_cmds[]` table, an `af_ieee80211` status callback, and a `wlan` clone callback for virtual AP/device creation.

The file wraps net80211 ioctl access through `lib80211_get80211()`, `lib80211_get80211len()`, `lib80211_get80211val()`, and `lib80211_set80211()`. Cached module state includes channel info, regulatory domain, roaming params, tx params, current channel, HT/VHT config, and the current ifmedia state.

Channel handling is substantial. `getchaninfo()`, `mapfreq()`, `mapchan()`, `promote()`, `getchannelflags()`, and `getchannel()` parse channel/frequency specifications with mode and width suffixes, promote ambiguous legacy channels to better HT/VHT-capable entries, and validate against the kernel channel list.

Regulatory-domain handling uses `lib80211_regdomain` data. `set80211regdomain()`, `set80211country()`, `set80211location()`, and `set80211ecm()` modify cached `regdomain`, then `setregdomain_cb()` fetches device capabilities, builds a legal channel list with `regdomain_makechannels()`, and pushes `IEEE80211_IOC_REGDOMAIN`.

Configuration commands cover SSID/mesh ID, station name, auth mode, powersave, WEP keys and NetBSD-compatible `nwkey`, BSSID, channel switching, tx power, roaming mode, WME/WMM parameters, ACL MAC policy/list edits, background scan, quiet timing, tx/roam rates, RTS/fragment/BMISS thresholds, HT/VHT toggles, AMPDU/AMSDU/STBC/LDPC/UAPSD, TDMA, mesh routing, HWMP, and clone parameters.

Status and list output are broad. `ieee80211_status()` prints SSID/mesh ID, channel, BSSID, station name, regulatory domain, auth/privacy/key status, powersave, tx power, tx params, scan/roam settings, HT/VHT feature state, WME, AP/TDMA/mesh settings, and parent device. `set80211list()` dispatches to station, scan/AP cache, channel/frequency, active channel, caps, WME, MAC ACL, tx power, roam, tx params, regdomain, country list, and mesh route listings.

The file contains extensive IE decoders for scan/station output: WPA, RSN, RSNXE, WPS, WME, Atheros, TDMA, HT/VHT, HE capability/operation, MU-EDCA, supported operating classes, country, BSS load, AP channel report, and generic element dumps in verbose mode.

Virtual AP clone support accumulates `struct ieee80211_clone_params`. `wlan_create()` requires `wlandev`, requires `wlanbssid` for WDS, calls `ifcreate_ioctl()`, then sets a default FCC/US regulatory domain if the driver left defaults unset.

Notable implementation details: string/key parsing accepts printable strings or `0x` hex; `print_string()` honors UTF-8 locales; line wrapping is handled by `LINE_INIT`, `LINE_CHECK`, and `LINE_BREAK`; several setters register callbacks so combined command-line options update one fetched structure once.

Risk notes: this is a dense legacy C command surface with many direct `atoi()`/`atof()` conversions, fixed local buffers, and protocol structure casts. Mesh metric/path setters copy exactly 12 bytes from the input pointer, so callers rely on kernel/userland command syntax discipline. The scan and IE decoders trust kernel-filtered IE lengths in several paths, which matches the comments but is an important assumption.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifieee80211.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifipsec.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifipsec.c

`ifipsec.c` adds ifconfig support for IPsec tunnel interfaces. It registers the `reqid` command and an `af_ipsec` status callback.

`ipsec_status()` fetches the current request ID with `IPSECGREQID` through `ioctl_ctx_ifr()` and prints `reqid: <value>` if available. `setreqid()` parses a numeric value with `strtoul()` and sends it using `IPSECSREQID`.

Dependencies are `net/if_ipsec.h`, standard ifreq ioctl plumbing, and the shared ifconfig registration interface.

Notable behavior: parse errors warn and return rather than exiting; ioctl set failures also warn and return. The parsed value is stored in `uint32_t`, but there is no explicit range or `ERANGE` validation beyond checking trailing characters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifipsec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/iflagg.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/iflagg.c

`iflagg.c` implements ifconfig support for link aggregation interfaces. It registers clone-time `laggtype`, runtime port/protocol/hash/options commands, status printing, and a `lagg` clone callback.

The command handlers manage ports (`SIOCSLAGGPORT`, `SIOCSLAGGDELPORT`), aggregation protocol (`SIOCSLAGG`), flowid shift and round-robin limit (`SIOCSLAGGOPTS`), boolean lagg options, and hash selection (`SIOCSLAGGHASH`). Protocol/type names are resolved from kernel-provided macro tables such as `LAGG_PROTOS` and `LAGG_TYPES`.

`lagg_status()` uses `ifconfig_lagg_get_lagg_status()` from libifconfig, prints protocol and hash fields, optionally prints lagg options/statistics in verbose mode, then prints every member port and LACP state/peer details where applicable.

The file includes helpers for formatting LACP actor/partner identifiers and MAC addresses. `lagg_create()` passes accumulated `struct iflaggparam params` to `ifcreate_ioctl()`.

Notable edge behavior: adding a failed/missing port warns and sets global `exit_code = 1` but does not immediately terminate, with a comment explaining this avoids taking down an entire lagg due to one failed NIC. Existing ports are ignored via `EEXIST`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/iflagg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmac.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmac.c

`ifmac.c` adds MAC Framework label support to ifconfig. It registers `maclabel` and an `af_maclabel` status callback.

`maclabel_status()` prepares an ifnet label with `mac_prepare_ifnet_label()`, fetches it via `SIOCGIFMAC`, converts it with `mac_to_text()`, and prints non-empty labels. `setifmaclabel()` parses a label from text with `mac_from_text()` and applies it through `SIOCSIFMAC`.

Dependencies include `<sys/mac.h>`, standard ifreq ioctls, and `ifconfig.h`. Label memory is released with `mac_free()`, and text output from `mac_to_text()` is freed normally.

Notable behavior: most failures are silent or printed with `perror()` rather than fatal, so unsupported MAC labeling does not break general ifconfig status output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmedia.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmedia.c

`ifmedia.c` implements generic media selection and reporting for interfaces. It registers `media`, `mode`, `mediaopt`, `-mediaopt`, `inst`, and `instance`, plus an `af_media` status callback.

`media_status()` fetches `struct ifmediareq` through libifconfig, prints current and active media, link status, optional down reason, and supported media when `supmedia` is enabled. Status text and media decoding are delegated to libifconfig helpers.

Setters fetch media state once with `ifmedia_getstate()`, mutate `ifm_current`, and register `setifmediacallback()` so `SIOCSIFMEDIA` is issued later. This supports combining media subtype, mode, instance, and options on one command line.

Parsing helpers map subtype/mode/options strings through `ifconfig_media_lookup_subtype()`, `ifconfig_media_lookup_mode()`, and `ifconfig_media_lookup_options()`. Options are comma split with allocated arrays.

Printing helpers produce user-facing media strings and ifconfig-replayable supported media lines. They include top-level type, subtype, non-autoselect mode, option list, and nonzero instance.

Notable behavior: `setifmediacallback()` uses a static `did_it`, so the deferred media ioctl is only performed once per process invocation. `get_media_mode()` returns `INVALID_IFMEDIA` for unknown modes while subtype/options treat unknown names as fatal.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmedia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifpfsync.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifpfsync.c

`ifpfsync.c` implements ifconfig support for pfsync interfaces. It registers commands for `syncdev`/`syncif`, `syncpeer`, `maxupd`, `defer`, and `version`, plus an `af_pfsync` status callback.

The module communicates with the kernel using nvlist payloads packed into `ifr.ifr_cap_nv` and sent through `SIOCGETPFSYNCNV` or `SIOCSETPFSYNCNV`. `pfsync_do_ioctl()` packs the input nvlist, allocates an ioctl buffer, calls the ioctl, destroys the old nvlist, and unpacks the returned nvlist.

`syncpeer` values are represented as nested nvlists containing address family and binary sockaddr data. Helpers convert between `sockaddr_storage` and nvlist form for IPv4/IPv6 when enabled.

Setters read the current nvlist, replace or clear the relevant key, and write the nvlist back. `maxupd` is range checked to 0-255; `version` is deliberately left to kernel validation.

`pfsync_status()` reads `syncdev`, `syncpeer`, `maxupdates`, `version`, and `flags`, then prints sync device, peer when non-default, defer state, version, and syncok state.

Risk notes: `pfsync_do_ioctl()` assumes packing, allocation, and buffer sizing succeed before `memcpy()`. It returns positive `EIO` on unpack failure while callers generally test only for `-1`, so error propagation is inconsistent in that path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifpfsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifstf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifstf.c

`ifstf.c` implements 6rd/STF tunnel configuration support. It registers `stfv4net` and `stfv4br`, plus an `af_stf` status callback.

All driver communication goes through `do_cmd()`, which wraps `SIOCSDRVSPEC`/`SIOCGDRVSPEC` with `struct ifdrv`. Status fetches `STF6RD_GV4NET` and prints IPv4 prefix plus border relay address.

`setstf_br()` parses an IPv4 border relay address and sends `STF6RD_SBR`. `setstf_set()` parses `address/prefixlen`, validates prefix length 1-32 using `strtonum()`, parses the IPv4 address, and sends `STF6RD_SV4NET`.

Notable behavior: `setstf_set()` temporarily writes a NUL over the slash in the argument string, restores it only on one error path, and otherwise exits or completes without restoring. This is typical old ifconfig-style parsing but assumes mutable command argument storage.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifstf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvlan.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvlan.c

`ifvlan.c` implements VLAN configuration. It registers clone-time and runtime `vlan`, `vlandev`, and `vlanproto`, runtime `vlanpcp`, `-vlandev`, VLAN capability toggles, status reporting, and clone callbacks for `vlan` names and `parent.tag` names.

State is accumulated in static `struct vlanreq params`, using `NOTAG` and `NOPROTO` sentinels. `vlan_parse_ethervid()` derives parent and VLAN tag from interface names like `em0.100`, rejects invalid tags, and detects ambiguous command-line combinations.

`vlan_create()` validates that tag and parent are both supplied when either is present, defaults protocol to 802.1Q, and passes params to `ifcreate_ioctl()`. `vlan_cb()` enforces paired `vlan`/`vlandev` arguments for non-create workflows.

Runtime setters fetch existing VLAN config when possible, preserve missing counterpart fields, then call `SIOCSETVLAN`. `vlan_status()` prints tag, protocol, optional PCP, and parent interface.

Supported protocols are `802.1q`, `802.1ad`, and `qinq`, mapped to `ETHERTYPE_VLAN` and `ETHERTYPE_QINQ`. PCP is range checked to 0-7.

Notable behavior: VLAN tag parsing checks representability in `vlr_tag` after `strtoul()`, but relies on struct field truncation comparison rather than a named VLAN max constant.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvlan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvxlan.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvxlan.c

`ifvxlan.c` implements VXLAN configuration. It registers clone-time and runtime VXLAN identity/address/port/learning commands, flush commands, VXLAN hardware capability toggles, status reporting, and a `vxlan` clone callback.

The file uses static `struct ifvxlanparam params` for clone-time accumulation. `vxlan_exists()` probes driver config with `VXLAN_CMD_GET_CONFIG`; setters update `params` before creation or send an immediate `SIOCSDRVSPEC` driver command after creation.

`vxlan_status()` fetches `struct ifvxlancfg`, suppresses output when VNI is unset, formats local and remote/group addresses with numeric host/service output, detects multicast group addresses, and in verbose mode prints learning, port range, TTL, and forwarding-table counters/limits.

Setters validate VNI, local/remote/group addresses, local and remote UDP ports, source port range, forwarding-table timeout and max address count, multicast device, TTL, and learning state. Address parsing uses `getaddrinfo()` and rejects multicast local/remote addresses while requiring multicast for `vxlangroup`.

`vxlan_check_params()` prevents mixed IPv4/IPv6 local/remote clone parameters and duplicate IPv4+IPv6 local or remote specifications. `vxlan_create()` validates and passes accumulated params to `ifcreate_ioctl()`.

Notable edge behavior: numeric parsing uses `strtoul()` with `ERANGE` checks. Port validation rejects values `>= UINT16_MAX`, so `65535` is not accepted as a port. TTL allows values through 256, matching the local implementation’s accepted range.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvxlan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/sfp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/sfp.c

`sfp.c` implements SFP/QSFP/CMIS transceiver status printing for ifconfig. It exposes `sfp_status(if_ctx *ctx)` for use by the wider ifconfig status path.

The function fetches module identity with `ifconfig_sfp_get_sfp_info()`, converts it to display strings, prints physical spec and connector, then fetches and prints vendor name, part number, serial number, and date.

Compliance output depends on module type and verbosity: CMIS skips legacy compliance, QSFP can show revision, and classic SFP can show class, length, technology, media, and speed at high verbosity.

Runtime diagnostic status prints module temperature, voltage, and per-lane RX power/TX bias using `power_mW()`, `power_dBm()`, and `bias_mA()`. Status resources are freed with `ifconfig_sfp_free_sfp_status()`.

At verbosity above 2, the module dumps raw EEPROM/page bytes using `hexdump()`, with different ranges for CMIS, QSFP/SFF8436, and SFP/SFF8472.

Dependencies include `libifconfig_sfp`, SFF8436/SFF8472 headers, and `libutil` hexdump support. The function returns silently when SFP data is unavailable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/sfp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/Makefile

This Makefile defines ATF shell tests for the ifconfig directory. It includes the tests `ifconfig` and `inet6`.

It also declares `NETBSD_ATF_TESTS_SH= nonexistent_test`, preserving a NetBSD test harness convention. Test metadata requests execution in a VNET jail with raw sockets: `execenv="jail"` and `execenv_jail_params="vnet allow.raw_sockets"`.

The file includes `<netbsd-tests.test.mk>` and `<bsd.test.mk>`, integrating the tests into the FreeBSD build/test framework.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/ifconfig.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/ifconfig.sh

`ifconfig.sh` is an ATF shell test file for general ifconfig behavior. It sources the shared VNET test helper from `../../sys/common/vnet.subr`.

The only test case is `badfib`. It requires root, initializes VNET state, creates an epair, verifies assigning FIB 0 succeeds, then verifies assigning FIB `net.fibs` fails with non-empty stderr because that FIB is outside the configured range.

Cleanup calls `vnet_cleanup`. `atf_init_test_cases()` registers `badfib`.

The test exercises argument validation and kernel error handling for per-interface FIB assignment in an isolated VNET environment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/ifconfig.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/inet6.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/inet6.sh

`inet6.sh` is an ATF shell test file for IPv6-specific ifconfig behavior. It sources the shared VNET helper and defines `netmask`, `broadcast`, and `delete6` test cases.

`netmask` validates bug 286910 coverage: using IPv4-style `netmask` with an IPv6 address must fail with `ifconfig: netmask: invalid option for inet6`, while CIDR `/64` succeeds and displays `prefixlen 64`. It also checks the invalid option is rejected during address removal syntax.

`broadcast` similarly verifies that `broadcast` is rejected for IPv6 add and remove forms with the expected error message.

`delete6` adds `fe80::42/64` to an epair, verifies the scoped address is visible, removes it with `inet6 -alias`, and verifies it no longer appears.

All tests require root and use VNET/epair isolation. Cleanup for each case calls `vnet_cleanup`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/inet6.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/init/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/init/Makefile

This Makefile builds the FreeBSD `init` program. It assigns `PACKAGE=runtime`, `PROG=init`, and `MAN=init.8`.

It marks the installed program as precious through `PRECIOUSPROG=`, uses backup install flags `-b -B.bak`, and adds compile definitions for `DEBUGSHELL`, `SECURE`, `LOGIN_CAP`, and `COMPAT_SYSV_INIT`.

Libraries linked are `util` and `crypt`. The file also declares the `ttys` configuration file through `CONFGROUPS= CONFTTYS`, `CONFTTYSNAME= ttys`, and `CONFTTYS+= ttys`.

Build integration is via `.include <bsd.prog.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/init/Makefile -->