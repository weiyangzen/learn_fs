# sources/distributed-fs/ceph-client/drivers/firmware/google/Makefile

Purpose: Maps Google firmware Kconfig symbols to objects and composes the VPD sysfs module from parser and sysfs pieces.

Important APIs/types/functions: Builds `gsmi.o`, `coreboot_table.o`, `framebuffer-coreboot.o`, `memconsole.o`, `memconsole-coreboot.o`, `memconsole-x86-legacy.o`, `cbmem.o`, and the composite `vpd-sysfs.o` from `vpd.o vpd_decode.o`.

Control flow: No runtime flow. Object ordering notes that `cbmem.o` must follow `coreboot_table.o` because it depends on the bus type exported by the table driver.

State and persistence behavior: No state. The file controls which modules are available for exposing firmware memory, logs, NVRAM, and VPD.

Dependencies and integration points: Integrates with Kbuild and the Kconfig symbols defined in the same directory. The composite VPD module links the decoder with the coreboot driver.

Risks and test signals: Ordering and composite-object names must remain consistent with module aliases and dependencies. Test with built-in and modular configurations for each symbol, especially `CONFIG_GOOGLE_VPD=m` and `CONFIG_GOOGLE_COREBOOT_TABLE=m`.
