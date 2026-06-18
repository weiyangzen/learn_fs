<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPath.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestPath.cpp

**Purpose:** Tests basic `Path` parsing of an absolute path into components.

**Important APIs/types/functions:** Constructs `Path` from `/xyz/subdir/file`, checks `size`, and indexes components with `operator[]`.

**Control flow:** Builds the path string from an expected vector, constructs `Path`, then verifies each parsed component equals the original vector element.

**State and persistence behavior:** In-memory parsing only; no filesystem access.

**Dependencies and integration points:** `Path` is used heavily by `StorageTk` for on-disk path creation, format files, and chunk layout.

**Risks:** Very narrow coverage: no relative paths, trailing slashes, duplicate slashes, root-only path, dirname/operator `/`, or absolute flag checks.

**Test signals:** Confirms baseline absolute path component extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestPath.cpp -->
