# sources/distributed-fs/ceph-client/tools/testing/cxl/config_check.c

Purpose: compile-time guard ensuring the kernel configuration supports the CXL test modules.

Important APIs, types, and functions: defines `check()` containing `BUILD_BUG_ON()` assertions for `CONFIG_64BIT`, CXL bus/acpi/pmem as modules, CXL region invalidation test, NVDIMM security test, debugfs, and memory hotplug.

Control flow: there is no runtime logic beyond the function body; Kbuild includes this object in multiple CXL test modules so build fails if required symbols are not configured.

State and persistence: none.

Dependencies and integration points: depends on Kconfig macros and `<linux/bug.h>`. It integrates with each mocked CXL module through Kbuild inclusion.

Risks: requirements are intentionally strict. If a valid new test configuration differs, this file must be updated or the build will fail. Because `check()` itself is not called, its value is in compile-time expression checking.

Test signals: a successful module build means required config predicates passed. Build failures identify missing module/test/debugfs/hotplug support.
