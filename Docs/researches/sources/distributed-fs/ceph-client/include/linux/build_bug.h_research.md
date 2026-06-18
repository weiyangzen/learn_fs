## sources/distributed-fs/ceph-client/include/linux/build_bug.h

**Purpose:** This header provides compile-time assertion helpers used throughout the kernel to enforce layout and constant invariants.

**Important APIs/types/functions:** `BUILD_BUG_ON_ZERO()`, `BUILD_BUG_ON_NOT_POWER_OF_2()`, `BUILD_BUG_ON_INVALID()`, `BUILD_BUG_ON_MSG()`, `BUILD_BUG_ON()`, `BUILD_BUG()`, `static_assert()`, and `ASSERT_STRUCT_OFFSET()` are the main macros.

**Control flow, state, persistence:** These macros affect compilation only. Some forms produce expression value `0` to be usable inside initializers; others emit compile-time assertions or evaluate type checking without runtime code.

**Dependencies/integration:** Depends on compiler assertion infrastructure from `linux/compiler.h`. It is used by layout-sensitive subsystems, generated protocol headers, and template macros.

**Risks and test signals:** Risks include using non-constant expressions where C requires integer constant expressions, relying on side effects in `BUILD_BUG_ON_INVALID()`, or over-constraining ABI/layout across architectures. Test signals are compile-only tests, allmodconfig/tinyconfig coverage, and intentional negative tests in headers that require fixed struct offsets.
