# Group Research: group_1352_ocfs2_tools_sources_local_fs_ocfs2_tools_o2image_o2image_c_sources__fde360b50dee

Scope checked against `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2image/o2image.c -->
# File Research: sources/local-fs/ocfs2-tools/o2image/o2image.c

`o2image.c` implements the `o2image` utility for creating and installing OCFS2 metadata images. It scans OCFS2 metadata structures, marks blocks in an `ocfs2_image_state` bitmap, then writes either compact image format with an `ocfs2_image_hdr` plus bitmap trailer or raw sparse-positioned metadata blocks.

Core traversal starts at the global inode allocator, recursively visits inode allocators, chain allocators, extent trees, indexed directory dx roots, and indexed xattr buckets. Regular file data is intentionally skipped except metadata reachable through system allocators or xattr trees. Backup superblocks and pre-first-cluster-group blocks are always marked.

The writer supports regular seekable outputs with `pwrite64()` and non-seekable outputs by streaming zero-filled holes before metadata blocks. Install mode reverses argument meaning, opens compact images with `OCFS2_FLAG_IMAGE_FILE` unless raw is requested, and always writes raw format to the destination device/file.

Important dependencies are `libocfs2`, `ocfs2/image.h`, OCFS2 on-disk structures, image bitmap helpers, and system file lookup APIs. Risk areas include destructive install mode, interactive prompting based on estimated image size, incomplete recovery if traversal hits corrupt metadata, and cleanup paths assuming an initialized `ofs->ost`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2image/o2image.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/o2info/Makefile

This makefile builds the `o2info` binary and a local static helper archive `libo2info.a`. The executable links `o2info.c`, `operations.c`, and `utils.c` with `libocfs2`, `libtools-internal`, `com_err`, AIO libraries, and the local helper library.

It installs/generates the `o2info.1` manpage and distributes source, headers, and the manpage template. Build flags use strict warnings with `-Wno-format`, include the repository `include` directory plus the local directory, and define `VERSION`.

The notable integration detail is that `libo2info.c` is separated into `libo2info.a`, while the CLI links that archive back into `o2info`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/libo2info.c -->
# File Research: sources/local-fs/ocfs2-tools/o2info/libo2info.c

`libo2info.c` provides offline/libocfs2 implementations for `o2info` data collection. It reads superblock fields for feature flags and volume info, reads the journal inode for mkfs-style journal size, scans slot inode allocators for free inode counts, and scans the global bitmap chain to calculate free-space fragmentation histograms.

The free-fragmentation path walks global bitmap chain records and group descriptors, counting contiguous free cluster runs, full free chunks, min/max/average extents, and histogram buckets. Values are later converted from clusters to KB by the caller/reporting code.

The FIEMAP path works on open file descriptors using `FS_IOC_FIEMAP`; it first asks for extent count, then batches extents through a stack buffer, accumulating clusters, shared/unwritten extents, holes, xattr clusters, extent counts, fragmentation percent, and score.

Dependencies include OCFS2 disk structures, bit operations, `linux/fiemap.h`, `linux/fs.h`, and verbose error helpers. Risk areas include manual bitmap scanning assumptions, static `fiemap` in `figure_extents`, and FIEMAP cluster-length truncation if extents are not cluster-aligned.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/libo2info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/libo2info.h -->
# File Research: sources/local-fs/ocfs2-tools/o2info/libo2info.h

This header defines the shared data model for `o2info` collection routines: filesystem feature bitsets, volume info, mkfs reconstruction data, per-slot free inode counts, free-fragmentation statistics/histogram, and FIEMAP-derived file layout statistics.

It exposes library entry points for offline OCFS2 filesystem queries and descriptor-based FIEMAP queries. Constants include `DEFAULT_CHUNKSIZE` and histogram sizing delegates to `OCFS2_INFO_MAX_HIST`.

The header is the contract between `libo2info.c` and `operations.c`; callers fill these structures either through libocfs2 or through mounted-filesystem ioctls before formatting output.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/libo2info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/o2info.1.in -->
# File Research: sources/local-fs/ocfs2-tools/o2info/o2info.1.in

This manpage template documents `o2info`, its mounted-file ioctl mode, and its privileged device/libocfs2 mode. It explains options for cluster-coherent querying, filesystem features, volume info, mkfs reconstruction, free inode counts, free fragmentation, space usage, file stat, version, and help.

The note section states that mounted filesystem queries depend on OCFS2 info ioctls added in Linux 2.6.37. Examples show non-root querying through a file path and privileged device-style queries.

The documented behavior matches the CLI: options can be composed, `--freefrag` requires a chunk size in KB, and file-focused commands require a mounted object rather than a block device.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/o2info.1.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/o2info.c -->
# File Research: sources/local-fs/ocfs2-tools/o2info/o2info.c

`o2info.c` is the CLI front end. It declares supported options as `struct o2info_option` entries, dynamically builds `getopt_long()` tables, appends selected operation objects to a task list, chooses the target path, opens it with the right method, and runs each requested operation.

It treats block/character devices as offline `libocfs2` targets and regular mounted objects as ioctl targets through `o2info_method()`. `-C/--cluster-coherent` flips the global `cluster_coherent` flag used by ioctl request flags.

Signal handling exits cleanly on termination signals, aborts on repeated SIGSEGV/SIGQUIT behavior, and ignores SIGPIPE. Main initialization sets up error tables, verbosity argv state, unbuffered output, and signals.

Risk notes: operation return values from `to_run()` are not accumulated in `o2info_run_task()`, duplicate long-only options report with the numeric generated value, and parsing errors often exit directly via `print_usage()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/o2info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/o2info.h -->
# File Research: sources/local-fs/ocfs2-tools/o2info/o2info.h

