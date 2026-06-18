# Group Research: group_1362_openbsd_src_sources_os_bsd_openbsd_src_sbin_dhcpleased_bpf_c_source_0a09c800bbfc

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/openbsd-src`. All source files listed in this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.c

## Purpose
`bpf.c` opens and configures `/dev/bpf` for `dhcpleased` packet capture and raw DHCP packet transmission on a specific interface.

## Main Responsibilities
- Defines a read-side BPF filter accepting IPv4 UDP packets addressed to DHCP client port 68.
- Defines a write-side BPF filter allowing DHCP client-to-server packets from UDP port 68 to port 67.
- Opens `/dev/bpf` as close-on-exec and nonblocking.
- Sets the BPF buffer length to `BPFLEN`, enables immediate mode, and configures filter-drop capture behavior.
- Installs read and write filters with `BIOCSETF` and `BIOCSETWF`.
- Attaches the BPF descriptor to the named interface with `BIOCSETIF`.
- Locks the descriptor configuration with `BIOCLOCK`.

## Important APIs
- `get_bpf_sock(const char *name)`: returns a configured BPF file descriptor for `name`, or `-1` if the interface disappeared before attachment.

## Integration Notes
The main process calls this helper in response to frontend requests, then passes the resulting descriptor back to the frontend over imsg. The frontend uses it for BPF reads and broadcast DHCP writes.

## Risk Notes
Most setup failures are fatal because an incorrectly configured BPF descriptor would break DHCP operation or filtering assumptions. `BIOCSETIF` is handled non-fatally because interfaces can legitimately disappear during startup or reconfiguration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.h

## Purpose
`bpf.h` declares the BPF socket helper used by `dhcpleased`.

## Exports
- `BPFLEN`: fixed BPF read buffer length, set to `2048`.
- `get_bpf_sock(const char *)`: opens and configures a BPF descriptor for an interface.

## Integration Notes
Included by the main process and frontend packet code. `BPFLEN` also sizes frontend per-interface BPF receive buffers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.c

## Purpose
`checksum.c` implements Internet checksum helpers for IPv4 and UDP packet validation/generation.

## Main APIs
- `checksum(uint8_t *buf, uint32_t nbytes, uint32_t sum)`: adds a buffer into an existing 16-bit one's-complement checksum accumulator, handling odd trailing bytes as high-order network-order bytes.
- `wrapsum(uint32_t sum)`: complements, masks, and returns the checksum in network byte order.

## Integration Notes
The engine uses these helpers to validate incoming IP and UDP checksums when BPF/kernel checksum flags do not say they were verified. The frontend uses them when constructing raw IPv4/UDP DHCP packets for BPF transmission.

## Risk Notes
The implementation casts byte buffers to `uint16_t *` for paired-byte reads, matching traditional BSD code but relying on platform tolerance for such access patterns.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.h

## Purpose
`checksum.h` declares the packet checksum helpers implemented in `checksum.c`.

## Exports
- `checksum(uint8_t *, uint32_t, uint32_t)`
- `wrapsum(uint32_t)`

## Integration Notes
This header assumes callers have included integer type definitions for `uint8_t` and `uint32_t`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.c

## Purpose
`control.c` implements the non-`SMALL` local UNIX-domain control socket for runtime management requests to `dhcpleased`.

## Main Responsibilities
- Creates, binds, chmods, and listens on the configured control socket path.
- Accepts nonblocking client connections and wraps each connection in an `imsgev`.
- Tracks active control clients in a `TAILQ`.
- Dispatches control imsgs for reload, verbose logging, interface info, and manual DHCP request/reboot.
- Forwards control requests to main, frontend, and engine processes as needed.
- Relays response imsgs back to the control client matching the original client pid.
- Temporarily pauses accept handling on `ENFILE`/`EMFILE`.

## Important APIs
- `control_init(char *path)`: creates and binds the control socket.
- `control_listen(int fd)`: starts listening and registers libevent handlers.
- `control_accept(...)`: accepts client connections and initializes imsg state.
- `control_dispatch_imsg(...)`: handles requests from clients.
- `control_imsg_relay(struct imsg *)`: forwards process responses back to the requesting client.

## Integration Notes
The frontend owns the control socket event loop after the main process passes the bound fd. Control actions are relayed to the main process or engine through existing frontend imsg plumbing.

## Risk Notes
Client identity for replies is tracked by imsg pid in the connection buffer; concurrent clients depend on consistent pid propagation. Malformed data payloads are ignored for that imsg rather than terminating the daemon.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.h

## Purpose
`control.h` declares the runtime control socket interface for non-`SMALL` builds.

## Exports
Under `#ifndef SMALL`, it declares:
- `control_init`
- `control_listen`
- `control_accept`
- `control_dispatch_imsg`
- `control_imsg_relay`

