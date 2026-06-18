## sources/distributed-fs/eos/namespace/CMakeLists.txt

Purpose: Defines the EOS namespace common object library, shared library, optional static library, include paths, dependencies, install target, and QuarkDB namespace subdirectory inclusion.

Important APIs and targets: `EosNsCommon-Objects` is the object library containing namespace interfaces, utilities, QuarkDB implementations, accounting, views, inspectors, and persistency code. `EosNsCommon` is the shared library built from those objects. `EosNsCommon-Static` is Linux-only.

Control flow: CMake includes generated and qclient headers, lists all object sources, links required public dependencies, enables PIC, creates shared/static products, sets version properties, installs the shared library, and descends into `ns_quarkdb`.

State and persistence: no runtime state; build graph state controls which sources and dependencies are part of namespace linkage.

Dependencies and integration: integrates `qclient`, EOS CLI protobuf objects, `EosCommon`, XRootD utils, RocksDB, JsonCpp, and CRC/common static variants. The source list is the central contract for namespace implementation compilation.

Risks: adding a new namespace source without this list can compile in tests only if included elsewhere, causing production link gaps. Public link dependencies can affect consumers. Static target exists only under `Linux`, so portability tests must account for target absence.

Test signals: CMake configure on Linux/non-Linux, shared/static target creation, install layout, link checks for QuarkDB and RocksDB symbols, and source-list coverage for new files.
