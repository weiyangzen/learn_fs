# subset-b-009795 Research

Grouped research for the requested rpcbind and s3fs-fuse files. Each section is source-path aligned for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_svc_com.c -->
# sources/user-network-fs/rpcbind/src/rpcb_svc_com.c

Purpose: Implements rpcbind's shared server-side procedures for RPCBIND versions 3 and 4, plus portmap compatibility support when compiled with `PORTMAP`. It owns the main mutable registration database operations, address lookup behavior, remote-call forwarding, and the custom polling loop used to service both normal RPC requests and forwarded datagram replies.

Important APIs, types, and functions: Public entry points declared in `rpcbind.h` include `rpcbproc_set_com`, `map_set`, `rpcbproc_unset_com`, `map_unset`, `delete_prog`, `rpcbproc_getaddr_com`, `rpcbproc_gettime_com`, `rpcbproc_uaddr2taddr_com`, `rpcbproc_taddr2uaddr_com`, `create_rmtcall_fd`, `rpcbproc_callit_com`, and `my_svc_run`. Internal state includes `list_rbl`, the global linked list of `RPCBLIST` mappings; optional `list_pml` portmap mappings; `rmtcallfd_list` for per-netid forwarding descriptors; and `FINFO[NFORWARD]`, a 64-slot table correlating original caller XIDs with forwarded XIDs.

Control flow: SET requests call `map_set`, reject conflicting existing registrations, allocate a new `RPCBLIST`, append it to `list_rbl`, and optionally mirror it to `list_pml`. UNSET requests call `map_unset`, match program/version/netid, enforce ownership, unlink matched nodes, and optionally delete compatible portmap entries. GETADDR locates a registered service by program/version/current transport, calls `mergeaddr` to return an address appropriate to the caller, and removes stale programs if address probing indicates the server died. UADDR/TADDR helpers translate via the current transport's `netconfig`.

Remote-call flow: `rpcbproc_callit_com` accepts only datagram transports. It decodes encapsulated remote-call arguments, applies `check_callit`, finds the target service, optionally validates it for indirect RPCB v4 calls, computes local and caller-facing universal addresses with `addrmerge`, registers the forwarded XID in `FINFO`, marshals the forwarded call with AUTH_NULL or AUTH_SYS credentials, and sends it through the per-netid forwarding fd. `my_svc_run` copies `svc_pollfd`, polls, checks forwarding fds first via `check_rmtcalls`, and then dispatches remaining normal RPC descriptors with `svc_getreq_poll`. `handle_reply` decodes the service reply, finds the original caller by forwarded XID, rewrites the `SVCXPRT` caller/XID, wraps the service result with the selected address/port result format, and frees the forwarding slot.

State and persistence: The authoritative runtime state is in-memory: `list_rbl`, optional `list_pml`, `rmthead/rmttail`, `rpcb_rmtcalls`, and `FINFO`. Persistence is not performed here directly; `warmstart.c` serializes `list_rbl`/`list_pml` on shutdown. Static reply buffers such as `uaddr` and `taddr` are reused between calls and freed/replaced on each invocation, which is acceptable for the single-threaded service loop assumption but would be fragile if the dispatcher became concurrent.

Dependencies and integration points: Depends heavily on libtirpc internals such as `__rpcb_get_dg_xidp`, `__rpc_fd2sockinfo`, `svc_pollfd`, `svc_max_pollfd`, `svc_getrpccaller`, and `svc_tli_create`. It integrates with `security.c` for indirect-call filtering, `util.c` for address merging/local address selection, `rpcbind.c` for initial self-registrations and rmtcall fd creation, stats functions such as `rpcbs_set`/`rpcbs_getaddr`/`rpcbs_rmtcall`, and optional portmap conversion helpers.

Risks: `map_unset` returns failure immediately if the first matching registration is owned by someone else, which can prevent later matching registrations from being considered. `delete_prog` mutates the list while iterating by calling `map_unset`, a pattern that is easy to break. The 64-slot forwarding table is bounded and expires stale entries only during new registrations. Several paths allocate strings or netbufs and rely on precise cleanup at `error`/`out` labels. The code uses libtirpc private structures and global service arrays, so ABI changes are a portability risk. Address parsing for PMAP reply conversion assumes dotted IPv4 universal address format.

Test signals: Exercise SET/UNSET ownership for root, non-root local clients, duplicate registration, conflicting registration, and wildcard netid removal. Test GETADDR for stale services, multi-homed hosts, version mismatch, and empty-hint behavior. For RMTCALLS, test duplicate forwarded requests, timeout slot reuse, AUTH_SYS propagation, forbidden program/procedure denial, and v3/v4 reply formatting. Regression tests should include builds with and without `PORTMAP`, `RMTCALLS`, and IPv6.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_svc_com.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcbind.c -->
# sources/user-network-fs/rpcbind/src/rpcbind.c

Purpose: Main daemon implementation for rpcbind. It parses daemon options, enforces singleton execution, initializes transports from netconfig and optional systemd sockets, registers rpcbind/portmap service versions, drops privileges, restores warm-start data, initializes network helpers, and enters the RPC service loop.

Important APIs, types, and functions: Public daemon globals include `debugging`, `doabort`, `dofork`, `createdsocket`, `list_rbl`, `list_pml`, `runasdaemon`, `insecure`, `oldstyle_local`, `verboselog`, `hosts`, `nhosts`, and `rpcbindlockfd`. Core functions are `main`, `init_transport`, `rbllist_add`, `terminate`, `rpcbind_abort`, `parseargs`, `reap`, and `toggle_verboselog`. Optional integrations are gated by `SYSTEMD`, `PORTMAP`, `WARMSTART`, `LIB_SET_DEBUG`, `RPCBIND_USER`, and `NSS_MODULES`.

Control flow: `main` parses `-adfh:ilsvw`, obtains `/run/rpcbind.lock` with `flock`, raises `RLIMIT_NOFILE` to at least 128, requires effective root, configures service NSS lookup, opens netconfig, initializes local/unix transport first, then all visible netconfig transports. It installs signal handlers, daemonizes unless `-f`, optionally drops to `daemon` or configured `RPCBIND_USER`, reads warm-start state when requested, runs `network_init`, notifies systemd readiness, and calls `my_svc_run`.

