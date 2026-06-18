# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/check_config.sh

Purpose: probes optional build dependencies for mm selftests and emits local config files.

Important APIs/types/functions: creates a temporary C file including `<liburing.h>`, compiles it with `$CC $CFLAGS`, writes `local_config.h` and `local_config.mk` with either liburing support or empty `IOURING_EXTRA_LIBS`.

Control flow: compile success produces `#define LOCAL_CONFIG_HAVE_LIBURING 1` and `IOURING_EXTRA_LIBS = -luring`; failure writes a comment/no-library setting. Temporary files are removed at the end.

State and persistence: creates or overwrites `local_config.h` and `local_config.mk` in the mm selftest directory/output context.

Dependencies and integration points: compiler, CFLAGS, liburing headers/libraries, Makefile include flow.

Risks: no `set -e`; cleanup uses `rm ${tmpname}.*`, which may fail noisily if glob expansion differs. Compile-only probing does not link liburing.

Test signals: affects whether COW/iouring-related code is compiled and whether missing liburing warning appears.
