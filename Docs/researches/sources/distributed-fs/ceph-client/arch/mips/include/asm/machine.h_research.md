# sources/distributed-fs/ceph-client/arch/mips/include/asm/machine.h

Purpose: Generic MIPS machine descriptor and FDT fixup interface. It lets platform code register machine matchers in a linker section and apply device-tree fixups during early boot.

Important APIs/types/functions: `struct mips_machine` contains OF match table, optional FDT pointer, `detect`, `fixup_fdt`, and `measure_hpt_freq` callbacks. `MIPS_MACHINE(name)` places descriptors in `.mips.machines.init`. `for_each_mips_machine(mach)` iterates between `__mips_machines_start` and `__mips_machines_end`. `mips_machine_is_compatible()` checks root-node compatible strings using `fdt_node_check_compatible`. `struct mips_fdt_fixup` and `apply_mips_fdt_fixups()` define fixup execution.

Control flow, state, and persistence: Descriptor state is static init data. Boot code iterates the linker section, checks compatibility or detect callbacks, and optionally mutates an FDT output buffer through ordered fixups.

Dependencies and integration: Depends on libfdt and Open Firmware IDs. It integrates with MIPS generic board boot, device-tree selection, and high-precision timer frequency measurement.

Risks and test signals: Section placement and sentinel bounds are linker-script sensitive. Test with multiple machine descriptors, malformed FDTs, and fixup failure paths that should return `-errno` with useful descriptions.