Transport setup: `init_transport` filters unsupported transport semantics, derives socket info, then tries systemd socket activation if enabled. A matching systemd fd must match address family, socket type, and protocol; IPv6 sockets must already be `IPV6_V6ONLY`. Without systemd, local/unix sockets are bound at `_PATH_RPCBINDSOCK`, while network sockets are bound to configured `-h` hosts plus loopback for datagram transports. It registers PMAP v2 when applicable, RPCB v3 and v4 via `svc_reg`, adds self mappings to `list_rbl`, tracks bindability with `add_bndlist`, and optionally creates remote-call forwarding fds for datagram transports.

State and persistence: Runtime registrations are stored in `list_rbl` and optional `list_pml`; self-registrations are added during initialization and warm-start data later appends non-rpcbind entries. The lock file and unix socket are cleaned in `terminate`; warm-start is written in `terminate` and `rpcbind_abort` when compiled with `WARMSTART`. `createdsocket` tracks whether this process created the local socket so it can unlink it.

Dependencies and integration points: Relies on libtirpc service creation/registration APIs, `/etc/netconfig`, `getaddrinfo`, systemd `sd_listen_fds`/`sd_notify`, NSS lookup configuration, privilege APIs (`setgid`, `setgroups`, `setuid`), `warmstart.c`, `rpcb_svc_com.c`, portmap service code, and `security.c` globals. The systemd unit in this subset passes `-f` and socket-activates the daemon.

Risks: The daemon must start as root and bind privileged ports before dropping privileges; failures before privilege drop are fatal. Host-specific binding mutates the `hosts` array by replacing `"*"` with `NULL`, which is subtle. Systemd dual-stack sockets are explicitly rejected, so unit/socket configuration must stay aligned with code expectations. Some error paths close `fd` after `svc_tli_create` may have taken ownership. The lock file mode is read-only and cleanup unlinks it; stale locks are handled by `flock`, not file existence.

Test signals: Validate command-line parsing, singleton lock behavior, root requirement, binding to local, IPv4, IPv6, and host-restricted addresses, systemd socket activation with separate IPv4/IPv6 sockets, privilege drop to configured user, warm-start restore ordering, and clean termination unlink/write behavior. Build matrix should cover `SYSTEMD`, `PORTMAP`, `WARMSTART`, and IPv6 feature combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcbind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcbind.h -->
# sources/user-network-fs/rpcbind/src/rpcbind.h

Purpose: Shared rpcbind header defining common request structures, daemon globals, service entry points, security hooks, warm-start hooks, and utility APIs used across the rpcbind daemon, service dispatchers, compatibility code, and helper modules.

Important APIs, types, and functions: Defines `encap_parms` and `r_rmtcall_args` for remote-call forwarding, including target program/version/procedure, local reply version, target universal address, and opaque argument payload. Declares global daemon flags (`debugging`, `doabort`, `verboselog`, `insecure`, `oldstyle_local`), the RPCB v3/v4 registration list `list_rbl`, and optional PORTMAP globals. Function groups include bind tracking (`add_bndlist`, `is_bound`), address merging (`mergeaddr`, `addrmerge`), RPCB stats, v3/v4 services, shared RPC procedures, event loop, abort/reap/log toggles, access checks, warm-start persistence, and network initialization.

Control flow and integration: The header links `rpcbind.c` startup with `rpcb_svc_com.c` request implementations, `security.c` access policy, `util.c` address selection, `warmstart.c` state persistence, version-specific RPC service files, and optional portmap service support. `RPCB_ALLVERS` and `RPCB_ONEVERS` define the semantic selector for GETADDR-style version matching.

State and persistence: The header exposes global mutable state rather than encapsulating it. Persistence-related declarations are limited to warm-start directory creation plus read/write functions; the actual serialized format and file paths live in `warmstart.c`.

Dependencies: Includes `<rpc/rpcb_prot.h>` and optionally `<rpc/pmap_prot.h>`, so consumers need libtirpc/SunRPC headers and the build-time feature macros that match the daemon configuration.

Risks: Wide global declarations make ordering and ownership implicit. Several functions return static storage or allocated strings depending on implementation, so callers must follow module-specific conventions. The conditional `PORTMAP` declarations change ABI expectations across builds.

Test signals: Header-level validation is compile/link coverage across feature combinations. Important tests are full daemon builds with and without `PORTMAP`, `WARMSTART`, `RMTCALLS`, and IPv6, because this header is the contract connecting those modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcbind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcinfo.c -->
# sources/user-network-fs/rpcbind/src/rpcinfo.c

Purpose: Implements the `rpcinfo` diagnostic CLI for dumping rpcbind/portmap registrations, pinging RPC services, broadcasting NULLPROC probes, deleting registrations, querying address lists, and printing rpcbind statistics.

Important APIs, types, and functions: Mode constants identify PMAP dump, TCP/UDP ping, broadcast, deletion, address ping, program ping, RPCB dump, short dump, address list, and stats. Core functions include `main`, `local_rpcb`, `ip_ping`, `pmapdump`, `ip_getclient`, `brdcst`, `rpcbdump`, `rpcbaddrlist`, `rpcbgetstat`, `deletereg`, `clnt_addr_create`, `addrping`, `progping`, `clnt_rpcbind_create`, `getclnthandle`, `pstatus`, `print_rmtcallstat`, and `print_getaddrstat`. Short dump aggregation uses `rpcbdump_short`, `verslist`, and `netidlist`.

Control flow: `main` parses mutually exclusive options and selects a function; no option defaults to a full RPCB dump or program ping depending on argument count. Local operations use AF_LOCAL `_PATH_RPCBINDSOCK` and optionally an abstract socket. Remote rpcbind clients are created over preferred nettype families (`circuit_n`, `circuit_v`, `datagram_v`) or an explicit netid. Ping modes issue NULLPROC calls, infer supported version ranges from `RPC_PROGVERSMISMATCH`, then iterate versions. Dump modes call `RPCBPROC_DUMP`, fall back to RPCB v4 or PMAP v2 when needed, and print long or grouped output. Stats mode calls `RPCBPROC_GETSTAT` and prints per-version counts plus getaddr/rmtcall breakdowns.

State and persistence: The tool keeps only process-local transient client handles, converted linked lists returned by RPC calls, and formatting aggregation lists. It does not persist state, but `deletereg` changes daemon state by calling `rpcb_unset`.

