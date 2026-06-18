# sources/distributed-fs/ceph-client/mm/kmsan/Makefile

## Purpose
This Makefile defines how the KernelMemorySanitizer runtime is built. It collects the always-built KMSAN runtime objects and applies compile flags that prevent the sanitizer runtime from recursively instrumenting itself or being wrapped by other tracing/sanitizer mechanisms.

## Important APIs, Types, And Functions
The build API is Kbuild metadata rather than C symbols. `obj-y` includes `core.o`, `instrumentation.o`, `init.o`, `hooks.o`, `report.o`, and `shadow.o`. `obj-$(CONFIG_KMSAN_KUNIT_TEST)` conditionally adds `kmsan_test.o`. File-specific variables set `KMSAN_SANITIZE := n`, `KCOV_INSTRUMENT := n`, `UBSAN_SANITIZE := n`, remove `$(CC_FLAGS_FTRACE)`, and assign `CC_FLAGS_KMSAN_RUNTIME` to every runtime object.

## Control Flow
During kernel build, Kbuild compiles the runtime with KMSAN, KCOV, UBSAN, branch profiling, ftrace, stack protector, and conserve-stack effects disabled where configured. The KUnit test is the exception: `KMSAN_SANITIZE_kmsan_test.o := y` intentionally instruments the tests so they can trigger KMSAN reports.

## State And Persistence
There is no runtime state. The file persists build policy: which objects are linked into `mm/kmsan/` and which compiler instrumentation is allowed for each object.

## Dependencies And Integration Points
It depends on Kbuild variables, compiler support for `cc-option` and `cc-disable-warning`, and Kconfig symbols `CONFIG_KMSAN_KUNIT_TEST` plus the global KMSAN build mode. It directly affects every C file in this directory by controlling recursion-prone instrumentation.

## Risks
If runtime objects become instrumented by KMSAN, ftrace, branch profiling, KCOV, or UBSAN, the sanitizer may recurse into itself, miss metadata updates, or deadlock. If the KUnit test is not instrumented, many tests stop exercising the compiler-inserted hooks. The disabled uninitialized warning on the test object is intentional because tests deliberately create uninitialized values.

## Test Signals
Build success with KMSAN enabled is the first signal. The stronger signal is `CONFIG_KMSAN_KUNIT_TEST`, where reports are expected from `kmsan_test.o` while the runtime remains non-recursive and stable.
