<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sdt.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/sdt.c

## Purpose

This selftest validates SDT probe discovery by embedding a DTrace-style probe in perf itself, adding perf's build-id to a temporary cache, and confirming the probe appears in the probe cache.

## Research

When both `HAVE_SDT_EVENT` and `HAVE_LIBELF_SUPPORT` are enabled, `target_function` fires `DTRACE_PROBE(perf, test_target)`. `build_id_cache__add_file` reads the executable build-id and calls `build_id_cache__add_s`. `get_self_path` reads `/proc/self/exe`. `search_cached_probe` opens `probe_cache__new` and looks for `sdt_perf:test_target`. `test__sdt_event` creates `./test-buildid-XXXXXX`, resolves an absolute build-id dir, sets it globally, adds the perf binary, searches the cached probe, calls the target function, and removes the temporary directory. Without support it skips. State is the temporary build-id cache and global buildid dir setting. Dependencies are libelf, sys/sdt.h, build-id cache, probe cache, and filesystem cleanup. Risks include missing build-id, unsupported SDT compilation, relative tempdir cleanup, and no actual probe recording despite cache validation. Test signal is finding the cached SDT event and returning `TEST_OK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sdt.c -->
