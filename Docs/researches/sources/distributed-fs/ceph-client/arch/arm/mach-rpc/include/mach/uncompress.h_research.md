# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/uncompress.h

Purpose: early decompressor output support for RiscPC.

Important APIs/types/functions: implements low-level `putc`/flush helpers and UART/IOMD access assumptions used before the kernel proper is running.

Control flow: decompressor calls these helpers to emit early boot text such as uncompressing messages.

State and persistence: writes directly to early serial/display hardware; no lasting state beyond device output.

Dependencies and integration points: used by ARM compressed boot path when `ARCH_RPC` is selected and depends on bootloader-initialized low-level port state.

Risks: early MMIO assumptions must be valid before normal mappings. Bad polling can hang decompression.

Test signals: visible early boot output and no decompressor hangs with low-level debug enabled.
