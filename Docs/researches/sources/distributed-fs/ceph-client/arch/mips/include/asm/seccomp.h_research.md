# sources/distributed-fs/ceph-client/arch/mips/include/asm/seccomp.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/seccomp.h

### Purpose
`seccomp.h` supplies MIPS architecture-specific seccomp mode 1 syscall allowlists for compat tasks and then includes the generic seccomp definitions.

### Important APIs, Types, And Functions
The main helper is `get_compat_mode1_syscalls`, enabled under `CONFIG_COMPAT`, returning O32 or N32 negative-terminated syscall arrays. It defines `get_compat_mode1_syscalls` for generic seccomp and includes `asm-generic/seccomp.h`.

### Control Flow
When compat seccomp mode 1 is evaluated, the helper chooses O32 if `CONFIG_MIPS32_O32` and `TIF_32BIT_REGS` are active, chooses N32 if enabled, and otherwise triggers `BUG()`.

### State, Persistence, Dependencies, And Integration
State is the current thread ABI flag and static syscall arrays; there is no persistence. Dependencies include `linux/unistd.h`, thread flags through included context, and generic seccomp. Integration is syscall filtering for compat MIPS ABIs.

### Risks
Syscall numbers must match ABI tables. The `BUG()` fallback is harsh if ABI detection is wrong. Missing updates when syscall numbering changes can make strict seccomp allow or deny the wrong calls.

### Test Signals
Run strict seccomp tests for O32 and N32 compat tasks, verify allowed `read`, `write`, `_exit`, and `sigreturn` numbers, and build non-compat and compat configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/seccomp.h -->
