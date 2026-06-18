# sources/distributed-fs/eos/namespace/ns_quarkdb/CMakeLists.txt

Purpose: builds and installs the QuarkDB-backed EOS namespace library and related inspection/conversion tools.

Important APIs/types/functions: declares `EosNsQuarkdb`, adds the `tests` subdirectory, links against namespace/common libraries, qclient, RocksDB, BZip2, and threads, and builds executables `eos-ns-convert-to-locality-hashes`, `eos-ns-inspect`, `eos-fid-to-path`, and `eos-inode-to-fid`.

Control flow: CMake configures include directories, compiles the library sources, links dependencies, installs the shared/static/runtime artifacts, then defines and installs the standalone utilities.

State and persistence: build configuration only. It controls installed binaries and library linkage, not runtime namespace data.

Dependencies and integration: integrates QuarkDB namespace code with `EosNsCommon`, `qclient`, `ROCKSDB::ROCKSDB`, `BZ2::BZ2`, `CLI11::CLI11`, and test targets.

Risks: missing or incompatible qclient/RocksDB/BZip2 dependencies break the namespace backend build. Tools link mostly against `EosNsCommon-Static`, so source list and library boundaries must stay consistent when new implementation files are added.

Test signals: `add_subdirectory(tests)` wires the QuarkDB namespace test suite into the build.
