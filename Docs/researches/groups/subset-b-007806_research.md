# subset-b-007806 Research

Grouped research for the listed OpenAFS dumpscan, Rx performance, threaded server build, AIX TSM authentication, salvage sync debug, and ubik files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/util.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/util.c

## Purpose
Provides internal helper routines for dumpscan parsing and repair paths. It normalizes low-level parser return codes into user-visible diagnostics, prepares tag parser options from a `dump_parser`, and probes candidate offsets to decide whether a dump stream is positioned at a plausible vnode or dump terminator.

## Important APIs, Types, And Functions
The file exposes `handle_return`, `prep_pi`, and `match_next_vnode`, all marked as intended for internal use. The code works with `XFILE`, `dump_parser`, `tag_parse_info`, `dt_uint64`, AFS vnode type constants, `DUMPENDMAGIC`, dumpscan error codes such as `DSERR_TAG`, `DSERR_DONE`, `DSERR_FMT`, and xfile errors such as `ERROR_XFILE_EOF`. It depends on primitive dump readers like `ReadByte`, `ReadInt32`, and 64-bit formatting helpers `decimate_int64` and `hexify_int64`.

## Control Flow
`handle_return` is the common post-read dispatcher: a zero return is interpreted as an unexpected tag unless the caller already translated successful parser completion to `DSERR_DONE`; EOF and ENOMEM get location-aware callbacks; `DSERR_DONE` is converted to success; other positive codes are reported as system errors, while negative codes are assumed to have already been reported. `prep_pi` zeroes a `tag_parse_info`, copies parser error callback fields, and maps repair flags to tag parser skip flags. `match_next_vnode` seeks to a requested position, reads the next tag, then validates vnode/dump-end shape, vnode ordering, uniquifier bounds, and vnode type parity.

## State And Persistence
The file does not own persistent state. It observes and mutates stream position through `xfseek`, `xftell`, and primitive reads, and it uses parser flags, repair flags, and the parser's `vol_uniquifier` as validation inputs. Error reporting is pushed through callback state stored in `dump_parser`.

## Dependencies And Integration Points
This is shared parser glue for dumpscan modules such as tag, vnode, volume, repair, and primitive parsing. It integrates the xfile abstraction with the dumpscan callback/error model and with AFS dump format conventions from `dumpfmt.h`.

## Risks And Test Signals
Risks include the special meaning of return value `0` in `handle_return`, off-by-one reporting around unexpected tags, and heuristic false positives/negatives in `match_next_vnode` when repairing damaged dumps. Useful tests are malformed tag streams, unexpected EOF at different offsets, ENOMEM injection, `DSFIX_SKIP`/`DSFIX_RSKIP` flag propagation, valid vnode order transitions, dump-end matching, and corrupt vnode uniquifier/type combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_files.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/xf_files.c

## Purpose
Implements concrete `XFILE` backends for local Unix files, existing `FILE *` streams, file descriptors, and standard input/output. It lets dumpscan code access ordinary files through the same `XFILE` interface used for profile wrappers, Rx calls, and volume dump streams.

## Important APIs, Types, And Functions
Public entry points are `xfopen_path`, `xfopen_FILE`, `xfopen_fd`, `xfon_path`, `xfon_fd`, and `xfon_stdio`. Static backend methods include `xf_FILE_do_read`, `xf_FILE_do_write`, `xf_FILE_do_tell`, `xf_FILE_do_seek`, `xf_FILE_do_skip`, `xf_FILE_do_close`, and `prepare`. The `O_MODE_MASK` macro limits mode handling to `O_RDONLY`, `O_WRONLY`, and `O_RDWR`.

## Control Flow
`xfopen_path` rejects write-only mode, opens a path with `open`, wraps the descriptor with `fdopen`, and calls `prepare`. `xfopen_FILE` and `xfopen_fd` do the same preparation for existing handles. `prepare` zeros the `XFILE`, installs stdio callbacks, marks writability for read/write mode, and enables seek/skip only for regular and block files detected by `fstat`. The concrete callbacks map `fread`, `fwrite`, `ftell`, `fseek`, and `fclose` to xfile return conventions.

## State And Persistence
The file stores no global state. Per-open state is the `FILE *` in `XFILE.refcon`; `xfclose` via the backend closes that stream. Disk state is whatever path or descriptor the caller opened, and `xfon_stdio` maps read mode to `stdin` and write/read mode to `stdout`.

## Dependencies And Integration Points
It depends on POSIX `open`, `close`, `fstat`, stdio, and xfile error constants. `xfiles.c` registers `xfon_path` under `FILE`, `xfon_fd` under `FD`, and uses `xfon_stdio` when the open name is `-`.

## Risks And Test Signals
The comments note missing handling for short/interrupted stdio reads and writes; `fread(buf, count, 1)` treats partial reads as EOF/error. Large offsets are squeezed through `off_t` via `get64`, so platform offset width matters. Tests should cover regular files, pipes/nonseekable input, block/regular seek detection, descriptor ownership after close, rejected `O_WRONLY`, stdin/stdout mode mapping, EOF behavior, and passthrough interactions through the higher-level `xfread`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_files.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_printf.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/xf_printf.c

## Purpose
Provides formatted output for `XFILE` streams without depending entirely on platform `printf` behavior. It implements `xfprintf`/`vxfprintf` over `xfwrite`, including integer/string/float formatting, `%n`, and a custom `%I` IPv4 address or hostname formatter.

## Important APIs, Types, And Functions
Public functions are `xfprintf` and `vxfprintf`. Static helpers are `mkint` for base conversion and `wsp` for batched space padding. The formatter supports standard integer specifiers, `%c`, `%s`, `%%`, `%n`, floating formats through `sprintf`, and `%I` for network-byte-order IPv4 addresses. Constants include `SPBUFLEN` and `MAXPREC`.

## Control Flow
`vxfprintf` scans literal text until `%`, writes pending literals, parses flags, width, precision, and `h`/`l` modifiers, then converts the next argument into a temporary string or points at an existing string. Width padding is emitted before or after the payload depending on left justification. `%I` optionally performs `gethostbyaddr`; on success it prints the host name with optional case conversion and precision truncation, otherwise it renders a dotted quad with optional zero/space padding.

## State And Persistence
The only module-level state is `spbuf`, lazily filled with spaces. The function writes to the caller's `XFILE` and advances that stream through `xfwrite`; it does not persist formatting state between calls. `%n` mutates caller-provided count pointers, and `%I` may mutate the hostname string returned by resolver storage when applying case conversion.

## Dependencies And Integration Points
The formatter is used by other dumpscan xfile backends, notably `xf_profile.c`, and by any dumpscan code wanting formatted output to an `XFILE`. It depends on libc formatting for floats, resolver APIs, `netinet/in.h`, and the generic xfile write path.

