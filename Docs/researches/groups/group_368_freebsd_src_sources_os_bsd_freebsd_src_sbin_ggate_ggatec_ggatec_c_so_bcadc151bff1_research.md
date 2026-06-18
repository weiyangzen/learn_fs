# Group Research: group_368_freebsd_src_sources_os_bsd_freebsd_src_sbin_ggate_ggatec_ggatec_c_so_bcadc151bff1

Read all listed files completely. Scope is within `Docs/research_subset_a.md` via `sources/os/bsd/freebsd-src`.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/ggatec.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/ggatec.c

`ggatec.c` implements the GEOM Gate network client. It supports `create`, `rescue`, `destroy`, and `list`, creating a local `/dev/ggateN` provider backed by a remote `ggated` export.

Key behavior:
- Establishes two TCP connections to the server, paired by a random token: one for client receive/server send and one for client send/server receive.
- Performs a version handshake using `GGATE_MAGIC` and `GGATE_VERSION`, then sends `g_gate_cinit` with path, flags, token, and connection direction.
- Receives remote media size and sector size through `g_gate_sinit`; user-provided sector size overrides server sector size only when set.
- `send_thread()` waits for kernel GEOM requests via `G_GATE_CMD_START`, translates `BIO_READ`, `BIO_WRITE`, and `BIO_FLUSH` into ggate protocol commands, and sends headers/data to the server.
- `recv_thread()` receives server completions, optional read data, and completes kernel requests with `G_GATE_CMD_DONE`.
- Reconnection is coordinated with a global `reconnect` flag and `SIGUSR1` to interrupt the peer thread; `g_gatec_loop()` reconnects and cancels outstanding requests.
- `create` loads/open the GEOM gate control device, creates the provider, daemonizes unless verbose, then enters the reconnect loop.
- `rescue` reconnects to an existing unit and cancels outstanding kernel requests before serving.
- `destroy` and `list` delegate to shared helpers.

Important details:
- Buffer sizing starts from `kern.maxphys` when available, otherwise 128 KiB.
- `-o ro|wo|rw|direct`, `-n`, `-p`, `-q`, `-R`, `-S`, `-s`, `-t`, `-u`, and `-v` are parsed with action-specific validation.
- Network fields are byte-swapped with shared inline helpers from `ggate.h`.
- Error handling generally exits through `g_gate_xlog()` for unrecoverable ioctl/protocol failures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/ggatec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggated/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggated/Makefile

Builds the `ggated` daemon.

Key contents:
- Adds `.PATH` for the shared ggate sources.
- Builds `ggated` from `ggated.c` and shared `ggate.c`.
- Installs man page `ggated.8`.
- Assigns package `ggate`.
- Links `pthread` and `util`.
- Adds include path for `../shared`.

This target does not define `LIBGEOM`, so the shared `g_gate_list()` implementation is excluded for this daemon.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggated/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggated/ggated.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggated/ggated.c

`ggated.c` implements the GEOM Gate TCP server. It exports local files/devices listed in an exports file, validates remote clients, and services protocol requests against the backing object.

Key behavior:
- Default exports file is `/etc/gg.exports`.
- Parses export lines as remote IP or host with optional CIDR mask, flags, and path.
- Supports export access flags `ro`, `rd`, `wo`, `rw`, plus `direct` and `nodirect`.
- Validates each incoming client by source address, requested path, requested access mode, and direct-I/O policy.
- Uses the shared ggate handshake: receives version, validates magic/version, receives `g_gate_cinit`, and responds with `g_gate_sinit`.
- Pairs two sockets into a `ggd_connection` by token. Incomplete connections older than 10 seconds are cleaned up.
- Once both sockets are present, forks a child process for that connection, removes it from the parent list, and lets the child serve I/O.
- Child process creates three threads:
  - `recv_thread()` receives protocol headers and write data, then queues requests.
  - `disk_thread()` performs `pread`, `pwrite`, or `fsync` against the exported object.
  - `send_thread()` sends completion headers and read data back to the client.
- Uses queue mutexes and condition variables for request handoff.
- Supports daemon mode, pidfile management, bind address selection, custom port, socket buffer tuning, verbose foreground mode, and SIGHUP export reload.

