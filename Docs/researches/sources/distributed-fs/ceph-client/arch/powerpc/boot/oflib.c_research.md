# sources/distributed-fs/ceph-client/arch/powerpc/boot/oflib.c

Purpose: implements raw Open Firmware client-interface calls, allocation/claim handling, and OF property wrappers.

Important APIs/types/functions: types `prom_args`, `prom_args`, `prom_args`; functions `of_init`, `of_call_prom`, `of_call_prom_ret`, `string_match`, `check_of_version`, `of_claim`, `of_exit`, `of_getprop`, `of_setprop`; macros `ADDR(x)`. Source size is 219 lines / 5210 bytes.

Implementation notes: PROM calls are marshalled through big-endian prom_args. Older OF versions may require separate physical and virtual claims plus an explicit map call before vmlinux allocation.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state includes dt_ops callbacks, the relocated FDT buffer or PROM pointer, and loader_info fields used until final kernel entry.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
