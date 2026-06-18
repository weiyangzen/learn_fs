# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zvol_os.c

Read completely: 1647 lines.

This is the FreeBSD zvol OS layer. It exposes ZFS volumes as either GEOM providers (`volmode=geom`) or character devices (`volmode=dev`) and bridges FreeBSD I/O, ioctl, open/close, kqueue, resize, rename, and destruction events to the common OpenZFS zvol core.

Key responsibilities:
- Defines FreeBSD-specific `zvol_state_os`, with a union for cdev state or GEOM provider state plus open/removal interlock flags.
- Registers the `zvol` character device switch and the `ZFS::ZVOL` GEOM class.
- Implements GEOM `open`, `close`, `access`, `BIO_GETATTR`, and bio strategy dispatch.
- Implements cdev open/close/read/write/ioctl/strategy/kqueue filtering.
- Performs zvol read/write/delete/flush by taking `zv_suspend_lock`, range locks, DMU transactions, ZIL logging, and optional `zil_commit()`.
- Creates, renames, resizes, removes, and frees FreeBSD device nodes/providers for zvol minors.

Important implementation details:
- `zpool_on_zvol` is a dangerous sysctl that controls whether zvols may be used recursively as pool vdevs. GEOM probing normally rejects zvols during ZFS vdev probe to avoid namespace-lock deadlocks.
- First open and last close carefully acquire `zv_suspend_lock` before `zv_state_lock`; retry paths drop locks and yield to avoid lock inversion with `spa_namespace_lock`.
- GEOM mode counts access deltas from `acr/acw/ace`, while cdev mode increments/decrements a single open count.
- `zvol_strategy_impl()` handles `BIO_READ`, `BIO_WRITE`, `BIO_FLUSH`, and `BIO_DELETE`. It chunks data by `zvol_maxphys`, maps checksum errors to `EIO`, updates dataset kstats, and commits the ZIL when synchronous semantics require it.
- Asynchronous GEOM/cdev bio handling hashes `(zv, curcpu, offset)` to a zvol taskq, while sync-capable contexts may execute inline.
- cdev ioctl supports sector/media size, flush, delete/unmap, stripe attributes, GEOM-style attributes, and `FIOSEEKHOLE`/`FIOSEEKDATA`.
- `zvol_ensure_zilog()` lazily opens the ZIL on first write and upgrades/downgrades the suspend lock to protect `zv_zilog`.
- `zvol_os_create_minor()` temporarily owns the objset read-only, reads volume metadata, allocates the OS device state, replays/destroys the ZIL if writable, prefetches beginning/end ranges, disowns the objset, then inserts the zvol globally.

Dependencies and interactions:
- Bridges common zvol code with FreeBSD GEOM, cdev, bio, kqueue, sysctl, DMU, ZIL, SPA namespace locking, dataset kstats, and range locks.
- Common zvol lifecycle functions such as `zvol_first_open()`, `zvol_last_close()`, `zvol_insert()`, `zvol_find_by_name_hash()`, and `zvol_fini_impl()` are assumed external.

Reliability/security notes:
- The most delicate code is lock ordering across GEOM topology, zvol state, suspend locks, and SPA namespace locks.
- Removal waits for in-progress opens (`zso_opening`) and clears provider/device backpointers before destroying OS-visible nodes.
- Write/open checks enforce readonly state and incompatible encryption version restrictions before allowing writable GEOM opens.
