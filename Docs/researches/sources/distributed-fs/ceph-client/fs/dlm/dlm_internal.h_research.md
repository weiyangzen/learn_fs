# sources/distributed-fs/ceph-client/fs/dlm/dlm_internal.h

## Purpose
`dlm_internal.h` is the central private header for the DLM implementation. It defines logging helpers, lockspace membership and recovery structures, lock block (`dlm_lkb`) state, resource block (`dlm_rsb`) state, wire protocol structures, lockspace-wide state (`dlm_ls`), flag conversion helpers, and debugfs stubs.

## Important Types and Constants
- `struct dlm_member` records member node id, weight, slot, communication sequence, and generation.
- `struct dlm_recover` carries recovery node configuration and sequence data.
- `struct dlm_args` is an internal normalized argument package passed from public lock/unlock entry points to lower stages.
- `struct dlm_user_args` and `struct dlm_callback` connect userspace lock requests with completion and blocking AST delivery.
- `struct dlm_lkb` is the lock block. It stores resource pointer, refcount, local and remote ids, external flags, status-block flags, distributed/internal flags, modes, wait state, queue links, callback state, recovery sequence, LVB pointer, and caller/user callback data.
- `struct dlm_rsb` is the resource block. It stores lockspace pointer, refcount, spinlock, resource name/hash, master and directory node ids, LVB state, lookup/grant/convert/wait queues, slow-list/scan/recovery/list membership, and recovery counters.
- `struct dlm_header`, `struct dlm_message`, `struct dlm_rcom`, `struct dlm_opts`, and `union dlm_packet` define the on-wire DLM message, recovery communication, option, and common header formats.
- `struct rcom_status`, `struct rcom_config`, `struct rcom_slot`, and `struct rcom_lock` define RCOM payloads.
- `struct dlm_ls` is the lockspace object and owns the global id, local flags, LKB xarray, RSB rhashtable and slow lists, scan timer, waiters/orphans, membership lists, slots, debugfs dentries, uevent/recovery state, request queue, recovery buffers, master/directory dump lists, callbacks, miscdevice, and lockspace name.

## Control Flow Role
This header does not implement the main algorithms, but it defines the state machine vocabulary consumed throughout the DLM:
- LKB status values distinguish waiting, granted, and converting queues.
- Internal flags track master copies, resend after recovery, dead/end-of-life locks, overlap unlock/cancel, and deadlock cancellation.
- RSB flags track uncertain masters, invalid LVBs, new masters, recovery grant/convert/LVB invalidation state, inactive state, and rhashtable membership.
- LS flags coordinate recovery stop/down/lock/work/running state, RCOM wait readiness, uevent wait, callback delay, no-directory mode, receive blocking, filesystem lockspace mode, and softirq behavior.

## State and Persistence Behavior
All definitions describe in-memory kernel state. There is no disk persistence here. Runtime persistence across membership changes is achieved by recovery protocols: RSBs/LKBs are rebuilt from surviving nodes, directory records are reconstructed, and waiter state is resent or locally completed. The `dlm_ls` object is the root lifetime owner; `lockspace.c` allocates it and `lock.c`, recovery, user, and communication modules mutate the embedded tables and lists.

## Dependencies and Integration Points
The header imports kernel infrastructure including xarrays, rhashtables, kobjects, misc devices, krefs, rwsems, workqueues, spinlocks, and user access types. It also imports UAPI DLM definitions from `<linux/dlm.h>` and `<uapi/linux/dlm_device.h>`. Almost every DLM source file includes this header; its layout is therefore a cross-module ABI within the kernel DLM implementation.

## Risks
- Many fields are protected by different locks (`res_lock`, `ls_rsbtbl_lock`, `ls_lkbxa_lock`, `ls_waiters_lock`, recovery locks). Misidentifying the owner lock for a field can introduce races or deadlocks.
- The distinction between `res_nodeid` and `res_master_nodeid` is explicitly called "odd" and slated for cleanup. Code must preserve the current semantics: `res_nodeid == 0` means local master, while `res_master_nodeid` stores the real node id.
- Wire structures use fixed endian annotations and flexible payloads. Any size/layout change must preserve protocol compatibility.
- Inline flag snapshot/set helpers assume contiguous min/max bit ranges and are used for message serialization and debug output.

## Test Signals
- Build tests with `CONFIG_DLM` and `CONFIG_DLM_DEBUG` should catch declaration drift.
- Sparse/endian checking is valuable for `__le*`/`__be*` protocol fields.
- Lockdep should cover common lock ordering involving `res_lock`, `ls_rsbtbl_lock`, waiters, and recovery rwsems.
- Recovery and mixed user/kernel lock tests should validate distributed flag serialization through `dlm_dflags_val()` and `dlm_set_dflags_val()`.
