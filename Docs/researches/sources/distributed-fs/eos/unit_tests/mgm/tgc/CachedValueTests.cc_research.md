# sources/distributed-fs/eos/unit_tests/mgm/tgc/CachedValueTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/tgc/CachedValueTests.cc

Purpose: tests `CachedValue<T>`, a small time-based value cache used in tape garbage collection components.

Important APIs and types: `CachedValue<uint64_t>`, constructor with getter lambda and `maxAgeSecs`, and `get()`.

Control flow: the no-cache test sets `maxAgeSecs` to zero, changes the backing source value, and expects the second `get()` to call the getter again. The cached test uses a long max age and expects the second `get()` to return the original cached value.

State and persistence: cache stores the last value and age metadata in memory. No external persistence.

Dependencies and integration: used by TGC components that poll expensive values such as free space or stats. Tests ensure cache age configuration controls freshness.

Risks and test signals: tests do not manipulate time directly, so expiration after a nonzero age is not covered here. They do protect the important zero-cache behavior.