Important details:
- Request bounds and alignment are enforced with assertions in `disk_thread()`.
- Short reads/writes are reported as `EIO` when errno is otherwise zero.
- `BIO_FLUSH` maps to `fsync()`.
- `malloc_waitok()` retries allocations indefinitely for per-request memory.
- SIGHUP reload is processed in the accept loop before handling the next connection.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggated/ggated.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/Makefile

Builds the local GEOM Gate provider utility `ggatel`.

Key contents:
- Adds `.PATH` for shared ggate sources.
- Builds from `ggatel.c` and shared `ggate.c`.
- Installs `ggatel.8`.
- Assigns package `ggate`.
- Defines `LIBGEOM`, enabling shared provider-listing code.
- Includes shared headers and links `geom` and `util`.

Unlike `ggated`, this target does not link pthread because `ggatel` serves synchronously in one worker loop.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/ggatel.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/ggatel.c

`ggatel.c` implements a local GEOM Gate provider backed directly by a local file or character device, without the network protocol.

Key behavior:
- Supports `create`, `rescue`, `destroy`, and `list`.
- `create` opens the backing path, creates a GEOM Gate provider with local media size and sector size, then serves requests.
- `rescue` opens the path, cancels outstanding requests for an existing unit, and resumes serving.
- `destroy` and `list` use shared ggate helpers.
- `g_gatel_serve()` daemonizes unless verbose, waits for kernel requests with `G_GATE_CMD_START`, performs local I/O, then completes requests with `G_GATE_CMD_DONE`.
- Handles `BIO_READ` with `pread()` and `BIO_WRITE`/`BIO_DELETE` with `pwrite()`.
- Unsupported commands return `EOPNOTSUPP`.
- Buffer grows on `ENOMEM` from the GEOM ioctl path or on large reads.

Important details:
- Access mode follows `-o ro|wo|rw`; `-o direct` adds direct I/O behavior to local opens.
- `create` opens with `O_DIRECT | O_FSYNC` in addition to the chosen access mode.
- `rescue` uses access flags but not the `O_DIRECT | O_FSYNC` additions used by `create`.
- Sector size and timeout are configurable only on create.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/ggatel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.c

`ggate.c` contains shared support for `ggatec`, `ggated`, and `ggatel`.

Key behavior:
- Provides logging wrappers that write to stdout in verbose mode or syslog otherwise.
- Provides fatal logging helpers that exit after reporting an error.
- Determines media size and sector size for character devices via disk ioctls, and for regular files via `stat`.
- Opens, closes, and performs ioctls on `/dev/<G_GATE_CTL_NAME>`.
- Destroys GEOM Gate units and loads `geom_gate` if the kernel module is absent.
- Provides robust send/receive wrappers:
  - `g_gate_send()` loops until all data is sent or an error occurs and optionally chunks sends by `MAX_SEND_SIZE`.
  - `g_gate_recv()` retries `EAGAIN`.
- Applies TCP/socket settings: `TCP_NODELAY` depending on global `nagle`, `SO_REUSEADDR`, receive/send buffers, and 8-second send/receive timeouts.
- When `LIBGEOM` is defined, implements provider listing by walking the libgeom tree and printing brief or verbose provider metadata.
- Resolves numeric IPv4 addresses or hostnames with `inet_addr()` and `gethostbyname()`.

Important details:
- Default `nagle` value is 1, but the code sets `TCP_NODELAY` when `nagle` is true; `-n` clears it.
- `MAX_SEND_SIZE` defaults to `MAXPHYS`, but comments describe a `ggatec` build-time workaround for large send performance.
- The libgeom listing path prints provider name, info, access, timeout, queue counts, references, media size, sector size, and mode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.h

`ggate.h` defines the shared userland GEOM Gate protocol and helper API.

Key definitions:
- Default TCP port, socket buffers, queue size, and timeout.
- Protocol magic string `GGATE_MAGIC`, protocol version `GGATE_VERSION`, and command codes for read, write, and flush.
- Protocol flags for read-only/write-only, send socket, receive socket, and direct I/O.
- Packed wire structs:
  - `g_gate_version`
  - `g_gate_cinit`
  - `g_gate_sinit`
  - `g_gate_hdr`
- Declarations for logging, device control, media/sector probing, socket I/O, socket tuning, provider listing, and hostname/IP resolution.
- Inline byte-order conversion helpers for all protocol structs.