Dependencies and integration points: Depends on libtirpc client APIs, rpcbind/portmap protocols, `/etc/rpc` lookups via `getrpcbyname`/`getrpcbynumber`, netconfig/nettype iteration, local rpcbind socket paths, and standard resolver APIs. It is both a test/debug client for `rpcbind.c`/`rpcb_svc_com.c` and an administrative tool that can remove mappings.

Risks: The file forces `PORTMAP` on, so code paths assume portmap headers and APIs. Several operations call `exit` from helper functions, which simplifies CLI flow but complicates library reuse. Version probing can loop over very large ranges if a server accepts version 0 and MAX_VERS. Some fallback PMAP conversion allocates mixed static and heap strings. `SUN_LEN_A` handles abstract sockets with Linux-specific semantics.

Test signals: CLI tests should cover invalid/mutually exclusive options, local and remote dumps, v3/v4 fallback, PMAP fallback, explicit netid handling, direct address ping, program ping with known and unknown versions, broadcast output, deletion failure/success, and stats output formatting. Mock or containerized rpcbind instances are useful because many branches depend on real RPC error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/security.c -->
# sources/user-network-fs/rpcbind/src/security.c

Purpose: Centralizes rpcbind access control, caller locality checks, verbose audit logging, and remote-call deny rules for sensitive RPC programs/procedures.

Important APIs, types, and functions: Exports `check_access`, `is_loopback`, `is_localroot`, `logit`, and `check_callit`. It defines constants for sensitive NFS, mountd, YP, ypbind, yppasswd, and rquota programs/procedures. With `LIBWRAP`, it integrates TCP wrappers through `request_info`, `hosts_access`, and severity globals. Logging severity defaults to auth/info for normal verbose logs and auth/warning for denials.

Control flow: `check_access` inspects the RPC procedure and denies SET/UNSET from non-loopback callers unless `insecure` is set. Other procedures pass this local-only gate. It then applies TCP wrappers for non-AF_LOCAL callers when enabled. Verbose logging records accepted and denied requests via `logit`. `check_callit` allows NULLPROC, denies indirect calls to rpcbind unless insecure, denies selected mountd/YP/NFS/rquota operations, and logs denial.

State and persistence: No persistent state. It reads global runtime options `insecure`, `oldstyle_local`, `debugging`, and `verboselog`. `logit` forks for syslog work so DNS/RPC name lookup does not block the daemon; `reap` in `rpcbind.c` collects those children.

Dependencies and integration points: Consumes caller addresses from `svc_getrpccaller`, depends on `rpcbind.h` request structures, uses `xlog` for debug, and integrates with the shared service code that calls access checks before serving procedures. Local-root behavior relies on AF_LOCAL or loopback with reserved source ports when `oldstyle_local` is enabled.

Risks: `oldstyle_local` disables IPv4/IPv6 loopback recognition when false but always treats AF_LOCAL as local. Reserved source port checks are legacy trust signals and should not be treated as strong authentication. `logit` forks per event, so verbose logging under high traffic can create process churn. TCP wrappers only see socket addresses and are bypassed for AF_LOCAL.

Test signals: Test SET/UNSET from AF_LOCAL, IPv4 loopback, IPv6 loopback, and remote addresses with `insecure` on/off and `oldstyle_local` on/off. Test `check_callit` deny matrix for NFS, mountd mount/unmount, ypbind setdom, selected YP calls, and rpcbind self-calls. With `LIBWRAP`, use allow/deny fixtures and verify log severity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/util.c -->
# sources/user-network-fs/rpcbind/src/util.c

Purpose: Provides network address utilities for rpcbind, primarily selecting the best server universal address for a caller on multi-homed systems and caching local RPC service addresses for remote-call forwarding.

Important APIs, types, and functions: Public functions are `addrmerge`, `network_init`, and `local_sa`. Internal helpers/macros include `bitmaskcmp`, `SA2SIN`, `SA2SINADDR`, and IPv6 variants. Static state stores `local_in4` and optional `local_in6`.

Control flow: `addrmerge` converts the caller and optional client hint universal address to transport addresses, treats local callers as direct-return cases, enumerates interfaces with `getifaddrs`, finds an exact or same-network interface matching the hint/caller family, copies that interface address, replaces its port with the registered service port, and converts it back to a universal address. `network_init` resolves local `sunrpc` IPv4/IPv6 addresses and, for IPv6 builds, joins the RPC multicast group on multicast-capable interfaces. `local_sa` returns the cached local address for a family.

State and persistence: Local address pointers are allocated during `network_init` and retained for daemon lifetime. No disk persistence. The selected addresses affect `rpcbproc_callit_com` forwarding behavior and `mergeaddr` semantics indirectly.

Dependencies and integration points: Depends on libtirpc address conversion (`taddr2uaddr`, `uaddr2taddr`, `rpcbind_get_conf`), POSIX `getifaddrs`, IPv4/IPv6 socket structures, `getaddrinfo`, and multicast socket operations. It is used by GETADDR/GETADDRLIST-style resolution and remote-call forwarding paths.

Risks: Interface selection relies on netmask comparisons and first/up interface heuristics; unusual routing, point-to-point interfaces, containers, or missing netmasks may produce surprising addresses. `network_init` does not free `local_in4/local_in6` during normal daemon lifetime. `addrmerge` has family-specific size handling and assumes service universal address conversion succeeds before port copy.

Test signals: Test callers from loopback, same subnet, different subnet, IPv6 link-local with scope id, explicit hint address, and local/unix addresses. Exercise hosts with multiple interfaces and point-to-point/loopback preferences. For IPv6, validate multicast join attempts are non-fatal and local_sa returns usable data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/warmstart.c -->
# sources/user-network-fs/rpcbind/src/warmstart.c

Purpose: Implements warm-start persistence for rpcbind registrations by writing and reading XDR-encoded registration lists under `RPCBIND_STATEDIR`.

Important APIs, types, and functions: Public functions are `mkdir_warmstart`, `write_warmstart`, and `read_warmstart`. Internal helpers `write_struct` and `read_struct` serialize or deserialize arbitrary XDR list structures. Files are `rpcbind.xdr` for `list_rbl` and, with `PORTMAP`, `portmap.xdr` for `list_pml`.

