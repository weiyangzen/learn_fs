<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/Kbuild

## Purpose
Controls exported UAPI header generation for OpenRISC.

## Important APIs, Types, And Functions
Adds `unistd_32.h` to syscall-generated headers and selects generic `ucontext.h`.

## Control Flow
Kbuild consumes this declarative file during `headers_install` and syscall header generation.

## State And Persistence
No runtime state. It affects generated header artifacts.

## Dependencies And Integration Points
Integrates OpenRISC UAPI with generic syscall and ucontext header generation.

## Risks
Omitting generated syscall headers breaks userspace builds; replacing generic `ucontext.h` would affect signal ABI expectations.

## Test Signals
`make headers_install` for OpenRISC and libc builds using generated unistd/ucontext headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/Kbuild -->
