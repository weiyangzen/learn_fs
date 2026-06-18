# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/init.c

`init.c` is the tiny static init program embedded in the KHO test initrd. It mounts minimal filesystems, loads `/kernel` through `kexec_file_load`, and reboots into it to exercise Kexec Handover restore.

Important APIs are `mount()`, `open()`, `read()`, `close()`, `syscall(__NR_kexec_file_load)`, `KEXEC_FILE_NO_INITRAMFS`, `reboot(RB_KEXEC)`, and `reboot(RB_AUTOBOOT)`. Functions are `mount_filesystems()`, `kexec_file_load()`, `kexec_load()`, and `main()`.

Control flow mounts debugfs and proc, reads `/proc/cmdline`, null-terminates it, opens `/kernel` from the initrd, loads it as a no-initramfs kexec target, and reboots via `RB_KEXEC`. Any failure path triggers `RB_AUTOBOOT`. State is the loaded kexec target and KHO/debugfs state visible to the next boot.

Dependencies are proc/debugfs mount support, `kexec_file_load`, `/kernel` in the initrd, and KHO kernel options. Risks include the hard-coded command-line buffer size and assuming the cmdline read has a trailing newline. Pass signal is indirect: `vmtest.sh` later sees `KHO restore succeeded` in serial output.