Control flow: `write_warmstart` ensures the state directory exists and writes `list_rbl` plus optional `list_pml`. `read_warmstart` decodes temporary lists, appends non-rpcbind registrations to the current in-memory lists, and discards stale self-registrations so current transport setup remains authoritative. `read_struct` unlinks the state file after success or non-ENOENT failure, making warm-start files one-shot recovery inputs.

State and persistence: This is the daemon's on-disk persistence layer. Files are written with `umask(077)` to restrict permissions. `mkdir_warmstart` creates the directory with mode 0770 and attempts to chown it to the post-drop user via an `O_DIRECTORY | O_NOFOLLOW` fd.

Dependencies and integration points: Depends on global `list_rbl` and optional `list_pml`, XDR routines `xdr_rpcblist_ptr` and `xdr_pmaplist_ptr`, `RPCBIND_STATEDIR`, and daemon shutdown/abort paths in `rpcbind.c`.

Risks: Files are opened with `fopen("w")`, not an atomic temp-and-rename sequence, so crashes can leave partial XDR. The fallback that closes fds 0 through 9 before retrying write is unusual and could affect diagnostics. Directory creation and chown errors are logged but not fatal. Warm-start data may still be stale for services that did not survive daemon restart; later GETADDR cleanup handles some stale entries.

Test signals: Validate write/read round trips for RPCB and PMAP lists, absence of files, corrupt XDR files, directory creation with expected ownership, one-shot unlink behavior, and filtering of RPCBPROG/PMAPPROG self-registrations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/warmstart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.c -->
# sources/user-network-fs/rpcbind/src/xlog.c

Purpose: Provides rpcbind's lightweight logging backend with syslog/stderr selection, debug facility masks, signal-triggered debug toggling, and fatal-error helpers.

Important APIs, types, and functions: Implements `xlog_open`, `xlog_stderr`, `xlog_syslog`, `xlog_config`, `xlog_sconfig`, `xlog_enabled`, `xlog_backend`, `xlog`, `xlog_warn`, `xlog_err`, and `xlog_errno`. Internal state includes `log_stderr`, `log_syslog`, `logging`, `logmask`, `log_name`, and `log_pid`. `debugnames` maps strings such as `general`, `call`, `auth`, `parse`, and `all` to debug masks.

Control flow: `xlog_open` initializes syslog identity, captures program name/pid, and installs SIGUSR1/SIGUSR2 handlers. Config functions update masks and enable debug logging. `xlog_backend` filters non-severity debug records unless enabled, writes to syslog at severity-derived priorities, writes to stderr with optional timestamp format, and exits on `L_FATAL`. Wrapper functions package variadic arguments and choose severity.

State and persistence: Logging state is process-global and mutable at runtime via config functions and signals. No disk persistence beyond syslog/stderr destinations. `export_errno` is set for selected error/general logs and exported through `xlog.h`.

Dependencies and integration points: Used by rpcbind daemon and helpers for debug/error reporting. It depends on POSIX signal APIs, syslog, stdio, and `va_list` handling.

Risks: Signal handlers call `xlog`, which is not async-signal-safe because it may use syslog, stdio, and allocation-like library internals. `xlog_backend` uses one `va_list` for syslog and a copied one for stderr, which is correct only because copying occurs before consuming. Facility/severity exact `switch` cases mean combined flags may fall to default behavior.

Test signals: Unit-style tests can validate mask enable/disable behavior, string facility parsing, syslog/stderr toggles, warning/error/fatal routing, and that `xlog_enabled` tracks runtime configuration. Signal behavior is best covered by integration tests because of process exit and handler side effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.h -->
# sources/user-network-fs/rpcbind/src/xlog.h

Purpose: Declares logging severity/debug masks, the debug facility name mapping structure, and the xlog API used by rpcbind source files.

Important APIs, types, and functions: Defines severity masks `L_FATAL`, `L_ERROR`, `L_WARNING`, `L_NOTICE`, and `L_ALL`, plus debug masks `D_GENERAL`, `D_CALL`, `D_AUTH`, `D_FAC3` through `D_FAC7`, `D_PARSE`, and `D_ALL`. Declares `struct xlog_debugfac`, `export_errno`, and all xlog functions.

Control flow and integration: Callers open the logging system with `xlog_open`, choose stderr/syslog outputs, enable facilities with numeric or string config functions, check debug state with `xlog_enabled`, and log through severity wrappers. `xlog_err` and `xlog_errno` are fatal through the implementation.

State and persistence: The header exposes only `export_errno`; all other state is internal to `xlog.c`. No persistence contract.

Dependencies: Requires `<stdarg.h>` because `xlog_backend` accepts a `va_list`.

Risks: The comment warns that callers should not OR debug and severity classes together; the numeric layout makes misuse possible. `L_FATAL` exits, so using it in reusable or cleanup-sensitive code changes process control flow.

Test signals: Compile coverage plus runtime tests for each macro class and wrapper function. Static analysis can catch accidental OR combinations or fatal wrapper use in paths expected to return.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.service.in -->
# sources/user-network-fs/rpcbind/systemd/rpcbind.service.in

Purpose: Template for the systemd service unit that runs rpcbind under socket activation with hardening and optional warm-start/configuration substitutions.

Important directives: `DefaultDependencies=no`, `RequiresMountsFor=@statedir@`, `Requires=rpcbind.socket`, `Wants=rpcbind.target systemd-tmpfiles-setup.service`, and `After=systemd-tmpfiles-setup.service` align service startup with state directory preparation and the socket unit. `Type=notify` matches `sd_notify(READY=1)` in `rpcbind.c`. `ExecStart=@_sbindir@/rpcbind $RPCBIND_OPTIONS @warmstarts_opt@ -f` runs rpcbind in foreground for systemd supervision.

Control flow and integration: systemd starts or activates `rpcbind.socket` first, passes sockets to the daemon, reads optional environment files from `/etc/rpcbind.conf`, `/etc/default/rpcbind`, and `/etc/sysconfig/rpcbind`, then waits for notify readiness. The daemon's systemd socket handling expects separate IPv4/IPv6 sockets and foreground execution.

State and persistence: `RequiresMountsFor=@statedir@` ensures warm-start state storage is mounted before service start. Environment files can change daemon behavior via `RPCBIND_OPTIONS`.

