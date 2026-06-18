<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-targz-src-pkg -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-targz-src-pkg

## Purpose

This shell test validates the kernel `make perf-targz-src-pkg` target by building perf from the generated source tarball outside the full kernel tree.

## Research

The script takes the perf binary path as `$1`, changes to the kernel root via `${PERF}/../..`, runs `make perf-targz-src-pkg`, selects the newest `perf-*.tar.gz`, extracts it to a temporary directory, deletes the tarball, returns to the original directory, and runs `make -C $TMP_DEST/perf*/tools/perf`. State is the generated tarball and temporary extraction directory, both removed after use. Dependencies are `make`, `tar`, a valid perf source tree, and a complete `tools/perf/MANIFEST`. Integration tests source package completeness after files move between `tools/perf`, `tools/include`, and related locations. Risks include `ls -rt` ambiguity if multiple tarballs exist, broad cleanup of `perf-*.tar.gz`, and build failures from host dependency gaps rather than manifest omissions. Test signal is the build exit code from the extracted package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-targz-src-pkg -->
