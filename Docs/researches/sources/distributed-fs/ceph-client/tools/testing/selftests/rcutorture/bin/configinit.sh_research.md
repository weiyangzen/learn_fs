# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configinit.sh

Purpose: creates a kernel `.config` from a rcutorture config specification and verifies it against the specification.

Important APIs and functions: builds a sed-generated update script to remove conflicting existing config lines, optionally runs `make clean`, runs `$TORTURE_DEFCONFIG`, applies overrides, runs `make oldconfig`, and calls `configcheck.sh`.

Control flow: capture config spec and result dir, generate filters for `CONFIG_*` names, run defconfig, save original `.config`, create new `.config`, run oldconfig with default answers, then verify.

State and persistence: modifies the kernel tree `.config`; writes `Make.clean`, `Make.defconfig.out`, `Make.oldconfig.out`, and `Make.oldconfig.err` into result dir.

Dependencies and integration: used by `kvm-build.sh`; depends on kernel make variables like `TORTURE_KMAKE_ARG`.

Risks and test signals: directly mutates the source tree build config. It exits 0 even if `configcheck.sh` prints mismatches, so callers must inspect diagnostics.
