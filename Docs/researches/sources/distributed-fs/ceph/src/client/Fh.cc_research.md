# sources/distributed-fs/ceph/src/client/Fh.cc

## Purpose
`Fh.cc` implements construction/destruction of the client file-handle object.

## Important APIs, Types, and Functions
`Fh::Fh(InodeRef, int flags, int cmode, uint64_t gen, const UserPerm&)` stores immutable open identity, initializes readahead, and registers the handle with `inode->add_fh(this)`. `Fh::~Fh()` unregisters from the inode via `rm_fh()`.

## Control Flow
Client open paths allocate `Fh` after resolving and opening an inode. Close/release paths eventually destroy it after refs drop, which removes it from the inode’s `fhs` set so future async errors are not propagated to a dead handle.

## State and Persistence Behavior
No persistent state is written. The constructor/destructor update transient inode bookkeeping.

## Dependencies and Integration Points
It depends on `Inode.h` and `Fh.h`. `Client` owns fd map entries and file-handle refcounts; `Inode::set_async_err()` iterates registered Fhs.

## Risks and Edge Cases
The constructor assumes a valid inode ref. Destruction must happen after fd and ll references are gone and while inode state is still valid. Missing unregister would leave dangling Fh pointers in `Inode::fhs`.

## Test Signals
Open/close refcount tests, async writeback error propagation to active handles only, and leak/assert checks around release paths.
