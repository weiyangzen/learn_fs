# sources/distributed-fs/coda/coda-src/venus/mgrp.h

## Purpose
This header declares the Venus multicast group abstraction and the per-operation replicated communication context. It exposes the small API used by replicated file/volume code to manage server membership, inspect return codes, choose primary/dominant hosts, and coordinate waiters for free mgrp objects.

## Important APIs, Types, and Functions
`RepOpCommCtxt` stores `HowMany`, per-VSG-member RPC2 handles, host addresses, return codes, the primary host, multicast info pointer, and pending-death flags. `mgrpent` privately inherits `RefCountedObject` and stores immutable VSG/user/authentication identity plus dynamic `rocc` state. Public methods include lifecycle (`Put`, `Kill`, `InUse`, `IsAuthenticated`), membership (`CreateMember`, `KillMember`, `GetHostSet`, `PutHostSet`), result collation (`CheckResult`, `CheckNonMutating`, `CheckCOP1`, `CheckReintegrate`), and host/version-vector selection (`RVVCheck`, `DHCheck`, `PickDH`, `GetPrimaryHost`).

## Control Flow
The header establishes a lifecycle where a `mgrpent` starts with a single reference, is linked into a VSG list, is used by friends for multi-RPCs, and is returned through `Put()`. `InUse()` treats detached entries as protected during initialization/destruction. `Mgrp_Wait()` and `Mgrp_Signal()` are declared for global coordination.

## State and Persistence Behavior
All fields are transient VM state. The header intentionally exposes `rocc` to friend classes because replicated operation state must be shared across call setup, RPC execution, and result reconciliation. Persistence effects occur indirectly through callers that use `UpdateSet` and return codes to decide whether replicated mutations reached stable storage.

## Dependencies and Integration Points
It includes RPC2, Coda inconsistency/version-vector definitions, dllist support, and `refcounted.h`. Integration is intentionally broad via friend declarations for filesystem objects, volumes, VSGs, modify logs, and CML entries.

## Risks and Test Signals
The main risks are friend-heavy coupling, raw arrays indexed by `VSG_MEMBERS`, and refcount/list invariants. Tests should verify that headers compile for all friend users, copied `RepOpCommCtxt` objects cannot be accidentally used, and `InUse()` protects both linked and detached lifecycle states.
