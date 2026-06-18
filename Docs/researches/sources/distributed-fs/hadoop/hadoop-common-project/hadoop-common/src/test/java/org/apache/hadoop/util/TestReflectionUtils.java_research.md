# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReflectionUtils.java

Purpose: tests `ReflectionUtils` constructor caching, cache clearing, thread safety, classloader leak resistance, inherited member discovery, thread-dump logging, and non-default constructor support.

Important APIs and types: `ReflectionUtils.newInstance`, `clearCache`, `getCacheSize`, `getDeclaredFieldsIncludingInherited`, `getDeclaredMethodsIncludingInherited`, `logThreadInfo`, `URLClassLoader`, and `GenericTestUtils.LogCapturer`.

Control flow: setup clears the cache. Cache tests instantiate several classes twice and verify cache size, then clear it. Thread-safety launches 32 threads doing the same construction. Negative construction checks a no-default-constructor class. Leak testing repeatedly loads a child class via fresh classloaders, instantiates it, forces GC, and expects cache size below iterations. Member tests use an anonymous subclass to require parent and child fields/methods. Other tests capture thread dump logs and validate non-default constructor argument validation.

State and persistence: state is global reflection constructor cache and captured logs. Child classloaders are intentionally made collectible.

Dependencies and integration points: foundational for configuration-driven instantiation across Hadoop.

Risks: cache synchronization bugs, classloader leaks, poor diagnostics, and confusing constructor argument errors. Test signals include cache size, multithread failure capture, log substring, and exact exception text.
