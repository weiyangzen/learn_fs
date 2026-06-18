# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/boot/compressed/Makefile`.

Important APIs and functions: declarative build entries include `KBUILD_CFLAGS := $(filter-out $(CC_FLAGS_FTRACE), $(KBUILD_CFLAGS)); KBUILD_CFLAGS := $(filter-out -fstack-protector, $(KBUILD_CFLAGS)); KBUILD_CFLAGS := $(filter-out -march=loongson3a, $(KBUILD_CFLAGS)) -march=mips64r2; KBUILD_CFLAGS := $(KBUILD_CFLAGS) -D__KERNEL__ -D__DISABLE_EXPORTS \; KBUILD_AFLAGS := $(KBUILD_AFLAGS) -D__ASSEMBLY__ \; targets := $(notdir $(vmlinuzobjs-y)); targets += vmlinux.bin; OBJCOPYFLAGS_vmlinux.bin := $(OBJCOPYFLAGS) -O binary -R .comment -S; targets += vmlinux.bin.z; targets += piggy.o dummy.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