Dependencies and security: Hardening directives include `ProtectSystem=full`, `ProtectHome=true`, `PrivateDevices=true`, hostname/clock/kernel/control-group protections, and `RestrictRealtime=true`. These reduce daemon access but must still allow configured state directory and socket operations.

Risks: Template substitutions must provide valid `@statedir@`, `@_sbindir@`, and `@warmstarts_opt@`. Overly restrictive hardening can break warm-start or platform-specific needs if state paths are not covered. Environment files are optional, so missing files are non-fatal.

Test signals: Validate generated unit with `systemd-analyze verify`, start with socket activation, confirm `READY=1`, verify warm-start path access, and test environment-file option propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.service.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket -->
# sources/user-network-fs/rpcbind/systemd/rpcbind.socket

Purpose: Concrete systemd socket unit for rpcbind activation on the local unix socket and TCP/UDP port 111 for IPv4 and IPv6.

Important directives: `ListenStream=/run/rpcbind.sock` creates the filesystem unix socket. `BindIPv6Only=ipv6-only` ensures IPv6 sockets are not dual-stack. `ListenStream` and `ListenDatagram` bind `0.0.0.0:111` and `[::]:111`. The unit wants and starts before `rpcbind.target` and installs under `sockets.target`.

Control flow and integration: systemd owns the listening sockets and passes them to `rpcbind.c` through `sd_listen_fds`. The daemon matches each fd against netconfig transport properties and rejects IPv6 dual-mode sockets, so `BindIPv6Only=ipv6-only` is required.

State and persistence: The unit owns socket lifetime while active; no persistent state. The commented abstract unix socket line is disabled in this concrete file.

Dependencies and risks: Requires privileges to bind port 111 and create `/run/rpcbind.sock`. If a distribution modifies IPv6 binding semantics or removes separate sockets, daemon startup can fail. Because it binds wildcard addresses, exposure is controlled by daemon access policy and network firewalls.

Test signals: Use `systemd-analyze verify`, `systemctl start rpcbind.socket`, inspect listening sockets for stream/datagram IPv4 and IPv6 plus unix socket, and confirm daemon activation works for local and network clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket.in -->
# sources/user-network-fs/rpcbind/systemd/rpcbind.socket.in

Purpose: Template version of the rpcbind systemd socket unit, adding conditional support for an abstract unix socket while otherwise matching the concrete socket unit.

Important directives: Same as `rpcbind.socket`, with `@ABSTRACT_TRUE@ListenStream=@/run/rpcbind.sock` allowing configure-time inclusion of the abstract socket. It sets `BindIPv6Only=ipv6-only` and binds stream/datagram sockets on IPv4 and IPv6 port 111.

Control flow and integration: Generated unit must align with daemon socket matching in `rpcbind.c`. Abstract socket support also aligns with `rpcinfo.c` local probing when `_PATH_RPCBINDSOCK_ABSTRACT` is defined.

State and persistence: No persistent state; generated content depends on configure substitution.

Risks: Incorrect `@ABSTRACT_TRUE@` substitution can leave invalid unit syntax or omit expected abstract socket support. Like the concrete unit, wildcard port 111 exposure depends on daemon policy and firewalling.

Test signals: Verify both generated variants, with and without abstract socket support. Confirm `rpcinfo` can connect via local socket and that daemon startup does not warn about dual-stack IPv6 sockets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/dependabot.yml -->
# sources/user-network-fs/s3fs-fuse/.github/dependabot.yml

Purpose: Configures Dependabot updates for GitHub Actions used by the s3fs-fuse repository.

Important fields: Uses Dependabot config version 2 with one update entry for `package-ecosystem: "github-actions"`, `directory: "/"`, and a monthly schedule.

Control flow and integration: GitHub reads this file outside the build. It affects workflow dependency freshness, especially actions such as `actions/checkout`.

State and persistence: No runtime state. Dependabot opens pull requests according to the schedule.

Dependencies and risks: Only GitHub Actions dependencies are covered; container image tags, OS packages, curl direct binary versions, and autotools/library versions are not managed here. Monthly cadence reduces churn but may delay security fixes.

Test signals: GitHub Dependabot UI should show the config as valid. Changes are validated by observing generated update PRs and CI behavior on those PRs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/ci.yml -->
# sources/user-network-fs/s3fs-fuse/.github/workflows/ci.yml

Purpose: Defines the s3fs-fuse CI pipeline across Linux containers, macOS, memory/sanitizer lanes, and static analysis lanes.

Important jobs and controls: Triggered by push, pull request, and weekly Sunday cron. The Linux job runs a broad container matrix including Ubuntu, Debian, Rocky Linux, Fedora, openSUSE, and Alpine with privileged FUSE access. The macOS job uses fuse-t and Homebrew packages. MemoryTest covers glibc debug, address/undefined/thread sanitizers, thread-safety warnings, and Valgrind on Fedora. `static-checks` builds and runs clang-tidy, cppcheck, and shellcheck.

Control flow: Linux containers install pre-checkout prerequisites where needed, check out with `actions/checkout@v6`, run `.github/workflows/linux-ci-helper.sh` to install OS packages and export configure options, then run `./autogen.sh`, `./configure`, `make`, and test suites. Memory lanes set `CXX`, `CXXFLAGS`, sanitizer options, valgrind options, and S3 test URL via `$GITHUB_ENV` before build/test.

State and persistence: CI state is ephemeral container or runner state. The workflow relies on privileged runners with `/dev/fuse` and on `$GITHUB_ENV` to pass helper-derived variables across steps.

Dependencies and integration points: Integrates with autotools files (`autogen.sh`, `configure.ac`, Makefiles), test directories, the Linux helper script, FUSE kernel support, Homebrew fuse-t, and static analyzers. It is the main executable test signal for the s3fs subset.

Risks: Container tags reference future/current distro versions and may break as images or package names change. Privileged FUSE access may be constrained by hosted runner policy. `actions/checkout@v6` availability must align with GitHub Actions release state. Some sanitizer settings alter kernel sysctl values inside privileged containers.

Test signals: The workflow itself runs build, unit tests, integration tests, static analysis, sanitizers, and Valgrind. For edits to build scripts or cache/header code, passing Linux, macOS, static-checks, and relevant MemoryTest lanes is the strongest signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/linux-ci-helper.sh -->
# sources/user-network-fs/s3fs-fuse/.github/workflows/linux-ci-helper.sh