## Integration Notes
The header is included by main/frontend control paths and compiles to no declarations in `SMALL` builds.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.c

## Purpose
`dhcpleased.c` is the privileged main process for the DHCP client daemon. It starts the engine and frontend children, brokers file descriptors, applies interface and route configuration, writes lease files, and handles reload/shutdown orchestration.

## Main Responsibilities
- Parses command-line flags for debug, child mode, config path, no-action config check, socket path, and verbosity.
- Parses configuration in full builds and supports `-n` validation/printing.
- Enforces root execution, singleton lockfile, and `_dhcp` user availability.
- Forks/execs engine and frontend child processes with an inherited imsg fd at descriptor 3.
- Creates main-to-child and frontend-to-engine socketpairs, including fd-passing setup.
- Opens privileged route, ioctl, BPF, control, and UDP resources and passes descriptors to children.
- Sets up route-socket filters for frontend interface/proposal events.
- Applies `unveil` restrictions for config, `/dev/bpf`, and lease storage.
- Dispatches imsgs from frontend and engine.
- Configures and deconfigures IPv4 addresses via `SIOCAIFADDR` and `SIOCDIFADDR`.
- Installs and withdraws routes by writing `RTM_ADD`/`RTM_DELETE` messages with label `dhcpleased`.
- Proposes or withdraws DNS resolver state with `RTM_PROPOSAL`.
- Writes lease files atomically under `/var/db/dhcpleased/`.
- Reads existing lease files so the engine can attempt INIT-REBOOT behavior.
- Manages config reload and config transfer to frontend/engine.

## Important Control Flow
- `main()` starts as coordinator unless invoked with `-E` or `-F`, in which case it enters the engine or frontend process function.
- `main_imsg_send_ipc_sockets()` creates the direct frontend-engine imsg channel and passes one end to each child.
- `main_dispatch_frontend()` handles BPF open requests, reload/log verbosity control, and interface updates from the frontend.
- `main_dispatch_engine()` applies engine requests for interface config/deconfig, route withdrawal, and DNS proposal/withdrawal.
- `configure_interface()` adds the leased address, routes, creates a bound UDP socket for renewal unicasts, passes it to the frontend, and writes the lease file.
- `deconfigure_interface()` removes the leased address; route deletion is intentionally disabled in one code block because removing the address lets the kernel clean interface routes without breaking duplicate-gateway cases.
- `configure_routes()` classifies direct, default, and gateway routes and may install a host route to an off-subnet default gateway.
- `main_reload()` parses a new config, sends it to children, then replaces the main copy.

## Dependencies and Integration
This file ties together `bpf`, `frontend`, `engine`, `control`, route sockets, ioctl interface configuration, lease file persistence, and config parsing. It is the only process retaining the privileges needed to mutate network state and open BPF.

## Risk Notes
The main process treats invalid imsg payload shapes as fatal, which is appropriate for trusted child-process protocol integrity. Lease file support is disabled if `unveil(_PATH_LEASE)` fails. Route message construction manually pads sockaddr payloads, so correctness depends on matching kernel routing socket ABI expectations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.h

## Purpose
`dhcpleased.h` is the shared protocol and data definition header for all `dhcpleased` processes.

## Main Contents
- Paths and constants for the lockfile, default config, control socket, daemon user, route label, lease directory, lease file format, and DHCP ports.
- DHCP option codes, message type codes, hardware type constants, and DHCP header layout.
- Limits for DHCP routes, DNS proposals, ignored servers, lease buffer size, domain search length, and DHCP packet string fields.
- Shared `struct imsgev` wrapper combining `imsgbuf`, event handler, libevent object, and event mask.
- `struct dhcp_route` for destination/mask/gateway tuples.
- `enum imsg_type` defining the internal protocol among main, frontend, engine, and control clients.
- Non-`SMALL` config structures: `iface_conf`, `dhcpleased_conf`, and control reporting structure `ctl_engine_info`.
- Wire structures for config transfer, interface info, DNS proposals, DHCP packets, and DHCP send requests.
- Function prototypes shared across main, frontend, engine, parser, and printconf modules.

## Integration Notes
This header is the central contract for imsg payload sizes and semantics. Several structures are copied directly across process boundaries, so layout changes must be coordinated across all three processes.

