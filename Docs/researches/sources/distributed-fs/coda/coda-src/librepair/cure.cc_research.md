# sources/distributed-fs/coda/coda-src/librepair/cure.cc

## Purpose
Conflict repair-plan generation for inconsistent replicated directories. It decides which per-replica repair operations create, remove, or rename objects.

## APIs, Types, and Functions
Exports `ObjExists()`, `RepairRename()`, `RepairSubsetCreate()`, and `RepairSubsetRemove()`. Uses `resreplica`, `resdir_entry`, `listhdr`, `struct repair`, repair opcodes such as `REPAIR_RENAME`, `REPAIR_CREATED`, `REPAIR_CREATES`, `REPAIR_CREATEF`, `REPAIR_CREATEL`, `REPAIR_REMOVED`, and `REPAIR_REMOVEFSL`, plus `InsertListHdr()`, `InRepairList()`, `IsCreatedEarlier()`, and `GetParent()`.

## Control Flow, State, and Persistence
`RepairRename()` finds parent paths for an object's FID on each replica, warns when renamed on some sites and removed on others, prompts the repairer to choose a preserved path, then inserts rename or removal operations for replicas that differ. `RepairSubsetCreate()` marks replicas missing an object and chooses create opcode based on directory/symlink/file, mount-point flag, hard-link-like existing FIDs, and existing repair list. `RepairSubsetRemove()` inserts remove operations at replicas where the object is present. State is accumulated in per-replica repair lists.

## Dependencies and Integration
Depends on resolution data structures from `resolve.h`, repair file/list helpers from `repio.h`, parser prompting, filesystem `stat/lstat`, and Vice FID conventions. Called by directory resolution code after predicates classify conflicts.

## Risks and Test Signals
Risks include interactive prompts inside library logic, fixed `MAXHOSTS`, path buffer concatenation, incomplete automation for created-parent cases, possible allocation-size off-by-one in path construction, and assumptions about FID/name equivalence across replicas. Test signals are generated repair op lists for subset create/remove/rename cases, warnings for mixed rename/remove, and successful subsequent `dorepair`.