Important details:
- The protocol uses big-endian/network order for multi-byte wire fields.
- The comments document the two-socket connection role: `GGATE_FLAG_SEND` and `GGATE_FLAG_RECV` distinguish the paired data channels.
- `g_gate_sinit` and `g_gate_hdr` swap only the fields that are actually used.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/growfs/Makefile

Builds the `growfs` utility.

Key contents:
- Includes `src.opts.mk`.
- Assigns package `ufs`.
- Builds `growfs` from `growfs.c`, with man page `growfs.8`.
- Optional `GFSDBG` adds `debug.c`, defines `FS_DEBUG`, and disables cast-alignment warnings.
- Links `ufs` and `util`.
- Declares tests and descends into `tests` when `MK_TESTS` is enabled.

This makefile keeps debug dumping out of normal builds unless explicitly requested.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/debug.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/growfs/debug.c

`debug.c` is compiled only with `FS_DEBUG` and provides detailed dump routines for growfs internals.

Key behavior:
- Opens/closes a debug output file, with `-` mapped to `/dev/stdout`.
- Dumps full filesystem blocks as hex.
- Dumps UFS superblock fields, including legacy UFS1 fields, UFS2 fields, cylinder summary totals, snapshot inode list, flags, and geometry values.
- Dumps cylinder group fields and embedded cylinder summary.
- Dumps cylinder summaries and total cylinder summaries.
- Dumps inode allocation, fragment allocation, cluster allocation, and cluster summary maps.
- Contains disabled legacy code for rotational layout tables under `NOT_CURRENTLY`.
- Dumps UFS1 and UFS2 dinodes, including direct and indirect block pointers relevant to file size.
- Dumps indirect blocks with element width selected by filesystem type.

Important details:
- All functions return immediately if the debug log is not open.
- The file is diagnostic-only and has no effect in normal builds.
- Some formatting accesses wide fields via integer pointer casts, which is why the debug build disables cast-alignment warnings.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/debug.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/growfs/debug.h

`debug.h` defines the growfs debug API and turns it into no-op macros when `FS_DEBUG` is not set.

Key contents:
- Under `FS_DEBUG`, declares dump functions for superblocks, cylinder groups, cylinder summaries, inode maps, fragment maps, cluster maps, inodes, indirect blocks, and hex blocks.
- Defines debug levels `DL_TRC` and `DL_INFO` and external `_dbg_lvl_`.
- Provides tracing macros for function entry/exit, trace points, and formatted debug printing.
- Selects UFS1 or UFS2 inode dump based on `fs_magic`.
- Without `FS_DEBUG`, all debug macros expand to nothing.

This header lets `growfs.c` contain extensive instrumentation with zero normal-build runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/growfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/growfs/growfs.c

`growfs.c` implements UFS filesystem growth for FreeBSD. It increases an existing UFS filesystem to a larger device or requested size by recalculating superblock fields, updating cylinder group metadata, and writing new summaries.

Key behavior:
- Parses `-N` dry-run, `-s size`, compatibility `-v`, and `-y` assume-yes.
- Resolves a device from either a special device path or a mounted filesystem using `getmntpoint()` and mount metadata.
- Reads the existing superblock via `sbget()`, rejects unclean filesystems, and copies old/new superblock state into separate globals.
- Defaults target size to provider size, or validates requested size suffixes `b`, `k`, `m`, `g`, `t`.
- Aligns target size to filesystem fragment size.
- Rejects shrink/no-op requests.
- Rejects active snapshots unless `-y` is used.
- Prompts before destructive growth unless `-y` or dry-run is used.
- If mounted read-write, uses `/dev/ufssuspend` and `UFSSUSPEND`/`UFSRESUME`; otherwise opens the device directly for writing.
- Tests read/write access to the new last filesystem fragment before modifying metadata.
- Recomputes `fs_size`, `fs_providersize`, UFS1 cylinder counts, `fs_ncg`, and `fs_cssize`.
- Drops an unusable final cylinder group if it lacks room for at least one data block.
- `growfs()` coordinates the actual metadata update:
  - Loads cylinder summaries.
  - Updates the former last cylinder group with new free fragments/blocks.
  - Initializes new cylinder groups.
  - Relocates cylinder summary storage when it grows.
  - Cleans dynamic superblock fields.
  - Writes the updated superblock with `sbput()`.
