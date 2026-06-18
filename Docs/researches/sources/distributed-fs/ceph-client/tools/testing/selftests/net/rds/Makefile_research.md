<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/Makefile

## Purpose

The RDS Makefile registers the RDS TCP selftest and generates a build-location include file so installed tests can find the kernel source/build tree needed for configuration and coverage checks.

## Important APIs, Types, and Functions

The `all` target writes `include.sh` containing `mk_build_dir=<current directory>`. `TEST_PROGS` names `run.sh`. `TEST_FILES` installs `include.sh`, `settings`, and `test.py`. `EXTRA_CLEAN` removes `include.sh` and `/tmp/rds_logs`. `include ../../lib.mk` imports kselftest rules.

## Control Flow

On build, `all` creates the include file. On install/run, kselftest consumes `TEST_PROGS` and `TEST_FILES`. Cleanup rules remove generated include and default logs.

## State and Persistence Behavior

The only generated persistent file is `include.sh`, used by `run.sh` to locate the original build directory when tests are run from an installed tree.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kselftest `lib.mk` and the RDS scripts. Integration is with installed selftest relocation and cleanup. The risk is stale `include.sh` pointing at a moved build tree, which makes `run.sh` skip or fail source/config discovery. Test signal is that `run.sh` is staged with `test.py`, `settings`, and a valid include file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/Makefile -->
