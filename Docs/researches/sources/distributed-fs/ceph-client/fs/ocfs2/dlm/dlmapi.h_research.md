# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmapi.h

## Purpose

`dlmapi.h` is the externally exported OCFS2 DLM interface. It defines DLM status codes, lock modes, public lock flags, lock status block layout, AST/BAST callback signatures, lock/unlock APIs, domain registration APIs, diagnostic printing, and eviction callback registration.

## Important APIs, Types, and Functions

`enum dlm_status` enumerates DLM return/status values, including traditional DLM outcomes and OCFS2 extensions such as `DLM_RECOVERING` and `DLM_MIGRATING`. `dlm_errname()` converts them to strings, and `dlm_error()` logs non-transient statuses.

`struct dlm_lockstatus` is the caller-visible lock status block. Callers are only allowed to access `status`, `flags`, `lockid`, and the 64-byte LVB. `DLM_LKSB_*` flags describe LVB get/put direction.

Lock modes are `LKM_NLMODE`, `LKM_PRMODE`, `LKM_EXMODE`, with other modes marked unsupported/invalid. Public flags include `LKM_VALBLK`, `LKM_NOQUEUE`, `LKM_CONVERT`, `LKM_UNLOCK`, `LKM_CANCEL`, `LKM_INVVALBLK`, `LKM_FORCE`, `LKM_LOCAL`, and many reserved/unsupported compatibility flags. Internal extension flags occupy high bits: `LKM_MIGRATION`, `LKM_PUT_LVB`, `LKM_GET_LVB`, and `LKM_RECOVERY`.

The core APIs are `dlmlock()`, `dlmunlock()`, `dlm_register_domain()`, `dlm_unregister_domain()`, `dlm_print_one_lock()`, and eviction callback helpers `dlm_setup_eviction_cb()`, `dlm_register_eviction_cb()`, and `dlm_unregister_eviction_cb()`.

## Control Flow

A filesystem registers a lock domain with `dlm_register_domain()`, passing a domain name, key, and filesystem locking protocol version. It then requests locks with `dlmlock()`, supplying a mode, LKS, flags, name, AST callback, callback data, and BAST callback. Granted or converted locks complete through AST callbacks; blocking notifications use BAST callbacks. Unlocks use `dlmunlock()` and optionally an unlock AST.

Domain unregister tears down the DLM context and associated network handlers. Eviction callbacks let upper layers learn when nodes are evicted or leave, allowing filesystem-level recovery and cleanup.

## State and Persistence Behavior

This header defines API state, not storage. Lock state lives in DLM contexts/resources/locks. The LVB is cluster-visible lock metadata associated with a lock resource and can carry filesystem state across lock transfers, but it is not persistent disk state by itself.

## Dependencies and Integration Points

The API integrates OCFS2 filesystem locking code with the O2CB DLM implementation. It depends on Linux list types for eviction callbacks and on internal DLM definitions for opaque `struct dlm_ctxt` and `struct dlm_lock`. It also integrates with debug code via status-name comments.

## Risks and Edge Cases

The flag namespace contains unsupported DLM compatibility flags and internal-only high bits. Public callers using unsupported or internal flags can get rejected or corrupt protocol assumptions. `DLM_LVB_LEN` is fixed at 64 bytes and is embedded into wire structures, so changing it would be ABI-wide.

Status interpretation matters: `DLM_NORMAL` is request in progress in comments, while granted/completion may be signaled asynchronously. Callers must honor AST/BAST callbacks and not assume `dlmlock()` return alone means the lock is usable unless the API documents synchronous status.

## Test Signals

Exercise domain register/unregister, PR and EX lock acquire, convert, noqueue failure, cancel, forced unlock, LVB get/put, recovery/migration rejection, eviction callbacks, and error-name logging. ABI tests should watch `struct dlm_lockstatus` and `DLM_LVB_LEN`.
