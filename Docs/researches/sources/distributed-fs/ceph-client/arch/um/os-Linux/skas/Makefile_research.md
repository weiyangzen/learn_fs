# sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/Makefile

## Purpose
Builds host-side SKAS support objects.

## Important APIs, Types, and Functions
Defines `obj-y := mem.o process.o` and marks them as `USER_OBJS`, then includes shared UML user-object build rules.

## Control Flow, State, and Persistence
No runtime behavior. It ensures SKAS memory syscall batching and userspace process control are compiled with user-side flags.

## Dependencies and Integration Points
Feeds the parent `os-Linux/Makefile` via the `skas/` directory. Includes `arch/um/scripts/Makefile.rules`.

## Risks and Test Signals
Risks are wrong user/kernel CFLAGS for host syscall code or missing SKAS objects. Test ptrace and seccomp SKAS boot paths after clean builds.