- `initcg()` creates a new cylinder group, initializes inode generation numbers, free block/fragment maps, cluster summaries, and cylinder summaries.
- `updjcg()` expands the old last cylinder group and updates free-space accounting.
- `updcsloc()` relocates cylinder summary data to the first newly created complete cylinder group when extra summary fragments are required.
- `frag_adjust()`, `updclst()`, `isblock()`, `setblock()`, and `clrblock()` manipulate UFS allocation maps and summary counters.
- `cgckhash()` recalculates cylinder-group CRC32C when metadata check hashes are enabled.

Important details:
- The source comments explicitly call out snapshot and crash-ordering limitations.
- Dry-run mode skips writes, but one branch notes it cannot fully simulate reading newly written cylinder-group data.
- The code supports both UFS1 and UFS2 layout differences.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/growfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/growfs/tests/Makefile

Defines the growfs legacy TAP test.

Key contents:
- `TAP_TESTS_PERL= legacy_test`
- Includes `bsd.test.mk`.

The test is Perl-based and runs through the FreeBSD test framework.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/tests/legacy_test.pl -->
# File Research: sources/os/bsd/freebsd-src/sbin/growfs/tests/legacy_test.pl

`legacy_test.pl` is a root-only TAP test for growfs.

Key behavior:
- Plans 19 tests.
- Creates a 40 MiB md device and cleans it up in `END`.
- Uses `gpart restore` to resize an `a` partition.
- Initializes UFS1 and UFS2 filesystems with `newfs -O`.
- Validates filesystems with `fsck_ffs -Ffy`, accepting exit status 0 or 7.
- Grows from 10 MiB to 20 MiB with zero-filled new space.
- Grows from 20 MiB to 30 MiB with patterned garbage-filled new space.
- Runs `growfs -y` for both growth steps.
- Handles growfs output that reports unallocatable trailing sectors by zeroing those sectors before fsck.
- Skips all tests when not run as UID 0.

This test exercises both clean and garbage-filled expansion regions for UFS1 and UFS2.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/growfs/tests/legacy_test.pl -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastctl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastctl/Makefile

Builds `hastctl`, the HAST control utility.

Key contents:
- Includes many source files from sibling `hastd` via `.PATH`.
- Builds control utility support for activemap, buffers, checksum, compression, protocol, metadata, nv pairs, parser/lexer, logging, and common proto/subr code.
- Links `md`, `util`, and `z`.
- Defines Capsicum, IPv4, and optional IPv6 support.
- Defines lexer flags to avoid unused input/unput code.
- Generates parser artifacts from yacc/lex inputs and cleans them.

This target shares most of the HAST library-like implementation with `hastd` but uses `hastctl.c` as the command frontend.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastctl/hastctl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastctl/hastctl.c

`hastctl.c` implements the command-line frontend for HAST administration.

Key behavior:
- Supports commands `create`, `role`, `list`, `status`, and `dump`.
- Reads configuration from `/etc/hast.conf` by default, overrideable with `-c`.
- `create` initializes local metadata and active bitmap directly:
  - Probes local provider.
  - Validates media size, sector size, and extent size.
  - Computes activemap on-disk size.
  - Sets data size, extent size, keepdirty, and local data offset.
  - Writes metadata and zeroes the initial bitmap area.
- `dump` reads and prints on-disk metadata for configured resources.
- `role` sends `HASTCTL_CMD_SETROLE` with `init`, `primary`, or `secondary`.
- `list` and `status` send `HASTCTL_CMD_STATUS`.
- Uses nv pairs over the configured control proto connection to communicate with `hastd`.
- Drops privileges after connecting to the control socket and before sending commands.
- Formats detailed status including role, provider, local path, remote/source addresses, replication mode, dirty bytes, worker pid, statistics, errors, and queue sizes.
- `status` prints a compact tabular view.

Important details:
- `create` defaults extent size to `HAST_EXTENTSIZE` and keepdirty to `HAST_KEEPDIRTY`.
- `all` is accepted for role/list/status/dump where appropriate.
- Unknown resources are reported without aborting the whole multi-resource command unless they determine the final exit code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastctl/hastctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/Makefile

Builds the `hastd` daemon.

