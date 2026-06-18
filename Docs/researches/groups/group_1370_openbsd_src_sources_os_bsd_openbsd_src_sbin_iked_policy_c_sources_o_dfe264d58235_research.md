# Group Research: group_1370_openbsd_src_sources_os_bsd_openbsd_src_sbin_iked_policy_c_sources_o_dfe264d58235

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/os/bsd/openbsd-src`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/policy.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/policy.c

This OpenIKED file owns policy lookup, IKE SA lifecycle state, SA indexing, traffic selector generation, address-pool/user lookup trees, active flow/CHILD SA comparison, and proposal negotiation.

Key responsibilities:
- Initializes policy, OCSP, RADIUS, user, SA, destination-ID SA, active-SA, and active-flow queues/trees in `policy_init`.
- Matches inbound IKE messages or existing SAs to configured policies through `policy_lookup`, `policy_lookup_sa`, `policy_test`, and `policy_test_flows`.
- Uses pf-style skip-step acceleration in `policy_calc_skip_steps` to jump across policies that cannot match by flags, address family, peer address, or local address.
- Reference-counts reload-surviving policies with `policy_ref` and `policy_unref`.
- Maintains SA state transitions, required validation flags, and iked statistics in `sa_state`, `sa_stateflags`, and `sa_stateok`.
- Allocates or reuses IKE SAs in `sa_new`, inserts them into RB trees keyed by initiator/SPI, attaches policy references, and initializes required authentication/certificate/EAP state flags.
- Builds traffic selector lists from configured flows with duplicate suppression in `policy_generate_ts` and `ts_insert_unique`.
- Frees IKE SAs, rekey links, destination-ID tree entries, flows, CHILD SAs, and associated policy references via `sa_free`, `sa_free_flows`, `childsa_free`, and `flow_free`.
- Configures virtual interface state for Configuration Payload-assigned DNS/address/routes in `sa_configure_iface`, delegating OS changes to `vroute.c`.
- Provides SA lookup by SPI and by authenticated destination ID through `sa_lookup`, `sa_dstid_lookup`, `sa_dstid_insert`, and `sa_dstid_remove`.
- Negotiates local/peer proposals with transform scoring through `proposals_negotiate` and `proposals_match`.

Important data structures:
- TAILQs for policies, flows, policy SA peers, and traffic selectors.
- RB trees generated at the bottom of the file for IKE SAs, destination-ID-indexed SAs, address pools, users, active CHILD SAs, and flows.
- `struct iked_policy`, `struct iked_sa`, `struct iked_flow`, `struct iked_childsa`, and `struct iked_proposal` are central callers/consumers.

Security and correctness notes:
- Policy matching requires compatible address family, peer/local prefixes, IDs, transport-mode setting, flows, and proposal transforms.
- Proposal matching handles AEAD transforms by rejecting separate integrity transforms and requiring mandatory transform classes for IKE, AH, and ESP.
- Destination-ID indexing is deliberately strict: missing/corrupt IDs are fatal because the RB-tree comparator depends on valid ID buffers.
- `sa_configure_iface` directly ties negotiated CP state to interface address/DNS/route side effects; failures propagate as SA configuration failures.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/policy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/print.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/print.c

This file prints OpenIKED runtime configuration in iked.conf-like form for verbose/debug output.

Key responsibilities:
- `print_xf` maps transform IDs and key lengths to names from `struct ipsec_xf` tables.
- `print_user` emits a configured user/password line.
- `print_policy` serializes an `iked_policy` including policy mode, active/passive state, IPComp, tunnel/transport, NAT-T, SA protocol, IP protocol filters, address family, rdomain, flow selectors, local/peer constraints, IKE/CHILD SA proposals, IDs, lifetimes, authentication, CP config attributes, interface, pf tag, and tap/enc device.

Important dependencies:
- Relies on transform tables such as `saxfs`, `authxfs`, `ikeencxfs`, `ipsecencxfs`, `prfxfs`, `groupxfs`, `esnxfs`, `methodxfs`, and `cpxfs`.
- Uses `print_verbose`, `print_addr`, `print_proto`, and `print_map` from OpenIKED utility code.
- Uses `if_indextoname` to display configured interface indexes.

Security and correctness notes:
- PSK material is printed when policy auth method is shared-key MIC, so output paths using this function must be treated as sensitive.
- The function walks RB flow trees and TAILQ proposal/config collections and is purely diagnostic; it does not mutate policy state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/proc.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/proc.c

This is OpenIKED’s generic privilege-separated process framework. It creates child processes, builds an imsg/socketpair communication mesh, drops privileges, runs libevent loops, and provides helpers for sending messages among process roles.

Key responsibilities:
- Maps process titles to `enum privsep_procid` with `proc_getid`.
- Re-execs child process roles with `-P <process>` and `-I <instance>` arguments in `proc_exec`.
- Initializes parent and child process topology in `proc_init` and `proc_setup`.
- Creates parent-child socketpairs first, then distributes inter-child socketpairs by file descriptor passing in `proc_connect` and `proc_open`.
- Accepts received process file descriptors with `proc_accept`, initializes `imsgbuf`, enables fd passing, and registers events.
- Closes imsg buffers/events and waits for child exits in `proc_close` and `proc_kill`.
- Runs a child role in `proc_run`: optional control socket setup, chroot, privilege drop, libevent initialization, signal registration, parent pipe acceptance, and role callback invocation.
- Dispatches imsg events in `proc_dispatch`, handling generic messages for verbosity, process-fd transfer, and process-ready handshakes after role-specific callbacks have had first chance.
- Provides message helper APIs: `imsg_event_add`, `imsg_compose_event`, `imsg_composev_event`, `proc_compose`, `proc_compose_imsg`, `proc_composev`, `proc_composev_imsg`, `proc_forward_imsg`, `proc_ibuf`, `proc_iev`, and `proc_flush_imsg`.

Important data flow:
- The parent constructs all socketpairs, passes endpoints using `IMSG_CTL_PROCFD`, then sends `IMSG_CTL_PROCREADY`.
- Children acknowledge readiness to the parent; once all acknowledgements arrive, the parent invokes the supplied connected callback.
- `proc_range` lets callers target all instances of a process role by passing `-1`.

Security and correctness notes:
- Child processes chroot and drop to configured users/groups before entering the event loop.
- `imsgbuf_allow_fdpass` is explicitly enabled for channels that pass descriptors.
- Unexpected generic imsg types are fatal, making the IPC protocol closed by default.
- `proc_flush_imsg` is documented as breaking async I/O and is used carefully during startup fd distribution to avoid descriptor buildup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/radius.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/radius.c

This file implements OpenIKED RADIUS integration for EAP authentication, Configuration Payload attribute mapping, accounting, retry/failover, and Dynamic Authorization Extensions disconnect handling.

Key responsibilities:
- Defines default RADIUS-to-IKEv2 CP mappings for IPv4 address, netmask, DNS, and NBNS attributes, including Microsoft vendor attributes.
- `iked_radius_request` converts EAP Response messages into RADIUS Access-Request packets, stores request state, includes User-Name, State, EAP-Message, NAS attributes, and schedules send/retry.
- `iked_radius_on_event` receives RADIUS responses, matches by ID, validates authenticators, processes Access-Challenge/Accept/Reject, extracts EAP MSK, updates protected User-Name/class attributes, advances SA auth state, maps CP attributes, and forwards EAP payloads back into IKE_AUTH.
- `iked_radius_request_send` performs server selection, retry backoff, request ID allocation, failover, NAS-IP/NAS-Identifier insertion, accounting delay calculation, authenticator generation, packet send, and timer rescheduling.
- `iked_radius_config` maps configured or default RADIUS attributes into SA/request Configuration Payload reply data.
- Accounting helpers send Accounting-On/Off, Start, Stop, and interim-style records through `iked_radius_acct_request`.
- `iked_radius_dae_on_event` implements Disconnect-Request handling from authorized DAE clients, with lookup by Acct-Session-Id, User-Name, or Framed-IP-Address, and emits ACK/NAK/CoA-NAK responses.

Important dependencies:
- Uses OpenBSD `radius(3)` packet APIs, libevent timers, OpenIKED `ibuf`, SA state management, and IKEv2 EAP send/delete helpers.
- Uses the shared timer helper from `timer.c`.

Security and correctness notes:
- Validates response authenticators and message authenticators before trusting authentication responses.
- Keeps RADIUS State pinned to a server; failover is refused once State exists.
- Accounting falls back to IKE ID when authenticated EAP identity is absent, but RFC guidance is noted in comments.
- DAE requests are accepted only from configured clients and authenticated with the client secret.
- Notable implementation quirk: the IPv6 CP mapping branch sets `addr->addr_af = AF_INET` before filling an IPv6 sockaddr; this looks inconsistent with the surrounding IPv6 handling and is worth reviewing against upstream history.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/radius.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/smult_curve25519_ref.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/smult_curve25519_ref.c

This is a compact public-domain Curve25519 scalar multiplication reference implementation derived from Matthew Dempsky and D. J. Bernstein code.

Key responsibilities:
- Exposes `crypto_scalarmult_curve25519(q, n, p)`.
- Clamps the scalar, loads the peer point, runs a Montgomery ladder, computes a field inverse, multiplies to affine form, freezes modulo `2^255 - 19`, and writes the 32-byte shared secret.
- Implements field operations over 32 byte-limb arrays: `add`, `sub`, `squeeze`, `freeze`, `mult`, `mult121665`, `square`, and `recip`.
- `select` performs branchless conditional selection for ladder state.
- `mainloop` executes the scalar ladder from bit 254 down to bit 0.

Security and correctness notes:
- The implementation uses fixed-size loops and branchless conditional swap/selection for scalar-dependent choices.
- It is reference-style, not optimized assembly.
- No allocation, file I/O, or OS interactions occur.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/smult_curve25519_ref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.c

This file is an amalgamated public-domain SUPERCOP reference implementation of the Streamlined NTRU Prime `sntrup761` KEM, generated from multiple upstream SUPERCOP files and adapted to OpenBSD’s `crypto_api.h` type/function names.

Public API:
- `crypto_kem_sntrup761_keypair(unsigned char *pk, unsigned char *sk)`
- `crypto_kem_sntrup761_enc(unsigned char *c, unsigned char *k, const unsigned char *pk)`
- `crypto_kem_sntrup761_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk)`

Key responsibilities:
- Provides constant-time-ish sorting helpers for signed and unsigned 32-bit arrays used in short polynomial generation.
- Implements division/modulo helpers avoiding variable-time CPU division for secret-dependent `x`, with `m` assumed constant.
- Fixes parameters to `SIZE761` and `SNTRUP`, not LPR.
- Implements recursive `Encode`/`Decode` for polynomial coefficient packing.
- Implements mod-3 and mod-q arithmetic, reciprocal calculations, ring multiplication, rounding, short polynomial generation, SHA-512 prefixed hashes, and random sampling.
- Implements Streamlined NTRU Prime core operations:
  - `KeyGen` generates public polynomial and secret components.
  - `Encrypt` computes rounded ciphertext polynomial.
  - `Decrypt` recovers the short input polynomial and masks failures.
- Implements encoding/decoding for small, full Rq, and rounded polynomials.
- Implements KEM construction:
  - `KEM_KeyGen` appends public key, random fallback secret, and public-key hash cache into the secret key.
  - `Encap` samples inputs, encrypts, confirms, and derives session key.
  - `Decap` decrypts, re-encrypts for confirmation, conditionally substitutes fallback secret on mismatch, and derives the final key.

Important dependencies:
- `crypto_api.h` supplies fixed-width crypto types, `randombytes`, and `crypto_hash_sha512`.
- No filesystem or socket I/O occurs; all OS dependence is through randomness and hash primitives.

Security and correctness notes:
- The decapsulation path uses `Ciphertexts_diff_mask` and masked substitution to avoid directly branching on ciphertext validity for the recovered secret.
- Comments explicitly discuss timing assumptions around division and multiplication.
- Large variable-length stack arrays are used throughout, matching the reference style.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.sh -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.sh

This shell script generates the amalgamated `sntrup761.c` source from SUPERCOP `supercop-20201130/crypto_kem/sntrup761/ref` and related sorting sources.

Key responsibilities:
- Emits OpenBSD header comments and public-domain author lines from SUPERCOP implementor metadata.
- Emits common includes and maps SUPERCOP integer type names to `crypto_api.h` names with preprocessor defines.
- Concatenates a fixed list of SUPERCOP source/header fragments.
- Applies `sed` transformations to:
  - Remove includes and externs.
  - Rename exported `crypto_kem_` symbols to `crypto_kem_sntrup761_`.
  - Make non-exported functions static.
  - Remove namespace macros and duplicate type defines.
  - Rename sort functions to `crypto_sort_int32` and `crypto_sort_uint32`.
  - Remove unused division helpers to prevent warnings.
  - Patch `int32_MINMAX` intermediate arithmetic to use `int64_t` and avoid signed 32-bit overflow when used by unsigned sorting.

Inputs and outputs:
- Expects to be run with the SUPERCOP root as `$1`.
- Writes the generated C source to stdout.

Security and correctness notes:
- The script is reproducibility-critical for auditing local modifications to the vendored cryptographic code.
- It relies on exact upstream paths and text patterns; upstream source layout changes could silently require script updates.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/timer.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/timer.c

This small file wraps libevent one-shot timers for OpenIKED’s `struct iked_timer`.

Key responsibilities:
- `timer_set` initializes or resets a timer object, cancels a pending event if necessary, stores the environment/callback/argument, and binds `timer_callback`.
- `timer_add` schedules the event after a timeout in seconds.
- `timer_del` cancels a timer if it belongs to the given environment and has an initialized callback/event.
- `timer_callback` invokes the stored OpenIKED callback with the stored environment and argument.

Important dependencies:
- Uses libevent `evtimer_*` APIs.
- Used by code such as RADIUS retry/failover handling.

Security and correctness notes:
- Ownership is guarded by comparing `tmr->tmr_env` to the supplied environment in `timer_del`.
- The helper does not clear callback pointers after firing; reuse is managed by callers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/timer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/types.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/types.h

This shared OpenIKED header defines global constants, default paths, option flags, transform metadata, IPC message types, privilege-separated process IDs, and reset modes.

Key contents:
- Default runtime user/config/socket/CA paths:
  - `_iked`
  - `/etc/iked.conf`
  - `/var/run/iked.sock`
  - `/etc/iked/` and certificate/key subdirectories
- Vendor/NAS identity strings used in IKE/RADIUS paths.
- Runtime option flags for verbose, no-action, and passive modes.
- IKE/NAT-T ports, nonce/cookie size limits, max message/config/tag/password sizes, and default lifetimes.
- `struct iked_constmap` for ID-to-name mappings.
- `struct iked_transform` for IKEv2 transform metadata and scoring.
- `enum imsg_type`, covering control messages, compile/config load messages, UDP/PF_KEY/IKE message passing, RADIUS config, virtual route/DNS/address changes, OCSP, auth/key operations, stats, and process-fd readiness.
- `enum privsep_procid` for parent, control, cert, and IKEv2 processes.
- `enum flushmode` for reload/reset scopes.
- Local `nitems` fallback macro.

Security and correctness notes:
- This header is a contract between multiple OpenIKED processes; enum ordering and message IDs must stay consistent across all participants.
- Size constants constrain fixed buffers in identity, PSK, message, and CP code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/util.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/util.c

This file provides OpenIKED socket, address, formatting, mask, string, and debug-output utilities.

Key responsibilities:
- Address/port helpers:
  - `socket_af`, `socket_getport`, `socket_setport`, `socket_getaddr`
- Socket setup:
  - `socket_bypass` sets IPsec bypass levels so IKE UDP sockets are not themselves protected by IPsec.
  - `udp_bind` creates nonblocking UDP sockets, applies IPsec bypass, reuse options, destination-address receive options, and binds.
- Address comparison:
  - `sockaddr_cmp` compares IPv4/IPv6 sockaddr values with optional prefix masking.
- Ancillary-data I/O:
  - `sendtofrom` sends packets with explicit source address using `IP_SENDSRCADDR` or `IPV6_PKTINFO`.
  - `recvfromto` receives source and local destination address information from control messages.
- Formatting:
  - `print_spi`, `print_map`, `print_hex`, `print_hexval`, `print_hexbuf`, `print_bits`, `print_addr`, and `print_proto`.
- Mask conversion:
  - `mask2prefixlen`, `mask2prefixlen6`, `prefixlen2mask`, and `prefixlen2mask6`.
- String helpers:
  - `lc_idtype`, `get_string`, `expand_string`, and `string2unicode`.
- Debug output:
  - `print_debug` and `print_verbose`, gated by `log_getverbose`.

Security and correctness notes:
- Several print helpers use rotating static buffers sized by `IKED_CYCLE_BUFFERS`; callers must not retain pointers indefinitely.
- `recvfromto` preserves IPv6 link-local scope IDs from packet info.
- `mask2prefixlen6` fatals on non-contiguous IPv6 masks, enforcing canonical prefix masks.
- `string2unicode` is a simple zero-high-byte expansion and contains a byte-order caveat comment.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/version.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/version.h

This tiny header defines the OpenIKED version string.

Key content:
- `#define IKED_VERSION "7.4"`