## Risks And Test Signals
Important risks include unsafe float formatting through `sprintf` into fixed buffers, precision/width arithmetic underflow because widths are unsigned but later assigned to signed padding, missing positional-argument support by design, no pointer `%p`, possible mutation of resolver-owned host strings, and limited handling of long long values. Tests should cover all integer flags, precision caps, literal flushing after errors, `%n`, null strings, custom `%I` with and without reverse DNS, and write-error propagation from a failing `XFILE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_printf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_profile.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/xf_profile.c

## Purpose
Implements an `XFILE` wrapper that records read/write/seek/tell/skip activity to a separate profile stream while forwarding operations to an underlying content stream. This is diagnostic instrumentation for dumpscan I/O behavior.

## Important APIs, Types, And Functions
The public open functions are `xfopen_profile` and `xfon_profile`. Internal `PFILE` holds two nested `XFILE`s: `content` and `profile`. Backend methods are `xf_PROFILE_do_read`, `xf_PROFILE_do_write`, `xf_PROFILE_do_tell`, `xf_PROFILE_do_seek`, `xf_PROFILE_do_skip`, and `xf_PROFILE_do_close`.

## Control Flow
`xfopen_profile` allocates a `PFILE`, opens the profile stream with `O_RDWR | O_CREAT | O_TRUNC`, opens the content stream with the caller's flags, installs wrapper methods, copies seekable/writable capability from the content stream, and writes an `OPEN` line. Each operation delegates to the content stream, logs operation name, byte count or offset, and result code to the profile stream, then returns the content result. `xfon_profile` parses `profile::xname` names, defaulting the profile stream to `-` when no profile name is provided.

## State And Persistence
Per-wrapper state is heap-allocated and freed on close. Persistent output is the profile file or stdout profile stream; persistent content effects are those of the wrapped `XFILE`. The wrapper has no global state and preserves the underlying stream capability flags.

## Dependencies And Integration Points
It depends on `xfiles.c` for recursive `xfopen`, on `xfprintf` for profile records, and on all backend types registered under the requested content/profile names. It is registered as the `PROFILE` type by `xfiles.c`.

## Risks And Test Signals
Profile logging errors are ignored in the operation wrappers, so profile loss may be silent. Closing a profile targeting `stdout` through `xfon_stdio` can close stdout. Tests should cover `PROFILE:file::FILE:data`, default profile output, nonseekable content behavior, delegation of error codes, close ordering, profile stream open failure cleanup, and nested profile wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_rxcall.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/xf_rxcall.c

## Purpose
Implements `XFILE` access over Rx bulk data calls and volume-server dump RPCs. It lets dumpscan read a remote AFS volume dump as an `XFILE`, and it can also wrap an already-created `rx_call`.

## Important APIs, Types, And Functions
Public entry points are `xfopen_rxcall`, `xfopen_voldump`, and `xfon_voldump`. Internal state is `struct rxinfo`, containing an Rx connection, active call, volserver transaction id, and stored result code. Backend callbacks are `xf_rxcall_do_read`, `xf_rxcall_do_write`, `xf_rxcall_do_close`, and `xf_voldump_do_close`.

## Control Flow
`xfopen_rxcall` rejects write-only mode, initializes an `XFILE` backed by `rx_Read`, `rx_Write`, and `rx_EndCall`, and marks writability for `O_RDWR`. `xfopen_voldump` creates a volserver transaction with `AFSVolTransCreate`, starts `StartAFSVolDump`, wraps the resulting call as read-only, and changes close behavior so the volume transaction is ended after the Rx call. `xfon_voldump` parses `volid[@server/partition][,date]`, initializes Rx, resolves server addresses, opens client config, obtains tokens if available, creates rxkad or rxnull security, and starts the remote dump.

## State And Persistence
Per-open state is the active Rx call plus, for volume dumps, the volserver transaction that must be ended on close. There is no local disk persistence. Authentication state is read from the client config and token cache; remote server state includes a busy volume transaction for the duration of the dump stream.

## Dependencies And Integration Points
This file integrates dumpscan with Rx, rxkad/rxnull security, AFS auth and cell config, VL/volser protocol headers, partition parsing, and volserver dump RPCs. `xfiles.c` registers it under the `AFSDUMP` type.

## Risks And Test Signals
The volume-name and volume-id lookup paths are incomplete and currently call `exit(-1)` when server/partition is omitted or a name lookup is needed. On short Rx read, the read callback returns `ERROR_XFILE_RDONLY`, which is semantically surprising for EOF. Security and connection objects are not explicitly destroyed in the shown path. Tests should cover wrapping an existing Rx call, short read/write behavior, transaction cleanup after start failures, explicit server/partition/date parsing, token-present and token-absent security selection, and close result precedence between Rx and `AFSVolEndTrans`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xf_rxcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.c

## Purpose
Provides the generic `XFILE` abstraction used by dumpscan. It centralizes read/write/seek/tell/skip/close dispatch, position accounting, passthrough copying, backend registration, and `TYPE:name` opening.

## Important APIs, Types, And Functions
Core operations are `xfread`, `xfwrite`, `xftell`, `xfseek`, `xfskip`, `xfpass`, `xfunpass`, `xfclose`, `xfregister`, and `xfopen`. Static registration support uses `struct xftype`, `xftypes`, `did_register_defaults`, and `register_default_types`. Default backend openers are declared externally for paths, file descriptors, vol dumps, profile wrappers, and stdio.

## Control Flow
Reads and writes call the backend callbacks, update the counted 64-bit file position, and in the read case optionally pass the bytes through to another writable `XFILE`. Seek/tell prefer backend methods when present, otherwise tell returns the counted position. Skip uses backend skip when available, then absolute seek, and finally a read-and-discard loop, which also preserves passthrough semantics. `xfopen` lazily registers default types, special-cases `-` as stdio, parses an optional `TYPE:` prefix by temporarily NUL-terminating the string, restores the separator, and dispatches to the registered opener.

## State And Persistence
Global state is the backend registry linked list and a boolean noting default registration. Per-stream state lives in each `XFILE`: callback pointers, counted `filepos`, capability flags, passthrough pointer, and backend `refcon`. No filesystem state is owned here, but operations propagate to backend persistence.

## Dependencies And Integration Points
This is the common I/O contract for the dumpscan tree. It depends on `intNN.h` 64-bit helpers, backend files such as `xf_files.c`, `xf_profile.c`, and `xf_rxcall.c`, plus xfile error constants.

## Risks And Test Signals
Risks include no registry synchronization, modification of the caller's open-name buffer during type parsing, no check for duplicate backend names, position drift if a backend performs short reads/writes but reports success, and passthrough write failures causing a read failure after data was consumed. Tests should cover each default backend name, custom registration, colon and non-colon names, passthrough copy and unpass errors, seekless skip fallback, position accounting, and close zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.h -->
# sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.h

## Purpose
Defines the `XFILE` type and declares the extensible file-like API used by dumpscan. It is the public contract shared by concrete xfile backends and dump parser code.

## Important APIs, Types, And Functions
The central type is `struct XFILE`, with backend callbacks for read, write, tell, seek, skip, and close; counted `dt_uint64 filepos`; capability flags; passthrough target; and backend `refcon`. The header declares openers for generic `xfopen`, path, `FILE *`, fd, Rx call, vol dump, and profile streams, registration via `xfregister`, and standard operations including `xfprintf`/`vxfprintf`.

## Control Flow
Consumers initialize an `XFILE` through one of the open functions, use standard operations for I/O and positioning, optionally install a passthrough stream, and release resources with `xfclose`. Backend implementers fill callback fields and capability flags to opt into seek, skip, write, and close behavior.

## State And Persistence
The header owns no state. It defines where per-stream runtime state and backend-specific pointers are stored. Persistent effects depend entirely on the backend implementation referenced by the callback table.

## Dependencies And Integration Points
It includes stdio, varargs, and dumpscan integer definitions from `intNN.h`, and forward-declares Rx call/connection types to avoid forcing Rx headers on all users. It connects all dumpscan parser and xfile backend modules.

## Risks And Test Signals
Because `XFILE` is a manual vtable, risks are uninitialized callbacks, mismatched capability flags, backend lifetime bugs in `refcon`, and ABI drift if fields are reordered. Compile coverage for all xfile backends and runtime tests for open/read/write/seek/close paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/rxperf/Makefile.in -->
# sources/distributed-fs/openafs/src/tools/rxperf/Makefile.in

## Purpose
Builds the `rxperf` standalone Rx performance tool. The makefile is intentionally small: it compiles `rxperf.o`, links it statically with the OpenAFS Rx library and crypto/roken/thread libraries, and removes generated artifacts on clean.

## Important APIs, Types, And Functions
Targets are `all`, `rxperf`, empty `install`/`dest`, and `clean`. It includes `Makefile.config` and `Makefile.pthread`, sets `top_builddir`, and defines `LIBS` as `src/rx/liboafs_rx.la`. Linking uses `$(LT_LDRULE_static)`, `$(LIB_hcrypto)`, `$(LIB_roken)`, and `$(MT_LIBS)`.

## Control Flow
`all` depends on `rxperf`. The executable target links the single object with Rx and support libraries. There is no install action from this directory. `clean` invokes libtool cleanup and removes the object and binary.

## State And Persistence
The makefile produces build artifacts `rxperf.o` and `rxperf`; it installs nothing. Persistent configuration is inherited from the generated top-level config and pthread make fragments.

## Dependencies And Integration Points
It is part of the OpenAFS autotools build and depends on libtool rules, configured library variables, pthread settings, and the Rx library target. It exists under `src/tools/rxperf`, outside normal server/client installation flows.

## Risks And Test Signals
The lack of install/dest rules means packaging must not assume `rxperf` is installed. Link failures reveal missing Rx, hcrypto, roken, or thread settings. Useful signals are `make rxperf`, clean idempotence, and successful pthread/non-pthread configured builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/rxperf/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/rxperf/rxperf.c -->
# sources/distributed-fs/openafs/src/tools/rxperf/rxperf.c

## Purpose
Implements `rxperf`, a client/server benchmark for the OpenAFS Rx RPC transport. It measures one-way send, one-way receive, request/response RPC, and scripted alternating file-pattern transfers with tunable packet/window/MTU/thread options.

## Important APIs, Types, And Functions
The command modes are `RX_PERF_SEND`, `RX_PERF_RECV`, `RX_PERF_RPC`, and `RX_PERF_FILE`, all using `RX_SERVER_ID`, protocol version `RX_PERF_VERSION`, and `RXPERF_MAGIC_COOKIE`. Important functions include `rxperf_ExecuteRequest`, `do_server`, `do_client`, `client_thread`, `do_readbytes`, `do_sendbytes`, `readfile`, `rxperf_server`, `rxperf_client`, `str2addr`, `get_sec`, timer helpers, signal handlers, and `main`. Global knobs include `somebuf`, `rxwrite_size`, `rxread_size`, and `use_rx_readv`.

## Control Flow
`main` initializes process support, sets signal handlers, zeros the transfer buffer, and dispatches `server` or `client`. The server initializes Rx, applies transport options, creates a null-security Rx service, sets min/max procs, and blocks in `rx_StartServer`. The request handler reads version, command, negotiated read/write chunk sizes, and command-specific sizes or file pattern data, then drains or emits bytes and replies with the magic cookie when applicable. The client parses command options, initializes Rx, creates a connection, starts a timer, runs one or more client threads, waits for completion, prints elapsed time and throughput, optionally dumps Rx stats, and finalizes Rx.

## State And Persistence
Most state is process-local benchmark configuration. The server is network state on the selected UDP port; the client may open an output file for results and may read a pattern file for `file` mode. No durable OpenAFS database or token state is changed. Multi-threaded clients share one `client_data` instance until the code creates additional connections after `RX_MAXCALLS` thread groups.

## Dependencies And Integration Points
The tool integrates with Rx core APIs, rxnull security, Rx stats/debug globals, pthreads or LWP process support, roken `err`/`warn` helpers, sockets, resolver APIs, and platform winsock setup on Windows. It is a diagnostic tool rather than a production service.

## Risks And Test Signals
Risks include several unchecked allocations, shared `client_data` and global chunk-size variables across threads, integer overflow for very large byte counts, `readfile` leaking its read/write list in client threads, no validation that `-f` is present for file mode, and benchmark results depending on null security and local buffering. Tests should cover client/server protocol version mismatch, all four commands, `-V` readv mode, max chunk-size bounds, multi-thread limits, stats output, output-file handling, invalid option parsing, and a loopback smoke run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/rxperf/rxperf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tptserver/Makefile.in -->
# sources/distributed-fs/openafs/src/tptserver/Makefile.in

## Purpose
Builds pthreaded variants of the Protection Server tools from sources in `src/ptserver`. It produces server, client, utility, consistency checker, and test binaries when pthreaded ubik support is enabled.

## Important APIs, Types, And Functions
Targets include `ptserver`, `pts`, `pt_util`, `prdb_check`, `readgroup`, `readpwd`, `testpt`, generated `pterror.c/.h`, `ptint.ss.c`, `ptint.xdr.c`, and `ptint.h`. It defines common, server, and client library groups around pthreaded ubik, Rx, rxkad, rxstat, cmd, util, audit, prot, sys, lwpcompat, and opr libraries. Build flags include `CFLAGS_NOSTRICT` for selected ptserver files.

## Control Flow
The makefile compiles ptserver source files from `$(PTSERVER)`, generates the pt RPC interface with `RXGEN`, builds binaries with static libtool link rules, and conditionally installs/dests outputs only when `ENABLE_PTHREADED_UBIK` is `yes`. Error table generation also creates `prerror.h` as a compatibility header aliasing PT error-table base.

## State And Persistence
Build outputs include generated RPC/error files, objects, and binaries. Install/dest targets persist server tools into configured server/client bindirs when pthreaded ubik is enabled. No runtime database state is touched by the makefile.

## Dependencies And Integration Points
This makefile is a bridge from `src/tptserver` to the canonical `src/ptserver` source tree, using pthread config and pthreaded ubik libraries. It integrates rxgen, compile_et, libtool, version generation, and install paths for OpenAFS server packaging.

## Risks And Test Signals
Risks are drift between ptserver sources and this wrapper, missing generated headers before dependent objects compile, and silent non-installation when `ENABLE_PTHREADED_UBIK` is not set. Useful signals are `make all`, generated-file rebuilds from `.xg`/`.et`, conditional install tests with the flag both enabled and disabled, and linking against the pthreaded ubik library set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tptserver/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsalvaged/Makefile.in -->
# sources/distributed-fs/openafs/src/tsalvaged/Makefile.in

## Purpose
Builds demand-attach fileserver salvage tools in a pthreaded layout: `salvageserver`, `dasalvager`, `dafssync-debug`, and `salvsync-debug`. It reuses volume and directory sources with normal and salvage-specific compile flags.

## Important APIs, Types, And Functions
Major object groups are `SALVAGEDOBJS`, `SALVAGEROBJS`, `DIROBJS`, `SDIROBJS`, `VLIBOBJS`, `SVLIBOBJS`, `FSSDEBUG_OBJS`, and `SSSDEBUG_OBJS`. `MODULE_CFLAGS` and `SCFLAGS` enable `RXDEBUG`, FSSYNC/SALVSYNC client/server support, and `AFS_DEMAND_ATTACH_FS`. Targets include all objects mapped from `../vol` and `../dir`, plus install/dest/clean.

## Control Flow
Normal salvageserver/debug objects use `AFS_CCRULE`; salvage-specific `s_*` objects use `SCCRULE` with pthread and demand-attach flags. The four binaries link statically with sys, Rx, util, cmd, lwpcompat, opr, crypto, roken, and crypt libraries. Install and dest targets place the salvage binaries into configured server libexec/sbin or legacy root.server paths.

## State And Persistence
The makefile produces build artifacts and installs server-side binaries. Runtime state such as volume partitions, salvage queues, and FSSYNC/SALVSYNC sockets is only affected when the built programs run.

## Dependencies And Integration Points
This wrapper integrates volume subsystem sources, directory package sources, daemon communication, fssync/salvsync client/server code, and pthread build settings. It is tied to demand-attach fileserver support through compile defines and the `salvsync-debug.c` command.

## Risks And Test Signals
Risks include duplicated object builds with different flags, missing demand-attach defines causing unsupported binaries, and link-order sensitivity across volume/dir/lwp/rx libraries. Signals include a full `make all`, install path checks, `salvsync-debug` build only with demand-attach flags, and clean removal of generated objects/binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsalvaged/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsalvaged/salvsync-debug.c -->
# sources/distributed-fs/openafs/src/tsalvaged/salvsync-debug.c

## Purpose
Implements `salvsync-debug`, a command-line utility for interacting with the demand-attach salvageserver SALVSYNC protocol. It can request stats/nop, schedule salvage, cancel one salvage, cancel all, raise priority, and query salvage status.

## Important APIs, Types, And Functions
The code is gated by `AFS_DEMAND_ATTACH_FS`; without it, `main` reports unsupported. Important types are `struct salv_state`, `struct fssync_state`, `SYNC_response`, and `SALVSYNC_response_hdr`. Main helpers include `common_prolog`, `common_salv_prolog`, `do_salvop`, response/command/reason/state string mappers, and operation callbacks `OpStats`, `OpSalvage`, `OpCancel`, `OpCancelAll`, `OpRaisePrio`, and `OpQuery`.

## Control Flow
Demand-attach `main` initializes server paths, creates `cmd` syntaxes and aliases, wires common parameters by fixed offsets, and dispatches. `common_prolog` initializes winsock when needed, initializes the volume package and directory package, parses optional reason and program type, and connects to SALVSYNC. `common_salv_prolog` allocates salvage request state and parses volume id, partition, and priority. `do_salvop` calls `SALVSYNC_SalvageVolume`, reports transport/protocol response details, prints queue/priority/state fields if valid, and disconnects.

## State And Persistence
The utility creates transient process state and sends requests to the salvageserver, which may persist or mutate salvage queue state for volumes. It initializes volume package state locally but mostly for client protocol setup. `struct salv_state` allocations are not freed before process exit.

## Dependencies And Integration Points
It depends on OpenAFS command parsing, directory/volume/partition packages, daemon communication, SALVSYNC/FSSYNC protocol headers, Windows event logging/winsock conditionals, and demand-attach fileserver definitions. It is built by `tsalvaged/Makefile.in`.

## Risks And Test Signals
Risks include fixed parameter offsets that must match syntax construction, `atoi` parsing with little validation, always calling `common_salv_prolog` for stats despite the syntax not requiring a volume, and command string typos such as `SALVSYNC_CANCELLALL`. Tests should cover unsupported non-DAFS builds, each subcommand, optional reason/programtype names and numeric values, missing/invalid volume id, queue response formatting, and behavior when no salvageserver is reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsalvaged/salvsync-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/Makefile.in -->
# sources/distributed-fs/openafs/src/tsm41/Makefile.in

## Purpose
Builds AIX TSM/LAM dynamic authentication modules for OpenAFS. It creates legacy AFS password modules, Kerberos-authenticated variants, and an AIX 5 Kerberos 5 `aklog` dynamic auth module.

## Important APIs, Types, And Functions
Outputs are `afs_dynamic_auth`, `afs_dynamic_kerbauth`, optional `aklog_dynamic_auth`, and optional Kerberos 5 targets controlled by `@MAKE_KRB5@`. Object groups are `AUTH_OBJS`, `AUTH_KRB_OBJS`, and `AUTH_KRB5_OBJS`. Library sets `AFSLIBS` and `KAFSLIBS` pull kauth/prot/ubik/auth/rxkad/sys/crypto/rx/lwp/cmd/com_err/audit/util/opr variants. Link entry points are `-eafs_initialize` and `-eaklog_initialize`.

## Control Flow
The makefile compiles platform-specific `aix_auth.o` from `aix41_auth.c` for AIX 4 or `aix5_auth.c` for AIX 5+, builds `aix_ktc.c` twice with or without `AFS_KERBEROS_ENV`, adds Kerberos 5 CPP flags for `aix_aklog.o`, and links dynamic auth modules with AIX TSM imports/libs. `dest` installs outputs into the client `usr/vice/etc` area.

## State And Persistence
Build artifacts are dynamic auth binaries and objects. Installed modules become persistent client authentication plugins consumed by AIX login/security infrastructure.

## Dependencies And Integration Points
The file integrates OpenAFS static libraries with AIX security method loader conventions and configured Kerberos/roken libraries. It is highly platform-specific to `rs_aix*` `SYS_NAME` values and AIX import/export behavior.

## Risks And Test Signals
Risks include stale AIX-only library names, conditional object selection that silently skips unsupported `SYS_NAME`, duplicate header/prototype quirks in the source set, and missing Kerberos 5 flags. Signals are AIX 4/AIX 5 build coverage, dynamic loader entry-point validation, install location checks, and login-method smoke tests using each generated module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix41_auth.c -->
# sources/distributed-fs/openafs/src/tsm41/aix41_auth.c

## Purpose
Defines the AIX 4.1 security method initialization entry point for the OpenAFS dynamic authentication module. It registers AFS authentication and identity hooks with AIX's `secmethod_table`.

## Important APIs, Types, And Functions
The single active function is `afs_initialize(struct secmethod_table *meths)`, compiled only for `AFS_AIX41_ENV` and not `AFS_AIX51_ENV`. It calls `ka_Init`, zeros the method table, and assigns `afs_chpass`, `afs_authenticate`, `afs_passwdexpired`, `afs_passwdrestrictions`, plus group/passwd lookup stubs from `aix41_ident.c`.

## Control Flow
When AIX loads the module, `afs_initialize` initializes kauth once, clears all method slots, installs password/authentication callbacks, and installs identity callbacks so non-local registries can fall through to local functions when the OpenAFS stubs return null.

## State And Persistence
The function initializes kauth package state in-process and mutates the caller-provided method table. It does not write persistent data, but the registered authenticate callback may later obtain tokens and set PAG/ticket state.

## Dependencies And Integration Points
It depends on AIX `usersec.h`, OpenAFS kauth/kautils, and prototypes in `aix_auth_prototypes.h`. It is compiled to `aix_auth.o` for AIX 4 by `tsm41/Makefile.in`.

## Risks And Test Signals
Risks include strict compile gating for old AIX, method-table ABI drift, and identity prototype mismatches. Tests are AIX 4 module load, `afs_initialize` callback table inspection, successful authentication through `afs_authenticate`, and fallback behavior for getpwnam/getgrnam hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix41_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix41_ident.c -->
# sources/distributed-fs/openafs/src/tsm41/aix41_ident.c

## Purpose
Provides AIX 4.1 identity lookup stubs for the OpenAFS security method. These are intentionally null implementations so AIX can fall back to local passwd/group mechanisms while treating AFS users as non-local registry users.

## Important APIs, Types, And Functions
Compiled only for `AFS_AIX41_ENV` and not `AFS_AIX51_ENV`, it defines `afs_getgrset`, `afs_getgrgid`, `afs_getgrnam`, `afs_getpwnam`, and `afs_getpwuid`. Each function returns `NULL` despite some declarations using integer return types.

## Control Flow
The functions have no internal flow beyond returning null. They are installed into `secmethod_table` by `aix41_auth.c`.

## State And Persistence
No state is read or written. The behavior affects AIX login lookup control flow by declining to provide AFS-specific identity records.

## Dependencies And Integration Points
It includes AIX security and OpenAFS kauth headers and `aix_ident_prototypes.h`. It exists for compatibility with AIX 4's security method behavior and is built as `aix_ident.o`.

## Risks And Test Signals
There are visible prototype/signature inconsistencies between this implementation and `aix_ident_prototypes.h`, including swapped argument/return expectations for passwd lookups. Build warnings or errors on stricter compilers are likely signals. Runtime tests should confirm AIX falls back to local identity lookup when these callbacks return null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix41_ident.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix5_auth.c -->
# sources/distributed-fs/openafs/src/tsm41/aix5_auth.c

## Purpose
Defines the AIX 5+ security method initialization entry point for OpenAFS kauth-based dynamic authentication. Compared with the AIX 4 module, it registers authentication/password callbacks and `getpasswd`, but not group/passwd identity lookup stubs.

## Important APIs, Types, And Functions
The active function is `afs_initialize(struct secmethod_table *meths)`, compiled for `AFS_AIX51_ENV`. It installs `afs_chpass`, `afs_authenticate`, `afs_passwdexpired`, `afs_passwdrestrictions`, and `afs_getpasswd`.

## Control Flow
At module load, `afs_initialize` calls `ka_Init`, clears the security method table, registers the AFS callbacks, and returns success.

## State And Persistence
It initializes kauth process state and fills the method table. Persistent authentication effects occur later in `afs_authenticate`, not in this file.

## Dependencies And Integration Points
The file depends on AIX `usersec.h`, OpenAFS kauth/kautils, and `aix_auth_prototypes.h`. `tsm41/Makefile.in` compiles it as `aix_auth.o` for AIX 5/6/7 system names.

## Risks And Test Signals
Risks are method-table ABI differences across AIX releases and missing callback slots for newer AIX expectations. Useful signals are AIX 5+ dynamic module load, callback table inspection, and login authentication through the shared `aix_auth_common.c` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix5_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_aklog.c -->
# sources/distributed-fs/openafs/src/tsm41/aix_aklog.c

## Purpose
Implements the AIX 5 Kerberos 5 `aklog_dynamic_auth` module. During AIX login/session authentication it obtains Kerberos 5 AFS service credentials, imports them as rxkad tokens, optionally resolves a PTS vice id, configures PAG behavior, and stores tokens via `ktc_SetTokenEx`.

## Important APIs, Types, And Functions
The exported entry point is `aklog_initialize`. Security callbacks include `aklog_authenticate`, `aklog_open`, `aklog_chpass`, `aklog_passwdexpired`, `aklog_passwdrestrictions`, and `aklog_getpasswd`. Core helpers are `afs_realm_of_cell`, `get_credv5`, `get_user_realm`, `get_cellconfig`, and `auth_to_cell`. Key globals are `uidpag`, `localuid`, `ak_cellconfig`, `linkedcell`, and `_krb425_ccache`.

## Control Flow
`aklog_initialize` clears the AIX method table and registers auth/open callbacks. `aklog_open` parses NUL-delimited options such as `uidpag` and `localuid`. `aklog_authenticate` initializes a Kerberos context and calls `auth_to_cell`. `auth_to_cell` reads client cell config, selects a Kerberos realm, tries `afs/<cell>` and optionally `afs` principals, builds a token jar, imports the V5 ticket as rxkad token data, derives the username and realm suffix, optionally queries PTS for the vice id or uses the local uid, sets token PAG policy, and either sets tokens directly or forks/setuids for root with UID-based PAGs.

## State And Persistence
The module stores process-global option flags, cached Kerberos ccache/principal state, and cell config. Its lasting effect is kernel/cache-manager token state and PAG assignment. It reads Kerberos credential caches, AFS client config, passwd data, and possibly PTS data.

## Dependencies And Integration Points
It integrates AIX LAM/TSM security methods, Kerberos 5 APIs with portability macros for principal and keyblock access, OpenAFS cell config, token import APIs, ktc, rxkad token formats, PTS client calls, syslog, passwd lookup, PAG APIs, and AIX process/session behavior.

## Risks And Test Signals
Risks are high because this is security-sensitive and platform-specific: fixed-size string copies, cached Kerberos objects without cleanup, comments noting `pr_Initialize` can crash long-running daemons, DES enctype request assumptions, UID/PAG ambiguity, fork/setuid error handling, and token vice-id mapping fallbacks. Tests should cover module load, options parsing, local and linked cells, `afs/<cell>` and `afs` service principal fallback, foreign-realm username suffixes, PTS unavailable, `localuid`, root `uidpag` fork path, missing Kerberos cache, expired tickets, and token visibility after login.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_aklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_auth_common.c -->
# sources/distributed-fs/openafs/src/tsm41/aix_auth_common.c

## Purpose
Provides common kauth-based authentication callbacks shared by the AIX dynamic auth modules. It prompts for an AFS password when needed, authenticates through `ka_UserAuthenticateGeneral`, sets a PAG, and arranges Kerberos ticket-file ownership when built in Kerberos mode.

## Important APIs, Types, And Functions
The main function is `afs_authenticate`. Supporting no-op callbacks are `afs_chpass`, `afs_passwdexpired`, `afs_passwdrestrictions`, and `afs_getpasswd`. It uses `ka_UserAuthenticateGeneral`, `getpass`, `getpwnam`, `aix_ktc_setup_ticket_file`, and AIX auth return constants such as `AUTH_SUCCESS`, `AUTH_FAILURE`, and `AUTH_NOTFOUND`.

## Control Flow
`afs_authenticate` clears reentry/message outputs, uses the provided response or prompts interactively, rejects empty passwords, verifies the user exists locally, then calls kauth with `KA_USERAUTH_VERSION + KA_USERAUTH_DOSETPAG`. `KANOENT` maps to not-found; other kauth failures allocate a message. On success it calls `aix_ktc_setup_ticket_file` and returns success. The other callbacks are success/no-op except `afs_getpasswd`, which returns `NULL` and sets `ENOSYS`.

## State And Persistence
Authentication can create/set AFS authentication state and a PAG through kauth. It may also affect Kerberos ticket-file ownership through the helper. Allocated error messages are returned to AIX for display/cleanup.

## Dependencies And Integration Points
This file is compiled for `AFS_AIX41_ENV` and used by both AIX 4 and AIX 5 kauth dynamic modules. It depends on AIX user security, passwd lookup, OpenAFS kauth/kautils, and prototypes from `aix_auth_prototypes.h`.

## Risks And Test Signals
Risks include use of `getpass`, fixed-size `sprintf` buffers, typoed error text, local passwd requirement before AFS auth, and message allocation ownership assumptions. Tests should cover response-supplied and prompt-based auth, empty password rejection, nonexistent user, `KANOENT`, general kauth failures, successful PAG creation, and ticket-file setup in Kerberos builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_auth_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_auth_prototypes.h -->
# sources/distributed-fs/openafs/src/tsm41/aix_auth_prototypes.h

## Purpose
Declares the AIX authentication callbacks and ticket-file helper used by the TSM/LAM dynamic auth modules.

## Important APIs, Types, And Functions
The header declares `afs_authenticate`, `afs_chpass`, `afs_passwdexpired`, `afs_passwdrestrictions`, `afs_getpasswd`, and `aix_ktc_setup_ticket_file`. Signatures match the AIX security method callback style with user names, password/message pointers, and reentry indicators.

## Control Flow
The header itself has no control flow. Initializer modules use these prototypes to assign callbacks into `secmethod_table`; implementation files provide kauth and no-op behavior.

## State And Persistence
No state is stored here. The declared functions may create authentication/PAG/token/ticket-file side effects at runtime.

## Dependencies And Integration Points
It is included by `aix41_auth.c`, `aix5_auth.c`, `aix_auth_common.c`, `aix_aklog.c`, and `aix_ktc.c`. It must remain consistent with AIX `usersec.h` callback expectations and the implementations.

## Risks And Test Signals
Risks are prototype drift against AIX headers and implementation mismatches. Compile warnings/errors in the AIX TSM module build are the primary signal, followed by module load and callback invocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_auth_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_ident_prototypes.h -->
# sources/distributed-fs/openafs/src/tsm41/aix_ident_prototypes.h

## Purpose
Declares identity lookup callback stubs for the AIX 4 OpenAFS security method.

## Important APIs, Types, And Functions
The header declares `afs_getgrset`, `afs_getgrgid`, `afs_getgrnam`, `afs_getpwnam`, and `afs_getpwuid`, with return types involving `int`, `struct group *`, and `struct passwd *`.

## Control Flow
There is no executable flow. `aix41_auth.c` installs the declared callbacks into `secmethod_table`, and `aix41_ident.c` implements null-return stubs.

## State And Persistence
No state is owned. Runtime behavior is to decline identity data so AIX can fall back to local lookup behavior.

## Dependencies And Integration Points
The declarations depend on consumers having appropriate `struct group` and `struct passwd` declarations in scope. This header is specific to AIX 4.1 identity integration.

## Risks And Test Signals
This header contains conflicting declarations for `afs_getpwnam` with different argument/return types, and the implementation also differs. Strict C compilers or modern headers may reject it. Build coverage on the intended AIX compiler and security-method callback tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_ident_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_ktc.c -->
# sources/distributed-fs/openafs/src/tsm41/aix_ktc.c

## Purpose
Provides a small helper for AIX kauth modules to adjust Kerberos ticket-file ownership after successful authentication.

## Important APIs, Types, And Functions
The only function is `aix_ktc_setup_ticket_file(char *userName)`, compiled for `AFS_AIX41_ENV`. When `AFS_KERBEROS_ENV` is defined, it uses `getpwnam`, `ktc_tkt_string_uid`, and `chown`.

## Control Flow
The helper opens the passwd database, resolves the authenticated user, and if found changes ownership of the user's ktc ticket-file path to the user's uid/gid. It prints `perror` diagnostics on `chown` or `getpwnam` failures and closes the passwd database.

## State And Persistence
In Kerberos builds it persists filesystem metadata changes on the ticket file path. Non-Kerberos builds compile the function as a no-op. It reads passwd database state.

## Dependencies And Integration Points
It is called after `ka_UserAuthenticateGeneral` succeeds in `aix_auth_common.c`. It depends on OpenAFS ktc APIs and AIX/POSIX passwd and ownership APIs.

## Risks And Test Signals
Risks include changing ownership of an unexpected path from `ktc_tkt_string_uid`, weak error reporting through stderr/perror in an auth module context, and no action in non-Kerberos builds. Tests should cover Kerberos and non-Kerberos builds, existing and missing passwd entries, chown failure, and resulting ticket-file ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tsm41/aix_ktc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tubik/Makefile.in -->
# sources/distributed-fs/openafs/src/tubik/Makefile.in

## Purpose
Builds pthreaded ubik test/debug utilities from the canonical `src/ubik` sources, especially `udebug`, `utst_server`, and `utst_client`.

## Important APIs, Types, And Functions
Targets generate `utst_int.cs.c`, `utst_int.ss.c`, `utst_int.xdr.c`, and `utst_int.h` via `RXGEN`, then build `utst_server`, `utst_client`, and `udebug`. It defines `LTLIBS` with util, ubik, and cmd libraries and includes pthread build fragments.

## Control Flow
`all` builds the three utilities. Source object rules compile files from `$(UBIK)`. Install/dest only place `udebug` into bindirs when `ENABLE_PTHREADED_UBIK` is `yes`; test clients are build/test artifacts. Clean removes objects, binaries, generated RPC files, and version files.

## State And Persistence
Build output includes generated RPC interface files and utility binaries. Installed persistent artifacts are limited to `udebug` under configured paths when enabled.

## Dependencies And Integration Points
This makefile integrates pthread config, ubik library output, rxgen-generated test interfaces, and OpenAFS install paths. It mirrors part of `src/ubik/Makefile.in` for pthreaded builds.

## Risks And Test Signals
Risks include generated file ordering, divergence from the canonical ubik makefile, and conditional install behavior. Signals are successful generation/build of test interfaces, `udebug` link success, `make test`, and install/dest behavior with pthreaded ubik enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tubik/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tvlserver/Makefile.in -->
# sources/distributed-fs/openafs/src/tvlserver/Makefile.in

## Purpose
Builds pthreaded versions of Volume Location Server tools from `src/vlserver`: `vlserver`, `vlclient`, `cnvldb`, and `vldb_check`, plus generated VL RPC and error headers.

## Important APIs, Types, And Functions
Targets include `vlserver`, `vlclient`, `cnvldb`, `vldb_check`, generated `vldbint.ss.c`, `vldbint.xdr.c`, `vldbint.h`, `vl_errors.c`, and `vlserver.h`. Library groups combine pthreaded ubik, sys, Rx, rxstat, rxkad, lwpcompat, cmd, util, opr, audit, and vldb client libraries.

## Control Flow
The makefile compiles source files from `$(VLSERVER)`, runs `RXGEN` on `vldbint.xg`, runs compile_et on `vl_errors.et`, links tools with static libtool rules, and conditionally installs server/checker/converter when `ENABLE_PTHREADED_UBIK` is `yes`. `vlclient` is built but not installed by the install target.

## State And Persistence
Generated files, objects, and binaries are build artifacts. Installed outputs persist server-side VLDB tools in configured directories. Runtime VLDB state is unaffected by the build.

## Dependencies And Integration Points
This is a pthreaded wrapper around the canonical VL server source tree and ubik library. It depends on rxgen, compile_et, version generation, OpenAFS library targets, and pthread configuration.

## Risks And Test Signals
Risks include missing dependency edges for generated headers, conditional installation surprises, and link-order differences from non-threaded builds. Test signals are a full `make all`, regenerated interface/error files, `vlserver` and `vldb_check` link success, and install gating with `ENABLE_PTHREADED_UBIK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tvlserver/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tvolser/Makefile.in -->
# sources/distributed-fs/openafs/src/tvolser/Makefile.in

