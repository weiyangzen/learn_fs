# sources/distributed-fs/ceph-client/tools/perf/util/build-id.h

## sources/distributed-fs/ceph-client/tools/perf/util/build-id.h

Purpose: this header declares the build-id data type and cache/session APIs used throughout perf.

Important types and constants: `BUILD_ID_SIZE` is 20 bytes, `BUILD_ID_MIN_SIZE` is 16, and string sizes are hex plus NUL. `struct build_id` stores byte data plus actual size. The header declares DSO filename resolution, hit marking, build-id table read/write/cache operations, cache path/list/add/remove helpers, and the global `buildid_dir`.

Control flow and state: inline `build_id_cache__add_s()` supplies default `proper_name` and `root_dir` arguments to `__build_id_cache__add_s()`. Otherwise this is declarations only.

Dependencies and integration: includes machine/tool types and Linux integer types, and forward declares DSO, feature fd, namespace, and strlist types. It is a central interface for record, report, symbol, and cache tooling.

Risks: API callers must respect ownership of returned strings. `struct build_id` fixed maximum truncates longer future ids unless constants are changed throughout perf.

Test signals: compile all users after signature changes and run build-id cache/session tests.
