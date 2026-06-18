# sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt-wrapper.c

Purpose: binds libfdt operations to the boot wrapper's generic dt_ops interface and grows the FDT buffer on demand.

Important APIs/types/functions: functions `expand_buf`, `fdt_wrapper_getprop`, `fdt_wrapper_setprop`, `fdt_wrapper_del_node`, `fdt_wrapper_finalize`, `fdt_init`; macros `DEBUG`, `BAD_ERROR(err)`, `check_err(err)`, `offset_devp(off)`, `devp_offset_find(devp)`, `devp_offset(devp)`, `EXPAND_GRANULARITY`. Source size is 185 lines / 4520 bytes.

Implementation notes: Device handles are encoded as offset+1. setprop/create_node retry after expanding the FDT buffer, finalize packs the tree, and fdt_init installs every dt_ops callback after copying the incoming blob to malloc-backed storage.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state includes dt_ops callbacks, the relocated FDT buffer or PROM pointer, and loader_info fields used until final kernel entry.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `page.h`, `libfdt.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