## Purpose
Builds the threaded volume server (`volserver`) and volume administration client (`vos`) from canonical volser, vol, dir, and vlserver sources.

## Important APIs, Types, And Functions
Object groups include volserver RPC/procedure objects, VLDB client RPC objects, directory objects, volume package objects, and common libraries. Generated files include `vl_errors.c`, `volerr.c`, and `volser.h`; volserver uses `volint.cs/ss/xdr` sources from `../volser`. Targets are `volserver`, `vos`, install/dest, and clean.

## Control Flow
The makefile compiles volser server/client sources with `-I../volser`, compiles shared volume and directory package files, generates error tables, links `vos` with ubik/volser client libraries, and links `volserver` with server-side ACL/common libraries. Install always installs `volserver`; `vos` installation is conditional on pthreaded ubik.

## State And Persistence
Build artifacts are objects, generated error headers/sources, `volserver`, and `vos`. Installed binaries affect persistent OpenAFS server/admin tooling, but the makefile itself does not touch volume data.

## Dependencies And Integration Points
This wrapper ties together volser RPC, VLDB interfaces, ubik client libraries, FSSYNC/SALVSYNC client support, volume package, directory package, rx/rxkad/rxstat, cmd, util, usd, and lwpcompat libraries. It has an AIX-specific link export flag for `volserver`.

