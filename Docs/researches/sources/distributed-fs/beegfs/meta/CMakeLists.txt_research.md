# sources/distributed-fs/beegfs/meta/CMakeLists.txt

Purpose: This CMake file defines the BeeGFS metadata server build. It creates the static `meta` library from metadata-specific application, network message, storage, session, component, resync, chunk-balancer, and fsck support sources; links it to `beegfs-common`, `dl`, `pthread`, and `blkid`; creates the `beegfs-meta` executable; and optionally builds `test-meta`.

Important build targets: `meta` is the central library. `beegfs-meta` links `source/program/Main.cpp` plus `meta`. `test-meta` is enabled unless `BEEGFS_SKIP_TESTS` is set and links `meta` with `gtest_main`. Installation rules place the daemon under `usr/sbin`, setup scripts under `usr/sbin`, systemd units under `${CMAKE_INSTALL_LIBDIR}/systemd/system`, default config under `etc/beegfs`, and the shell wrapper under `opt/beegfs/sbin`.

Control flow and integration: The file enumerates source paths explicitly, so adding/removing metadata code requires updating this list. It includes `source/`, making project-local includes like `<app/App.h>` available. The test target copies `build/dist/etc/beegfs-meta.conf` into `dist/etc/` before running `test-meta --compiler`.

State and persistence behavior: Build-time only, but it controls packaging of persistent config and service units. Missing files here can silently exclude code from the daemon or tests.

Risks and test signals: The explicit source list is easy to drift. There are duplicate/near-duplicate entries for some storage message files with inconsistent indentation, which is mostly cosmetic but can hide maintenance errors. The build tests cover config/serialization/buddy mirroring but not the full runtime daemon.
