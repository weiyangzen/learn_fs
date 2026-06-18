## sources/distributed-fs/beegfs/storage/CMakeLists.txt

Purpose: Builds and installs the BeeGFS storage server library, daemon executable, tests, and packaged runtime files.

Important APIs/types/functions: Defines static library `storage` with storage app, network message handlers, storage targets, sessions, benchmarker, buddy resyncer, chunk fetcher/balancer, quota, and toolkit sources. Links `beegfs-common`, `dl`, `pthread`, and `blkid`. Builds `beegfs-storage` from `source/program/Main.cpp`. Optionally builds `test-storage`.

Control flow: CMake includes `source`, declares source lists, links targets, copies default test config when tests are enabled, registers `test-storage --compiler`, and installs binary, systemd units, setup script, config, and wrapper script.

State and persistence: Controls installation paths under `usr/sbin`, systemd unit directory, `etc/beegfs`, and `opt/beegfs/sbin`. Test setup copies default config into the build tree.

Dependencies and integration: Integrates storage code with common BeeGFS library, GoogleTest, system libraries, and packaging components.

Risks and test signals: Manual source lists can omit new files and break link/test coverage. The library includes `source/program/Main.cpp` while the executable also compiles it, which should be checked for duplicate-symbol expectations. Test coverage currently only includes storage config tests in this file.