This header defines the `o2info` CLI framework: target access method enum, `struct o2info_method` union for either `ocfs2_filesys *` or fd, operation descriptors, option descriptors, and task list nodes.

The `DEFINE_O2INFO_OP` macro creates global `struct o2info_operation` objects used by `operations.c` and referenced by `o2info.c`. This keeps operation metadata and run callbacks decoupled from command-line parsing.

It depends on `getopt.h`, `libocfs2`, and the kernel list implementation for the operation task list.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/o2info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/operations.c -->
# File Research: sources/local-fs/ocfs2-tools/o2info/operations.c

`operations.c` implements all user-visible `o2info` operations. Each operation can use mounted-filesystem `OCFS2_IOC_INFO` ioctls or offline `libo2info` routines depending on `o2info_method`.

Operations include feature printing, volume info, mkfs option reconstruction, free inode counts, free-space fragmentation reports, file space usage, and extended filestat output. Mounted queries build `ocfs2_info_*` request structures, optionally add `OCFS2_INFO_FL_NON_COHERENT`, call the ioctl, and inspect filled/error flags.

The reporting code formats feature strings with line wrapping, renders free-fragment histograms, prints stat-like file metadata, and uses FIEMAP-derived counts for shared/unwritten/hole/xattr clusters. File-only operations reject device/libocfs2 mode.

Risk areas include several unchecked `malloc()`/`strdup()` results, freefrag argument handling assuming an argument is present, possible divide-by-zero in report percentages for unusual empty filesystems, and ioctl fallbacks that report per-request state but usually fail the whole operation.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/operations.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/utils.c -->
# File Research: sources/local-fs/ocfs2-tools/o2info/utils.c

`utils.c` contains shared helpers for `o2info`: feature flag string conversion, target open/close, method selection, file type naming, permission rendering, uid/gid lookup, timestamp extraction/formatting, and symlink path formatting.

Feature helpers wrap `ocfs2_snprint_feature_flags()` for compat, incompat, and ro-compat bitsets. Open/close chooses either `ocfs2_open()` with heartbeat-device allowance and read-only flags or a plain read-only fd. Method selection uses `stat()` and routes block/character devices to libocfs2.