Usage:
- Consumed wherever OpenIKED needs to report or embed its version, including vendor/version-identification paths.

Security and correctness notes:
- No logic, state, or OS interaction.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/vroute.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/vroute.c

This file implements OpenIKED virtual route, DNS, and interface-address management. It lets less-privileged OpenIKED processes request network configuration changes via imsg, while the parent performs routing socket and ioctl operations.

Key responsibilities:
- Initializes route/ioctl sockets and cleanup tracking state in `vroute_init`.
- Reads routing socket messages in `vroute_rtmsg_cb`, especially DNS proposal solicitations, and re-advertises tracked DNS proposals.
- Tracks added interface addresses, routes, and DNS proposals in TAILQs so `vroute_cleanup` can remove them on shutdown.
- Serializes child-to-parent requests:
  - `vroute_setaddr` / `vroute_getaddr`
  - `vroute_setdns` / `vroute_getdns`
  - `vroute_setaddroute`, `vroute_setcloneroute`, `vroute_setdelroute`, `vroute_setroute`
  - `vroute_getroute`, `vroute_getcloneroute`
- Maintains cleanup lists with insert/remove helpers for routes, DNS, and addresses.
- Emits DNS proposals with `vroute_dodns`.
- Emits route messages over `AF_ROUTE` with `vroute_doroute`, including route GET handling.
- Parses route GET replies in `vroute_process`.
- Applies interface addresses with `vroute_doaddr` using `SIOCAIFADDR`/`SIOCDIFADDR` for IPv4 and `SIOCAIFADDR_IN6`/`SIOCDIFADDR_IN6` for IPv6.