## Risks And Test Signals
Risks include many shared sources compiled with different include paths/defines, generated header ordering, conditional `vos` install, and platform-specific linker flags. Signals include full threaded build, generated `volser.h` rebuilds, `vos` and `volserver` link success, AIX link testing, and install path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tvolser/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/Makefile.in -->
# sources/distributed-fs/openafs/src/ubik/Makefile.in

## Purpose
Builds the core ubik replicated database library, authenticated ubik client subset, generated ubik RPC interfaces, error headers, debug/test utilities, and libtool libraries.

## Important APIs, Types, And Functions
Important target groups are `LT_authent_objs`, `LT_objs`, `LT_deps`, `libubik.a`, `liboafs_ubik.la`, `libauthent_ubik.la`, `udebug`, `utst_server`, and `utst_client`. Generated outputs include `ubik_int.cs/ss/xdr.c`, `ubik_int.h`, kernel `Kubik_int.*`, `utst_int.*`, `uerrors.c`, and `ubik.h`.

## Control Flow
`all` performs dependency install, builds static and libtool libraries, and builds debug/test tools. RXGEN produces user and kernel ubik interfaces; compile_et produces ubik errors and public `ubik.h`. Installation copies `libubik.a`, `ubik.h`, `ubik_int.h`, and `udebug` to configured library/include/bindir paths. Clean removes objects, generated interfaces, error outputs, libraries, tools, and version files.

