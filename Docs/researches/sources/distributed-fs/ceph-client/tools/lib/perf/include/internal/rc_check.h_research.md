## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/rc_check.h

Purpose: Provides optional sanitizer-assisted reference-count checking macros for libperf objects.

Important APIs/macros: `DECLARE_RC_STRUCT`, `RC_STRUCT`, `ADD_RC_CHK`, `RC_CHK_ACCESS`, `RC_CHK_FREE`, `RC_CHK_GET`, `RC_CHK_PUT`, and `RC_CHK_EQUAL`. `REFCNT_CHECKING` is enabled under address/leak sanitizer defines.

Control flow: Normal builds make macros mostly transparent. Checking builds wrap reference-counted objects in an extra allocated indirection on get/add, clear/free wrappers on put, and free the original object on final free, allowing leaks/double-frees/use-after-free to surface via sanitizers.

State/persistence: Adds heap wrapper allocations in sanitizer builds. No persistent state.

Dependencies/integration: Used by cpumap and potentially other refcounted internal structs. Includes `zalloc` for `zfree`.

Risks: Macro-generated type changes can surprise code that assumes pointer identity or direct layout. All access must go through `RC_CHK_ACCESS` in checking builds. `ADD_RC_CHK` allocation failure can turn a valid object into NULL result.

Test signals: Build and run libperf tests with ASAN/LSAN, intentionally exercise balanced get/put, missed put, double put, pointer equality, and final free paths.
