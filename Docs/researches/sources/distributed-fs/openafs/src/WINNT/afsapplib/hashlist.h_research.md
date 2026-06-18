# sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.h

## Purpose
Declares a generic, thread-safe object list with optional hash indexes. The header is also the primary usage documentation: it explains ownership, enumeration lifetime, key callbacks, duplicate handling, update requirements, and safe object deletion patterns.

## Important APIs and Types
Core exported types are `EXPANDARRAY`, `HASHLIST`, `HASHLISTKEY`, and `ENUMERATION`/`ENUM`. `HASHLISTENTRY` stores a generic object pointer, its hash value, and slot links. `HASHLISTKEYDEBUGINFO` reports bucket counts and distribution effectiveness. Callback typedefs define the key contract: compare object to data, hash object, and hash raw lookup data.

`HASHLIST` exposes `Add`, `Remove`, `Update`, `AddUnique`, `fIsInList`, `CreateKey`, `FindKey`, `RemoveKey`, list enumeration, object accessors, count retrieval, and explicit `Enter`/`Leave` locking. `HASHLISTKEY` exposes hash callback wrappers, keyed enumeration/object lookup, keyed membership, and debug distribution helpers. `ENUMERATION` exposes `GetObject`, `FindNext`, and `FindPrevious`, with destructor-based lock release.

## State, Dependencies, and Integration
The declarations assume Win32 types (`PVOID`, `LPCTSTR`, `CRITICAL_SECTION`, `BOOL`) and OpenAFS's `EXPORTED` convention. The owning list stores raw pointers and never deletes caller objects, so integration code must manage object lifetimes and call `Update` after mutating indexed fields. `SetCriticalSection` lets a caller supply a shared lock to coordinate hashlist access with broader object state.

## Risks and Test Signals
The public contract makes enumeration lifetime part of synchronization; callers that break early must delete the enumeration. `AddUnique` semantics differ depending on whether a key is provided: no key means pointer uniqueness, key means compare-callback uniqueness. Callback correctness is critical: hash-object/hash-data must agree with compare or lookup silently misses entries. Header examples are the main test signal; additional tests should assert the documented auto-delete behavior at traversal end, explicit delete behavior mid-traversal, key lookup with colliding values, and update requirements after changing key fields.
