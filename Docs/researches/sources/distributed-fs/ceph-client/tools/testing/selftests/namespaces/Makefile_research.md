## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/Makefile

**Purpose:** Build manifest for the namespace selftests in this subset. It compiles tests for namespace IDs, nsfs file handles, init namespace inode constants, active references, `listns`, permissions, EFAULT handling, socket namespace lookup, credential changes, stress, pagination regression, and pidfd `setns`.

**Important APIs and flow:** `CFLAGS` enables warnings, debug info, no optimization, and kernel/tool include paths. `LDLIBS += -lcap` supports tests using libcap. `TEST_GEN_PROGS` lists generated binaries. After `include ../lib.mk`, several targets add `../filesystems/utils.c` as an extra source, matching tests that call `setup_userns()`, `get_userns_fd()`, or related helpers.

**State, dependencies, integration:** There is no runtime state; it is a kselftest build declaration. It integrates with the top-level selftests framework through `lib.mk` and with namespace tests through shared utility compilation. The dependency on libcap is important for permission-drop tests.

**Risks and test signals:** If a test using `setup_userns()` is added but not listed with `../filesystems/utils.c`, link failures occur. If libcap is absent, capability permission tests fail to build. Successful build confirms all namespace programs are registered for kselftest execution.
