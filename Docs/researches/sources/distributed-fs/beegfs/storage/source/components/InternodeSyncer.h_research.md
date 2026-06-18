## sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.h

Purpose: Declares the PThread component responsible for cluster synchronization.

Important APIs/types/functions: Static download/register/session helpers, `publishTargetState()`, `publishLocalTargetStateChanges()`, `requestBuddyTargetStates()`, and force setters for target states, capacities, storage pools, and network checks. Private helpers implement `syncLoop()`, network checks, idle connection cleanup, target updates, capacity publishing, and mgmtd pool refresh.

Control flow: Header exposes force setters that lock a mutex, set a boolean, and are consumed by private get-and-reset methods in the sync loop.

State and persistence: Owns in-memory force flags and log context. It does not directly persist, but coordinates updates to persistent target/buddy/session-related state through other components.

Dependencies and integration: Extends `PThread`, uses BeeGFS node stores, datagram listener, storage target forward declaration, and common logging/component headers. Called by `App`, message handlers, and storage targets.

Risks and test signals: Force flags are boolean, so repeated requests coalesce. Tests should verify each force setter triggers one sync-loop action and is reset safely under concurrency.
