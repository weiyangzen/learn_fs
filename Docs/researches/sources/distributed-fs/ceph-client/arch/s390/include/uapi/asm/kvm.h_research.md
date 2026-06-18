## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm.h` is a s390 KVM userspace ABI in
the s390 ceph-client Linux source snapshot. It has 622 lines and 15885 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
VM/vCPU state, interrupt, memory operation, CMMA, SIE, protected virtualization, CPU model,
migration, and crypto structures
Important macros/constants: `__LINUX_KVM_S390_H`, `__KVM_S390`, `KVM_S390_CMMA_PEEK`, `KVM_S390_RESET_POR`, `KVM_S390_RESET_CLEAR`, `KVM_S390_RESET_SUBSYSTEM`, `KVM_S390_RESET_CPU_INIT`, `KVM_S390_RESET_IPL`, `KVM_S390_MEMOP_LOGICAL_READ`, `KVM_S390_MEMOP_LOGICAL_WRITE`, `KVM_S390_MEMOP_SIDA_READ`, `KVM_S390_MEMOP_SIDA_WRITE`, `KVM_S390_MEMOP_ABSOLUTE_READ`, `KVM_S390_MEMOP_ABSOLUTE_WRITE`, `KVM_S390_MEMOP_ABSOLUTE_CMPXCHG`, `KVM_S390_MEMOP_F_CHECK_ONLY`, `KVM_S390_MEMOP_F_INJECT_EXCEPTION`, `KVM_S390_MEMOP_F_SKEY_PROTECTION`, `KVM_S390_MEMOP_EXTENSION_CAP_BASE`, `KVM_S390_MEMOP_EXTENSION_CAP_CMPXCHG`; plus 119 more.
Important types/layouts: `kvm_s390_skeys`, `kvm_s390_cmma_log`, `kvm_s390_mem_op`, `kvm_s390_psw`, `kvm_s390_interrupt`, `kvm_s390_io_info`, `kvm_s390_ext_info`, `kvm_s390_pgm_info`, `kvm_s390_prefix_info`, `kvm_s390_extcall_info`, `kvm_s390_emerg_info`, `kvm_s390_stop_info`, `kvm_s390_mchk_info`, `kvm_s390_irq`, `kvm_s390_irq_state`, `kvm_s390_ucas_mapping`, `kvm_s390_pv_sec_parm`, `kvm_s390_pv_unp`, `kvm_s390_pv_dmp`, `kvm_s390_pv_info_dump`; plus 25 more.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 1.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
QEMU/KVM, libvirt, migration tooling, protected virtualization, and KVM ioctls. Direct include
dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for QEMU/KVM, libvirt, migration tooling,
protected virtualization, and KVM ioctls. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
ABI drift breaks virtual machines, migration streams, or protected-guest isolation

### Test Signals
KVM selftests, QEMU boot/migration, PV guest tests, and ioctl layout checks
