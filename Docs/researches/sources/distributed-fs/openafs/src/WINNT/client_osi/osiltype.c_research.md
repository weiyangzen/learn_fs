<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.c

Purpose: Implements the registry of dynamic OSI lock operation types, allowing alternate lock implementations such as statistics-gathering locks to be selected by name.

Important APIs, types, and functions: Globals are `osi_lockOps[OSI_NLOCKTYPES]`, `osi_lockOpNames[OSI_NLOCKTYPES]`, `osi_lockTypeIndex`, and `osi_lockTypeDefault`. `osi_LockTypeFind` returns a registered index by name. `osi_LockTypeAdd` installs an ops vector/name pair and returns the assigned index through `indexp`. `osi_LockTypeSetDefault` selects a named type or resets the default to base type 0.

Control flow and state: Types are appended from index 1 upward; index 0 is reserved for the built-in fast implementation. Lock initialization code can use `osi_lockTypeDefault` to decide whether to create a base lock or dispatching lock. There is no unregister path.

Persistence and dependencies: No persistence. State is process-global and initialized by static zeroing. It depends on `osi_lockOps_t` from `osiltype.h`, aggregate `osi.h`, and string comparison.

Integration points: `osistatl.c` registers the `"stat"` lock type through `osi_LockTypeAdd`, and base lock functions dispatch through `osi_lockOps` for nonzero lock types.

Risks: No synchronization protects the registry, so types should be registered during single-threaded initialization. Overflow silently returns without setting `indexp`. `osi_LockTypeSetDefault` has implicit return type in old C and silently ignores unknown names. Names are stored by pointer, not copied.

Test signals: Register mock ops, verify lookup and default selection, test overflow behavior at `OSI_NLOCKTYPES`, and ensure initialization order sets `"stat"` before selecting it as default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.c -->
