<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfs.sh -->
# sources/distributed-fs/lizardfs/tests/tools/lizardfs.sh

Purpose: provides the core shell harness for building an isolated LizardFS test installation: it writes master, shadow, metalogger, chunkserver, exports, goals, topology, and mount configs; starts daemons; exposes admin/probe shortcuts; and stores all runtime addresses and paths in the global lizardfs_info_ associative array.

Important APIs, functions, and commands: `setup_local_empty_lizardfs` is the entry point; daemon wrappers include `lizardfs_master_daemon`, `lizardfs_master_n`, `lizardfs_chunkserver_daemon`, and `lizardfs_metalogger_daemon`; helpers include config writers, mount control, chunk finders, `lizardfs_probe_master`, `lizardfs_admin_master`, `lizardfs_wait_for_ready_chunkservers`, and `lizardfs_shadow_synchronized`.

Control flow: Control flow starts in `setup_local_empty_lizardfs`: prepare directories, optionally install MooseFS or legacy LizardFS, write common master files, add master/shadows, start daemons, add chunkservers, mount clients, optionally add an auto shadow/CGI server, wait for readiness, and export the info array.

State and persistence behavior: State is concentrated under `$TEMP_DIR/lizardfs/etc`, `$TEMP_DIR/lizardfs/var`, `$TEMP_DIR/mnt`, ramdisk/loop disk paths, generated config files, daemon data directories, and the exported `lizardfs_info_` array. Persistent behavior under test includes metadata files, changelogs, chunk files, export passwords, goal definitions, daemon ports, and mount command state.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `PATH`, `LIZARDFSXX_DIR`, `MAGIC_DEBUG_LOG_C`, `USE_BDB_FOR_NAME_STORAGE`, `PERSONALITY`, `SYSLOG_IDENT`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; checksum assertions can miss bugs if corruption/recalculation timing is not exercised. Test signals: hard assertions, probe/admin porcelain output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfs.sh -->