Important OS interactions:
- `socket(AF_ROUTE, SOCK_RAW, AF_UNSPEC)`
- `setsockopt(AF_ROUTE, ROUTE_MSGFILTER, ...)`
- routing messages `RTM_ADD`, `RTM_DELETE`, `RTM_GET`, and `RTM_PROPOSAL`
- interface address ioctls on IPv4/IPv6 datagram sockets

Security and correctness notes:
- The design centralizes privileged network mutations in the parent process.
- Imsg parsing performs length checks before reading variable-length sockaddr payloads.
- Added state is recorded before OS operations for cleanup coordination.
- Notable implementation quirk: `vroute_setaddr` zeroes the `mask` integer parameter before computing IPv4 masks, which makes the fallback full-length mask path always used for IPv4 in that function. This should be checked against upstream intent.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/vroute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/init/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/init/Makefile

This OpenBSD makefile builds the `init` program.

Key contents:
- `PROG= init`
- Installs/associates `init.8` man page.
- Links against `libutil` via `DPADD=${LIBUTIL}` and `LDADD=-lutil`.
- Adds `-DDEBUGSHELL -DSECURE` to `CFLAGS`, enabling alternate-shell prompt support and secure single-user password checks.
- Includes `<bsd.prog.mk>`.

Relevance:
- The compile-time flags directly enable branches in `init.c` for debug shell selection and root password validation before single-user shell access on insecure console settings.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/init/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/init/init.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/init/init.c

