# sources/distributed-fs/ceph-client/arch/m68k/Makefile

Purpose: architecture-specific build flags, cross-compiler defaults, compression targets, and install hooks for m68k.

It sets `KBUILD_DEFCONFIG := multi_defconfig`, chooses a default `CROSS_COMPILE` prefix when cross compiling, computes CPU compiler flags in priority order, and appends those flags to assembly and C builds. Non-MMU builds add `UTS_SYSNAME="uClinux"` and `__uClinux__`; MMU builds reserve register `a2` with `-ffixed-a2`. It sets the linker emulation to `-m m68kelf`.

Build targets include `all: zImage`, `lilo`, `zImage compressed: vmlinux.gz`, `bzImage: vmlinux.bz2`, `archheaders`, and `install`. Compression strips temporary `vmlinux.tmp` unless `CONFIG_KGDB` is enabled, where debug information and frame pointers are preserved.

State/persistence: no runtime state; persistent outputs are compressed images, installed files, and generated syscall headers.

Dependencies include the global Kbuild variables, toolchain support for selected `-m68000`/`-m68040`/ColdFire flags, gzip/bzip2 helpers, and `arch/m68k/lib/`. Integration controls every architecture object compiled in this source tree.

Risks and test signals: CPU flag ordering matters because 68040/68060 flags must not override lower baseline targets. Validate by building representative CPU configs, confirming toolchain fallback behavior, checking `CHECKFLAGS`, and verifying compressed images are generated and cleaned correctly.
