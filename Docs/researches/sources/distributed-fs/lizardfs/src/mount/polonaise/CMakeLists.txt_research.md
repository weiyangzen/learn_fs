## sources/distributed-fs/lizardfs/src/mount/polonaise/CMakeLists.txt

Purpose: conditionally builds and installs the `lizardfs-polonaise-server` executable, a Thrift/Polonaise bridge over the LizardFS mount client.

Important behavior: returns early when Boost.Program_options, Polonaise, or Thrift are missing. It collects sources under `MOUNT_POLONAISE`, enables install rpath/link path handling, adds include directories, links `mfscommon`, `mount`, Polonaise, Thrift, Boost.Program_options, and Boost.System, and installs to `${BIN_SUBDIR}`.

Integration: part of the LizardFS CMake source collection pattern. The executable depends on both generated Polonaise/Thrift code and the regular mount client library.

Risks and tests: optional dependencies silently skip the server, so packaging tests should assert expected feature availability. Rpath settings affect deployment behavior and should be covered in install-tree smoke tests.