This is OpenBSD’s classic PID 1 implementation. It manages the system boot state machine, single-user shell, `/etc/rc`, multi-user getty sessions from `/etc/ttys`, signal-driven transitions, security level changes, and shutdown/reboot.

Key responsibilities:
- Validates it is root and PID 1, redirects stdio to `/dev/null`, opens syslog, creates an initial session, sets login to root, parses `-s` and `-f`, installs signal handlers, blocks unrelated signals, and starts the state machine in `main`.
- Defines states:
  - `single_user`
  - `runcom`
  - `read_ttys`
  - `multi_user`
  - `clean_ttys`
  - `catatonia`
  - `death`
  - `do_reboot`
  - `hard_death`
  - `nice_death`
- Provides logging helpers `stall`, `warning`, and async-safe-ish emergency logging through `emergency`.
- Handles kernel securelevel via `getsecuritylevel` and `setsecuritylevel`.
- Runs single-user mode in `f_single_user`, including console controlling-terminal setup, optional root password check under `SECURE`, optional alternate shell under `DEBUGSHELL`, shell exec fallback, and restart/transition behavior.
- Runs `/etc/rc autoboot` or `/etc/rc` in `f_runcom`; on success logs reboot and proceeds to `/etc/ttys`.
- Builds and manages session descriptors from tty entries:
  - `new_session`, `setupargv`, `construct_argv`, `free_session`
  - linked list for ordered sessions
  - RB tree keyed by process ID for child lookup
