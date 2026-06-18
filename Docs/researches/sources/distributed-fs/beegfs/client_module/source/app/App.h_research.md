## sources/distributed-fs/beegfs/client_module/source/app/App.h

### Purpose
Declares the BeeGFS client kernel module `App` object, lifecycle functions, helper functions, runtime state fields, and inline accessors used throughout the client module.

### Important APIs, Types, and Functions
- Return codes: `APPCODE_NO_ERROR`, `APPCODE_PROGRAM_ERROR`, `APPCODE_INVALID_CONFIG`, `APPCODE_INITIALIZATION_ERROR`, and `APPCODE_RUNTIME_ERROR`.
- Forward declarations cover config, logger, components, node stores, mappers, state stores, buffer stores, ack store, filters, inode ref store, and statfs cache.
- Lifecycle declarations: `App_init`, `App_uninit`, `App_run`, `App_stop`.
- Internal setup declarations: `__App_initDataObjects`, inode ops, local node info, components, start/stop/join, logging, mount check, and interface discovery.
- External helpers: version string, local interface update/clone, fsUUID clone/update, local/RDMA NIC clone.
- `struct App` stores configuration, logger, fsUUID mutex, filters, preferred lists, RDMA NIC list and mutex, local and remote node stores, target/buddy mappers, state stores, buffer stores, ack/inode/statfs stores, components, lock ack counter, retry/benchmark flags, inode operation tables, socket domain, and debug counters under `BEEGFS_DEBUG`.
- Inline getters expose nearly all internal fields, plus setters for retry and benchmark flags.
- Debug inline functions increment counters under a mutex; in non-debug builds increments compile to no-ops.

### Control Flow and State
The header centralizes ownership and access patterns for the `App` state object. Most modules obtain dependencies through inline getters rather than receiving narrower interfaces. `App_lockNicList` and `App_unlockNicList` define a manual lock protocol for direct RDMA NIC list access.

### Dependencies and Integration Points
Includes mount config, list iterators, NIC address list, atomic/mutex/thread abstractions, common definitions, and bit store headers. It is included by most client module subsystems that need application context or shared stores.

### Risks and Edge Cases
The broad `App` struct and many inline getters create tight coupling across the client module. Manual NIC-list locking is error-prone because callers must pair lock/unlock. `connRetriesEnabled` is volatile but not a full synchronization primitive. Inline non-static function definitions in a header can be risky in C unless compiler/linkage expectations are controlled; declarations are `static inline` prototypes but definitions omit `static inline` text in the shown file, relying on prior declarations style and compiler behavior.

### Test Signals
Compile tests across supported kernels are essential because struct members and inode operation fields depend on feature macros. Runtime mount/unmount tests exercise getter wiring and state ownership. Debug builds should exercise counter increments.