## State And Persistence
Persistent build/install artifacts are ubik libraries, public headers, generated RPC files, and `udebug`. Runtime database state is not affected by the makefile.

## Dependencies And Integration Points
The makefile is central to ubik consumers: ptserver, vlserver, volser, auth clients, and test tools. It integrates LWP build rules, rxgen, compile_et, libtool static/shared rules, auth/comerr/lwp/rx/util/opr dependencies, and public include/library install locations.

## Risks And Test Signals
Risks include ABI drift in generated RPC headers, mismatch between static and libtool object sets, generated kernel/user interface confusion, and public header install ordering. Test signals are full `make all`, generated-file determinism, `libubik.a` and `liboafs_ubik.la` link success, `udebug` smoke execution, and downstream rebuilds of pt/vl/volser targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/beacon.c -->
# sources/distributed-fs/openafs/src/ubik/beacon.c

## Purpose
Implements ubik beaconing and sync-site election. It builds the server list, initializes security connections, sends periodic vote beacons, determines whether the local site has quorum, handles clone/magic-host voting behavior, and exchanges multihomed address information.

## Important APIs, Types, And Functions
Public functions include `ubeacon_Debug`, `ubeacon_AmSyncSite`, `ubeacon_SyncSiteAdvertised`, `ubeacon_InitServerListByInfo`, `ubeacon_InitServerList`, `ubeacon_InitSecurityClass`, `ubeacon_NewVOTEConnection`, `ubeacon_ReinitServer`, `ubeacon_Interact`, `ubeacon_updateUbikNetworkAddress`, and `ubik_SetClientSecurityProcs`. Internal helpers are `amSyncSite`, `ubeacon_InitServerListCommon`, and `verifyInterfaceAddress`. Important globals include `nServers`, `amIMagic`, `amIClone`, `ubik_singleServer`, security callbacks, `addr_globals`, `beacon_globals`, `ubik_quorum`, and `ubik_servers`.

