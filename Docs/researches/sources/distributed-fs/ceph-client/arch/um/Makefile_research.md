<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Makefile -->
# sources/distributed-fs/ceph-client/arch/um/Makefile

Purpose: supplies the architecture Makefile glue for building a UML kernel binary. It chooses the default config, maps `SUBARCH` to `HEADER_ARCH`, includes subarchitecture and SKAS make fragments, prepares UML-specific include paths and defines, separates kernel-space and host-user C flags, configures linker flags, and creates the legacy `linux` hard link to `vmlinux`.

Important APIs/types/functions: important variables are `KBUILD_DEFCONFIG`, `ARCH_DIR`, `HEADER_ARCH`, `HOST_DIR`, `ARCH_INCLUDE`, `MODE_INCLUDE`, `KBUILD_CFLAGS`, `USER_CFLAGS`, `KERNEL_DEFINES`, `LINK-*`, `LINK_WRAPS`, `LDFLAGS_EXECSTACK`, `CFLAGS_vmlinux`, `CFLAGS_NO_HARDENING`, and exported `HEADER_ARCH SUBARCH USER_CFLAGS CFLAGS_NO_HARDENING DEV_NULL_PATH`.

Control flow: the top-level kbuild includes this file, it selects a defconfig based on `SUBARCH` and host `uname -m`, includes `Makefile-skas`, `$(HOST_DIR)/Makefile.um`, and `Makefile-os-Linux`, then defines `linux`, `archheaders`, `archprepare`, and cleanup targets. Link mode is derived from `CONFIG_LD_SCRIPT_STATIC`, `CONFIG_LD_SCRIPT_DYN`, and `CONFIG_LD_SCRIPT_DYN_RPATH`.

State and persistence: generated outputs are build artifacts: `vmlinux`, `linux`, generated arch headers, gcov files, and make variables exported to sub-makes. It does not define runtime state.

Dependencies and integration points: depends on bash, host architecture make fragments, shared UML headers, OS-Linux build rules, kbuild's link-vmlinux support, binutils/ld features, LTO flags, and libc symbol-renaming workarounds. `USER_CFLAGS` is consumed by user-mode helper objects in `arch/um/drivers`.

Risks: incorrect filtering between `KBUILD_CFLAGS` and `USER_CFLAGS` can leak kernel-only defines into host helper code or vice versa. Symbol remapping such as `strrchr=kernel_strrchr` and `errno=kernel_errno` prevents libc/kernel collisions; removing it can break links. Static/dynamic link flags are sensitive to toolchain changes.

Test signals: build UML for x86/i386/x86_64 subarchitectures, verify user objects compile with host headers, run `make linux`, inspect `CFLAGS_vmlinux` under static and dynamic configs, run clean/mrproper, and validate no libc symbol conflicts appear at link time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Makefile -->