## Risk Notes
The comment “keep in sync with iface_conf” for `imsg_iface_conf` is important: it intentionally mirrors only the fixed-size subset of interface config before variable-length DHCP option blobs are sent separately.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.c

## Purpose
`engine.c` implements the unprivileged DHCP state machine, lease interpretation, timers, and decisions about when to request, configure, renew, rebind, deconfigure, or enter IPv6-only mode.

## Main Responsibilities
- Runs as the `_dhcp` user with restricted `unveil`/`pledge`.
- Maintains a list of `dhcpleased_iface` state objects keyed by interface index.
- Receives interface state updates from the main process and DHCP packets from the frontend.
- Parses incoming Ethernet/IP/UDP/DHCP packets and validates destination MAC, IP checksum, UDP checksum, DHCP cookie, xid, and option lengths.
- Handles DHCPOFFER, DHCPACK, and DHCPNAK according to current interface state.
- Tracks lease times, renewal time, rebinding time, server identifier, requested address, subnet mask, routes, DNS servers, boot file, hostname, and domain name.
- Implements RFC 2131 retry/backoff behavior for discover/request/renew/rebind flows.
- Supports RFC 8925 IPv6-only preferred option, enforcing a minimum wait time.
- Honors config options to ignore DNS, ignore routes, ignore specific servers, and prefer IPv6.
- Sends main-process requests to configure/deconfigure addresses, withdraw routes, and propose/withdraw DNS.
- Sends frontend requests to transmit DHCPDISCOVER or DHCPREQUEST.
- Serves control-socket interface-info requests in non-`SMALL` builds.

## State Machine
States are:
- `IF_DOWN`
- `IF_INIT`
- `IF_REQUESTING`
- `IF_BOUND`
- `IF_RENEWING`
- `IF_REBINDING`
- `IF_REBOOTING`
- `IF_IPV6_ONLY`

`state_transition()` sets timers and side effects. `iface_timeout()` advances retries, renewals, rebinding, expiry, and IPv6-only wait completion.

## Packet and Option Parsing
Recognized DHCP options include message type, server identifier, lease time, subnet mask, routers, DNS servers, hostname, domain name, renewal/rebinding time, client identifier, classless static routes, and IPv6-only preferred. Classless static routes override router options per RFC 3442. Unknown options are skipped with verbose debug logging.

## Integration Notes
The engine never directly mutates the system. It sends desired actions to the privileged main process and send-packet requests to the frontend. This keeps packet parsing and lease policy mostly unprivileged.

## Risk Notes
Malformed child/main/frontend imsg protocol is fatal. Incoming network packets are handled defensively and usually logged/ignored on validation failure. `send_rdns_proposal()` logs and sends even when the nameserver list is empty; withdrawal uses a separate imsg type with count zero.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.h

## Purpose
`engine.h` declares the engine process entry point and the main-process configuration message used when applying a lease.

## Exports
- `struct imsg_configure_interface`: fixed-size payload carrying interface index, rdomain, IPv4 address, mask, next-server address, boot file, domain name, hostname, routes, and route count.
- `engine(int, int)`: starts the engine process.
- `engine_imsg_compose_frontend(int, pid_t, void *, uint16_t)`: sends an imsg from engine to frontend.

## Integration Notes
The large string buffers are sized for `vis(3)` expansion of DHCP fields before crossing process boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.c

## Purpose
`frontend.c` implements the unprivileged interface watcher and packet I/O process for `dhcpleased`.

## Main Responsibilities
- Runs as `_dhcp` with restricted `unveil`/`pledge`.
- Maintains per-interface frontend records with BPF event state, interface metadata, pending DHCP send fields, and optional UDP renewal socket.
- Receives fd-passed route, BPF, UDP, control, and frontend-engine imsg sockets.
- Discovers initial interfaces with `IFXF_AUTOCONF4` via `if_nameindex()`/`getifaddrs()`.
- Watches route socket messages for interface updates, interface departure, and DNS proposal solicit events.
- Requests BPF descriptors from the main process for autoconf-enabled interfaces.
- Reads BPF packets, validates BPF capture headers, and forwards full DHCP candidate packets to the engine.
- Builds DHCPDISCOVER and DHCPREQUEST payloads from engine requests and local config.
- Sends renewals by UDP unicast when a bound UDP socket and server address are available, falling back to BPF broadcast on failure.
- Sends broadcast packets by constructing Ethernet, IPv4, UDP, and DHCP buffers and writing them to BPF.
- Rebuilds frontend config from main-process imsgs and triggers engine reboot requests for changed interface configs.
- Relays control responses between engine/main and control clients.

