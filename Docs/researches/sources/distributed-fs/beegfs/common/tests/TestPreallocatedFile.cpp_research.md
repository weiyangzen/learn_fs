<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPreallocatedFile.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestPreallocatedFile.cpp

**Purpose:** Tests `PreallocatedFile` allocation guarantees, allocation failure, serialization size enforcement, optional empty state, and truncated-file error handling.

**Important APIs/types/functions:** Fixture creates/removes temp directories. Tests construct `PreallocatedFile<char, 1024*1024>`, `PreallocatedFile<char, max off_t>`, `PreallocatedFile<uint64_t>`, and `PreallocatedFile<uint64_t, 1>`; call `write`, `read`, `stat`, and `truncate`.

**Control flow:** Allocation test checks logical size `Size + 1` and block allocation at least that many bytes. Failure test expects huge preallocation to throw `std::system_error`. Read/write test writes a `uint64_t`, verifies too-small serialization throws, reads the value back, confirms unwritten file returns `boost::none`, truncates the good file, and expects read to throw.

**State and persistence behavior:** Creates real temporary files and removes them through `StorageTk::removeDirRecursive`.

**Dependencies and integration points:** Direct test signal for `PreallocatedFile.h` and indirect signal for `StorageTk` recursive deletion.

**Risks:** Allocation block-count expectations depend on filesystem behavior; sparse/preallocation semantics may differ. Huge allocation failure assumption is practical but environment-dependent.

**Test signals:** Covers the main API contract and important failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPreallocatedFile.cpp -->
