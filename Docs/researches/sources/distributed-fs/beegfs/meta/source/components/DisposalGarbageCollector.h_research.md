# sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.h

Purpose: This header exposes the disposal garbage collector scheduling entry point.

Important APIs/types: It declares a single function, `void disposalGarbageCollector();`.

Control flow and state: The header intentionally carries no state or class. The implementation function is scheduled on `App`'s `gcQueue` and requeues itself based on configuration.

Dependencies/integration: Consumers only need this header to schedule the GC function, as `App.cpp` does when `tuneDisposalGCPeriod` is nonzero. The implementation depends on `Program::getApp()`, `DisposalCleaner`, and metadata node stores.

Risks and test signals: The minimal API leaves lifecycle management implicit. Callers must ensure the global `App` and `gcQueue` are valid for the duration of the callback. No header-level tests are meaningful; behavioral tests should target the `.cpp` cleanup and requeue behavior.
