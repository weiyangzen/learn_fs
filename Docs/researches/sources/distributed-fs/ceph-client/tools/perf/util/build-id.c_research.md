# sources/distributed-fs/ceph-client/tools/perf/util/build-id.c

## sources/distributed-fs/ceph-client/tools/perf/util/build-id.c

Purpose: this file implements perf build-id handling: discovering build ids, writing build-id tables to perf data, maintaining the build-id cache, resolving cached filenames, listing/completing cached ids, and caching DSOs after a session.

Important APIs and functions: discovery/formatting includes `build_id__snprintf()`, `sysfs__snprintf_build_id()`, `filename__snprintf_build_id()`, `build_id__init()`, and `build_id__is_defined()`. Session integration includes `build_id__mark_dso_hit()`, `perf_session__write_buildid_table()`, `perf_session__read_build_ids()`, `perf_session__cache_build_ids()`, and `__perf_session__cache_build_ids()`. Cache APIs include `build_id_cache__linkname()`, `build_id_cache__origname()`, `build_id_cache__kallsyms_path()`, `build_id_cache__list_all()`, `build_id_cache__complement()`, `build_id_cache__cachedir()`, `build_id_cache__list_build_ids()`, `build_id_cache__add()`, `__build_id_cache__add_s()`, `build_id_cache__cached()`, and `build_id_cache__remove_s()`.

Control flow: sample processing marks DSOs as hit from IP and callchain maps. Writing a build-id table walks host and guest machines, skips unhit non-vdso DSOs, selects kernel/user misc flags, and writes padded `PERF_RECORD_HEADER_BUILD_ID` records. Caching creates a source-shaped directory under `buildid_dir`, stores `elf`, `debug`, `kallsyms`, or `vdso` files, updates `.build-id/xx/yyyy` symlinks, scans SDT probes when enabled, and optionally fetches debuginfo through debuginfod. Listing/completion walks `.build-id` two-level directories and can validate ids against current files.

State and persistence: `no_buildid_cache` disables cache writes process-wide. The build-id cache persists on disk under `buildid_dir`, with both source-path directories and `.build-id` symlinks. DSO hit flags and build ids live in perf machine/session state.

Dependencies and integration: depends on DSO, machine, map, symbol, session, namespace, probe cache, debuginfod, filesystem utility, and perf header code. It integrates with recording/reporting to make binaries and debug info available after collection.

Risks: many paths manipulate filesystem names and symlinks; namespace/root-dir handling must be correct for containers and guests. `build_id_cache__valid_id()` only validates absolute regular paths and kallsyms. Debug file detection uses a `.ko` suffix check that assumes name length is at least three. Cache removal follows relative symlink paths and then removes directories, so path correctness matters. Build ids larger than SHA-1 are truncated to `BUILD_ID_SIZE`.

Test signals: read build ids from files and sysfs; write/read session build-id tables for host/guest/vdso/kcore/modules; cache with namespaces, root dirs, stripped binaries with debug files, debuginfod enabled/disabled; list/complete ids; remove cache entries; and run with `disable_buildid_cache()`.
