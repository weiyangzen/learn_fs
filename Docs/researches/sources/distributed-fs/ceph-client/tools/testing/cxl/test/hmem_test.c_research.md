# sources/distributed-fs/ceph-client/tools/testing/cxl/test/hmem_test.c

Purpose: optional hmem platform-device stub used by CXL tests to exercise dax_hmem integration.

Important APIs, types, and functions: module parameter `hmem_test` gates registration. Defines empty `hmem_test_work()`, `hmem_test_release()`, static `hmem_test_device`, `hmem_test_init()`, and `hmem_test_exit()`.

Control flow: `hmem_test_init()` returns zero without action unless the module parameter is true; when enabled it registers `hmem_platform.1`. `hmem_test_exit()` unregisters it only when enabled. The release callback clears the static device structure after unregister.

State and persistence: the static `hmem_platform_device` persists for the module lifetime. Registering it creates a platform device with initialized work item and release callback.

Dependencies and integration points: includes DAX bus internals and integrates with wrapped `walk_hmem_resources()` in `mock.c`/`cxl.c`, which recognizes `hmem_platform.1`.

Risks: the release callback `memset()` on a static object means re-registration after release depends on module lifecycle and reinitialization. The work function is intentionally empty.

Test signals: with `hmem_test=1`, a platform device named `hmem_platform.1` should exist and trigger the mock hmem resource path; without it, no device is registered.
