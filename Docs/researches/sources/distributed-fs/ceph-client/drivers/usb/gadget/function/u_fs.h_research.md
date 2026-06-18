## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_fs.h

Purpose: declares internal FunctionFS utility types, state machines, and option structures used by the FunctionFS gadget function.

Important APIs and types:
- `struct ffs_dev` represents a named FunctionFS device/mount with descriptor readiness, mount state, single-device mode, callbacks for ready/closed/acquire/release, and link into a global device list.
- `ffs_lock`, `ffs_dev_lock()`, and `ffs_dev_unlock()` protect global FunctionFS device state. `ffs_name_dev()` and `ffs_single_dev()` assign naming/singleton behavior.
- `enum ffs_state` models descriptor/string reading, active operation, deactivated no-disconnect mode, and closing/error state.
- `enum ffs_setup_state` models pending/cancelled EP0 setup handling.
- `struct ffs_data` is the core FunctionFS runtime state: gadget pointer, EP0 mutex/request/completion, endpoint spinlock, refcount/open count, state/setup_state, event queue, flags, wait queues, active function, descriptor/string storage, endpoint address map, mount superblock, file permissions, eventfd, I/O completion workqueue, no-disconnect flag, reset work, and endpoint files.
- `struct f_fs_opts` embeds `usb_function_instance`, links to `ffs_dev`, tracks refcount, and records whether configfs is bypassed.
- `to_f_fs_opts()` converts a function instance to its options object.

Control flow and state machine:
- FunctionFS starts in `FFS_READ_DESCRIPTORS`, transitions to `FFS_READ_STRINGS`, then `FFS_ACTIVE` after user space supplies descriptors/strings and callbacks succeed.
- If files close with `no_disconnect`, the function can enter `FFS_DEACTIVATED`, remaining visible but refusing transfers/setup until reactivated.
- `FFS_CLOSING` is terminal for unrecoverable errors or all endpoints closed.
- EP0 setup events move between `FFS_NO_SETUP`, `FFS_SETUP_PENDING`, and `FFS_SETUP_CANCELLED`, with comments documenting required locks.

State and persistence:
- All state is in kernel memory tied to the mounted FunctionFS instance and its USB function instance.
- Raw descriptors/strings are stored after user-space writes and drive later binding.
- File permissions and superblock are write-once mount properties.

Dependencies and integration:
- Depends on USB composite, lists, mutexes, workqueues, refcounts, eventfd, superblock/VFS concepts, and endpoint-file implementations elsewhere.
- User-space FunctionFS applications provide descriptors, strings, and endpoint I/O through the FunctionFS filesystem.
- Composite gadget binding uses `f_fs_opts` and `ffs_data->func`.

Risks:
- EP0 setup cancellation races are subtle; comments require use of helper clearing functions rather than direct `setup_state` mutation.
- Descriptor/string buffers have several internal pointers into raw allocation; lifetime bugs can corrupt bind-time descriptor parsing.
- `no_disconnect` deliberately keeps a visible but nonfunctional USB function, which can surprise host-side tests.
- Global `ffs_lock` and per-instance locks must be observed consistently to avoid mount/configfs races.

Test signals:
- FunctionFS smoke tests should mount, write descriptors/strings, bind to a gadget, transfer on endpoints, close/reopen with and without `no_disconnect`, and unmount.
- Race tests around EP0 setup while user space is slow or closes files.
- Validate descriptor count/address map limits up to `FFS_MAX_EPS_COUNT`.
