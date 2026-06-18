# sources/distributed-fs/lizardfs/cmake/FindDB.cmake

## Purpose
This find module locates Berkeley DB headers and library and extracts a version string from `db.h`.

## Important APIs, Types, and Functions
It sets `DB_LIBRARY`, `DB_INCLUDE_DIR`, `DB_VERSION_STRING`, and `LIZARDFS_HAVE_DB` when found. It uses `find_library(db)`, `find_path(db.h)`, `file(STRINGS ...)`, regex extraction of version macros, and `find_package_handle_standard_args`.

## Control Flow and State
If headers are found, version macro lines are read and transformed into a five-component version string. Package handling requires both library and include dir and accepts a version variable for CMake's find-package reporting.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(DB 11.2.5.2)`. `config.h.in` can emit `LIZARDFS_HAVE_DB`.

## Risks and Edge Cases
The regex assumes Berkeley DB version macros are present and formatted as expected. Version extraction may produce incorrect strings if the header changes. The module does not set include/library variables into a namespaced imported target.

## Test Signals
CMake find-package success and generated `LIZARDFS_HAVE_DB` are the primary signals. Build targets depending on Berkeley DB will reveal missing link/include propagation.
