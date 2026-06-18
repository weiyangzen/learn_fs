## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ptrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ptrace.h` is a s390 ptrace/register
ABI in the s390 ceph-client Linux source snapshot. It has 332 lines and 8724 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
pt_regs offsets, PSW/GPR/ACR/FPR/PER constants, and user_regs_struct layout
Important macros/constants: `_UAPI_S390_PTRACE_H`, `PT_PSWMASK`, `PT_PSWADDR`, `PT_GPR0`, `PT_GPR1`, `PT_GPR2`, `PT_GPR3`, `PT_GPR4`, `PT_GPR5`, `PT_GPR6`, `PT_GPR7`, `PT_GPR8`, `PT_GPR9`, `PT_GPR10`, `PT_GPR11`, `PT_GPR12`, `PT_GPR13`, `PT_GPR14`, `PT_GPR15`, `PT_ACR0`; plus 99 more.
Important types/layouts: `user_regs_struct`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
ptrace, core dumps, debuggers, seccomp/audit register access, and perf. Direct include dependencies
detected here: `linux/const.h`, `linux/stddef.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for ptrace, core dumps, debuggers,
seccomp/audit register access, and perf. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
offset drift breaks debuggers and syscall tracing

### Test Signals
ptrace selftests, GDB register dumps, core-file validation, and compat debug sessions
