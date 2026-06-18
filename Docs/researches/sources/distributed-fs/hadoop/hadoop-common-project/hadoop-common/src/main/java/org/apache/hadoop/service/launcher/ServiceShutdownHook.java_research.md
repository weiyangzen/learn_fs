# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceShutdownHook.java

Purpose: `ServiceShutdownHook` adapts a Hadoop `Service` into a JVM shutdown hook that calls `stop()` during process shutdown.

Important APIs and types: constructor stores a `WeakReference<Service>`. `register(int)` adds the hook to `ShutdownHookManager`; `unregister()` removes it; `run()` delegates to `shutdown()`; `shutdown()` stops and clears the service reference and returns whether stop succeeded.

Control flow: registration first unregisters any existing hook registration for the same instance. On shutdown, the service reference is read and cleared under synchronization, then `service.stop()` is invoked outside that synchronized block. Stop failures are logged and swallowed.

State and persistence behavior: state is only the weak service reference. Clearing the reference prevents duplicate stops from the same hook and avoids pinning the service in memory. No durable persistence occurs.

Dependencies and integration points: used by `ServiceLauncher.coreServiceLaunch`; integrates with Hadoop `ShutdownHookManager`, `Service`, and SLF4J.

Risks: weak references mean a service can be garbage-collected before shutdown if nothing else holds it. `unregister()` may see `IllegalStateException` during shutdown and logs at info. Stop exceptions do not affect process exit.

Test signals: cover register/unregister idempotence, weak reference clearing, successful stop return value, exception-swallowing path, and behavior when `ShutdownHookManager` is already shutting down.
