# sources/distributed-fs/ceph-client/arch/mips/include/asm/reg.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/reg.h

### Purpose
`reg.h` is a thin architecture include wrapper that re-exports UAPI MIPS register definitions to kernel code.

### Important APIs, Types, And Functions
It directly includes `<uapi/asm/reg.h>` and defines no local API.

### Control Flow
There is no runtime flow; consumers receive UAPI register constants through this include.

### State, Persistence, Dependencies, And Integration
No state exists here. Integration is between kernel-internal users and the userspace-visible register ABI definitions.

### Risks
Because it is ABI glue, replacing or removing the include can break ptrace/core/regset consumers expecting the UAPI definitions.

### Test Signals
Build ptrace, core dump, and register-set users; run ABI tests that include both UAPI and kernel MIPS register constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/reg.h -->