Key contents:
- Builds daemon sources for activemap, control, ebuf, event, checksum, compression, protocol, hooks, metadata, nv, secondary, primary, parser/lexer, socket protocols, rangelock, and common helpers.
- Installs `hastd.8` and `hast.conf.5`.
- Defines Capsicum, default TCP port 8457, IPv4, and optional IPv6 support.
- Links `geom`, `md`, `pthread`, `util`, and `z`.
- Generates and cleans yacc/lex artifacts.

This is the full HAST runtime target, including primary/secondary worker roles and network protocol support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/activemap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/activemap.c

`activemap.c` implements HAST dirty-extent tracking for replication and resynchronization.

Key behavior:
- Tracks extents over a media range using:
  - `am_memtab`: pending write/reference count per extent.
  - `am_memmap`: in-memory dirty bitmap.
  - `am_diskmap`: bitmap image intended for disk.
  - `am_syncmap`: extents needing synchronization.
  - `am_keepdirty`: LRU-ish list of recently dirty extents kept dirty to reduce bitmap updates.
- `activemap_init()` validates power-of-two extent/sector sizes, computes extent count, bitmap sizes, and allocates all maps.
- `activemap_write_start()` marks extents dirty before writes and reports when disk metadata should be updated.
- `activemap_write_complete()` decrements pending writes and cleans extents when no pending writes remain and they are not kept dirty.
- `activemap_extent_complete()` clears dirty state after a sync extent’s expected requests complete.
- `activemap_copyin()` loads an on-disk bitmap and initializes pending request counts for dirty extents.
- `activemap_merge()` merges a remote dirty bitmap into local sync state.
- `activemap_bitmap()` materializes the disk bitmap from memory and overlays keep-dirty extents.
- `activemap_sync_offset()` iterates dirty extents in `MAXPHYS` chunks for resync work and returns completed extent IDs through `syncextp`.
- `activemap_need_sync()` marks extents for synchronization when a component is unavailable.
- `activemap_calc_ondisk_size()` computes the rounded bitmap storage size without creating a map.
- `activemap_dump()` prints memory/disk/sync bitmaps for diagnostics.

Important details:
- Extent size must be a power of two; `bitcount32(extentsize - 1)` derives the shift.
- Last extents shorter than full extent size are handled by `ext2reqs()` and `activemap_sync_offset()`.
- The keep-dirty cache can intentionally leave disk bitmap bits set even after memory writes complete.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/activemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/activemap.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/activemap.h

`activemap.h` declares the opaque activemap API used by HAST.

Key API groups:
- Lifecycle: `activemap_init()`, `activemap_free()`.
- Write tracking: `activemap_write_start()`, `activemap_write_complete()`, `activemap_extent_complete()`.
- Querying: `activemap_ndirty()`, `activemap_differ()`, `activemap_size()`, `activemap_ondisk_size()`.
- Bitmap I/O: `activemap_copyin()`, `activemap_merge()`, `activemap_bitmap()`, `activemap_calc_ondisk_size()`.
- Synchronization: `activemap_sync_rewind()`, `activemap_sync_offset()`, `activemap_need_sync()`.
- Diagnostic dump: `activemap_dump()`.

The header keeps `struct activemap` opaque to callers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/activemap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/control.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/control.c

`control.c` implements HAST control-plane handling between `hastctl`, the parent daemon, and worker processes.

Key behavior:
- `child_cleanup()` closes worker control/event/connection proto channels and clears the worker pid.
- Role changes:
  - Resolve resource by name.
  - Return previous role in the response.
  - If role changes, log it, update resource role, kill/wait for an existing worker, and start a primary worker when entering primary role.
  - Execute configured hooks for role transitions.
- `control_handle()` accepts a control socket connection from `hastctl`, receives an nv command, validates fields, dispatches `setrole` or `status`, and sends an nv response.
- Supports operating on all resources or selected resource names.
- `control_status()` emits static resource status fields and, when a worker exists, asks the worker for live status.
- `control_status_worker()` sends a `CONTROL_STATUS` request over the parent-worker control channel and copies worker counters/queue sizes into the user response.
- `ctrl_thread()` runs in a worker and handles parent requests:
  - `CONTROL_STATUS` returns complete/degraded status, dirty bytes, extent/keepdirty settings, I/O counters, error counters, and role-specific auxiliary queue information.
  - `CONTROL_RELOAD` applies primary config reload state.
  - Unknown commands return `EINVAL`.