Formatting helpers emulate `stat(1)` output, including file mode strings, localtime timestamps with nanoseconds, and symlink `path -> target` display. Risk notes include custom KMP code for nanosecond placeholder replacement, unchecked allocation in that path, `readlink()` truncation bounded by `PATH_MAX`, and hard failure if uid/gid names cannot be resolved.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/utils.h -->
# File Research: sources/local-fs/ocfs2-tools/o2info/utils.h

This header exposes common `o2info` utility functions for feature formatting, target method/open/close, file type and permission rendering, uid/gid lookup, stat timestamp extraction, human-readable time, symlink path formatting, and method detection.

It includes `o2info.h`, so callers inherit the method and operation type definitions. The header is used by the CLI and operation implementations as the shared utility boundary.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2info/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2monitor/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/o2monitor/Makefile

This makefile builds `o2hbmonitor` as an extra sbin program from `o2hbmonitor.c`. It uses strict warning flags, repository includes, a `VERSION` define, and installs/generates `o2hbmonitor.8`.

The binary has no explicit local library dependencies in this makefile; it links through the common `$(LINK)` rule with standard libc/system dependencies.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2monitor/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.8.in -->
# File Research: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.8.in

This manpage documents `o2hbmonitor`, a daemon for monitoring O2CB disk heartbeat latency. It describes configfs/debugfs requirements, default daemon behavior, syslog logging, and options for warning threshold percent, interactive mode, verbose output, and version display.

It notes Linux 2.6.37+ dependency and references `o2cb(7)`. The description aligns with the implementation’s polling of heartbeat region debugfs elapsed-time files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.c -->
# File Research: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.c

`o2hbmonitor.c` is a daemon/interactive monitor for O2CB disk heartbeat. It discovers the active cluster in configfs, reads dead threshold settings, scans `/sys/kernel/debug/o2hb/*/elapsed_time_in_ms`, resolves heartbeat region devices, and logs warnings when elapsed time exceeds a configured percent of the idle/dead threshold.

Polling adapts between config polling, slow polling, and fast polling after warnings. Verbose mode prints every sampled region to stdout; daemon mode logs through syslog. A SysV semaphore keyed by `O2HB_SEM_MAGIC_KEY` prevents multiple active instances.

Dependencies are configfs, debugfs, syslog, dirent, and SysV semaphores. Risks include reliance on `d_type`, fixed path buffers with `sprintf`, singleton lock semantics that leave semaphore objects behind, and no signal-driven graceful shutdown path.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2.pc.in -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2.pc.in

This pkg-config template describes the userspace `libocfs2` library. It substitutes prefix, exec prefix, libdir, includedir, and version, declares dependencies on `o2dlm`, `o2cb`, and `com_err`, and exposes `-locfs2 -laio` plus include flags.

Consumers use this to compile/link external programs against OCFS2 userspace libraries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/Makefile

This makefile builds stack-specific `ocfs2_controld` daemons: `ocfs2_controld.cman` when CMAN support is enabled and `ocfs2_controld.pcmk` when Pacemaker support is enabled. Shared daemon sources are `main.c`, `cpg.c`, `mount.c`, `ckpt.c`, and `dlmcontrol.c`; stack adapters are `cman.c` or `pacemaker.c`.

It links against `libo2cb`, OpenAIS checkpoint, Corosync/OpenAIS CPG, dlmcontrol, and stack-specific CMAN or Pacemaker/CRM libraries. It also builds an uninstalled `test_client` with `libocfs2` and `libo2cb`.

Build defines include flat include compatibility macros, optional `HAVE_COROSYNC`, and `VERSION`. This is the integration point for the controld daemon’s cluster-stack variants.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/ckpt.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/ckpt.c

