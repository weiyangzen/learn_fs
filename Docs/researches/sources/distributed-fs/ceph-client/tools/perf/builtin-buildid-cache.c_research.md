# sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-cache.c

Purpose: implements `perf buildid-cache`, managing perf's build-id cache by adding, removing, purging, updating, listing, finding missing DSOs, and storing kcore snapshots.

Important APIs, types, and functions: kcore helpers include `build_id_cache__kcore_buildid()`, `build_id_cache__kcore_existing()`, and `build_id_cache__add_kcore()`. File operations are `build_id_cache__add_file()`, `build_id_cache__remove_file()`, `build_id_cache__purge_path()`, `build_id_cache__purge_all()`, `build_id_cache__update_file()`, and `build_id_cache__show_all()`. Missing-cache reporting uses `dso__missing_buildid_cache()` and `build_id_cache__fprintf_missing()`. `perf_buildid_cache_config()` reads `buildid-cache.debuginfod`. `cmd_buildid_cache()` parses options and orchestrates actions.

Control flow: config is read first to configure debuginfod, then options are parsed. The command rejects missing action/list and list combined with mutations. Optional namespace context is created from `--target-ns`. Missing-cache mode opens a perf session for the supplied perf.data file. Symbol initialization and pager setup occur before executing the requested list/add/remove/purge/update/kcore actions.

State and persistence: this command directly mutates `buildid_dir`, adding files keyed by build-id, removing entries, purging all entries, and writing kcore snapshots under `[kernel.kcore]/<buildid>/<timestamp>`. It may also use debuginfod settings and namespace mount context. It reads perf.data when reporting missing cache entries.

Dependencies and integration points: relies on perf build-id utilities, namespace helpers, symbol/session code, kcore copy helpers, proc module comparison, strlist parsing, debuginfod setup, and config loading.

Risks: partial kcore copy failures attempt best-effort recursive cleanup but can leave cache fragments. Multiple actions can be specified together, so ordering matters. Many helper failures only warn and continue, with `ret` not always reflecting per-file failures. Namespace entry must bracket build-id reads correctly. `errno`-based diagnostics after helper calls may be stale if helpers do not preserve errno.

Test signals: test add/remove/update/purge/list on temporary ELF files, `--purge-all` on an isolated buildid dir, missing-cache reporting from small perf.data, kcore add with forced and duplicate detection paths, target namespace behavior, and debuginfod config parsing.