## Control Flow
Initialization verifies the local interface address, initializes a client security class, builds remote `ubik_server` records with separate vote and disk Rx connections, detects clone servers, chooses the lowest-address magic host for tie-breaking, computes quorum, and special-cases single-server cells as sync site. `ubeacon_Interact` loops every `POLLTIME`, skips if another candidate is better, multicasts `VOTE_Beacon` calls, validates returned vote times and connection errors, updates per-server up/vote state, asks the local vote module for a self-vote, and sets or clears sync-site state based on weighted vote totals. Address exchange calls `DISK_UpdateInterfaceAddr` on remotes and updates alternate addresses.

## State And Persistence
The file maintains in-memory cluster membership/election state: server connection lists, vote times, server up/down flags, sync-site expiration, advertised status, epoch time, security class/index, and local interface addresses. It does not directly write the ubik database, but becoming sync site updates `version_globals.ubik_epochTime` under database/version locks.

## Dependencies And Integration Points
It integrates with Rx/rx_multi, rxkad/rxnull security, cell config/netinfo/netrestrict parsing, ubik vote service, ubik disk service, recovery reset/lost-server hooks, `ubik_dbase` locking/version state, and server address utilities. It is tightly coupled with `vote.c`, `recovery.c`, `remote.c`, and `ubik.p.h` internals.

