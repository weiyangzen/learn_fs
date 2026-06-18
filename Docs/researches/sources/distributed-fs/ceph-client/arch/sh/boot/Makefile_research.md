# sources/distributed-fs/ceph-client/arch/sh/boot/Makefile



Source read size: 115 lines, 3344 bytes.



Purpose: top-level SH boot-image build rules for compressed `zImage`, ROM images, raw and compressed `vmlinux.bin`, Motorola S-records, and U-Boot `uImage` variants.

Important APIs/types/functions: Kbuild targets `zImage`, `romImage`, `uImage`, `vmlinux.bin.*`, exported address variables `KERNEL_MEMORY`, `KERNEL_LOAD`, `KERNEL_ENTRY`, and compression suffix selection from `CONFIG_KERNEL_*`.

Control flow: Kbuild builds `compressed/vmlinux`, objcopies it to `zImage`, optionally wraps it as `romImage`, derives binary/compressed payloads from `vmlinux`, then creates U-Boot images with load/entry addresses computed from page, memory, and zero-page offsets.

State and persistence: generated boot artifacts are build outputs; the Makefile only exports address/config variables to subdirectories.

Dependencies and integration points: depends on Kbuild `if_changed`, objcopy, gzip/bzip2/lzma/xz/lzo helpers, mkimage/uimage rules, and `arch/sh/boot/compressed` plus `romimage` subbuilds.

Risks and test signals: wrong load or entry calculations produce unbootable images; dummy defaults can mask missing config values. Test by building every configured compression format, checking `uImage` headers, objdumping load addresses, and booting zImage/romImage on target hardware or emulator.
