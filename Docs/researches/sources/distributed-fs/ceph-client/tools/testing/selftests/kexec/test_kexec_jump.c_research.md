# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.c

`test_kexec_jump.c` is an x86_64 helper for `KEXEC_PRESERVE_CONTEXT` jump testing. It loads a tiny in-process purgatory segment, jumps into it, returns to Linux, and jumps again to the alternate entry.

Important pieces are inline assembly labels `purgatory_start`, `purgatory_start_b`, and `purgatory_end`, `struct kexec_segment`, `syscall(__NR_kexec_load)`, `KEXEC_PRESERVE_CONTEXT`, and `syscall(__NR_reboot, ..., LINUX_REBOOT_CMD_KEXEC)`.

The assembly triggers `int3`, writes the next purgatory entry into the saved return slot at `8(%rsp)`, and returns. `main()` loads the segment at physical address `0x400000`, invokes two kexec reboot commands, and prints `Success` if both return. Kernel state is the loaded kexec image and preserved execution context.

Dependencies are x86_64, root, `CONFIG_KEXEC_JUMP`, `kexec_load`, reboot syscall support, and a system that can survive the debug exception path. Risks are high because failures may crash or reboot the kernel; the load address and assembly are architecture-specific. Pass signal is returning from both jumps and printing success.