Important details:
- Primary role asserts a worker should exist for status.
- Secondary status can be reported with or without a worker depending on state.
- Worker status treats missing remote input/output connections as degraded.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/control.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/control.h

`control.h` declares HAST control-plane entry points and worker command IDs.

Key contents:
- Worker control commands:
  - `CONTROL_STATUS`
  - `CONTROL_RELOAD`
- Declares:
  - `child_cleanup()`
  - `control_set_role()`
  - `control_handle()`
  - `ctrl_thread()`

This header is shared by parent daemon code and worker-role code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/control.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.c

`ebuf.c` implements an extensible byte buffer that can grow at both the head and tail.

Key behavior:
- `ebuf_alloc()` allocates a buffer with initial headroom, placing used data at one quarter of a page into the allocation.
- `ebuf_add_head()` prepends data or reserves head space, extending the head when needed.
- `ebuf_add_tail()` appends data or reserves tail space, extending the tail when needed.
- `ebuf_del_head()` and `ebuf_del_tail()` remove bytes from either side.
- `ebuf_data()` returns the contiguous used-data pointer and optional size.
- `ebuf_size()` returns used size.
- Head extension allocates a new buffer and copies used data.
- Tail extension uses `realloc()` and adjusts pointers.

Important details:
- Used by the HAST protocol layer to prepend the fixed main header before serialized nv data.
- Internal magic value assertions catch invalid use in debug/asserting builds.
- `ebuf_head_extend()` currently does not free the old allocation after copying, which is notable when reviewing memory behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.h

`ebuf.h` declares the opaque extensible buffer API.

Key API:
- Allocate/free: `ebuf_alloc()`, `ebuf_free()`.
- Modify: `ebuf_add_head()`, `ebuf_add_tail()`, `ebuf_del_head()`, `ebuf_del_tail()`.
- Access: `ebuf_data()`, `ebuf_size()`.

The abstraction exposes only contiguous used data and hides head/tail capacity details.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/event.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/event.c

`event.c` implements synchronous event messages from HAST workers to the parent daemon.

Key behavior:
- `event_send()` sends an nv header with an event number over `hr_event`, waits for a reply, and frees both nv structures.
- `event_recv()` receives an event in the parent, validates it, maps it to a hook event string, executes the configured hook, and replies with success.
- Recognized events:
  - connect
  - disconnect
  - syncstart
  - syncdone
  - syncintr
  - split-brain
- Receive errors are initially logged at debug level because a worker may have exited normally.

Important details:
- The child waits for the parent’s reply so event delivery is less likely to be lost during immediate worker exit.
- Hook execution uses resource name and role prefix context.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/event.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/event.h

`event.h` defines HAST worker-to-parent event IDs and declares the event API.

Key contents:
- Event constants from `EVENT_CONNECT` through `EVENT_SPLITBRAIN`.
- `EVENT_MIN` and `EVENT_MAX` validation bounds.
- Declares `event_send()` and `event_recv()`.

