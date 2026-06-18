# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h

### Purpose
`kvm_mte.h` declares ARM64 KVM support for Memory Tagging Extension in guests, including VM enablement, tag copying, fault handling, and page/tag synchronization.

### Important APIs, Types, And Functions
It exports helpers around `kvm_has_mte()`, MTE VM ioctl support, tag-copy operations, page tag initialization/synchronization, and conditional stubs when `CONFIG_ARM64_MTE` or KVM MTE support is absent.

### Control Flow
Userspace enables guest MTE through VM attributes/ioctls. KVM maps guest memory with tag-aware behavior, synchronizes tags during page faults or migration-like copy operations, and handles tag faults according to guest configuration.

### State, Persistence, And Dependencies
State lives in VM flags, page flags/tag storage, and CPU MTE registers. It depends on `asm/mte.h`, page table attributes, KVM memory slots, and CPU feature detection.

### Integration Points
Connects KVM VM ioctls, guest memory fault handling, ARM64 MTE core, and migration/debug tag copy paths.

### Risks
Missing tag synchronization can leak stale tags or corrupt guest memory semantics. Host/guest tag ownership is subtle around shared pages and migration. Stubs must preserve build compatibility.

### Test Signals
Run KVM MTE selftests, tag copy ioctl tests, guest tag fault tests, migration/save-restore tag checks, and non-MTE config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_mte.h -->