## Risks And Test Signals
Risks include election timing invariants, lock ordering between DB/beacon/address/version locks, stale security token reconnection, multihomed address verification errors, clone quorum handling, and treating anomalous positive vote values as transport/security failures. Tests should cover single-server startup, clone servers, even-sized magic-host tie-break, vote expiry, loss/regain of quorum, netinfo/netrestrict address selection, `DISK_UpdateInterfaceAddr` compatibility errors, token refresh, and recovery reset when sync-site status is lost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/beacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/disk.c -->
# sources/distributed-fs/openafs/src/ubik/disk.c

## Purpose
Implements ubik's local transactional disk layer: a fixed-size page cache, write-ahead log record generation, read/write/truncate operations, transaction begin/commit/abort/end, dirty-buffer flushing, and database version labeling on commit.

## Important APIs, Types, And Functions
Public functions include `udisk_Debug`, `udisk_Init`, `udisk_Invalidate`, `udisk_read`, `udisk_truncate`, `udisk_write`, `udisk_begin`, `udisk_commit`, `udisk_abort`, and `udisk_end`. Internal helpers include `udisk_LogOpcode`, `udisk_LogEnd`, `udisk_LogTruncate`, `udisk_LogWriteData`, `DRead`, `DNew`, `DRelease`, `DFlush`, `DSync`, `DAbort`, `DTrunc`, truncation-list helpers, `FixupBucket`, `newslot`, `DedupBuffer`, and `unthread`.

## Control Flow
`udisk_Init` allocates page metadata and data buffers and initializes an LRU ring/hash table. Reads find a clean visible page for read transactions, prefer dirty pages for write transactions, or allocate/read a page from physical storage. Writes first append log data, then update cached pages and mark them dirty. Truncates are logged but deferred in a transaction truncation list. A write transaction begins by logging `LOGNEW` and setting `DBWRITING`. Commit may relabel a newly elected sync site's database, increments the version counter, logs `LOGEND`, flushes dirty buffers to files, syncs files, applies truncations, writes the database label, and truncates the log. Abort logs `LOGABORT`, truncates the log, and discards dirty buffers.

## State And Persistence
Persistent state is the ubik database files and log file through `ubik_dbase` physical callbacks. In-memory state includes global page buffers, hash/LRU structures, dirty/locker flags, transaction lists, active truncations, `DBWRITING`, reader count, version fields, and write transaction counters. Commit ordering is designed so crash recovery can replay a committed log or ignore an uncommitted one.

