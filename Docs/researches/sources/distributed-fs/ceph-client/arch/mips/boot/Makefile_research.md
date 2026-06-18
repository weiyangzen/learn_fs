# sources/distributed-fs/ceph-client/arch/mips/boot/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/boot/Makefile`.

Important APIs and functions: declarative build entries include `hostprogs := elf2ecoff; suffix-y			:= bin; suffix-$(CONFIG_KERNEL_BZIP2)	:= bz2; suffix-$(CONFIG_KERNEL_GZIP)	:= gz; suffix-$(CONFIG_KERNEL_LZMA)	:= lzma; suffix-$(CONFIG_KERNEL_LZO)	:= lzo; targets := vmlinux.ecoff; targets += vmlinux.bin; targets += vmlinux.srec; targets += vmlinux.bin.bz2`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
