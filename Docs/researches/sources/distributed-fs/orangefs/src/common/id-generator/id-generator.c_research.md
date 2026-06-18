# sources/distributed-fs/orangefs/src/common/id-generator/id-generator.c

Purpose: Implements the "safe" opaque ID registry that maps generated integer IDs to arbitrary pointers using a quickhash table.

Important APIs/functions: `id_gen_safe_initialize()` creates the hash table and increments an init count. `id_gen_safe_finalize()` decrements the count and destroys the table when it reaches zero. `id_gen_safe_register()` allocates an entry, assigns a monotonically increasing nonzero ID, stores the item pointer, and inserts it. `id_gen_safe_lookup()` returns the registered pointer. `id_gen_safe_unregister()` removes and frees an entry. `hash_key()` and `hash_key_compare()` adapt IDs to quickhash.

Control flow: Register/lookup/unregister take `s_id_gen_safe_mutex` around hash operations. Finalize locks only around destruction. Initialize is not locked.

State/persistence: Process-global registry state includes the mutex, init count, next tag, and hash table pointer. No disk persistence. IDs remain valid until unregistered/finalized.

Dependencies/integration: Uses `quickhash`, `qlist`, `gen-locks`, `pvfs2-internal.h`, and `BMI_id_gen_t` from the header. Likely used by BMI/common code that cannot safely expose raw pointers as IDs.

Risks: `id_gen_safe_register()` leaks the mutex lock if `malloc()` fails after locking. Initialize/finalize reference counting is not fully synchronized and can race. ID wraparound only skips zero, not collisions with still-live IDs after wrap. Assertions enforce initialization in register but disappear under `NDEBUG`.

Test signals: Concurrent register/lookup/unregister, init/finalize nesting, allocation-failure path, null item rejection, ID wrap simulation, and hash collision behavior.