Purpose: OS-specific CI helper that installs packages inside Linux matrix containers and exports compiler/configure environment for later workflow steps.

Important APIs and variables: Accepts exactly one container name like `ubuntu:24.04` or `fedora:44`. Sets defaults `CXX=g++`, `CXXFLAGS=-O`, `LDFLAGS=`, and `CONFIGURE_OPTIONS="--prefix=/usr --with-openssl"`. Defines package manager commands, install options, package arrays, optional repository options, optional `--allowerasing`, and `CURL_DIRECT_INSTALL`. Direct curl install uses a pinned static-curl URL and architecture-specific SHA256.

Control flow: The script parses OS name/version, selects an exact branch for supported containers, updates package metadata, installs packages, prints Java version, optionally downloads/verifies/replaces `/usr/local/bin/curl` for older distributions, prints curl version, then appends environment variables to `$GITHUB_ENV`.

State and persistence: Mutates the running container by installing packages and possibly installing `/usr/local/bin/curl` plus a certificate symlink. Persists build variables only through GitHub Actions' environment file.

Dependencies and integration points: Called by `ci.yml` Linux and MemoryTest jobs. Depends on distro package managers (`apt-get`, `dnf`, `zypper`, `apk`), shell array behavior through bash-compatible execution, Java packages for tests, FUSE3 development headers, libcurl/OpenSSL/libxml2, and autotools.

Risks: The header comment says it runs in `sh`, but the shebang is bash and it uses arrays; Alpine pre-installs bash before running it. The argument-count error logs but does not immediately exit, though nounset may later fail. Package names for future distro releases can drift. Direct curl replacement is supply-chain sensitive but mitigated with SHA256 checks. `$GITHUB_ENV` must be set by GitHub Actions; local invocation without it will fail at the final append.

Test signals: Run the helper in every matrix container, verify package install success, `curl --version`, Java availability, and exported `CONFIGURE_OPTIONS`. ShellCheck is run by CI and should cover quoting/branch issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/linux-ci-helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/Makefile.am

Purpose: Top-level automake file for s3fs-fuse, organizing subdirectories and project-wide static-analysis targets.

Important targets and variables: `SUBDIRS=src test doc` controls recursive builds. `EXTRA_DIST=default_commit_hash` packages the generated fallback commit hash. Phony targets `clang-tidy`, `cppcheck`, and `shellcheck` delegate or run analysis. `cppcheck` excludes pjd test directories, enables warning/style/information/missingInclude checks, sets C++ standard from `@CPP_VERSION@`, applies platform defines/undefines, and uses a custom Python addon. `shellcheck` checks both `/bin/sh` and `/bin/bash` scripts discovered by shebang.

Control flow: Normal `make` recurses into src/test/doc. Analysis targets are opt-in and are invoked by CI static-check jobs. `clang-tidy` delegates to `src` and `test`; `cppcheck` runs over `src/ test/`; `shellcheck` finds scripts dynamically and fails on ShellCheck errors.

State and persistence: No runtime state. Generated substitution `@CPP_VERSION@` comes from `configure.ac`; `default_commit_hash` is distributed for non-git builds.

Dependencies and integration points: Integrates autotools output, CI static checks, source and test Makefiles, ShellCheck, cppcheck, and a repo-local addon script.

Risks: Dynamic `find | xargs grep` can behave poorly if no files match, though current repo likely has scripts. Suppressions can hide some style findings. The cppcheck ignore for pjd tests depends on directory naming.

Test signals: `autoreconf/configure && make`, `make cppcheck`, `make shellcheck`, and `make clang-tidy` validate this file's behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/autogen.sh -->
# sources/user-network-fs/s3fs-fuse/autogen.sh

Purpose: Bootstrap script for generating autotools build files and capturing a short git commit hash fallback.

Important commands: Detects `git` and `.git`, runs `git rev-parse --short HEAD`, writes the result or an empty string to `default_commit_hash`, then runs `autoupdate`, `aclocal`, `autoheader`, `automake --add-missing`, and `autoconf`.

Control flow: The script logs hash generation, continues even when git hash extraction fails, then chains autotools commands with `&&` so failure stops the chain. It exits 0 unconditionally after the chain, meaning a failed autotools command could still be masked depending on shell behavior after the `&&` list completes.

State and persistence: Writes `default_commit_hash` in the repo root. Generates or updates autotools artifacts such as `configure`, `config.h.in`, Makefile templates, and helper scripts.

Dependencies and integration points: Called by CI before `configure`. Depends on POSIX sh, git optionally, and autotools commands. `configure.ac` later consumes `default_commit_hash` when no `.git` exists.

Risks: Unconditional `exit 0` can hide bootstrap failures. `autoupdate` may rewrite configure macros, creating noisy changes if run by developers. The generated hash file changes with commits and must be managed carefully in release/source distributions.

Test signals: Run `./autogen.sh` in a clean checkout and verify generated `configure` exists, `default_commit_hash` contains the current short hash, and CI build proceeds to `./configure`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/configure.ac -->
# sources/user-network-fs/s3fs-fuse/configure.ac

Purpose: Autoconf source for configuring s3fs-fuse build dependencies, compiler flags, crypto backend selection, feature probes, generated files, manpage date, and commit hash macro.

Important APIs and macros: Initializes package `s3fs` version `1.97`, `config.h`, canonical host, automake, C/C++ compilers, and C++14 via `CPP_VERSION`. Probes xattr headers, `fallocate`, `malloc_trim`, `clock_gettime`, pthread recursive mutex symbol, libcurl options, and `dlopen`. Requires FUSE3 with platform-specific minimum versions. Supports `--with-openssl`, `--with-gnutls`, `--with-nettle`, and `--with-nss` with automake conditionals `USE_SSL_OPENSSL`, `USE_SSL_GNUTLS`, `USE_GNUTLS_NETTLE`, and `USE_SSL_NSS`.

Control flow: Sets hardening/portability CXXFLAGS (`-Wall`, no exceptions, file offset bits, `_FORTIFY_SOURCE`, C++14), selects min FUSE version by host, checks selected crypto backend dependencies via pkg-config and library probes, defines feature macros, substitutes `MAN_PAGE_DATE`, configures Makefiles and `doc/man/s3fs.1`, computes `COMMIT_HASH_VAL` from git or `default_commit_hash`, and runs `AC_OUTPUT`.

