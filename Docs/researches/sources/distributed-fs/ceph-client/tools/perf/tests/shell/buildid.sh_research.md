<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/buildid.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/buildid.sh

## Purpose

This shell test validates build-id cache add/remove/purge operations and build-id collection during `perf record` for ELF SHA1, ELF MD5, and optionally PE binaries.

## Research

The script requires `readelf` and `cc`, conditionally enables PE testing based on libbfd and wine, builds two tiny busy-loop binaries with different linker build-id styles, and references the checked-in `pe-file.exe`. `get_build_id` extracts ELF ids via readelf and PE ids by dumping `.buildid` with objcopy and rearranging CodeView GUID bytes. `check` validates `.build-id` symlink layout, cached file existence/permissions/content, `perf buildid-cache -l`, and optional `perf buildid-list -i`. `test_add`, `test_remove`, `test_purge`, and `test_record` exercise manual cache commands and post-record cache population. State includes temporary sources, binaries, perf.data, logs, build-id dirs, wine prefix, and `/tmp/jitted`-style artifacts for PE only indirectly. Dependencies include compiler, binutils, perf buildid cache, optional libbfd/wine. Risks include shell-generated source via heredoc, PE extraction fragility, permission-bit checks, and qemu/wine environment noise. Passing signals are exact cache symlink/file validation and removal/purge absence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/buildid.sh -->