The event vocabulary matches hook names emitted by `event.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast.h

`hast.h` is the central HAST public/internal header for resource configuration, protocol constants, roles, and runtime state.

Key definitions:
- Protocol version history and current `HAST_PROTO_VERSION` 2.
- HAST error codes for control responses.
- Control command IDs.
- Roles: undefined, init, primary, secondary.
- Sync source IDs.
- HAST I/O operation IDs: read, write, delete, flush, keepalive.
- Default user, paths, timeout, control socket, listen addresses, pidfile, extent size, keepdirty, address size, token size, and keepalive interval.
- Replication modes: fullsync, memsync, async.
- Compression modes: none, hole, lzf.
- Checksum modes: none, crc32, sha256.

Main structs:
- `hastd_listen`: listen address plus proto connection.
- `hastd_config`: control address/connection, pidfile, listen list, resource list.
- `hast_resource`: comprehensive per-resource configuration and runtime state.

`hast_resource` includes:
- Names, replication/compression/checksum settings, protocol version, exec hook.
- Local provider path/fd/offset/data size/media size/sector size/flush settings.
- GEOM Gate descriptor and unit.
- Remote/source addresses, inbound/outbound proto connections, token, timeout.
- Resource ID and local/remote modification counters.
- Role/previous role, worker pid, parent-worker control/event/connection channels.
- Activemap pointer and locks.
- I/O and error statistics.
- Worker-specific status callback.
- TAILQ linkage.

This file is the shared contract across parser, daemon, worker, protocol, and control code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.c

`hast_checksum.c` implements optional data checksumming for HAST protocol payloads.

Key behavior:
- Supports checksum names `none`, `crc32`, and `sha256`.
- CRC32 uses zlib `crc32()`.
- SHA256 uses FreeBSD SHA256 routines.
- `checksum_send()` computes the selected hash for outgoing data, adds `checksum` and `hash` nv fields, and leaves payload data unchanged.
- `checksum_recv()` verifies incoming payload data against `checksum` and `hash` nv fields.
- Missing checksum field means no checksum was used.
- Unknown algorithms, missing hash, invalid hash size, or mismatch fail receive validation.

Important details:
- CRC32 stores the native `uint32_t` bytes with a comment questioning endian conversion.
- Max hash stack buffer size is SHA256 digest length.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.h

`hast_checksum.h` declares the checksum pipeline API.

Key API:
- `checksum_name()` maps numeric checksum mode to a string.
- `checksum_send()` adds checksum metadata for outgoing data.
- `checksum_recv()` validates incoming data against checksum metadata.

The function signatures match the HAST protocol pipeline stage interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_checksum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.c

`hast_compression.c` implements optional payload compression for HAST protocol data.

Key behavior:
- Supports compression names `none`, `hole`, and `lzf`.
- `hole` compression detects all-zero buffers and replaces them with a 32-bit little-endian original size.
- `lzf` compression first tries `hole`; otherwise it attempts LZF when original size is greater than 1024 bytes.
- LZF compressed payloads start with a little-endian original size.
- `compression_send()` may replace the data pointer with a newly allocated compressed buffer and marks `freedatap`.
- `compression_recv()` reverses `hole` or `lzf` compression and updates data pointer/size.
- Unknown compression algorithms or decompression failures are errors.

Important details:
- `allzeros()` probes beginning, middle, and end first, then ORs every 64-bit word.
- It asserts the buffer size is a multiple of 8.
- LZF intentionally allocates less than original size to require useful compression.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.h

`hast_compression.h` declares the compression pipeline API.

Key API:
- `compression_name()` maps numeric compression mode to a string.
- `compression_send()` optionally compresses outgoing data and annotates nv metadata.
- `compression_recv()` decompresses incoming data based on nv metadata.

The function signatures are compatible with the HAST protocol pipeline stage table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.c

`hast_proto.c` implements the HAST message framing layer over generic proto connections.

Key behavior:
- Defines a packed main header containing protocol version and serialized nv header size.
- Defines a send/receive pipeline with stages:
  - compression
  - checksum
- `hast_proto_send()`:
  - Optionally runs outgoing data through compression then checksum.
  - Adds final payload `size` to nv metadata.
  - Serializes nv to an `ebuf`.
  - Prepends main header.
  - Sends header/nv bytes, then payload bytes if present.
- `hast_proto_recv_hdr()`:
  - Receives main header.
  - Rejects versions newer than supported with `ERPCMISMATCH`.
  - Allocates an ebuf for nv bytes, receives them, and deserializes nv.
- `hast_proto_recv_data()`:
  - Reads payload size from nv.
  - Receives the encoded payload.
  - Runs receive pipeline in reverse order: checksum verification, then decompression.
  - Copies decoded data into caller-provided buffer if pipeline allocated a replacement buffer.
  - Rejects decoded data larger than caller capacity.

Important details:
- Header size is little-endian on wire.
- When `res` is NULL, send uses the current maximum protocol version.
- The pipeline ignores send-stage return values in `hast_proto_send()`, so stages signal hard nv errors through later `nv_error()` checks or errno paths only when visible.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.h

`hast_proto.h` declares the HAST protocol framing API.

Key API:
- `hast_proto_send()` sends an nv header and optional payload over a proto connection.
- `hast_proto_recv_hdr()` receives and deserializes the nv header.
- `hast_proto_recv_data()` receives and decodes payload data associated with an nv header.

This header is used by `hastctl`, parent/worker control, events, and primary/secondary replication code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.h -->