State and persistence: Generates `config.h`, Makefiles, manpage, and preprocessor definitions. The commit hash embeds dirty-state information using `git status -s --untracked-files=no`; despite the string text saying `+untracked files`, it actually reports tracked modifications.

Dependencies and integration points: Drives `src/Makefile.am` source selection for crypto backends and `doc/man/s3fs.1.in` substitution. It must align with CI package installation and source code `#ifdef`s for curl/FUSE/SSL features.

Risks: Crypto backend options are mutually constrained; invalid combinations fail configure. `_FORTIFY_SOURCE` detection compiles manually and depends on compiler warning text. Future OpenSSL/FUSE/pkg-config naming changes can break checks. The commit dirty label is misleading because untracked files are excluded.

Test signals: Run configure with default OpenSSL, explicit `--with-openssl`, `--with-gnutls`, `--with-nettle --with-gnutls`, and `--with-nss` where dependencies exist. CI matrix plus macOS build validates platform-specific FUSE minimum logic and feature probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/doc/Makefile.am

Purpose: Automake file for installing the generated s3fs manpage.

Important fields: `dist_man1_MANS = man/s3fs.1` marks the section 1 manpage for distribution and installation.

Control flow and integration: `configure.ac` generates `doc/man/s3fs.1` from `doc/man/s3fs.1.in`, and automake installs/distributes it through this variable during doc subdir processing.

State and persistence: No runtime state. The generated manpage is a build artifact; the `.in` file is the maintained source.

Dependencies and risks: Depends on `configure.ac` listing `doc/Makefile` and `doc/man/s3fs.1` in `AC_CONFIG_FILES`. If the generated manpage is missing, install/dist targets fail.

Test signals: `make -C doc distcheck` or a full `make distcheck` verifies the manpage is generated and packaged.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/man/s3fs.1.in -->
# sources/user-network-fs/s3fs-fuse/doc/man/s3fs.1.in

Purpose: Source template for the `s3fs(1)` manual page documenting command syntax, authentication, mount options, utility modes, local storage behavior, performance considerations, and known S3 consistency caveats.

Important content: Documents mounting forms, unmounting commands, incomplete multipart upload utility modes, AWS credentials file and passwd file formats, environment-variable credentials, and a large set of `-o` mount options. Options cover ACLs, caching, storage class, SSE variants, credentials, public buckets, timeouts, stat cache/negative cache, TLS validation, multipart behavior, host/region/signature mode, permissions, threading, metadata/IAM modes, xattrs, compatibility modes, logging/debugging, and parent directory stat updates.

Control flow and integration: This is documentation, not executable code, but it must match option parsing and behavior in the s3fs binary. `@MAN_PAGE_DATE@` is substituted by `configure.ac` using the current build month/year. The manpage is installed through `doc/Makefile.am`.

State and persistence: Describes persistent credential files, local cache directories, temporary storage, log files, and multipart upload cleanup behavior. It also explains local cache deletion and disk-free controls.

Dependencies and integration points: Integrates with AWS S3 semantics, FUSE mount options, libcurl/TLS behavior, IAM/metadata services, object-store compatibility settings, and local cache/stat cache implementations.

Risks: The option surface is large, so drift between code and documentation is likely. Security-sensitive options such as `no_check_certificate`, `ssl_verify_hostname=0`, and `insecure_logging` are documented with warnings and should remain explicit. The BUGS section calls out S3 eventual consistency, a user-visible operational risk.

Test signals: Validate generated `man/s3fs.1` substitution, lint with manpage tools if available, and cross-check option names/defaults against s3fs help output and option parser tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/doc/man/s3fs.1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/src/Makefile.am

Purpose: Automake file defining the main `s3fs` binary, crypto-backend source selection, unit test helper binaries, and clang-tidy target for the source directory.

Important fields: `bin_PROGRAMS=s3fs`; `AM_CPPFLAGS=$(DEPS_CFLAGS)` plus `-DUSE_GNUTLS_NETTLE` when applicable; conditional `AUTH_SOURCES` selects `openssl_auth.cpp`, `gnutls_auth.cpp`, or `nss_auth.cpp`. `s3fs_SOURCES` includes core filesystem, curl, cache, credential, fd-cache, threading, metadata, additional-header, signal, and sync filler modules. `noinst_PROGRAMS` defines `test_curl_util`, `test_page_list`, and `test_string_util`; `TESTS` runs them.

Control flow and integration: `configure.ac` conditionals determine authentication source composition and `DEPS_*` flags/libs. `make check -C src` builds and runs the unit helper programs. `clang-tidy` runs over headers, main sources, and test sources with configured C++ standard and dependency flags.

State and persistence: No runtime state. Determines which object files are built and linked into `s3fs` and tests.

Dependencies and risks: Source list must stay in sync with new modules; missing additions cause build/link failures or omitted functionality. Conditional auth source logic must match configure backend choices. The clang-tidy target uses shell globbing and broad source lists, so new files may need explicit inclusion.

Test signals: `make -C src`, `make check -C src`, and `make -C src clang-tidy` validate build composition and unit binaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.cpp -->
# sources/user-network-fs/s3fs-fuse/src/addhead.cpp

Purpose: Implements `AdditionalHeader`, a singleton that loads file-extension or regex based rules and injects additional HTTP headers into S3 request metadata or curl header lists.

Important APIs, types, and functions: Implements destructor, `Load`, `Unload`, `AddHeader(headers_t&, const char*)`, `AddHeader(curl_slist*, const char*)`, and `Dump`. Uses `ADD_HEAD_REGEX` prefix `reg:` for regex rules and `curl_slist_sort_insert` to build sorted curl headers.

Control flow: `Load` clears existing rules, opens the configured file, skips blank/comment lines, parses optional key/suffix, header name, and remainder-of-line value. Keys beginning with `reg:` are compiled as POSIX extended regex with `REG_NOSUB`; other keys are treated as suffix strings. Valid rules are appended to `addheadlist` and enable the singleton. `AddHeader` scans every rule for a given path, matches regex or suffix, and writes matching headers into `headers_t`; the curl overload converts those pairs into a curl slist. `Dump` logs the loaded rules only when debug logging is enabled.

State and persistence: In-memory singleton state consists of `is_enable` and `addheadlist`. The input configuration file is persistent external state, but not modified here.

