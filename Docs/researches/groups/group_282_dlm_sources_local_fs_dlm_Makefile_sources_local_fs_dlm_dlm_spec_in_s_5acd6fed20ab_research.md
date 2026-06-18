# Group Research: group_282_dlm_sources_local_fs_dlm_Makefile_sources_local_fs_dlm_dlm_spec_in_s_5acd6fed20ab

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/dlm`.

Read validation: every listed source file was read completely. The checked line counts match the work item: 10,228 total lines across 15 files.

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/Makefile -->
# File Research: sources/local-fs/dlm/Makefile

## Purpose
Top-level build, cleanup, tarball, and RPM entry point for the DLM userspace source tree. It delegates normal build targets to `libdlm`, `dlm_controld`, `dlm_tool`, and `fence`, then handles release metadata generation and RPM packaging.

## Main Behavior
- `all install clean` loops through subdirectories and runs the same make target in each.
- The delegated targets also remove generated packaging artifacts, including `dlm.spec`, tarballs, rpm output directories, and `.version` when in a git checkout.
- `.version` is generated only inside a git repository. It derives `relver` from the latest `dlm-*` tag, counts commits since that tag, records the short commit id as `alphatag`, and stores an RPM changelog date.
- `dlm.spec` is rendered from `dlm.spec.in` using `.version` values; when building from a release tarball without `.git`, it strips `%global numcomm` and `%global alphatag`.
- `tarball` creates `dlm-$tarver.tar.gz`, using plain release version for release builds and `relver.numcomm.alphatag` for non-release git builds.
- `srpm` and `rpm` run `rpmbuild` with all rpm build directories redirected to the current source directory.

## Integration Points
- Consumes `include/version.cf`, `.git` metadata, and `dlm.spec.in`.
- Produces `.version`, `dlm.spec`, source tarballs, SRPMs, and binary RPMs.
- Assumes subdirectories have compatible `all`, `install`, and `clean` targets.

## Risks and Notes
- Build orchestration is serial and shell-loop based; one failing subdirectory stops the whole target through `set -e`.
- `.version` cannot be regenerated from a release tarball, so cleanup intentionally preserves it outside git.
- `tar --transform "s/^./dlm-$$relver/"` prefixes archive paths with the release version, not the non-release `tarver`, which is worth preserving for compatibility with the generated spec.
<!-- END FILE RESEARCH: sources/local-fs/dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm.spec.in -->
# File Research: sources/local-fs/dlm/dlm.spec.in

## Purpose
RPM spec template for packaging the DLM userspace daemon, tools, libraries, headers, pkg-config metadata, udev rules, man pages, and systemd unit/sysconfig files.

## Main Behavior
- Uses template substitutions for `@relver@`, `@rpmdate@`, `@numcomm@`, and `@alphatag@`.
- Defines package name `dlm`, version from `@relver@`, and release suffixes based on optional commit count and alphatag globals.
- Declares license mix as GPLv2, GPLv2+, and LGPLv2+, with README license breakdown.
- Requires Corosync libraries >= 3.1.0, Pacemaker development libraries, systemd development headers, kernel headers, gcc, and make.
- `%build` uses `%set_build_flags` and explicitly disables parallelism via `%make_build -j1`.
- `%install` runs `make install` with RPM `_libdir` and `_sbindir`, then installs `init/dlm.service` and `init/dlm.sysconfig`.
- Defines three packages:
  - Main `dlm` package: daemon, tool, stonith helper, man pages, systemd unit, sysconfig.
  - `dlm-lib`: shared runtime libraries and udev rules.
  - `dlm-devel`: unversioned shared-library links, headers, and pkg-config files.

## Integration Points
- Rendered by the top-level `Makefile`.
- Build uses the repo makefiles directly; upstream has no configure step.
- Runtime dependency links daemon packaging to `corosync`, optional distro kernel module packages, and systemd scriptlets.

## Risks and Notes
- `%make_build -j1` documents that upstream does not support parallel builds.
- Distro conditionals distinguish SUSE/Fedora packaging names.
- Main package requires the exact matching `dlm-lib` version-release.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm.spec.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/Makefile -->
# File Research: sources/local-fs/dlm/dlm_controld/Makefile

## Purpose
Build and install rules for the `dlm_controld` daemon binary and `libdlmcontrol` shared library.

## Main Behavior
- Builds `dlm_controld` from daemon sources including membership, CPG, configfs/sysfs action code, fencing, plock, config, logging, member, and node config modules.
- Builds `libdlmcontrol.so.3.2` from `lib.c`, with symlinks `libdlmcontrol.so` and `libdlmcontrol.so.3`.
- Generates `libdlmcontrol.pc` from `libdlmcontrol.pc.in` by substituting prefix and library directory.
- Applies hardened compiler/linker defaults: `_FORTIFY_SOURCE=2`, stack protector, stack clash protection, PIE for the daemon, relro/now, and extensive warning flags.
- Uses `pkg-config` to discover Corosync libraries (`libcpg`, `libcmap`, `libcfg`, `libquorum >= 3.1.0`) and optionally `libsystemd` when `USE_SD_NOTIFY=yes`.
- Installs daemon, shared library, symlinks, pkg-config file, header, and man pages under configurable `DESTDIR`, `PREFIX`, `BINDIR`, `LIBDIR`, `HDRDIR`, `MANDIR`, and `PKGDIR`.

## Integration Points
- Includes headers from `../include` and `../libdlm`.
- Links daemon with pthread, rt, uuid, Corosync, and optionally systemd.
- Exported control library ABI is versioned as major 3, minor 2.

## Risks and Notes
- The makefile compiles all daemon sources in one compiler invocation rather than object-by-object, so incremental rebuilds are coarse.
- It uses GNU make `.SHELLSTATUS` after `$(shell pkg-config ...)`; non-GNU make would not work.
- `LIB_LDFLAGS` includes `-pie` even for shared library linking; this is inherited local style and should be tested before changing.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/action.c -->
# File Research: sources/local-fs/dlm/dlm_controld/action.c

## Purpose
Kernel-facing action layer for `dlm_controld`. It writes DLM sysfs/configfs controls, discovers cluster names and misc device minors, initializes configfs cluster options, manages configfs node/member directories, and detects abandoned kernel lockspaces.

## Main Behavior
- Detects Corosync cluster name through `cmap_get_string("totem.cluster_name")` and stores it in global `cluster_name`.
- `check_uncontrolled_lockspaces()` scans `/sys/kernel/dlm`; if lockspaces exist before daemon control is established, it logs them and kicks the local node from the cluster.
- Sysfs helpers write lockspace `control`, `event_done`, `id`, and `nodir` values under `/sys/kernel/dlm/<name>/`.
- Configfs member helpers manage `/sys/kernel/config/dlm/cluster/spaces/<lockspace>/nodes/<nodeid>`:
  - Create lockspace and node directories.
  - Remove old members no longer present.
  - Renew nodes by rmdir/mkdir when a node left and rejoined.
  - Write each node's `nodeid` and configured master `weight`.
  - Optionally write `release_recover` for a member before removal.
- Configfs communication helpers manage `/sys/kernel/config/dlm/cluster/comms/<nodeid>`:
  - Create node directories.
  - Write nodeid, padded sockaddr storage address, optional skb mark, and local flag.
  - Delete individual comm nodes or clear all comm nodes.
- `setup_configfs_options()` clears stale configfs state, recreates base cluster directory, writes selected cluster options, validates protocol selection (`tcp`/`sctp`; `detect` is rejected to TCP), configures SCTP receive buffers, enables recovery callbacks, and writes cluster name unless deprecated fscontrol mode is active.
- `setup_misc_devices()` parses `/proc/misc` for `dlm-control`, `dlm-monitor`, and `dlm_plock`, then waits for matching `/dev/misc/*` device nodes.

## Integration Points
- Calls cross-module helpers from `main.c`, `member.c`, and `config.c`: `do_write`, `kick_node_from_cluster`, `is_cluster_member`, `update_cluster`, and `get_weight`.
- Consumes daemon options from `dlm_options` through `opt`, `optu`, and `opts`.
- Provides kernel control primitives used by the CPG membership code in `cpg.c`.

## Risks and Notes
- Many operations require mounted configfs, loaded DLM kernel module, and correct permissions.
- String formatting uses fixed-size buffers with `snprintf` in most places; paths longer than `PATH_MAX` are truncated but not explicitly detected.
- `add_configfs_node()` treats failure to open the optional `mark` file as non-fatal because older kernels may not support it.
- Cleaning configfs at setup removes previous daemon-managed DLM configfs state; this is intentional startup hygiene.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/action.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/config.c -->
# File Research: sources/local-fs/dlm/dlm_controld/config.c

## Purpose
Parses `dlm.conf` for daemon options and per-lockspace master/weight configuration, and supports runtime option changes from distributed helper-run commands.

## Main Behavior
- `get_weight()` returns DLM master weight for a node in a lockspace: default weight is 1 when no masters are configured; non-listed nodes get weight 0 when a master list exists.
- `setup_lockspace_config()` scans `/etc/dlm/dlm.conf` for `lockspace <name>` sections, applies `nodir=`, and reads following `master <name> node=<id> [weight=<n>]` lines.
- Generic option parsing supports int, uint, bool, and string daemon options from `key=value` lines. CLI settings take precedence over config-file values, which take precedence over defaults.
- `set_opt_file(update)` reads the config file:
  - Initial mode populates file values.
  - Update mode only applies options marked reloadable and detects reloadable file options that were removed/commented out.
  - Reload actions currently include writing `log_debug` to configfs and updating logfile priority.
- Dynamic online configuration is parsed by `set_opt_online()`, using the same argument tokenizer as the helper command parser. It supports `restore_all` and per-option `restore`.

## Integration Points
- Uses `dlm_options[]` defined elsewhere and `get_ind_name()` from `main.c`.
- Calls `set_configfs_opt()` from `action.c` and `set_logfile_priority()` from `logging.c` for live reload effects.
- Per-lockspace master weights feed `set_configfs_members()` in `action.c`.

## Risks and Notes
- Parser is intentionally simple and whitespace-sensitive; it is not a general config grammar.
- String parsing uses fixed `MAX_LINE` buffers and `strcpy`/`strdup`; valid config lines are expected to fit 256 bytes.
- Dynamic string option changes allocate a new `dynamic_str` without freeing any previous dynamic string before assignment in that path; reset frees it later.
- `set_opt_online()` returns early on malformed escaping and does not free duplicated argument strings, acceptable for infrequent control operations but still a leak.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/cpg.c -->
# File Research: sources/local-fs/dlm/dlm_controld/cpg.c

## Purpose
Implements per-lockspace Corosync CPG membership control. It translates CPG membership changes into safe DLM kernel stop/reconfigure/start cycles, synchronizes start barriers between lockspace members, coordinates plock state transfer, and exposes lockspace/node status to the control API.

## Main Behavior
- Maintains per-lockspace `change` records for CPG confchg events and `node_history` records for node add/remove/failure/fencing/fs-notify state.
- On a lockspace membership change:
  - Record member, joined, removed, and failed node sets.
  - Stop kernel lock activity through sysfs `control=0`.
  - Mark failed nodes as needing fencing when fencing is enabled and the node had previously sent a valid start.
  - Purge plock state for removed nodes.
  - Wait for required conditions: matching Corosync/quorum ring IDs, quorum if enabled, fencing completion, and fs notification acknowledgements.
  - Send a `DLM_MSG_START` message containing full change details.
  - Wait for all members' start messages as an agreed barrier.
  - Update configfs lockspace members, set lockspace id/nodir when joining, and restart kernel locking via `control=1`.
  - Finish initial kernel join by writing sysfs `event_done`.
- Uses detailed change matching in received start/plock-done messages. Matching checks sender membership, node add times, counts, member IDs, NACK flags, and duplicate/old change patterns.
- Sends NACK start messages for older identical changes so peers do not accidentally match stale messages.
- Coordinates plock handoff:
  - New joiners set `need_plocks`.
  - The lowest member reporting plock state becomes the data node.
  - New nodes ignore/suspend plock messages until saved state is ready, then replay saved messages after `DLM_MSG_PLOCKS_DONE`.
  - The data node sends all plock state when nodes have been added.
- Handles `DLM_MSG_RELEASE_RECOVER` on leave, allowing the initiator's release-recovery option to be written to configfs before member removal.
- Joins lockspace CPG groups named `dlm:ls:<lockspace>`, deriving a global id from the CPG name CRC.
- Leaves lockspace CPGs on kernel offline events, finalizes CPG handles after the leave callback, purges local plocks, and frees lockspace state.
- Exposes `set_lockspace_info()`, `set_node_info()`, `set_lockspaces()`, and `set_lockspace_nodes()` for `libdlmcontrol` queries.

## Integration Points
- Uses sysfs/configfs functions from `action.c`.
- Uses cluster membership and fencing state from `member.c`/`daemon_cpg.c`.
- Dispatches plock messages to `plock.c` and receives plock state completion callbacks.
- Uses message send, header conversion, message validation, and protocol-state transitions from `daemon_cpg.c`.
- Called by the main daemon event loop via CPG client callbacks.

## Risks and Notes
- Correctness relies on Corosync CPG's ordered delivery and identical confchg sequence across members.
- The code deliberately waits for CPG and cluster ring IDs to match to avoid acting on inconsistent membership views.
- Fencing and fs-notify waits can hold a lockspace stopped until external conditions complete.
- Deadlock message handling is present only under inactive `#if 0` blocks in this file, so the active daemon does not dispatch deadlock messages from lockspace CPG.
- Many status/debug fields are maintained specifically for control-socket diagnostics.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/cpg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/crc.c -->
# File Research: sources/local-fs/dlm/dlm_controld/crc.c

## Purpose
Provides `cpgname_to_crc()`, a CRC32 helper used to derive a stable 32-bit id from a CPG/lockspace name.

## Main Behavior
- Contains a static 256-entry CRC32 little-endian lookup table.
- `cpgname_to_crc(data, len)` computes the same result as kernel `crc32_le(0xFFFFFFFF, data, len) ^ 0xFFFFFFFF`.
- Intended to match GFS2/DLM kernel hashing behavior and produce uniform directory/resource hash distribution.

## Integration Points
- Declared in `dlm_daemon.h`.
- Used by `dlm_join_lockspace()` in `cpg.c` to set `ls->global_id` from `dlm:ls:<name>`.

## Risks and Notes
- The function treats input as bytes and does not validate null termination.
- Consistency with kernel CRC behavior is more important than substituting a different hash implementation.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/daemon_cpg.c -->
# File Research: sources/local-fs/dlm/dlm_controld/daemon_cpg.c

## Purpose
Implements the daemon-wide Corosync CPG group `dlm:controld`. It coordinates cluster-wide protocol negotiation, fencing, startup safety, stateful merge handling, distributed helper-run requests, message encoding, and daemon status export.

## Main Behavior
- Defines DLM daemon protocol structures for maximum supported daemon/kernel protocol and selected runtime daemon/kernel protocol.
- Provides common CPG message send and header conversion helpers used by both daemon-wide and per-lockspace CPG code.
- Validates incoming message sender nodeid and daemon protocol major/minor compatibility.
- Tracks daemon members in `node_daemon`, including membership state, clean protocol state, stateful merge flag, fencing state, fence actor candidates, fence agent pid, timestamps, and per-node fence config.
- Maintains `fence_in_progress_unknown` (FIPU) so newly joined nodes do not start lockspaces while previous members may still be fencing failed nodes.
- Fencing work loop:
  - Waits for daemon and cluster ring IDs to match.
  - Optionally waits for quorum.
  - Detects stateful merges and kills/defers merged members based on quorum/two-node rules.
  - Handles startup fencing by moving startup nodes into normal `need_fencing` state after delay.
  - Selects the lowest surviving fence actor from nodes present when failure was observed.
  - Runs fence agents through `fence_request()` and checks completion through `fence_result()`.
  - Supports serial or concurrent fencing based on options.
  - Uses parallel-priority fence config sequencing: next parallel device on success, next priority device on failure.
  - Broadcasts `DLM_MSG_FENCE_RESULT` and `DLM_MSG_FENCE_CLEAR`.
  - Clears FIPU through startup fencing completion, explicit clears from prior members, or all-members-FIPU detection when startup fencing is disabled.
- Protocol negotiation:
  - On daemon CPG join, all nodes send max/run protocol data.
  - Once all protocol messages are present, the daemon proposes minimum compatible versions.
  - Nodes adopt nonzero run protocol from a peer or their own proposal.
  - `set_protocol_stateful()` marks the local daemon as stateful after lockspace recovery begins, making later partition merges detectable.
- Distributed run support:
  - Receives and sends `DLM_MSG_RUN_REQUEST`/`DLM_MSG_RUN_REPLY`.
  - Tracks replies only on the starting node.
  - Dispatches accepted commands to the helper process through `send_helper_run_request()`.
  - Supports start-node participation flags and destination-node targeting.
- CPG callbacks:
  - `confchg_cb_daemon()` records member/join/remove lists, sends protocol on joins, marks failed members for recovery/fencing, and sets clear flags for joining nodes.
  - `totem_cb_daemon()` stores daemon ring id and reruns fencing work.
  - `deliver_cb_daemon()` dispatches protocol, fence, clear, and run messages.
- Lifecycle:
  - `setup_cpg_daemon()` initializes protocol maxima, joins `dlm:controld`, and returns its CPG fd.
  - `close_cpg_daemon()` leaves/finalizes daemon and lockspace CPGs, stopping kernel lockspaces first.
  - `send_state_daemon*()` exports daemon, daemon-node, and startup-node textual state records.

## Integration Points
- Called by the main daemon event loop for daemon CPG dispatch.
- Supplies message helpers to `cpg.c`, `plock.c`, `deadlock.c`, and run-helper code.
- Uses fencing primitives from `fence.c` and fence config from `fence_config.c`.
- Uses cluster state globals maintained by membership/quorum code outside this file.
- Kicks nodes from Corosync through `kick_node_from_cluster()` when safety requires it.

## Risks and Notes
- Fencing correctness is central: lockspaces can remain blocked while FIPU, startup nodes, or `need_fencing` are unresolved.
- Stateful merge handling is conservative and may intentionally kill peer cluster membership to avoid using stale DLM state.
- Some send helpers pre-convert fields manually and call `_send_message()` directly rather than `dlm_send_message_daemon()`.
- Run-command payloads are trusted only after helper-level command allowlisting.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/daemon_cpg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/deadlock.c -->
# File Research: sources/local-fs/dlm/dlm_controld/deadlock.c

## Purpose
Implements a distributed DLM deadlock detection prototype using debugfs lock snapshots, OpenAIS/SaCkpt checkpoints, CPG deadlock-cycle messages, transaction wait-for graph construction, and lock cancellation. In the active daemon path, deadlock dispatch is disabled by surrounding `#if 0` blocks in `cpg.c` and related fields in `dlm_daemon.h`.

## Main Behavior
- Initializes a global checkpoint service handle when deadlock detection is enabled.
- Models lock snapshots as resources (`dlm_rsb`), locks (`dlm_lkb`), and transactions (`trans`).
- Reads local lock state from `/sys/kernel/debug/dlm/<lockspace>_locks`.
- Normalizes local, master, and process-copy lock records so process copies can be combined with master copies.
- Writes local lock snapshots into per-node checkpoints named `dlmdeadlk.<lockspace>.<nodeid>`, with one checkpoint section per resource.
- Reads peer checkpoints, converts packed little-endian lock records, and merges them into the local resource graph.
- Cycle protocol:
  - `send_cycle_start()` asks all members to capture lock state.
  - `receive_cycle_start()` reads local debugfs locks, writes a checkpoint, and broadcasts checkpoint-ready.
  - `receive_checkpoint_ready()` reads a peer checkpoint and marks the peer ready.
  - Once all participating nodes are ready, the lowest node id runs detection.
  - `send_cycle_end()` ends the cycle and triggers cleanup on all nodes.
- Deadlock detection:
  - Builds a transaction list from all locks grouped by `xid`.
  - For each waiting/convert lock, finds incompatible granted/convert locks on the same resource and adds wait-for edges to owning transactions.
  - Repeatedly removes transactions with no wait-for dependencies, assuming they can complete.
  - Remaining transactions imply deadlock.
  - Chooses a transaction others wait on, sends `DLM_MSG_DEADLK_CANCEL_LOCK` for its blocked lock(s), and reduces again.
- `receive_cancel_lock()` opens the lockspace through libdlm and calls `dlm_ls_deadlock_cancel()` for the target lkid.
- Handles membership changes during a cycle by purging departed nodes' locks and recalculating the lowest detector node when needed.

## Integration Points
- Depends on `libdlm.h`, `dlm_ls_deadlock_cancel()`, DLM debugfs output, and OpenAIS/SaCkpt APIs.
- Sends DLM CPG messages through `dlm_send_message()`.
- Uses lockspace fields that are currently compiled out in `dlm_daemon.h` under `#if 0`.

## Risks and Notes
- The file references `cfgd_enable_deadlk`, which is not part of the active option set in the read headers, reinforcing that this code is disabled/stale.
- The checkpoint buffer is a fixed 10 MiB global buffer; oversized lock state is logged and truncated by packing limits.
- Debugfs line parsing depends on kernel debug output format.
- The detector cancels one transaction candidate, not necessarily the globally optimal victim.
- Because active CPG dispatch for deadlock messages is disabled, this file should be treated as dormant research/prototype code unless re-enabled with corresponding struct fields and options.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/deadlock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/dlm_controld.h -->
# File Research: sources/local-fs/dlm/dlm_controld/dlm_controld.h

## Purpose
Defines the private control-socket protocol between `dlm_controld` and `libdlmcontrol`.

## Main Contents
- Socket path names: `dlmc_sock` and `dlmc_query_sock`.
- Magic/version constants: `DLMC_MAGIC` and `DLMC_VERSION`.
- Command IDs for debug dumps, plock dumps, lockspace/node queries, fs registration notifications, deadlock checks, fence ack, status/config dumps, run operations, config reload, and online config setting.
- `struct dlmc_header` with magic, version, command, option, payload length, small embedded data field, flags, and a fixed lockspace name buffer.
- State transfer constants and `struct dlmc_state` for daemon, daemon-node, startup-node, and run state messages.
- `struct dlmc_run_check_state` for run-check status.

## Integration Points
- Included by `dlm_daemon.h` and `libdlmcontrol.h` users.
- State constants are produced by `daemon_cpg.c` and consumed by control clients.

## Risks and Notes
- Field `unsued2` is misspelled but part of the local ABI layout.
- Lockspace names have no terminating null space in `dlmc_header.name`, so consumers must treat them as fixed-length fields.
- Header changes affect daemon/control-library compatibility.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/dlm_controld.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/dlm_daemon.h -->
# File Research: sources/local-fs/dlm/dlm_controld/dlm_daemon.h

## Purpose
Central internal header for `dlm_controld`. It pulls in system, Corosync, kernel DLM, control-library, config, list, rbtree, and endian headers; defines global daemon state; declares message structures; defines lockspace/run data structures; and declares cross-module functions.

## Main Contents
- Filesystem paths for runtime, logs, and `/etc/dlm/dlm.conf`.
- Default logging modes and priorities.
- Option index enum and `struct dlm_option`, including default, CLI, file, and dynamic values plus reload/dynamic flags.
- Global daemon variables controlled by `EXTERN`, including cluster membership, quorum, node ids, misc minors, lockspaces list, fence state, plock fd/client, and run operations.
- DLM CPG message type enum covering protocol negotiation, lockspace start, plock operations, deadlock messages, fencing, helper-run requests/replies/cancel, and release-recover.
- `struct dlm_header`, the common internal CPG message header, with version, type, sender/target nodeids, global lockspace id, flags, and two message data fields.
- `struct lockspace` with config, CPG handle/fd/client, membership-change state, kernel/FS flags, plock state, resource trees, and dormant deadlock fields under `#if 0`.
- Run-command structures: `run_info`, `node_run_result`, `run`, `run_request`, and `run_reply`.
- Function prototypes for action/config/cpg/daemon/deadlock/main/member/fence/netlink/plock/logging/crc/helper modules.

## Integration Points
- Included by nearly every `dlm_controld` implementation file.
- Ties together global state ownership and cross-file contracts.
- Bridges public control protocol (`dlm_controld.h`) with internal daemon message protocol.

## Risks and Notes
- Large global-state surface makes module coupling high; many functions depend on globals rather than explicit context.
- Several deadlock fields/prototypes remain although the struct fields and active dispatch are disabled.
- `MAX_NODES` is tied to Corosync CPG member limits; mismatches with upstream Corosync would affect arrays throughout the daemon.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/dlm_daemon.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/fence.c -->
# File Research: sources/local-fs/dlm/dlm_controld/fence.c

## Purpose
Runs external fence/unfence agents and reports their asynchronous results for daemon-wide fencing coordination.

## Main Behavior
- `run_agent()` creates a pipe, forks, writes newline-separated agent arguments to child stdin, redirects child stdout/stderr to `/dev/null`, and `execlp()`s the configured agent.
- `fence_request()` builds fence arguments from `fence_config_agent_args()`, adds `fail_time=<walltime>`, launches the selected agent, logs request context, and returns the child pid.
- `fence_result()` polls a fence-agent pid with `waitpid(WNOHANG)`:
  - `-EAGAIN` means still running.
  - Exit status is returned as result.
  - Signal termination returns result `-1`.
- `unfence_node()` reads node fence config, runs all devices marked `unfence` with `action=on`, waits synchronously for each, and fails on the first run/wait/nonzero-exit error.

## Integration Points
- Used by `daemon_cpg.c` fencing work loop.
- Consumes parsed config from `fence_config.c`.
- Uses `reason_str()` for logging daemon CPG failure reason names.

## Risks and Notes
- Agent output is discarded, so diagnosis depends on daemon logs and agent exit status.
- Parent writes the entire argument buffer once and treats short writes as failure.
- `unfence_node()` is synchronous and can block daemon progress while agent commands run.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/fence.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/fence_config.c -->
# File Research: sources/local-fs/dlm/dlm_controld/fence_config.c

## Purpose
Parses DLM fence configuration from `dlm.conf`-style sections and provides iteration and argument construction helpers for fencing/unfencing.

## Main Behavior
- Supports two config forms:
  - `fence_all <name> <agent> <args>` plus optional `unfence_all`, applying one device to all nodes.
  - Repeated `device <name> <agent> <args>` sections with `connect <name> node=<nodeid> <args>` and optional `unfence <name>`.
- `fence_config_init()` scans the config file for devices connected to a target node and fills up to `FENCE_CONFIG_DEVS_MAX` device/connect pairs.
- `read_config_section()` validates device/connect name matching, finds the target node's connection line, captures device and connection args, and tracks unfence markers.
- `same_base_name()` treats device names with matching prefixes before `:` as parallel devices.
- `fence_config_next_parallel()` advances to the next device with the same base name.
- `fence_config_next_priority()` advances to the next device with a different base name.
- `fence_config_agent_args()` combines device args, connection args, optional extra args, converts spaces to newlines, and adds `node=<nodeid>` when missing.
- `fence_config_free()` releases allocated device/connect entries and zeroes the config.

## Integration Points
- Public declarations are in `fence_config.h`.
- Used by `fence.c` and `daemon_cpg.c`.
- Falls back to a global `fence_all_device` in `daemon_cpg.c` when no node-specific config exists.

## Risks and Notes
- Config grammar is line-oriented and intentionally narrow; malformed sections return negative errno-style errors.
- `fence_config_init()` increments `pos` without an explicit bound check before assigning arrays, so configs listing more than four devices for a node can overflow the fixed arrays.
- Argument conversion is simplistic: every space becomes newline, so values containing spaces are not representable.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/fence_config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/fence_config.h -->
# File Research: sources/local-fs/dlm/dlm_controld/fence_config.h

## Purpose
Public internal header for parsed fence configuration structures and helper functions.

## Main Contents
- Limits:
  - `FENCE_CONFIG_DEVS_MAX` = 4 devices per node.
  - `FENCE_CONFIG_NAME_MAX` = 256 bytes including NUL.
  - `FENCE_CONFIG_ARGS_MAX` = 4096 bytes including NUL.
- `struct fence_device`: device name, agent executable, device args, and unfence flag.
- `struct fence_connect`: connection name and per-node connection args.
- `struct fence_config`: arrays of device/connect pointers for one node plus nodeid and current position.
- Declares initialization, free, parallel/priority iteration, and final agent-argument construction functions.

## Integration Points
- Included by `dlm_daemon.h`.
- Implemented by `fence_config.c`, consumed by `fence.c` and `daemon_cpg.c`.

## Risks and Notes
- Structures expose raw pointers owned by `fence_config_init()`/`fence_config_free()`.
- Callers must respect `pos` and fixed array bounds.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/fence_config.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/helper.c -->
# File Research: sources/local-fs/dlm/dlm_controld/helper.c

## Purpose
Child helper process for running a restricted set of distributed commands requested through daemon CPG run messages, then reporting results back to the main daemon.

## Main Behavior
- Maintains up to 32 running commands, mapping pid to run UUID and command id.
- `_get_cmd_id()` allowlists only:
  - `lvm lvchange --refresh ...`
  - `lvm lvs ...`
- `exec_command()` tokenizes a command string with limited backslash escaping, reports the recognized command id to its helper parent through a pipe, then `execvp()`s only if allowed.
- `run_helper()`:
  - Clears supplementary groups.
  - Sends periodic blank status replies to the main daemon.
  - Polls an input fd for `run_request` messages.
  - Forks a child for each request and records its pid/uuid/cmd id.
  - Handles `DLM_MSG_RUN_CANCEL` by clearing tracking state for the UUID.
  - Uses `waitid(P_ALL, WEXITED | WNOHANG)` to collect child exits.
  - Sends `run_reply` messages containing UUID, pid, and local result.
  - Logs nonzero results to syslog.

## Integration Points
- Parent/main daemon side is in `main.c` and `daemon_cpg.c` through `send_helper_run_request()`, `receive_run_request()`, and `receive_run_reply()`.
- Uses `RUN_UUID_LEN`, `RUN_COMMAND_LEN`, `run_request`, and `run_reply` from `dlm_daemon.h`.

## Risks and Notes
- Command parsing is restrictive and avoids shell execution; this is important because commands arrive through cluster messages.
- Cancel currently does not kill the running child; it only removes bookkeeping.
- Duplicated argument strings are not freed in the child before exec/exit, which is not significant for one-shot child processes.
- If helper bookkeeping loses a pid, the exit is logged and no UUID result is sent.
<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/helper.c -->