## Packet Construction
`build_packet()` creates a DHCP BOOTREQUEST with cookie, message type, optional hostname, client identifier, vendor class identifier, parameter request list, requested address, and server identifier. It requests IPv6-only preferred when the interface config says `prefer ipv6`.

## Interface Tracking
`update_iface()` reacts to route `RTM_IFINFO` messages. If `IFXF_AUTOCONF4` is removed, it tells the engine to remove the interface and closes frontend state. Otherwise it updates link/running/rdomain/hardware address information and sends `IMSG_UPDATE_IF` to main.

## Integration Notes
The frontend does not open BPF itself; it asks the main process to do so and receives the descriptor. This allows privilege separation while still performing packet I/O in the unprivileged process.

## Risk Notes
`iface_conf_cmp()` treats any `NULL` hostname on either side as different, so reloads can conservatively trigger DHCP reboot behavior even when other fields are unchanged. DHCP option insertion has comments noting space checks for configured client/vendor IDs, relying on parser-enforced maximum lengths and packet buffer headroom.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.h

## Purpose
`frontend.h` declares the frontend process entry point and imsg dispatch/send helpers.

## Exports
- `frontend(int, int)`
- `frontend_dispatch_main`
- `frontend_dispatch_engine`
- `frontend_imsg_compose_main`
- `frontend_imsg_compose_engine`

## Integration Notes
The main process and control code use these helpers to send or route messages through the frontend.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.c

## Purpose
`log.c` provides `dhcpleased` logging, debug output, verbosity control, warning helpers, and fatal-exit helpers.

## Main Responsibilities
- Initializes logging to stderr in debug mode or syslog otherwise.
- Tracks process name for fatal messages.
- Tracks verbosity for debug logging.
- Preserves `errno` across logging calls.
- Provides formatted warning helpers with or without `strerror(errno)`.
- Provides fatal helpers that log and exit.

## Important APIs
- `log_init`
- `log_procinit`
- `log_setverbose`
- `log_getverbose`
- `logit`
- `vlog`
- `log_warn`
- `log_warnx`
- `log_info`
- `log_debug`
- `fatal`
- `fatalx`

## Integration Notes
All daemon processes use this module. In debug mode it appends a newline and writes to stderr; otherwise it logs through syslog.

## Risk Notes
The logging code is intentionally best-effort under allocation failure, falling back to direct `vfprintf`/separate error logging.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.h

## Purpose
`log.h` declares logging APIs and provides no-op/fallback macros for `SMALL` builds.

## Exports
In normal builds it declares logging, debug, syslog, and fatal functions with printf-format attributes. In `SMALL` builds, log calls compile to no-ops and fatal calls exit directly.

## Integration Notes
This header is included across the daemon and parser. It also includes `<stdlib.h>` so `SMALL` fatal macros can call `exit(1)`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/parse.y

## Purpose
`parse.y` implements the yacc grammar and lexer for `dhcpleased.conf`.

## Main Responsibilities
- Parses interface blocks and per-interface DHCP client options.
- Supports macros with `name = value` and `$name` expansion.
- Supports quoted strings with escapes and line continuations.
- Tracks file stack state, line numbers, unget buffers, EOF handling, and parse errors.
- Validates optional “secret” file permissions through `check_file_secrecy()`, though the main config path is pushed as non-secret.
- Builds `struct dhcpleased_conf` with `iface_conf` entries.
- Frees nonpersistent macros after parsing and warns about unused macros at high verbosity.

## Grammar Features
Supported interface options include:
- `send vendor class id STRING`
- `send client id STRING`
- `send host name STRING`
- `send no host name`
- `ignore routes`
- `ignore dns`
- `ignore STRING` for server IPv4 addresses
- `prefer ipv6`

Client ID strings are first parsed as colon-separated hex bytes including the type byte; if that fails, they are parsed as escaped text. Vendor class IDs and text client IDs are decoded with `strnunvis()` and serialized into DHCP option buffers.

## Important APIs
- `parse_config(const char *filename)`: returns a parsed config, an empty config for missing default config, or `NULL` on parse/open errors.
- `cmdline_symset(char *s)`: stores a persistent macro from `name=value`.
- `conf_get_iface(char *name)`: finds or creates an interface config.

## Integration Notes
The parser builds the same config structures later sent by the main process to frontend and engine. `printconf.c` can print the parsed config back out.

## Risk Notes
Duplicate options for the same interface are parse errors. Interface names longer than `IF_NAMESIZE` terminate via `errx`. The lexer has its own macro-expansion sentinels to avoid recursive expansion state confusion.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/printconf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/printconf.c

