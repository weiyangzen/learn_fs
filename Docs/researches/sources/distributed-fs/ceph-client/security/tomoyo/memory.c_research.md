# sources/distributed-fs/ceph-client/security/tomoyo/memory.c

## Purpose

`memory.c` provides TOMOYO policy memory accounting, quota checks, allocation commit helpers, group object creation, interned string storage, and initial kernel namespace/domain setup.

## Important APIs, types, and functions

`tomoyo_warn_oom()` logs quota/allocation failures and panics if MAC initialization has not completed. `tomoyo_memory_ok()` charges allocated policy memory against `tomoyo_memory_quota[TOMOYO_MEMORY_POLICY]`. `tomoyo_commit_ok()` allocates and copies committed policy objects. `tomoyo_get_group()` finds or creates named group containers. `tomoyo_get_name()` interns strings as shared `struct tomoyo_name` entries. `tomoyo_mm_init()` initializes name hash buckets, the kernel namespace, and the initial `<kernel>` domain.

## Control flow

Most callers allocate a temporary stack object, then call `tomoyo_commit_ok()` while holding `tomoyo_policy_lock`; successful commit copies the object to heap storage, zeroes the source object to transfer references, and returns the heap pointer. `tomoyo_get_name()` hashes the string, searches the intern table under the policy mutex, increments the users count on a live match, or allocates and initializes a new `tomoyo_name`. `tomoyo_get_group()` similarly interns group containers by group name within a namespace/type list.

## State and persistence behavior

The file defines `tomoyo_memory_used[]`, `tomoyo_memory_quota[]`, `tomoyo_name_list[]`, and `tomoyo_kernel_namespace`. It initializes `tomoyo_kernel_domain` fields declared in `domain.c`. Interned names and group containers are shared, reference-counted, and reclaimed later by GC when users drop to zero. Memory use is adjusted on allocation here and on free in `gc.c`.

## Dependencies and integration points

It depends on Linux slab `ksize()`, hashing, TOMOYO path-info filling, namespace initialization from `common.c`, and global lists declared in `common.h`. Nearly every parser uses `tomoyo_get_name()`, and group policy uses `tomoyo_get_group()`. Boot initialization calls `tomoyo_mm_init()` before policy loading and enforcement.

## Risks

`tomoyo_memory_ok()` charges based on allocator size, not requested size, so quota behavior can vary by slab allocator. It assumes callers hold `tomoyo_policy_lock` where required. `tomoyo_commit_ok()` zeroes the source object on success to prevent double puts; callers must follow that ownership convention. If initialization fails before `tomoyo_policy_loaded`, `tomoyo_warn_oom()` can panic the system.

## Test signals

Signals include memory quota boundary tests, repeated intern/get/put/GC cycles, duplicate group and name reuse, allocation failure injection, boot initialization of `<kernel>` namespace/domain, and accounting returning to baseline after deleting policy objects.
