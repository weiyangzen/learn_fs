<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/android/binder.h

## Purpose
Defines the Android Binder character-device IPC ABI: object wire formats, read/write ioctl payloads, transaction data, protocol commands returned by the driver, and commands sent by userspace.

## Important APIs, Types, And Functions
Core types include `binder_size_t`, `binder_uintptr_t`, object headers, `flat_binder_object`, `binder_fd_object`, `binder_buffer_object`, `binder_fd_array_object`, `binder_write_read`, `binder_version`, freeze/debug/error structs, and `binder_transaction_data` variants. Ioctls include `BINDER_WRITE_READ`, context-manager setup, thread exit/version/debug-node queries, freeze operations, oneway spam detection, and extended error retrieval. Protocol enums define `BR_*` driver returns and `BC_*` userspace commands.

## Control Flow
Userspace writes `BC_*` commands and reads `BR_*` responses using `BINDER_WRITE_READ`. Transactions carry target handles or local object pointers, cookies, code, flags, sender identity, buffers, and offsets to embedded Binder objects. The driver rewrites object references, installs or transfers file descriptors, manages reference counts, asks processes to spawn loopers, and reports death/freeze notifications.

## State And Persistence
Binder state is per process and per binder device: nodes, handles, refs, buffers, thread looper counts, context manager, death/freeze notifications, frozen status, and queued transactions. State is runtime IPC state and vanishes with process/device teardown.

## Dependencies And Integration Points
Depends on Linux ioctl/types and Android userspace Binder libraries. Integrates with binderfs, SELinux security contexts, process freezer, file descriptor passing, Android service manager, and native handle marshaling.

## Risks And Edge Cases
32-bit vs 64-bit pointer sizing, offset-array validation, nested buffer parent fixups, fd-array bounds, reference-count protocol ordering, EINTR retry behavior, ECONNREFUSED teardown semantics, frozen target responses, and untrusted transaction buffers are high-risk.

## Test Signals
Binder selftests, libbinder IPC round trips, 32/64-bit compat tests, fd and fd-array transfer tests, death/freeze notification tests, oneway spam detection, extended-error checks, malformed offset/buffer rejection, and SELinux secctx transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder.h -->
