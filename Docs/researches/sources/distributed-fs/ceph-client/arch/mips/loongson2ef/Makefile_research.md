# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Makefile

Purpose: selects common and machine-specific Loongson2EF platform directories.

Important APIs/types/functions: builds `common/` for `CONFIG_MACH_LOONGSON2EF`, `fuloong-2e/` for `CONFIG_LEMOTE_FULOONG2E`, and `lemote-2f/` for `CONFIG_LEMOTE_MACH2F`.

Control flow: object recursion follows machine Kconfig selections.

State and persistence: build-system only.

Dependencies and integration: connects Kconfig machine choice to common platform setup and board-specific reset/IRQ/DMA code.

Risks: wrong selection causes missing board hooks at link or boot.

Test signals: machine defconfig builds and board boot coverage.