- Starts optional window systems and getty processes with resource classes in `start_window_system` and `start_getty`.
- Prevents getty thrashing with monotonic timestamp spacing and sleep backoff.
- Handles child exits in `collect_child`, clears utmp/wtmp/fbtab state, restarts gettys, or removes shutdown sessions.
- Handles SIGHUP/SIGINT/SIGTERM/SIGUSR1/SIGUSR2/SIGTSTP in `transition_handler` by setting requested state transitions.
- Enters multi-user mode in `f_multi_user`, raises securelevel to 1 if appropriate, starts all gettys, and waits/restarts children until a transition is requested.
- Re-reads `/etc/ttys` in `f_clean_ttys`, updating changed sessions, marking removed/off sessions for shutdown, and adding new sessions.
- Blocks new logins in `f_catatonia`.
- Performs shutdown flows:
  - `f_death` brings system to single-user by signaling processes.
  - `f_nice_death` runs `/etc/rc shutdown`, may request powerdown, escalates SIGHUP/SIGTERM/SIGKILL, and calls `reboot`.
  - `f_do_reboot` and `f_hard_death` set reboot/powerdown flags.

Important OS/filesystem interactions:
- Reads `/etc/ttys` through ttyent APIs.
- Executes `/etc/rc` and shell paths from `pathnames.h`/`paths.h`.
- Opens/revokes terminal devices under `/dev`.
- Updates login accounting through `logout`, `logwtmp`, `login_fbtab`, and `acct`.
- Uses `login_cap` resource classes: `daemon`, `default`.
- Calls `reboot`, `sysctl`, `kill(-1, ...)`, `waitpid`, `setsid`, `login_tty`, and secure password functions under `SECURE`.

