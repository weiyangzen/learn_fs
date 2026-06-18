# sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c

### Purpose
Userspace API for Book3S VAS accelerators, currently NX-GZIP. It creates a character device, opens one transmit window per file descriptor, maps the paste address into userspace, handles paste faults, and updates user completion status blocks on translation errors.

### Important APIs, Types, And Functions
Key types are static `struct coproc_dev` and `struct coproc_instance`. Important functions include `get_vas_user_win_ref()`, `vas_update_csb()`, `vas_dump_crb()`, `coproc_open()`, `coproc_ioc_tx_win_open()`, `coproc_release()`, `do_fail_paste()`, `vas_mmap_fault()`, `vas_mmap_close()`, `coproc_mmap()`, `coproc_ioctl()`, `vas_register_coproc_api()`, and `vas_unregister_coproc_api()`.

### Control Flow
An accelerator driver calls `vas_register_coproc_api()` to create the char device under `crypto/`. Users open it, issue `VAS_TX_WIN_OPEN`, then `mmap()` one page at offset zero to map the paste address. Fault handling remaps active windows after migration/credit recovery or emulates failed paste by clearing CR0 EQ and advancing NIP. Translation faults call `vas_update_csb()` to copy a big-endian CSB to the saved user address and signal SIGSEGV if the address is invalid.

### State, Persistence, And Dependencies
State includes global `coproc_device`, per-file `coproc_instance`, VAS window pointers, task/pid/mm references, VMA pointers, and char-device class/cdev/device nodes. Device nodes are runtime kernel objects, not durable storage. Dependencies include VAS core ops, uapi `vas-api.h`, user copy APIs, kthread mm borrowing, signals, VM fault/remap APIs, and POWER paste instruction encoding.

### Integration Points
Bridges NX/VAS kernel drivers to userspace libraries using copy/paste instructions and `/dev/crypto/nx-gzip`.

### Risks
High ABI and lifetime risk: one window per fd, pid/mm/tgid reference handling, migration/lost-credit remapping, user CSB copy ordering, module owner references, and instruction emulation must be precise. User-visible ioctl/mmap behavior is compatibility-sensitive.

### Test Signals
Run NX-GZIP userspace open/ioctl/mmap/paste/close tests, invalid version and duplicate window tests, migration/lost-credit fault tests, invalid CSB address signal tests, module unload/register cycles, and concurrent multi-thread open/exit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c -->