Dependencies and integration points: Depends on `addhead.h`, `metaheader.h` `headers_t`, POSIX regex, `curl_util.h`, and `s3fs_logger.h`. The manpage's `ahbe_conf` option documents the configuration consumed here.

Risks: Suffix matching requires `basestring.length() < pathlength`, so a suffix equal to the entire path does not match. Duplicate matching header keys collapse in `headers_t`, so later matches overwrite earlier values even though the scan allows duplicate rules. Regex compile errors log and skip the rule, while some parse errors unload all rules and fail. Values preserve the remainder after the header token, so spacing matters.

Test signals: Unit tests should cover comments/blank lines, empty suffix as match-all, suffix matches and non-matches including equal-length path, regex matches and invalid regex, duplicate header precedence, curl slist output ordering, null file/path handling, and unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.h -->
# sources/user-network-fs/s3fs-fuse/src/addhead.h

Purpose: Declares the additional HTTP header rule structures and `AdditionalHeader` singleton interface.

Important APIs and types: `RegexPtr` is a `std::unique_ptr<regex_t, regfree>` for RAII regex cleanup. `add_header` owns an optional regex, base string, header key, and header value; copy operations are deleted and moves are partially supported. `addheadlist_t` is a vector of rules. `AdditionalHeader` exposes `get`, `Load`, `Unload`, two `AddHeader` overloads, and `Dump`.

Control flow and integration: Callers use `AdditionalHeader::get()` to load rules from an `ahbe_conf` path, then ask it to augment metadata maps or curl slists for individual object paths. The singleton is function-local static to avoid global initialization ordering problems.

State and persistence: Holds process-local enabled flag and rule vector. Persistent state is external configuration only.

Dependencies: Includes C++ memory/string/vector/utility, POSIX `regex.h`, and `metaheader.h`; the curl slist overload forward-references `struct curl_slist`.

Risks: `add_header& operator=(add_header&&) = delete` means vector operations rely on move construction and no move assignment. Header insertion semantics are implemented in the cpp and use map overwrite behavior. Singleton makes tests order-dependent unless `Unload` is called between cases.

Test signals: Compile coverage for move-only vector behavior, singleton lifecycle tests, and functional tests through `addhead.cpp`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.cpp -->
# sources/user-network-fs/s3fs-fuse/src/cache.cpp

Purpose: Implements the process-wide `StatCache` for s3fs path metadata, negative entries, directory object lists, and symlink targets.

Important APIs, types, and functions: Implements `GetCacheSize`, `SetCacheSize`, `GetStat`, `GetS3ObjList`, `AddStatHasLock`, two `AddStat` overloads, `AddS3ObjList`, `UpdateStat`, `AddNegativeStat`, `ClearNoTruncateFlag`, `TruncateCacheHasLock`, `DelStatHasLock`, `DelStat`, `GetSymlink`, `AddSymlink`, `RawGetChildStats`, `GetChildStatList`, `GetChildStatMap`, and `Dump`. Static `stat_cache_lock` protects all tree operations. The root cache node is `pMountPointDir`.

Control flow: Reads lock the cache, find nodes by path and optional ETag, handle negative entries as misses while still returning type, and copy stat/meta/list/symlink data out. Writes lock the cache, add or overwrite entries in the `DirStatCache` tree, then truncate expired entries when count exceeds `CacheSize`. Negative cache insertion removes any existing entry first, then stores a `NEGATIVE` node if caching is enabled. Symlink insertion replaces non-symlink entries and stores target text as extra data. Child stat retrieval merges cached child names/types into caller-provided lists/maps.

State and persistence: Entirely in-memory. Default `CacheSize` is 100,000 entries. `NoTruncate` entries protect newly created but not-yet-uploaded files from eviction until cleared. Directory/list and symlink caches share stat cache sizing and timeout behavior through underlying cache nodes.

Dependencies and integration points: Depends on `cache_node.h` tree/node behavior, `s3objlist.h`, `metaheader.h`, object type enums, logging macros, and thread-safety annotation macros from `common.h`. It supports FUSE operations in other modules that need path metadata without repeated S3 HEAD/LIST calls.

Risks: `SetCacheSize` is not locked, so concurrent size changes can race with readers/writers. Several methods return true when caching is disabled, which may be interpreted as success without data by careless callers (`GetSymlink` returns true when size < 1). Truncation only removes expired/truncatable nodes; protected or non-empty directory nodes can let cache count exceed target. Child cache merging is best-effort and returns true even when no directory cache exists.

Test signals: Unit tests should cover positive stat hits, ETag mismatch, negative cache type/miss behavior, size zero behavior, add/update/delete, mount-point clearing, no-truncate clearing, truncation when over capacity, symlink replacement/update, S3 object list caching, child list/map merging, and concurrent access under ThreadSanitizer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.h -->
# sources/user-network-fs/s3fs-fuse/src/cache.h

Purpose: Declares the `StatCache` singleton interface and synchronization contract for s3fs metadata, negative, directory-list, and symlink caching.

Important APIs and types: `StatCache::getStatCacheData` returns a function-local singleton. Public methods expose cache sizing, stat reads/writes, S3 object list caching, negative cache insertion, metadata update, no-truncate flag clearing, deletion, symlink cache access, child stat list/map retrieval, and debug dump. Private helpers are annotated with `REQUIRES(StatCache::stat_cache_lock)` and fields with `GUARDED_BY`.

Control flow and integration: Other s3fs modules call this singleton during FUSE lookup/getattr/readdir/readlink/create/update paths. The underlying cache tree starts at mount point `/` and is represented by `DirStatCache`.

State and persistence: Declares static mutex protection, root directory cache node, and maximum cache size. All cached data is process-local and non-persistent.

Dependencies: Includes mutex/string/stat headers plus project headers `common.h`, `metaheader.h`, `s3objlist.h`, and `cache_node.h`.

Risks: Public API returns booleans with nuanced meanings, especially negative cache and disabled-cache cases. Thread-safety annotations help static checking, but only if the toolchain honors them. Singleton lifecycle can make tests order-dependent unless they clear state between cases.

Test signals: Compile with thread-safety annotations, run source unit tests (`test_page_list` adjacent cache structures where applicable), and add direct StatCache tests for all public overloads and concurrency-sensitive paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache.h -->