## Dependencies And Integration Points
This file depends on ubik database callbacks for physical read/write/sync/truncate/setlabel/buffered append, beacon sync-site checks, recovery flags and quorum version propagation, lock release from `lock.c`, condition/LWP wakeups, and network propagation via `ContactQuorum_DISK_SetVersion`.

## Risks And Test Signals
Risks include global cache state shared across databases, no explicit allocation failure checks for buffer arrays, LRU exhaustion when all buffers are locked or dirty, subtle read visibility rules around dirty duplicate pages, panic-on-I/O-error after commit point, and strict log format coupling with `recovery.c`. Tests should cover read/write transactions, abort discarding uncommitted changes, commit log replay after crash, truncate ordering, version counter updates, dirty duplicate invalidation, low-buffer pressure, read transactions not seeing uncommitted writes, and wakeup behavior for blocked writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/disk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/lock.c -->
# sources/distributed-fs/openafs/src/ubik/lock.c

## Purpose
Provides ubik transaction-level read/write locking over a single database-wide `rwlock`. It supports two-phase locking by associating one lock type with each transaction and releasing only when the transaction ends.

## Important APIs, Types, And Functions
Public functions are `ulock_Init`, `ulock_getLock`, `ulock_relLock`, and `ulock_Debug`. The module-level lock is `struct Lock rwlock`. Helper macros `WouldReadBlock` and `WouldWriteBlock` inspect existing write/read/wait state for nonblocking lock attempts.

## Control Flow
`ulock_Init` initializes the lock. `ulock_getLock` validates requested type and transaction state, rejects duplicate locks and some read/write upgrade misuse, optionally checks whether a nonblocking attempt would fail, marks the transaction as `LOCKWAIT`, releases the DB lock, obtains the read or write lock unless `TRREADWRITE` is set, reacquires the DB lock, and records the final lock type. `ulock_relLock` releases the recorded read/write lock unless the transaction is flagged `TRREADWRITE`, then clears the transaction lock type. `ulock_Debug` reports current read/write lock presence.

## State And Persistence
State is process-local: the global lock and each transaction's `locktype`. No disk state is modified directly, but lock behavior controls safe access to transactional database state.

## Dependencies And Integration Points
The module depends on OpenAFS lock primitives, DBHOLD/DBRELE ordering from ubik internals, transaction flags from `ubik.h`, and `udisk_end`, which releases locks at transaction teardown.

## Risks And Test Signals
Risks include a likely inverted nonblocking helper macro interpretation, deadlocks if callers request locks out of order, aborts on duplicate lock attempts, and special `TRREADWRITE` behavior bypassing actual locks. Tests should cover read/read concurrency, write exclusion, nonblocking `EAGAIN`, lock release on abort/end, duplicate lock detection, and debug field accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/phys.c -->
# sources/distributed-fs/openafs/src/ubik/phys.c

## Purpose
Implements the default physical storage backend for ubik database files. It maps ubik file ids to on-disk pathnames, handles header offsets, caches file descriptors, performs read/write/truncate/sync/stat operations, and reads/writes database version labels.

## Important APIs, Types, And Functions
Public callbacks include `uphys_stat`, `uphys_read`, `uphys_write`, `uphys_truncate`, `uphys_getnfiles`, `uphys_getlabel`, `uphys_setlabel`, `uphys_sync`, `uphys_invalidate`, and `uphys_buf_append`. Internal helpers are `uphys_open`, `uphys_close`, `uphys_pread`, `uphys_pwrite`, `uphys_buf_append_open`, and `uphys_buf_flush`. File descriptor state lives in `fdcache[MAXFDCACHE]` and `buf_fdcache`.

## Control Flow
`uphys_open` lazily initializes the fd cache, reuses an idle cached descriptor for the requested file id, or opens/creates `<pathName>.DB[SYS]<id>` and inserts it into a free/reclaimable slot. Data reads/writes add `HDRSIZE` to logical offsets so database labels live in file headers. Labels are stored as `struct ubik_hdr` with network-order version, magic, and header size. Truncate and sync flush any buffered append stream first. `uphys_buf_append` uses a cached `FILE *` in append mode for log writes that can be buffered before an explicit sync.

## State And Persistence
Persistent state is the database files under `adbase->pathName`, including system log files and header labels. Process state includes fd cache entries, refcounts, a single buffered append stream, and a static pathname buffer. `uphys_invalidate` marks cached descriptors stale and closes idle ones.

## Dependencies And Integration Points
This backend is installed in ubik database structures and is called by `disk.c` and `recovery.c`. It depends on POSIX file APIs, optional `pread/pwrite`, LWP include context, `HDRSIZE`, `UBIK_MAGIC`, and ubik version/header definitions.

## Risks And Test Signals
Risks include static global fd caches not keyed by database path, no locking around caches, append stream interaction with descriptor cache, pathname truncation in `pbuffer`, open fallback to read-only while later write paths may fail, and `uphys_getnfiles` hardcoded to one data file. Tests should cover label read/write, logical offset header adjustment, log buffered append followed by sync/truncate, fd cache reuse/invalidate, read-only open failures, crash persistence via fsync, and multiple ubik database instances if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/phys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/recovery.c -->
# sources/distributed-fs/openafs/src/ubik/recovery.c

## Purpose
Implements ubik recovery: crash log replay, local database initialization, determining when a server has a current database, probing down peers, finding the best database version after election, fetching it to the sync site, relabeling newly initialized databases, and distributing the current database to other servers.

## Important APIs, Types, And Functions
Public functions are `urecovery_ResetState`, `urecovery_LostServer`, `urecovery_AllBetter`, `urecovery_AbortAll`, `urecovery_CheckTid`, `urecovery_Initialize`, `urecovery_Interact`, and `DoProbe`. Internal helpers are `ReplayLog` and `InitializeDB`. Important globals include `ubikPrimaryAddrOnly`, `urecovery_state`, `ubik_dbase`, `ubik_servers`, `ubik_quorum`, and `ubik_currentTrans`.

## Control Flow
Startup calls `urecovery_Initialize`, which holds the DB lock, replays any committed log, truncates the log, and reads or creates the database label. The recovery thread loops every few seconds, probes down servers periodically, exits early unless this site is sync site, polls up non-clone servers for versions, proceeds only after contacting quorum, fetches the best version via `DISK_GetFile` if local state is stale, writes the incoming database to a temporary file with an invalid label, renames and labels it on success, upgrades epoch 1 newly initialized databases to epoch 2 after quorum, and sends the current database to peers with stale versions via `DISK_SendFile`.

## State And Persistence
Persistent state includes database files, temporary fetch files, labels, and the replayed/truncated log. In-memory recovery state is a bitmask indicating sync-site, found-db, have-db, relabeled-db, and sent-db progress, plus per-server version/current/up fields. Fetch failures can invalidate local version to `0.0`; successful sends mark remote current state.

## Dependencies And Integration Points
The file is tightly coupled to `disk.c` log format, physical database callbacks, `beacon.c` sync-site/quorum/up status, `vote.c` sync/version knowledge, Rx bulk calls generated from `ubik_int.xg`, server connection/address state, transaction abort/end logic, and platform rename behavior.

## Risks And Test Signals
Risks include log format drift, recovery proceeding only after quorum version probes, temporary-file rename failure paths, invalidating old data after fetch failure, long waits for `DBWRITING`, multi-interface probe connection replacement, and frequent low-level logging while peers are down. Tests should cover committed and uncommitted log replay, new database labeling, sync-site election followed by best-version discovery, fetch success/failure, send-to-peer success/failure, down-server probing over alternate interfaces and primary-only mode, remote transaction tid mismatch aborts, and `urecovery_AllBetter` for sync and non-sync sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ubik/recovery.c -->