Security and correctness notes:
- PID 1 ignores/stages signals carefully so execed children get normal dispositions.
- Secure single-user mode checks root password when console is not marked secure.
- Securelevel is lowered for single-user and raised for multi-user unless configured otherwise.
- Shutdown escalates signals with timed wait windows to avoid hanging forever on stubborn processes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/init/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/init/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/init/pathnames.h

This header supplies init-specific path definitions.

Key contents:
- Includes `<paths.h>` for standard system paths such as `_PATH_DEV`, `_PATH_DEVNULL`, `_PATH_CONSOLE`, `_PATH_BSHELL`, and `_PATH_STDPATH`.
- Defines `_PATH_RUNCOM` as `/etc/rc`.

Usage:
- `init.c` uses `_PATH_RUNCOM` for boot and shutdown script execution.
- Other standard paths from `<paths.h>` drive console, shell, device, and stdpath behavior.

Security and correctness notes:
- Centralizing `/etc/rc` here keeps boot/shutdown script path consistent across `init.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/init/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/Makefile

This OpenBSD makefile builds `ipsecctl`.

Key contents:
- `PROG= ipsecctl`
- Man pages: `ipsecctl.8` and `ipsec.conf.5`
- Sources:
  - `ike.c`
  - `ipsecctl.c`
  - `pfkey.c`
  - `pfkdump.c`
  - `parse.y`
- Adds include path for the current directory.
- Enables warning flags including strict prototypes, missing prototypes/declarations, shadowing, pointer arithmetic, cast-qual, and sign-compare.
- Includes `<bsd.prog.mk>`.

Relevance:
- The source list shows this batch includes the command front-end and IKE config generator but not the PF_KEY backend/parser files in this work item.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/ike.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/ike.c

This file converts parsed `ipsecctl` IKE rules into legacy `isakmpd` FIFO configuration commands. It supports printing generated config and adding/removing IKE/IPsec connections through `/var/run/isakmpd.fifo` or a user-specified FIFO.

Key responsibilities:
- Generates `[General]`, Phase 1, identity, Phase 2, transform, and connection sections using command prefixes understood by isakmpd:
  - `C set`
  - `C add`
  - `C rms`
  - `C rmv`
- `ike_section_general` sets dynamic-mode check intervals.
- `ike_section_peer` binds peer/default Phase 1 entries, addresses, local address, and PSK auth strings.
- `ike_section_ids` emits local/remote ID sections and supplies hostname FQDN as source ID for dynamic rules without an explicit source ID.
- `ike_section_ipsec` emits Phase 2 linkage, local/remote/NAT IDs, pf tag, and sec interface.
- `ike_section_p1` maps parsed Phase 1 exchange/auth/encryption/hash/group/lifetime options to isakmpd transform settings.
- `ike_section_p2` maps Phase 2 ESP/AH encryption/auth/group/encapsulation/lifetime options to isakmpd transform settings, including AEAD/no-auth cases.
- `ike_section_p2ids` and `ike_section_p2ids_net` generate host/subnet Phase 2 ID sections and protocol/port constraints.
- `ike_connect` adds active/dynamic rules to `Connections` and passive rules to `Passive-Connections`.
- `ike_setup_ids` derives stable Phase 1/Phase 2 section names from peer/local/src/dst/proto/ports/interface/NAT information.
- `ike_gen_config` and `ike_delete_config` generate add/delete command streams.
- `ike_print_config` writes generated commands to stdout.
- `ike_ipsec_establish` opens and validates the FIFO, wraps it in `FILE *`, and writes add/delete commands.

Important dependencies:
- Consumes `struct ipsec_rule` and transform enums from `ipsecctl.h`.
- Uses address names and masks prepared by parser/address code.
- Interacts with filesystem namespace through the isakmpd FIFO path.

Security and correctness notes:
- The FIFO is validated with `fstat` and `S_ISFIFO` before use.
- Generated section names embed addresses/protocols/ports; the code assumes parser-normalized names are safe for isakmpd command syntax.
- Unsupported transforms or illegal modes produce warnings and fail generation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/ike.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.c

This is the main `ipsecctl` command front-end. It parses command-line options, loads rules, commits them to PF_KEY or isakmpd, flushes state, shows SPD/SAD state, monitors PF_KEY, prints rules, and manages parsed rule memory.

Key responsibilities:
- `main` handles options:
  - `-c` collapse rules
  - `-D macro=value`
  - `-d` delete
  - `-f file` load rules
  - `-F` flush
  - `-i fifo` select isakmpd FIFO
  - `-k` show keys
  - `-m` monitor
  - `-n` dry run
  - `-v` verbose / extra verbose
  - `-s flow|sa|all` show state
- `ipsecctl_rules` initializes parse state, invokes `parse_rules`, commits add/delete actions unless dry-run, and frees all parsed rules.
- `ipsecctl_fopen` opens config files and rejects directories.
- `ipsecctl_commit` opens PF_KEY and dispatches each rule to either `ike_ipsec_establish` for IKE rules or `pfkey_ipsec_establish` for static PF_KEY rules.
- `ipsecctl_add_rule` queues rules and optionally prints them in verbose dry-run style.
- `ipsecctl_free_rule` frees nested address, auth, transform, lifetime, key, and generated-name allocations.
- `ipsecctl_merge_rules`, `ipsecctl_cmp_ident`, `ipsecctl_rule_matchsrc`, and `ipsecctl_rule_matchdst` implement collapsed display grouping for compatible flow rules.
- Print helpers render addresses, protocols, ports, keys, flows, SAs, bundles, and whole rules.
- `ipsecctl_flush` flushes PF_KEY-managed IPsec state unless dry-run.
- `ipsecctl_get_rules` and `ipsecctl_parse_rules` dump and parse SPD rules from `sysctl` `NET_KEY_SPD_DUMP`.
- `ipsecctl_show` dumps flows and/or SAs, pledges down after data collection, sorts SAD entries by SPI, and prints state.
- `ipsecctl_monitor` delegates to PF_KEY monitor code.
- `unmask` computes prefix length from stored masks.

Important OS interactions:
- Uses PF_KEY sysctl dumps:
  - `NET_KEY_SPD_DUMP`
  - `NET_KEY_SADB_DUMP`
- Uses PF_KEY backend functions from files outside this work item.
- Uses `pledge("stdio dns")` and then `pledge("stdio")` in show mode.
- Opens config/FIFO paths through standard file APIs.

Security and correctness notes:
- Dry-run mode avoids committing or flushing.
- `-k` can print key material, so output must be treated as sensitive.
- Rule collapse assumes sorted SPD dump order; the code explicitly notes that only comparing with the last entry depends on sorted input.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.h

This header defines the `ipsecctl` parser/runtime data model, option bits, enums, transform metadata structures, address wrappers, rule structures, queues, and cross-file function prototypes.

Key contents:
- Command option bit flags for enable/disable/noaction/verbose/show/flush/delete/monitor/showkey/collapse/showflows/showsas.
- Action enum for add/delete.
- Rule type flags:
  - `RULE_FLOW`
  - `RULE_SA`
  - `RULE_IKE`
  - `RULE_BUNDLE`
- Enums for direction, protocol/SA type, tunnel mode, ID type, flow type, auth transforms, encryption transforms, compression transforms, DH groups, IKE active/passive/dynamic mode, IKE auth method, and IKE exchange mode.
- `struct ipsec_addr` union for IPv4/IPv6/address-word views.
- `struct ipsec_addr_wrap` for address, mask, address family, name, linked entries, and source NAT.
- Rule components:
  - hosts, auth, keys, transforms, lifetimes, IKE modes
- `struct ipsec_rule` containing complete parsed rule state: addresses, local/peer, auth, transform/lifetime pointers, keys, tags, generated names, protocols, modes, ports, SPI values, interface, collapsed/bundle queue links, and bundle metadata.
- Queue heads for rule and bundle queues.
- `struct ipsecctl` parser/run state with rule number, options, and queues.
- Prototypes for parser integration, command-line macros, rule management, printing, IKE establishment, and mask setup.

Security and correctness notes:
- This is the shared ABI between parser, main command, IKE generator, and PF_KEY backend.
- The struct owns many heap pointers; cleanup must stay synchronized with parser allocation patterns and `ipsecctl_free_rule`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.h -->