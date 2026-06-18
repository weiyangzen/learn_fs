## sources/distributed-fs/beegfs/storage/source/app/App.h

Purpose: Declares the storage daemon application object and exposes shared runtime services to components.

Important APIs/types/functions: `App` derives from `AbstractApp` and overrides `run()`, `stopComponents()`, component exception/network failure handlers, and message/listener accessors. It owns config, node stores, target stores/mappers, work queues, sessions, stats, listeners, workers, timer queue, chunk/buddy/benchmark components, quota stores, storage pools, and ZFS handle.

Control flow: Header declares private lifecycle phases (`preinitStorage`, `initDataObjects`, `initBasicNetwork`, `initStorage`, `initComponents`, `startComponents`, `joinComponents`, registration helpers) and public getters used throughout storage code. `getWorkQueue(targetID)` falls back to the first queue for unknown targets or global mode.

State and persistence: Owns process-wide mutable state and persistent-resource handles: PID lock, target directory locks, session store, storage targets, and dynamic `libzfs` handle.

Dependencies and integration: Includes most storage component headers and common networking/storage abstractions. `Program::getApp()` users depend on these getters.

Risks and test signals: Wide ownership surface makes destruction order important. `getWorkQueue()` assumes `workQueueMap` is non-empty. Tests should instantiate enough app state to verify queue fallback, ZFS lazy load behavior, and safe stop/delete ordering.
