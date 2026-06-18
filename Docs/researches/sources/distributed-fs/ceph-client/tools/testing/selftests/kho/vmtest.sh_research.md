# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/vmtest.sh

`vmtest.sh` builds and runs a QEMU-based Kexec Handover selftest. It configures and builds a kernel, creates an initrd containing a tiny init and the kernel image, boots QEMU with `kho=on`, and verifies the serial log reports successful KHO restore.

Important functions are `usage()`, `cleanup()`, `skip()`, `fail()`, `build_kernel()`, `mkinitrd()`, `run_qemu()`, `target_to_arch()`, and `main()`. It sources `kselftest/ktap_helpers.sh` and an arch `.conf`, runs `make olddefconfig`, image builds, `headers_install`, static `$CROSS_COMPILE`gcc with nolibc includes, `usr/gen_init_cpio`, and QEMU.

Control flow parses build directory, job count, and target arch; prints a one-test KTAP plan; validates cross-compile requirements; writes required KHO config into `.config`; verifies options survive `olddefconfig`; builds kernel and headers; compiles `init.c`; creates a cpio initrd with `/init` and `/kernel`; runs QEMU; and greps serial output for `KHO restore succeeded`.

State includes a build tree, temp files under `/tmp/kho-test.*`, initrd, installed headers, and a QEMU serial log. Dependencies are kernel source/build tools, compiler or cross compiler, QEMU, `gen_init_cpio`, nolibc headers, KHO configs, and KTAP helpers. Risks include many setup failures becoming skips due to `trap skip ERR` and `.config` replacement in the build directory. Pass signal is a KTAP pass with the KHO serial marker.
