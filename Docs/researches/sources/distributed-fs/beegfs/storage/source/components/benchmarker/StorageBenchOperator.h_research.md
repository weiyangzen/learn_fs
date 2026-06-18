## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.h

Purpose: Declares the storage benchmark frontend object.

Important APIs/types/functions: Owns a `StorageBenchSlave` and exposes benchmark lifecycle/control methods plus inline `getStatus()`, `getType()`, and `getLastRunErrorCode()`.

Control flow: Header inlines read-only delegation.

State and persistence: Encapsulates the slave's in-memory status and disk benchmark file operations.

Dependencies and integration: Includes `StorageBenchSlave.h`; owned by `App`.

Risks and test signals: Copying this object would be unsafe because it owns a thread-like slave, but copying is not explicitly disabled. Tests should avoid accidental copies and validate lifecycle shutdown through `App`.
