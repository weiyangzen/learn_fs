<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_build.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_build.sh

## Purpose
This shell selftest verifies that bpftool can be built through several supported make entry points and output-directory modes from the kernel tree.

## Important APIs, Types, and Functions
The script supports `-h|--help` and forwards all other arguments to make as `J`, typically `-j`. Helper functions are `return_value` for cleanup and exit, `check` for locating an executable `bpftool`, `make_and_clean` for in-tree builds, and `make_with_tmpdir` for `OUTPUT`/`O` builds in a temporary directory.

## Control Flow
The script computes the kernel root relative to its own path, skips with KSFT code 4 if bpftool sources are absent, traps exit for tempdir cleanup, and then tries builds through top-level kbuild, `tools/bpf/bpftool`, `tools/`, and the bpftool directory. Unsupported `OUTPUT` combinations are printed as skips. Any failed make or missing binary sets `ERROR=1`, but the script continues through remaining cases before exiting with accumulated status.

## State and Persistence
It creates temporary directories with `mktemp -d`, removes them after checks, and runs `make clean` in build directories. It mutates build outputs transiently in the kernel tree or temp output roots.

## Dependencies and Integration Points
It depends on bash, GNU make, `realpath`, `find`, kernel source layout, and bpftool Makefiles. It integrates with kselftest through skip exit code 4 and human-readable build logs.

## Risks
Running `make clean` affects build artifacts under the tested directories. The script assumes it is launched from a location where `realpath --relative-to=$PWD $0` resolves under `tools/testing/selftests/bpf`. Unsupported output modes are explicitly skipped.

## Test Signals
For each attempted build, the script prints the command and expects an executable named `bpftool` under the relevant output directory. Final exit status is nonzero if any attempted build failed or no binary was found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_build.sh -->
