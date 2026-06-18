# sources/distributed-fs/ceph-client/arch/parisc/include/asm/socket.h

Purpose: provides PA-RISC socket flag ABI definitions while including the uapi socket constants.

Important APIs/types/functions: includes `uapi/asm/socket.h` and defines PA-RISC `SOCK_NONBLOCK` as `0x40000000`.

Control flow: socket syscalls translate user flags through these constants when creating or accepting sockets.

State and persistence: socket flags persist in file/socket state. Dependencies and integration: networking syscall layer and userspace ABI headers.

Risks and test signals: flag mismatch breaks nonblocking socket creation for PA-RISC userspace. Test socket/accept4 flag selftests and header ABI comparison.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
