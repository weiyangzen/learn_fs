<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat.h

## Purpose
This header defines SPARC64 32-bit compatibility ABI types and helpers.

## Important APIs, Types, and Functions
It defines compat register, pointer, time, stat, signal, IPC, and syscall-layout types/macros used when a SPARC64 kernel runs 32-bit SPARC user programs.

## Control Flow
Compat syscall entry and data marshaling code use these definitions to translate 32-bit userspace structures to native kernel representations.

## State and Persistence Behavior
No state is owned here. It defines ABI layouts that persist as user/kernel contract.

## Dependencies and Integration Points
It integrates with generic compat syscalls, ELF compat loading, signal delivery, ptrace, IPC, and filesystem ioctl translation.

## Risks
ABI layout mistakes break 32-bit userspace or corrupt copied structures. Alignment and big-endian field order are especially important.

## Test Signals
Run 32-bit userspace on SPARC64, including signals, ptrace, stat, IPC, time, and ioctl-heavy programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat.h -->