`ckpt.c` wraps the OpenAIS checkpoint service for `ocfs2_controld`. It initializes/finalizes the CKPT service, opens global/node checkpoints, reads/writes bounded named sections, retries transient `SA_AIS_ERR_TRY_AGAIN`, and maps AIS errors to negative errno values plus log messages.

Checkpoint names are prefixed with `ocfs2:`. The global daemon checkpoint is `ocfs2:controld`; node checkpoints are `ocfs2:controld:<nodeid>`. Section size, count, and id lengths are fixed, with validation before store/get.

The daemon uses these checkpoints for cluster-wide protocol negotiation and per-node maximum protocol advertisement. Risks include indefinite retry loops for busy/existing checkpoints, small fixed section size limiting future protocol data, and a debug-only main under `DEBUG_EXE`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/ckpt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/cman.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/cman.c

`cman.c` is the CMAN stack adapter for `ocfs2_controld`. It initializes normal and admin CMAN handles, gets the cluster name and local node id, tracks node membership snapshots, registers CMAN notification callbacks, and adds the CMAN fd to the daemon poll loop.

It implements the stack interface declared in `ocfs2_controld.h`: cluster validation, cluster name lookup, node id to name lookup, node kill via `cman_kill_node()`, setup, and teardown. Shutdown requests are denied while OCFS2 mounts exist.

Risk notes include membership tracking being mostly diagnostic, a FIXME about waiting for local membership, and daemon shutdown if the CMAN connection dies.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/cman.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/cpg.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/cpg.c

`cpg.c` manages Corosync/OpenAIS CPG groups for the daemon and per-filesystem mount groups. It maintains `cgroup` objects with CPG handles, poll-loop clients, current members, locally tracked nodes, callbacks, and user data hooks for mount code.

The daemon joins `ocfs2:controld`; each mounted filesystem joins `ocfs2:<uuid>`. Configuration change callbacks are copied into group state, then processed in the main loop. Daemon-group leaves trigger node-down handling for all mount groups; filesystem-group joins/leaves call mount-layer callbacks.

The code deliberately fences/kicks nodes whose `ocfs2_controld` process goes down while the node remains up. Risks include strict dependence on correct CPG ordering, fail-fast daemon shutdown when membership bookkeeping is inconsistent, and several comments marking incomplete behavior around daemon-group node leave processing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/cpg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/dlmcontrol.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/dlmcontrol.c

`dlmcontrol.c` connects `ocfs2_controld` to `dlm_controld` through libdlmcontrol. It registers filesystem lockspaces before kernel mounts proceed, unregisters them on last unmount, and sends node-down notifications until dlm_controld acknowledges them.

It tracks registered filesystems in `register_list`, each with pending notification nodes and a registration result callback. The fd from `dlmc_fs_connect()` is added to the main poll loop, and result messages drive register completion or notification retry/cleanup.

Failure policy is conservative: unexpected errors in notification paths call `shutdown_daemon()` because OCFS2 cannot safely continue without ordered DLM coordination.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/dlmcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/main.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/main.c

`main.c` is the `ocfs2_controld` daemon core. It owns the poll-loop client table, signal pipe, listening socket for `mount.ocfs2` clients, debug ring buffer, daemonization/lockfile handling, stack verification, protocol negotiation, and startup/shutdown sequence.

Startup initializes o2cb, verifies the built daemon stack matches configured stack, optionally daemonizes, raises scheduler priority, lowers OOM score, sets up signal handling, cluster stack, checkpoint service, node protocol checkpoint, daemon CPG, DLM control, kernel control device, and client listener. CPG join completion negotiates or reads global daemon/filesystem protocol versions.

Client protocol handling supports mount, mount-result, unmount, list clusters, list filesystems, and debug dump messages. It validates filesystem type and cluster name before delegating to `mount.c`.

Risk areas include global mutable state, fixed-size debug buffer protocol chunking, fail-stop behavior while mounts exist, PID lock under `/var/run`, and protocol negotiation depending on checkpoint availability and format correctness.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/mount.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/mount.c

