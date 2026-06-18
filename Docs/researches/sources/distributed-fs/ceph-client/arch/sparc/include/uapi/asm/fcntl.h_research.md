<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fcntl.h

Purpose: Defines SPARC-specific open and fcntl constants before including generic fcntl definitions.

Important APIs and control flow: preserves Sun/SPARC values for `O_*` flags, including special `O_NDELAY` behavior that differs for 64-bit SPARC, the historical `O_DSYNC`/`O_SYNC` split, file-lock commands, and flock padding macros. Generic fcntl definitions fill in the shared remainder.

State, dependencies, and risks: state is syscall ABI flag values and structure padding. Dependencies include `asm-generic/fcntl.h` and libc headers. Risks include applications using bitwise constants directly, older kernels interpreting `O_SYNC`, and compat differences for nonblocking mode. Test signals are open/fcntl syscall ABI tests, structure-size checks, and 32-bit/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fcntl.h -->