## Purpose
`printconf.c` prints a parsed `dhcpleased_conf` back as configuration text, used for config validation/inspection.

## Main Responsibilities
- Converts stored DHCP option buffers for vendor class ID and client ID into config statements.
- Prints host-name behavior, ignore flags, ignored servers, and `prefer ipv6`.
- Escapes text option values using `strvisx()`.
- Prints Ethernet-style client IDs as colon-separated hex.

## Important APIs
- `print_config(struct dhcpleased_conf *)`
- `print_dhcp_options(char *indent, uint8_t *p, int len)`

## Integration Notes
Used by `dhcpleased -n -v` after parsing. It expects option buffers shaped by `parse.y`.

## Risk Notes
Unknown DHCP option buffers are fatal, which is acceptable because this printer is only intended for the limited options generated by the parser.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/printconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/Makefile

## Purpose
This Makefile builds the OpenBSD `disklabel` utility.

## Main Contents
- Sets `PROG=disklabel`.
- Builds sources `disklabel.c`, `dkcksum.c`, `editor.c`, and generated `manual.c`.
- Links against `libutil`.
- Installs manuals `disklabel.8` and `disklabel.5`.
- Generates `manual.c` from the rendered `disklabel.8` manual compressed through gzip and emitted as a C byte array.
- Provides a `NOMAN` fallback that embeds compressed text saying `no manual`.
- Adds sparc64-specific `SUN_CYLCHECK` and `SUN_AAT0` compile definitions.

## Integration Notes
`manual.c` is a generated build artifact consumed by the interactive editor/manual path outside the listed files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/disklabel.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/disklabel.c

## Purpose
`disklabel.c` implements the command-line `disklabel` utility for reading, displaying, editing, restoring, validating, and writing OpenBSD disk labels.

## Main Responsibilities
- Parses command modes: read, write, restore, edit through text editor, and interactive editor.
- Opens the target disk device with `opendev()`.
- Reads current or prototype labels through disklabel ioctls.
- Supports auto-allocation and autotable parsing through helper functions from other disklabel modules.
- Reads mountpoint hints from fstab by device name or DUID.
- Displays labels in human-readable or disktab format.
- Writes labels through `DIOCWDINFO` after setting magic values and checksum.
- Restores labels from text prototype files.
- Edits labels by writing a temp file, invoking `$VISUAL`/`$EDITOR`/vi, reparsing, and writing if changed.
- Parses ASCII label text generated by `display()`.
- Validates geometry, partition count, partition bounds, and selected architecture-specific constraints.
- Handles DUID parsing and unit scaling for output.

## Important APIs and Functions
- `main()`: option parsing, pledge selection, operation dispatch.
- `readlabel(int f)`: obtains active/prototype disklabel data with `DIOCGDINFO`, `DIOCGPDINFO`, and optional `DIOCRLDINFO`.
- `writelabel(int f, struct disklabel *lp)`: computes checksum, writes via `DIOCWDINFO`, refreshes UID, and saves mountpoints.
- `display()` / `display_partition()`: print label geometry and partition table.
- `makedisktab()`: emit a disktab-style label.
- `edit()` / `editit()`: temp-file edit loop and editor execution.
- `getasciilabel()`: parse displayed text back into a `struct disklabel`.
- `checklabel()`: validate required geometry and partition extents.
- `cmplabel()`: compare labels while ignoring magic, checksum, and bound fields.

## Integration Notes
This file depends on helper modules and headers not in this group, including `editor.c`, mountpoint helpers, display/editor support declarations in `extern.h`, `pathnames.h`, and kernel disklabel definitions. It is a userland front end around disklabel ioctls.

## Risk Notes
This is a disk-mutating administrative tool; write and restore paths are guarded by validation but still operate directly on kernel disklabel state. The editor path executes through the shell to allow editor flags, so it relies on trusted local environment variables.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/disklabel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/dkcksum.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/dkcksum.c

## Purpose
`dkcksum.c` computes the OpenBSD disklabel checksum.

## Main API
- `dkcksum(const struct disklabel *lp)`: XORs 16-bit words from the start of the disklabel through the configured partition array end, using `d_npartitions` to determine the endpoint.

## Integration Notes
`disklabel.c` sets `d_checksum` to zero, calls `dkcksum()`, then writes the resulting checksum before issuing `DIOCWDINFO`.

## Risk Notes
The checksum covers only partitions up to `d_npartitions`; callers must ensure `d_npartitions` is valid before computing/writing the label.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/dkcksum.c -->