`mount.c` manages OCFS2 filesystem mountgroups inside `ocfs2_controld`. A mountgroup is keyed by UUID, stores the source device, active services/mountpoints, CPG group pointer, DLM registration state, in-progress service, client fd/ci, and pending error state.

First mount creates a mountgroup, validates device identity, joins a CPG group, registers with dlm_controld, then notifies the mount client. Additional real mounts return `EALREADY` so the client can call `mount(2)` without repeating group setup. Last unmount unregisters DLM, leaves CPG, notifies the client, and frees the mountgroup.

Node-down callbacks tell the kernel control device and dlm_controld about departed nodes. Unexpected group leave while live causes an immediate `_exit(1)` after logging to encourage fencing/cluster recovery.

Risk areas include delicate in-progress state transitions, special handling when a mounter dies after notification but before known mount success, fail-fast unexpected leave behavior, and string/device validation relying on stat `st_rdev` comparisons.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/ocfs2_controld.h -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/ocfs2_controld.h

This header is the internal interface for `ocfs2_controld`. It declares shared globals, logging macros, subsystem entry points, stack abstraction functions, checkpoint APIs, CPG APIs, DLM control APIs, mount APIs, and retry/backoff helpers.

`log_debug` writes to the in-memory daemon dump buffer and optionally stderr; `log_error` also syslogs. `retry_warning` logs on power-of-two retry counts using a local hweight helper.

The header is central glue for daemon modules and stack-specific adapters. Its global state and macro logging model tightly couple all daemon source files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/ocfs2_controld.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/pacemaker.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/pacemaker.c

`pacemaker.c` is the Pacemaker stack adapter for `ocfs2_controld`. It initializes CRM/AIS cluster communication, records local node name/id, subscribes to membership notifications, adds the AIS fd to the daemon poll loop, and dispatches AIS messages when readable.

It implements the same stack interface as `cman.c`: cluster name validation, cluster name lookup, node id to name via CRM peers, node kill via `crm_terminate_member_no_mainloop()`, setup, and teardown. The reported cluster name is the fixed string `pacemaker`.

Risks include old Pacemaker/AIS API dependencies, `nodeid2name()` assuming `crm_get_peer()` succeeds, and dynamically adding a stonith fd during node kill if Pacemaker returns one.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/pacemaker.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/test_client.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/test_client.c

`test_client.c` is an uninstalled diagnostic client for the `ocfs2_controld` protocol. It connects to the daemon socket and can send fake mount, fake unmount, listclusters, and listfs requests.

The mount path sends `CM_MOUNT`, accepts `CM_STATUS` including `EALREADY`, fakes a successful kernel mount, then sends `CM_MRESULT`. Unmount sends `CM_UNMOUNT`. List operations use the shared receive-list helpers and print returned items.

There is disabled code for deriving UUIDs from mtab/device state. The active tool expects explicit arguments and is useful for daemon protocol testing rather than production mounting.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_controld/test_client.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/Makefile

This makefile builds `ocfs2_hb_ctl` as a root sbin program. It links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, AIO, and optional fsdlm/cmap stack libraries. Unless `OCFS2_DYNAMIC_CTL` is set, it adds static linking.

It installs/generates `ocfs2_hb_ctl.8` and distributes the single C source plus manpage template. The build defines `VERSION`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.8.in -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.8.in

This manpage documents `ocfs2_hb_ctl`, a helper for starting/stopping local O2CB heartbeat on an OCFS2 device by device path or UUID. It explicitly warns users not to run it directly because it is invoked by mount and other tools.

Documented actions include start, stop, reference count display, and heartbeat thread I/O priority adjustment through `ionice`. It states the tool only operates in local heartbeat mode and silently fails in global heartbeat mode.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.c

