<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/visibility.h -->
# sources/distributed-fs/ceph-client/include/kunit/visibility.h

## Purpose
`visibility.h` provides macros for symbols that should be private in production builds but visible/exported for KUnit builds.

## Important APIs, types, and functions
`VISIBLE_IF_KUNIT` expands to nothing when `CONFIG_KUNIT` is enabled and to `static` otherwise. `EXPORT_SYMBOL_IF_KUNIT(symbol)` exports into the `EXPORTED_FOR_KUNIT_TESTING` namespace only with KUnit enabled; otherwise it emits nothing.

## Control flow
There is no runtime control flow. The macros alter linkage and module export tables at compile time.

## State and persistence behavior
No runtime state is created. The persistent effect is the presence or absence of exported symbols and symbol visibility in the built kernel/module.

## Dependencies and integration points
The header relies on Kconfig state and `EXPORT_SYMBOL_NS()` being available from included kernel headers in users. KUnit test modules must import `EXPORTED_FOR_KUNIT_TESTING` when using the exported symbols.

## Risks and test signals
Risks include accidentally exposing production-only ABI when KUnit is enabled, tests depending on internals too strongly, and missing namespace imports. Test signals are build tests with KUnit on/off, module namespace checks, and confirming non-KUnit builds keep helper symbols static/unexported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/visibility.h -->