`ocfs2_hb_ctl.c` starts/stops OCFS2 local heartbeat regions, reports heartbeat reference counts, and adjusts heartbeat thread I/O priority. It can identify a region by device or UUID; UUID lookup scans `/proc/partitions`, filters IDE non-disk devices, opens candidates with libocfs2, and compares heartbeat descriptors.

Descriptor handling reads heartbeat and cluster descriptions from the OCFS2 volume, duplicates embedded strings, and frees them carefully. Start calls `o2cb_begin_group_join()` and immediately `o2cb_complete_group_join()` for manual starts; stop calls `o2cb_group_leave()`; priority uses `o2cb_get_hb_thread_pid()` and executes `/usr/bin/ionice`.

The main path initializes OCFS2/O2DL/O2CB error tables, validates option combinations, fills UUID from device when needed, blocks most signals during heartbeat action, and frees allocated option strings/descriptors. Risks include hardcoded `/proc/partitions` probing, string allocation ownership complexity, and external `ionice` dependency.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2cdsl/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2cdsl/Makefile

This makefile builds `ocfs2cdsl` as a root sbin program from `ocfs2cdsl.c`. It uses `libocfs2`, `libo2dlm`, `libo2cb`/optional dlm_lt, GLib flags/libs, and `com_err`.

It defines `VERSION` and `G_DISABLE_DEPRECATED`, installs/generates `ocfs2cdsl.8`, and includes distribution rules. The resulting tool is GLib-heavy despite linking mostly through common build variables.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2cdsl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.8.in -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.8.in

This manpage documents `ocfs2cdsl`, a utility for creating context-dependent symbolic links on OCFS2. It explains CDSL types such as hostname, machine, OS, and node number; copy, force, dry-run, quiet, verbose, and version options; and the use case of per-node views of a shared path.

The examples describe moving/copying common data into `.cluster/...` and replacing the original path with a symbolic link whose target contains a context token like `{hostname}`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.c

`ocfs2cdsl.c` creates OCFS2 context-dependent symbolic links. It validates the target is on an OCFS2 mount, determines the filesystem root, builds `.cluster/common/<type>` and `.cluster/<type>/<value>` storage paths, moves or copies existing files/directories, and replaces the original with a symlink containing a context placeholder.

Supported context types include hostname, machine, OS, node number, machine+OS, uid, and gid, though the manpage documents fewer. Node number is read from `/proc/fs/ocfs2/<major>_<minor>/nodenum`. GLib handles path building, quoting, spawning shell commands, and file tests.

Options control copy/local behavior, no-common copy, force replacement, dry-run, verbosity, and quiet mode. Risks include executing shell commands (`cp -a`, `rm -rf`, `mkdir -p`) through quoted command strings, deprecated/legacy OCFS2 procfs dependence for nodenum, symlink-relative path complexity, and process exits deep inside helpers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/Makefile

This top-level console makefile descends into `blkid` and `ocfs2interface`, installs/generates `ocfs2console.8`, and marks `ocfs2console` as an extra sbin script/program distributed with its manpage template.

It is a simple dispatcher makefile; actual console functionality lives in subdirectories and external script/interface files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/Makefile

This makefile builds an internal PIC `libblkid-internal.a` only when system blkid support is unavailable. It compiles legacy blkid implementation files for cache, devices, names, probing, reading, resolving, tags, and version handling.

It defines config-style preprocessor symbols for available headers and `lseek64`, includes the parent console directory, and distributes blkid headers/source plus ChangeLog. This is a compatibility vendored blkid for `ocfs2console`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkid.h -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkid.h

`blkid.h` is the public interface for the vendored legacy libblkid copy. It defines opaque device/cache/iterator types, version/date constants, device lookup flags, and prototypes for cache management, device iteration, probing, resolving tag values, tag iteration, tag parsing, and version parsing.

The header uses LGPL terms, C++ guards, and `blkid_types.h` for fixed-width blkid types. It mirrors early e2fsprogs/libblkid API shape so `ocfs2console` can build without a system blkid.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkid.h -->