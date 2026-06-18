# subset-b-000812 research

Grouped research for PowerPC xmon support and early RISC-V architecture build, boot, devicetree, crypto, errata, ACPI, and alternatives files. Each source section is wrapped with deterministic markers for source-tree-aligned per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc.h

## Purpose
Defines the opcode, operand, and macro table contracts used by the PowerPC disassembler that xmon embeds from binutils-derived sources.

## Important APIs, Types, And Functions
Key types are `ppc_cpu_t`, `struct powerpc_opcode`, `struct powerpc_operand`, and `struct powerpc_macro`. It declares `powerpc_opcodes`, `vle_opcodes`, `powerpc_operands`, and macro tables, plus flag constants such as `PPC_OPCODE_POWER8`, `PPC_OPCODE_VLE`, `PPC_OPERAND_RELATIVE`, and `PPC_OPERAND_OPTIONAL`.

## Control Flow
The header has no executable flow. Disassembler code indexes opcode tables, filters by CPU/dialect flags, uses masks to match instructions, and uses operand descriptors to extract or print operands.

## State And Persistence
All state is static table metadata owned by companion source files. The header fixes ABI-like structure layouts between xmon's PowerPC opcode database and printer.

## Dependencies And Integration Points
Included by xmon disassembly code alongside binutils-style `dis-asm.h` and opcode table implementations. It integrates xmon instruction dumps with the imported PowerPC instruction description database.

## Risks And Edge Cases
Structure layout, flag bit, or operand semantic changes can silently corrupt disassembly. The file is GPL/binutils-derived and must stay compatible with the generated/static opcode data.

## Test Signals
Signals are successful xmon instruction dumps, build coverage of `ppc-dis.c`/`ppc-opc.c`, and spot checks that dialect-specific instructions decode with expected mnemonics.

Source read size: 452 lines, 16307 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/spr_access.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/spr_access.S

## Purpose
Provides xmon's generic runtime accessors for all 1024 PowerPC special purpose registers.

## Important APIs, Types, And Functions
`xmon_mfspr(sprn, default_value)` and `xmon_mtspr(sprn, new_value)` are exported assembly entry points. The shared `xmon_mxspr` masks the SPR number to 10 bits, scales it by eight bytes, and branches through generated mfspr/mtspr tables.

## Control Flow
Callers pass the SPR number in r3 and a default or new value in r4. The wrapper selects either `.Lmfspr_table` or `.Lmtspr_table`, computes the branch target, and executes the generated two-instruction slot for that SPR.

## State And Persistence
No persistent state is held. Fault behavior is handled by xmon.c with `catch_spr_faults` and longjmp recovery around these calls.

## Dependencies And Integration Points
Used by `read_spr()` and `write_spr()` in xmon.c. Depends on PowerPC assembler macros, the 1024-entry SPR namespace, and exception handling that can recover from illegal SPR access.

## Risks And Edge Cases
Invalid or privileged SPR accesses may fault. The table assumes each generated slot is the expected size; changing instruction sequence length would break indexing. Writes are especially hazardous and are gated by xmon read-only mode in C.

## Test Signals
Signals are `S`, `Sr`, `Sw`, and `Sa` xmon commands reading implemented SPRs, reporting faults for inaccessible SPRs, and preserving monitor control after a fault.

Source read size: 47 lines, 814 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/spr_access.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon.c

## Purpose
Implements the PowerPC xmon in-kernel monitor: exception entry, SMP rendezvous, command interpreter, breakpoints, memory inspection and mutation, register dumps, stack walking, symbol lookup, platform diagnostics, sysrq/debugfs control, and early boot enablement.

## Important APIs, Types, And Functions
Important entry points are `xmon()`, `xmon_irq()`, `xmon_setup()`, `early_parse_xmon()`, and debugger hooks registered by `xmon_init()`. Core helpers include `xmon_core()`, `cmds()`, `bpt_cmds()`, `mread()`, `mwrite()`, `mread_instr()`, `read_spr()`, `write_spr()`, `do_step()`, `xmon_show_stack()`, `show_pte()`, `dump_log_buf()`, and `clear_all_bpt()`. State is represented by `struct bpt`, `bpts[]`, `dabr[]`, `iabr`, `in_xmon`, `xmon_on`, `xmon_is_ro`, and SMP masks/ownership fields.

## Control Flow
Exception or sysrq entry disables interrupts, checks lockdown, removes CPU breakpoints, coordinates other CPUs into xmon on SMP, prints exception context, and runs the command loop on the owning CPU. Commands dispatch to memory, dump, breakpoint, register, CPU-switch, trace, task, reboot, procedure-call, and symbol handlers. Exit reinserts breakpoints, releases other CPUs, restores watchdog/tracing state, and returns whether execution may continue.

## State And Persistence
Persistent monitor state includes enabled software breakpoints, data breakpoints, instruction breakpoint selection, default dump/memory sizes, last command repetition, read-only mode, and debugfs/sysrq enablement. Runtime state includes temporary bus-error and SPR-fault longjmp buffers, current input line, and the set of CPUs stopped in xmon.

## Dependencies And Integration Points
Integrated with PowerPC debugger hook globals, text patching, hw breakpoint APIs, kallsyms, kmsg dump, ftrace, debugfs, sysrq, RTAS surveillance, OPAL/XIVE diagnostics, paca/MMU structures, watchdogs, security lockdown, SMP IPIs, and the nonstdio console backend.

## Risks And Edge Cases
This is privileged live-kernel debugging code. Risks include corrupting memory or SPRs, failing to restore patched instructions, placing breakpoints on prefixed-instruction suffixes, deadlocking during SMP rendezvous, stale stack/PACA reads, and lockdown bypass if read-only checks regress. Recovery relies on careful fault catching around direct memory and SPR access.

## Test Signals
Signals are successful kernel entry through sysrq or `xmon=early`, safe return from faults inside memory/SPR reads, breakpoint hit/clear/reinsert behavior, single-step behavior, SMP CPU switching, read-only mode refusing writes/procedure calls/breakpoints, and command output for registers, stack, logs, PTEs, tasks, and platform diagnostics.

Source read size: 4092 lines, 88178 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.S

## Purpose
Reserves the executable breakpoint trampoline table used by xmon software breakpoints.

## Important APIs, Types, And Functions
Exports global symbol `bpt_table`. The table is aligned to 64 bytes and reserves `NBPTS * BPT_SIZE` bytes from `xmon_bpts.h`.

## Control Flow
There is no runtime branch flow here. xmon.c patches saved original instructions and trap instructions into each reserved slot, then redirects execution through these slots when needed.

## State And Persistence
The table is persistent kernel text/storage for the lifetime of the kernel. Its contents are modified by xmon breakpoint insertion and removal paths.

## Dependencies And Integration Points
Depends on `NBPTS`/`BPT_SIZE`, PowerPC instruction width including prefixed instructions, and `patch_instruction()` users in xmon.c.

## Risks And Edge Cases
Alignment is important because prefixed PowerPC instructions cannot cross 64-byte boundaries. Size mismatches with xmon.c's indexing would corrupt adjacent breakpoint slots.

## Test Signals
Signals are successful builds, breakpoints that single-step through table slots, and absence of prefixed-instruction boundary failures.

Source read size: 11 lines, 269 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.h

## Purpose
Defines the xmon breakpoint-table sizing contract shared by C and assembly.

## Important APIs, Types, And Functions
`NBPTS` is 256. For C, `BPT_SIZE` is two `ppc_inst_t` values, `BPT_WORDS` derives the word count, and `bpt_table` is declared as the backing storage.

## Control Flow
No executable flow. xmon.c uses the constants to index `bpts[]` and `bpt_table`; xmon_bpts.S uses them to reserve storage.

## State And Persistence
The constants fix the amount of persistent breakpoint storage available in the kernel image.

## Dependencies And Integration Points
Depends on `asm/inst.h` for `ppc_inst_t` and on assembly inclusion for `NBPTS` only.

## Risks And Edge Cases
Changing `NBPTS` or instruction slot sizing without updating C/assembly assumptions can break breakpoint restoration or table bounds.

## Test Signals
Signals are compile-time agreement between C and assembly and runtime ability to create up to 256 software breakpoints.

Source read size: 14 lines, 338 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon_bpts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kbuild -->
# sources/distributed-fs/ceph-client/arch/riscv/Kbuild

## Purpose
Selects the top-level RISC-V architecture subdirectories that participate in kernel builds.

## Important APIs, Types, And Functions
Exports `obj-y` for `kernel/`, `mm/`, `net/`, always includes `errata/`, conditionally includes `crypto/`, `kvm/`, and `purgatory/`, and marks `boot` as a clean-only subdirectory.

## Control Flow
Kbuild evaluates config symbols and descends into selected directories while linking arch objects into vmlinux.

## State And Persistence
State is build graph state only: selected object directories and clean traversal.

## Dependencies And Integration Points
Integrated with global Linux kbuild, RISC-V Kconfig symbols, crypto, KVM, kexec purgatory, networking, MM, and errata subsystems.

## Risks And Edge Cases
Missing a directory here can silently omit architecture functionality. Adding unconditional directories can break configs that lack dependencies.

## Test Signals
Signals are `make ARCH=riscv` object traversal, clean coverage for boot artifacts, and config-specific inclusion of crypto/KVM/purgatory objects.

Source read size: 11 lines, 233 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kconfig -->
# sources/distributed-fs/ceph-client/arch/riscv/Kconfig

## Purpose
Defines the primary RISC-V architecture configuration surface for Linux, including architecture capabilities, ISA options, memory models, SMP, alternatives, toolchain feature gates, unaligned-access policy, boot options, ACPI/EFI, KASLR, compatibility, power management, and KVM inclusion.

## Important APIs, Types, And Functions
Key symbols include `RISCV`, `64BIT`, `32BIT`, `RISCV_M_MODE`, `RISCV_SBI`, `MMU`, `PGTABLE_LEVELS`, `NONPORTABLE`, `ARCH_RV32I`, `ARCH_RV64I`, `CMODEL_MEDLOW`, `CMODEL_MEDANY`, `SMP`, `NR_CPUS`, `RISCV_ALTERNATIVE`, many `RISCV_ISA_*` extension symbols, `FPU`, `IRQ_STACKS`, scalar/vector unaligned access choices, `RISCV_BOOT_SPINWAIT`, `RELOCATABLE`, `RANDOMIZE_BASE`, `RISCV_USER_CFI`, `EFI`, `PORTABLE`, and source includes for SoC, errata, vendor, power, cpufreq/cpuidle, KVM, ACPI, and virtio.

## Control Flow
Kconfig starts by declaring architecture-wide `select` capabilities, then derives toolchain compatibility symbols, memory and platform choices, ISA extension choices, unaligned access policy, kernel feature menus, boot option menus, and downstream subsystem menus. The resulting configuration drives the RISC-V Makefile, compiler ISA strings, runtime patching, drivers, and ABI support.

## State And Persistence
State is configuration-time state persisted in `.config` and generated headers. It controls boot ABI, supported ISA extensions, page-table layout, runtime alternatives, module support, and whether firmware, ACPI, EFI, KVM, crypto, and power features are compiled.

## Dependencies And Integration Points
Depends on global kernel Kconfig infrastructure, compiler/binutils feature probes, RISC-V SoC/errata/vendor Kconfig fragments, kernel power and virtualization menus, ACPI, virtio, and architecture source files that test these symbols.

## Risks And Edge Cases
Bad dependencies can produce kernels that boot on the wrong privilege level, emit unsupported instructions, expose unsupported user ABI, or miss required runtime patching. `NONPORTABLE` options and assumed unaligned access settings are intentionally risky. Toolchain probes are brittle across compiler/assembler versions.

## Test Signals
Signals are defconfig/randconfig coverage for RV32/RV64, toolchain option probes, successful builds with and without MMU/SMP/EFI/ACPI/KVM, boot logs showing detected ISA and alternatives, and hwprobe/user ABI behavior for vector and unaligned access.

Source read size: 1381 lines, 45085 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/Makefile

## Purpose
Defines RISC-V architecture compiler, assembler, linker, Rust, image, VDSO, and install rules for the kernel build.

## Important APIs, Types, And Functions
Important variables and targets include `LDFLAGS_vmlinux`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_LDFLAGS`, `KBUILD_RUSTFLAGS`, `BITS`, `UTS_MACHINE`, `riscv-march-y`, `KBUILD_BASE_ISA`, `CC_FLAGS_FPU`, `KBUILD_IMAGE`, `libs-y`, `vdso_prepare`, `BOOT_TARGETS`, `install`, `rv32_randconfig`, `rv64_randconfig`, and `archhelp`.

## Control Flow
The Makefile derives ABI and ELF format from RV32/RV64 config, builds an ISA string from enabled extensions, strips F/D/V where inappropriate, applies relocation/ftrace/LTO/shadow-call-stack flags, prepares VDSO offsets, and routes image targets through `arch/riscv/boot`.

## State And Persistence
State is build-system state: generated flags, image target selection, VDSO generated headers, and install target behavior. It does not create runtime state directly but strongly shapes emitted instructions and boot image format.

## Dependencies And Integration Points
Integrated with top-level kbuild, toolchain feature probes, RISC-V Kconfig, EFI libstub zboot, arch/riscv/lib, VDSO builds, module builds, and `arch/riscv/boot/install.sh`.

## Risks And Edge Cases
Wrong ISA string construction can emit instructions unsupported by the boot CPU or by module builds. Relocatable/ftrace/LTO relaxation flags are subtle and can cause incorrect relocations. Stack protector offset extraction depends on generated asm offsets.

## Test Signals
Signals are successful RV32/RV64 builds, `make Image*`, `make vmlinuz.efi`, module builds with no relaxation issues, VDSO offset generation, sparse predefines, and boot tests on hardware or QEMU.

Source read size: 223 lines, 7947 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/Makefile

## Purpose
Builds RISC-V bootable kernel images from vmlinux, including raw Image, compressed images, M-mode loader, XIP image, and EFI zboot artifacts.

## Important APIs, Types, And Functions
Key targets and variables are `OBJCOPYFLAGS_Image`, `OBJCOPYFLAGS_loader.bin`, `OBJCOPYFLAGS_xipImage`, `targets`, `$(obj)/Image`, compression targets, `$(obj)/loader.o`, `$(obj)/loader`, `$(obj)/loader.bin`, `EFI_ZBOOT_PAYLOAD`, `EFI_ZBOOT_BFD_TARGET`, and `EFI_ZBOOT_MACH_TYPE`.

## Control Flow
Kbuild objcopies vmlinux to `Image`, compresses it on demand, assembles loader.o by embedding Image, links loader with loader.lds, converts loader to loader.bin, and includes the shared EFI zboot makefile for `vmlinuz.efi`.

## State And Persistence
State is generated boot artifacts in the object tree. No runtime state is owned here, but linker/objcopy choices define what bootloaders consume.

## Dependencies And Integration Points
Depends on top-level RISC-V Makefile targets, objcopy, compression tools, LD, `loader.S`, `loader.lds.S`, and EFI libstub zboot infrastructure.

## Risks And Edge Cases
Bad objcopy stripping, missing Image dependencies, or incorrect EFI target metadata can produce unbootable images. Loader linking is specific to M-mode/K210-style paths.

## Test Signals
Signals are `make ARCH=riscv Image`, compressed image targets, `loader.bin`, `xipImage`, and `vmlinuz.efi`, plus bootloader/QEMU smoke tests.

Source read size: 59 lines, 1633 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/Makefile

## Purpose
Declares vendor subdirectories that contain RISC-V devicetree sources.

## Important APIs, Types, And Functions
The only API is the ordered `subdir-y` list: allwinner, andes, anlogic, canaan, eswin, microchip, renesas, sifive, sophgo, spacemit, starfive, tenstorrent, and thead.

## Control Flow
Kbuild descends into each listed subdirectory during DTB builds so that vendor Makefiles can add config-gated DTB targets.

## State And Persistence
State is build graph traversal state only.

## Dependencies And Integration Points
Depends on kbuild DTB recursion and the presence of each vendor Makefile.

## Risks And Edge Cases
Omitting a vendor directory prevents its DTBs from being built. Adding a directory without a valid Makefile breaks `make dtbs`.

## Test Signals
Signals are `make ARCH=riscv dtbs` descending into all listed vendor directories.

Source read size: 14 lines, 296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/allwinner/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/allwinner/Makefile

## Purpose
Adds sun20i-d1-clockworkpi-v3.14, sun20i-d1-devterm-v3.14, sun20i-d1-dongshan-nezha-stu, sun20i-d1-lichee-rv variants, sun20i-d1-mangopi-mq-pro, sun20i-d1-nezha, sun20i-d1s-mangopi-mq RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_SUNXI` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_SUNXI)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 11 lines, 612 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/allwinner/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/andes/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/andes/Makefile

## Purpose
Adds qilai-voyager RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_ANDES` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_ANDES)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 2 lines, 81 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/andes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/anlogic/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/anlogic/Makefile

## Purpose
Adds dr1v90-mlkpai-fs01 RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_ANLOGIC` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_ANLOGIC)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 2 lines, 88 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/anlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/canaan/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/canaan/Makefile

## Purpose
Adds canaan_kd233, k210_generic, sipeed_maix_bit, sipeed_maix_dock, sipeed_maix_go, sipeed_maixduino RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_CANAAN` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_CANAAN)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 7 lines, 324 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/canaan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/eswin/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/eswin/Makefile

## Purpose
Adds eic7700-hifive-premier-p550 RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_ESWIN` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_ESWIN)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 2 lines, 95 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/eswin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/microchip/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/microchip/Makefile

## Purpose
Adds mpfs-beaglev-fire, mpfs-disco-kit, mpfs-icicle-kit, mpfs-icicle-kit-prod, mpfs-m100pfsevp, mpfs-polarberry, mpfs-sev-kit, mpfs-tysom-m, pic64gx-curiosity-kit RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_MICROCHIP` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_MICROCHIP)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 10 lines, 509 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/renesas/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/renesas/Makefile

## Purpose
Adds r9a07g043f01-smarc RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_R9A07G043` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_R9A07G043)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 2 lines, 90 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sifive/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sifive/Makefile

## Purpose
Adds hifive-unleashed-a00, hifive-unmatched-a00 RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_SIFIVE` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_SIFIVE)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 3 lines, 124 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sifive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/Makefile

## Purpose
Adds cv1800b-milkv-duo, cv1812h-huashan-pi, sg2002-licheerv-nano-b, sg2042-milkv-pioneer, sg2042-evb-v1, sg2042-evb-v2, sg2044-sophgo-srd3-10 RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_SOPHGO` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_SOPHGO)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 8 lines, 397 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv18xx-reset.h -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv18xx-reset.h

## Purpose
Provides devicetree reset IDs for Sophgo CV18xx/SG200x-style reset controller consumers.

## Important APIs, Types, And Functions
Exports `RST_*` numeric constants for DDR, codecs, VIP/TPU, USB, Ethernet, NAND/eMMC/SD, SDMA, I2S, UART, I2C, PWM, SPI, GPIO, efuse, watchdogs, timers, audio, camera, Ethernet PHY, and CPU/core auto-clear reset lines.

## Control Flow
No executable control flow. DTS files include the header and pass these constants in reset phandles to reset-controller providers.

## State And Persistence
The numeric IDs are persistent ABI between devicetree sources and the reset controller binding/driver.

## Dependencies And Integration Points
Depends on DTS include preprocessing and matching Sophgo reset-controller hardware definitions.

## Risks And Edge Cases
Renumbering constants breaks existing DTS reset references. Gaps are intentional hardware numbering and should not be compacted.

## Test Signals
Signals are dtc preprocessing success, reset-controller binding checks, and device probe logs showing resets deasserting expected hardware blocks.

Source read size: 98 lines, 2347 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/cv18xx-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/sg2044-reset.h -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/sg2044-reset.h

## Purpose
Provides devicetree reset IDs for the Sophgo SG2044 platform.

## Important APIs, Types, And Functions
Exports `RST_*` constants for AP system/core, interrupt/debug blocks, DMA, efuse, RTC/timer/watchdog, I2C/GPIO/PWM/SPI/UART, Ethernet/eMMC/SD, mailbox, C2C/CXP, DDR lanes, BAR/K2K, chiplet/cluster reset groups, TPSYS, SPACC/PKA/security engine, and interrupt controllers.

## Control Flow
There is no runtime flow. DTS files use these integer definitions as reset specifier cells.

## State And Persistence
The values are hardware/binding ABI and persist across kernel versions once consumed by devicetree.

## Dependencies And Integration Points
Integrated with SG2044 devicetree files and the corresponding reset-controller binding/driver.

## Risks And Edge Cases
Incorrect IDs can hold critical interconnect, memory, or security blocks in reset or reset the wrong block. Header guard comment naming is slightly inconsistent but harmless.

## Test Signals
Signals are dtc include success, schema validation for reset consumers, and board boot/probe behavior for reset-controlled peripherals.

Source read size: 128 lines, 3301 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/sg2044-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/spacemit/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/spacemit/Makefile

## Purpose
Adds k1-bananapi-f3, k1-milkv-jupiter, k1-musepi-pro, k1-orangepi-r2s, k1-orangepi-rv2, k3-pico-itx RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_SPACEMIT` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_SPACEMIT)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 7 lines, 335 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/spacemit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/Makefile

## Purpose
Adds jh7100-beaglev-starlight, jh7100-starfive-visionfive-v1, multiple jh7110 boards RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_STARFIVE` is enabled. It also enables dtc overlay symbol generation with `-@` for selected JH7100/JH7110 boards.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_STARFIVE)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 20 lines, 1025 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110-pinfunc.h

## Purpose
Defines StarFive JH7110 pinmux encoding helpers and signal IDs for devicetree pinctrl nodes.

## Important APIs, Types, And Functions
Important macros are `GPIOMUX(n, dout, doen, din)` and `PINMUX(n, func)`. Constants enumerate sys/aon output selectors, output-enable selectors, input selectors, `GPI_NONE`, and peripheral signals for UART, CAN, USB, QSPI/SPI, SPDIF, HDMI, I2C, SDIO, JTAG, PDM, I2S, TDM, PWM, GMAC, trace, watchdog, and wake GPIOs.

## Control Flow
No executable flow. DTS pinctrl entries expand these macros into packed cells consumed by the JH7110 pinctrl driver.

## State And Persistence
The bit layout and numeric selectors are persistent devicetree ABI for board files and overlays.

## Dependencies And Integration Points
Depends on JH7110 pinctrl binding/driver semantics and DTS preprocessing.

## Risks And Edge Cases
Wrong bit packing or selector numbers produce misrouted pins that are difficult to diagnose at runtime. The 0xff `GPI_NONE` sentinel must be preserved for outputs without an input path.

## Test Signals
Signals are dtbs_check pinctrl schema validation, board peripheral bring-up, and pinctrl debugfs showing expected mux, output-enable, and input selections.

Source read size: 308 lines, 9645 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/tenstorrent/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/tenstorrent/Makefile

## Purpose
Adds blackhole-card RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_TENSTORRENT` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_TENSTORRENT)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 2 lines, 88 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/tenstorrent/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/thead/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/thead/Makefile

## Purpose
Adds th1520-lichee-pi-4a, th1520-beaglev-ahead RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_THEAD` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_THEAD)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 2 lines, 112 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/thead/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/install.sh

## Purpose
Implements `make install` behavior for RISC-V kernel images.

## Important APIs, Types, And Functions
The script consumes four positional arguments: kernel version, image file, System.map file, and install path. It selects `vmlinuz` for `Image.*` and `vmlinuz.efi`, otherwise `vmlinux`.

## Control Flow
With `set -e`, it renames any existing destination image/System.map to `.old`, copies the new image with `cat`, and copies the map file.

## State And Persistence
Persistent state is the installed kernel image and `System.map` under the requested install path, plus `.old` backups.

## Dependencies And Integration Points
Called by the arch Makefile install command and compatible with traditional Linux installkernel flows.

## Risks And Edge Cases
Unquoted path expansions can be fragile for paths with spaces. Failures abort due to `set -e`. The base name policy intentionally treats all compressed images as `vmlinuz`.

## Test Signals
Signals are `make ARCH=riscv install`, correct image/map files in `INSTALL_PATH`, and preserved `.old` backups after repeated installs.

Source read size: 44 lines, 976 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.S -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/loader.S

## Purpose
Creates a minimal loader object that embeds the raw RISC-V `Image` payload.

## Important APIs, Types, And Functions
Exports `_start` in the `.payload` executable section and includes `arch/riscv/boot/Image` with `.incbin`.

## Control Flow
There is no instruction flow beyond the symbol/section definition. Linker placement makes the payload available at the configured kernel link address.

## State And Persistence
State is the embedded Image bytes in the resulting loader object/binary.

## Dependencies And Integration Points
Depends on `loader.lds.S`, the boot Makefile, and a previously built `Image` file.

## Risks And Edge Cases
If the Image path, section name, or linker placement changes, M-mode loader binaries can be malformed.

## Test Signals
Signals are successful `loader.o`, `loader`, and `loader.bin` builds and boot tests for loader-based platforms.

Source read size: 8 lines, 143 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/loader.lds.S

## Purpose
Links the RISC-V loader payload at the kernel link address.

## Important APIs, Types, And Functions
Sets `OUTPUT_ARCH(riscv)`, `ENTRY(_start)`, starts at `KERNEL_LINK_ADDR`, emits `.payload`, and aligns the end to eight bytes.

## Control Flow
The linker script has declarative flow only: it places all `.payload` input sections from `loader.o` into the output image.

## State And Persistence
State is link-time layout of the loader binary.

## Dependencies And Integration Points
Depends on `asm/page.h`, `asm/pgtable.h`, `KERNEL_LINK_ADDR`, and `loader.S`'s `.payload` section.

## Risks And Edge Cases
Wrong link address or section name can produce a loader that firmware jumps into incorrectly or that omits the embedded Image.

## Test Signals
Signals are successful LD invocation for `arch/riscv/boot/loader` and inspection of the payload address/size.

Source read size: 17 lines, 206 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/loader.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/Kconfig

## Purpose
Adds RISC-V accelerated AES and SM4 crypto algorithm configuration options.

## Important APIs, Types, And Functions
`CRYPTO_AES_RISCV64` enables AES ECB/CBC/CTS/CTR/XTS using Zvkned plus Zvbb/Zvkb/Zvkg where needed. `CRYPTO_SM4_RISCV64` enables SM4 using Zvksed and Zvkb. Both require 64-bit RISC-V, vector crypto toolchain support, and efficient vector unaligned access.

## Control Flow
Kconfig exposes module/built-in options; selected symbols cause the crypto Makefile to build the glue and vector assembly objects.

## State And Persistence
State is build configuration and module availability. Runtime registration still checks actual CPU ISA and VLEN.

## Dependencies And Integration Points
Integrated with Linux crypto API symbols, RISC-V vector crypto toolchain probes, and the arch/riscv crypto Makefile.

## Risks And Edge Cases
Enabling with insufficient runtime hardware results in module init `-ENODEV`; wrong dependencies could compile assembly the toolchain cannot parse or register algorithms on unsupported CPUs.

## Test Signals
Signals are config visibility, successful module builds, runtime registration only when ISA extensions and VLEN are present, and crypto self-tests for AES/SM4.

Source read size: 38 lines, 1190 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/Makefile

## Purpose
Builds RISC-V vector crypto AES and SM4 objects selected by Kconfig.

## Important APIs, Types, And Functions
Defines `aes-riscv64.o` from glue plus three AES assembly files and `sm4-riscv64.o` from glue plus the SM4 assembly file.

## Control Flow
Kbuild evaluates `CONFIG_CRYPTO_AES_RISCV64` and `CONFIG_CRYPTO_SM4_RISCV64`, then links the listed composite objects.

## State And Persistence
State is build graph composition for crypto modules or built-ins.

## Dependencies And Integration Points
Depends on the arch/riscv Kbuild including `crypto/`, the crypto Kconfig symbols, and object names matching source files.

## Risks And Edge Cases
Missing an assembly object leaves declared glue symbols unresolved. Including objects without the right config can fail on unsupported assemblers.

## Test Signals
Signals are clean `M=arch/riscv/crypto` builds and `modinfo`/link output containing the expected composite objects.

Source read size: 8 lines, 323 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-macros.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-macros.S

## Purpose
Provides shared RISC-V vector AES assembly macros for the accelerated AES mode implementations.

## Important APIs, Types, And Functions
Macros include `aes_begin`, `aes_encrypt`, `aes_decrypt`, and `aes_crypt`. They load expanded round keys from `struct crypto_aes_ctx`, select AES-128/192/256 paths, set vector type/length, and emit Zvkned AES round instructions.

## Control Flow
Callers invoke `aes_begin` to preload round keys into vector registers, branch to key-length labels, then call encrypt/decrypt macros over vector registers containing one or more blocks.

## State And Persistence
State is transient vector register contents and the caller's key pointer progression. No memory is persisted except through caller stores.

## Dependencies And Integration Points
Included by AES ECB/CBC/CTS, CTR, and XTS assembly files. Depends on RV64I, vector VLEN >= 128, Zvkned, and the generic AES key schedule layout.

## Risks And Edge Cases
The macros assume key layout and key-length storage offsets used by Linux AES. Register allocation mistakes affect every AES mode. AES-192 is explicitly supported through generic key expansion rather than Zvkned key expansion.

## Test Signals
Signals are AES crypto manager known-answer tests across 128/192/256-bit keys and all modes using these macros.

Source read size: 166 lines, 5418 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-macros.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-glue.c -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-glue.c

## Purpose
Registers Linux skcipher AES algorithms backed by RISC-V vector crypto assembly.

## Important APIs, Types, And Functions
Declares assembly entry points for ECB, CBC, CBC-CTS, CTR32, and XTS. C helpers include `riscv64_aes_setkey`, mode-specific encrypt/decrypt functions, `struct riscv64_aes_xts_ctx`, algorithm arrays, and module init/exit registration.

## Control Flow
Setkey uses generic AES expansion. Each request walks scatterlists with `skcipher_walk_virt`, brackets vector assembly with `kernel_vector_begin/end`, handles partial tails for CTR, and ensures CTS/XTS tail blocks are contiguous when ciphertext stealing is needed. Module init checks Zvkned, Zvbb, Zvkg, Zvkb, and VLEN before registering mode groups.

## State And Persistence
Persistent state is per-tfm AES context, XTS tweak key, algorithm registration, and request IV updates. Vector state is borrowed only inside kernel vector sections.

## Dependencies And Integration Points
Integrated with Linux crypto skcipher API, scatterwalk, generic AES library, XTS helpers, RISC-V vector state management, and runtime ISA detection.

## Risks And Edge Cases
Tail handling around CTR overflow and CTS/XTS scatterlist boundaries is subtle. Missing vector bracketing can corrupt task vector state. Runtime extension checks must match the assembly used by each registered algorithm.

## Test Signals
Signals are crypto self-tests for ecb/cbc/cts/ctr/xts, scatterlist fragmentation tests, in-place operation, partial final CTR blocks, counter overflow boundaries, and module load on supported versus unsupported CPUs.

Source read size: 566 lines, 17100 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvbb-zvkg.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvbb-zvkg.S

## Purpose
Implements AES-XTS encrypt/decrypt using RISC-V vector AES, bitmanip, and GCM multiply support.

## Important APIs, Types, And Functions
Exports `aes_xts_encrypt_zvkned_zvbb_zvkg` and `aes_xts_decrypt_zvkned_zvbb_zvkg`. Internal macros generate tweak multiplication, byte/bit reversals, block loops, and ciphertext stealing paths.

## Control Flow
The routines load round keys with `aes_begin`, load/update the tweak, process full blocks in vector batches, multiply tweaks in GF(2^128), and handle final partial blocks with XTS ciphertext stealing.

## State And Persistence
State includes transient vector registers and the caller-provided tweak buffer, which is updated to the next tweak.

## Dependencies And Integration Points
Called by the AES glue XTS path after C prepares the initial tweak by AES-encrypting the IV. Depends on Zvkned, Zvbb, Zvkg, VLEN >= 128, and XTS crypto API semantics.

## Risks And Edge Cases
Partial-block stealing and tweak endian handling are high-risk. The C glue must ensure the last full and partial blocks are in a single walk segment.

## Test Signals
Signals are XTS known-answer tests for encrypt/decrypt, non-block-aligned lengths, in-place buffers, and fragmented scatterlists.

Source read size: 312 lines, 10728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvbb-zvkg.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvkb.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvkb.S

## Purpose
Implements AES-CTR using RISC-V vector AES plus Zvkb byte/bit manipulation.

## Important APIs, Types, And Functions
Exports `aes_ctr32_crypt_zvkned_zvkb`. The macro loads the IV, builds vector counters from the low big-endian 32-bit counter word, encrypts counters, XORs keystream with input, and stores the updated IV.

## Control Flow
The loop processes as many blocks/bytes as vector length allows. C glue splits calls when the low 32-bit counter would overflow, while assembly handles a contiguous no-overflow segment.

## State And Persistence
Persistent state is the updated IV/counter buffer supplied by the caller. Other state is transient vector register data.

## Dependencies And Integration Points
Called by `riscv64_aes_ctr_crypt()` and depends on `aes-macros.S`, Zvkned, Zvkb, and crypto API CTR IV conventions.

## Risks And Edge Cases
The assembly intentionally does not handle 32-bit counter overflow; the C split logic is part of the correctness contract. Final partial blocks must XOR only requested bytes.

## Test Signals
Signals are CTR known-answer tests, arbitrary lengths including partial final blocks, and counter values near `0xffffffff`.

Source read size: 146 lines, 4805 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvkb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned.S

## Purpose
Implements AES ECB, CBC, and CBC-CTS using RISC-V Zvkned vector AES instructions.

## Important APIs, Types, And Functions
Exports `aes_ecb_encrypt_zvkned`, `aes_ecb_decrypt_zvkned`, `aes_cbc_encrypt_zvkned`, `aes_cbc_decrypt_zvkned`, and `aes_cbc_cts_crypt_zvkned`. Internal macros cover ECB loops, CBC chaining, vectorized CBC decrypt, and CS3 ciphertext stealing.

## Control Flow
Each entry loads round keys with `aes_begin`, selects key length labels, then processes block-aligned input. CBC updates IV from the last ciphertext block. CTS handles single-block, block-aligned, and partial-final-block cases with special fixups.

## State And Persistence
State persisted through caller buffers includes output data and updated IV for CBC modes. Vector registers hold round keys, IVs, ciphertext, and plaintext temporarily.

## Dependencies And Integration Points
Called by AES glue skcipher handlers. Depends on `aes-macros.S`, Linux AES context layout, Zvkned, VLEN >= 128, and C glue enforcing length constraints.

## Risks And Edge Cases
CBC-CTS decrypt fixups are complex and sensitive to length and in-place overlap. ECB/CBC require nonzero block-multiple lengths, which the C walk passes to assembly.

## Test Signals
Signals are AES ECB/CBC/CTS known-answer tests for all key sizes, single-block CTS, block-aligned CTS, partial-tail CTS, and in-place encryption/decryption.

Source read size: 312 lines, 10938 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-glue.c -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-glue.c

## Purpose
Registers a RISC-V vector-accelerated SM4 cipher implementation with generic fallback when SIMD is unavailable.

## Important APIs, Types, And Functions
Declares `sm4_expandkey_zvksed_zvkb` and `sm4_crypt_zvksed_zvkb`. Defines setkey/encrypt/decrypt wrappers and `riscv64_sm4_alg` for the crypto cipher API.

## Control Flow
Setkey uses vector expansion when `crypto_simd_usable()` and key length is valid, otherwise generic `sm4_expandkey()`. Encrypt/decrypt use vector crypt when usable, otherwise generic `sm4_crypt_block()`. Module init registers only if ZVKSED, ZVKB, and VLEN >= 128 are available.

## State And Persistence
Persistent state is `struct sm4_ctx` round keys and crypto algorithm registration. Vector state is used only inside kernel vector sections.

## Dependencies And Integration Points
Integrated with Linux crypto cipher API, generic SM4 library, RISC-V vector state management, and runtime ISA detection.

## Risks And Edge Cases
Fallback and vector key expansion must produce identical round-key ordering. Registering only single-block `sm4` means mode users rely on higher-level templates. Missing SIMD checks could use vector state in invalid contexts.

## Test Signals
Signals are SM4 known-answer tests, module load/unload, fallback operation in non-SIMD contexts, and runtime rejection on unsupported CPUs.

Source read size: 107 lines, 2848 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-zvksed-zvkb.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-zvksed-zvkb.S

## Purpose
Implements SM4 key expansion and single-block encryption/decryption primitives using RISC-V vector crypto instructions.

## Important APIs, Types, And Functions
Exports `sm4_expandkey_zvksed_zvkb` and `sm4_crypt_zvksed_zvkb`. It uses `vsm4k.vi` for key schedule rounds, `vsm4r.vs` for cipher rounds, `vrev8.v` for endian conversion, and `FAMILY_KEY` constants.

## Control Flow
Key expansion loads the user key, xors the SM4 family key, computes 32 round keys four at a time, stores encryption keys forward and decryption keys in reverse. Crypt loads one block, executes eight groups of four rounds, reverses endian/order, and stores output.

## State And Persistence
State is caller-provided round-key arrays and output block. Vector registers are temporary.

## Dependencies And Integration Points
Called by SM4 glue and depends on RV64I, VLEN >= 128, Zvksed, Zvkb, and Linux SM4 context layout.

## Risks And Edge Cases
Endian and reverse-key ordering are correctness-critical. The primitive processes one block; mode-level batching must happen elsewhere.

## Test Signals
Signals are SM4 encrypt/decrypt known-answer tests, setkey comparison with generic SM4, and cross-endian review of stored blocks.

Source read size: 117 lines, 3685 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-zvksed-zvkb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/Makefile

## Purpose
Configures RISC-V vendor errata build flags and selects vendor errata subdirectories.

## Important APIs, Types, And Functions
Adds `-fno-pie -mcmodel=medany` for relocatable early errata parsing, disables fortify for early alternatives when needed, and includes andes, mips, sifive, and thead directories based on config symbols.

## Control Flow
Kbuild applies special flags before compiling early errata code, then descends into enabled vendor directories.

## State And Persistence
State is build configuration and compiler flags for errata objects.

## Dependencies And Integration Points
Integrated with RISC-V alternatives, relocatable kernel support, fortify, and vendor errata Kconfig symbols.

## Risks And Edge Cases
Early boot code cannot rely on GOT/PIE or fortified helpers. Wrong flags can break alternatives before relocation or instrumentation is ready.

## Test Signals
Signals are relocatable and early-alternative builds, plus vendor errata object inclusion only for enabled configs.

Source read size: 18 lines, 573 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/andes/Makefile

## Purpose
Builds Andes RISC-V errata support.

## Important APIs, Types, And Functions
Sets `CFLAGS_errata.o := -mcmodel=medany` for early alternatives and always adds `errata.o` within the enabled Andes errata directory.

## Control Flow
Kbuild compiles the errata object with early-boot-safe code model when required.

## State And Persistence
State is build flags and object inclusion only.

## Dependencies And Integration Points
Depends on top-level errata Makefile gating and `CONFIG_RISCV_ALTERNATIVE_EARLY`.

## Risks And Edge Cases
Incorrect code model can break early patching before full relocation.

## Test Signals
Signals are successful builds with `CONFIG_ERRATA_ANDES` and early alternatives enabled.

Source read size: 5 lines, 97 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/andes/errata.c

## Purpose
Handles Andes AX45MP IOCP/cache-management errata detection and platform noncoherent DMA setup.

## Important APIs, Types, And Functions
Important constants include AX45MP marchid/mimpid and Andes SBI extension/function IDs. Functions are `ax45mp_iocp_sw_workaround()`, `errata_probe_iocp()`, and `andes_errata_patch_func()`.

## Control Flow
At boot alternative stage, the probe checks config, runs once, matches AX45MP IDs, calls the Andes SBI workaround query, and if needed sets `riscv_cbom_block_size` and marks noncoherent support. There are currently no text patches.

## State And Persistence
Persistent state includes the static `done` guard and global noncoherent/cache block state.

## Dependencies And Integration Points
Integrated with SBI, RISC-V alternatives, vendor extension IDs, cacheflush, and noncoherent DMA support.

## Risks And Edge Cases
A wrong SBI result or CPU ID match can enable noncoherent handling incorrectly or miss required cache maintenance. The function intentionally returns without patching text.

## Test Signals
Signals are boot logs/noncoherent DMA behavior on AX45MP platforms and no-op behavior on other Andes or non-Andes CPUs.

Source read size: 75 lines, 1890 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/errata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/mips/Makefile

## Purpose
Builds MIPS RISC-V errata support.

## Important APIs, Types, And Functions
Sets early-alternative `CFLAGS_errata.o := -mcmodel=medany` and includes `errata.o`.

## Control Flow
Kbuild compiles the MIPS errata object when the top-level errata directory selects it.

## State And Persistence
State is build graph and flags only.

## Dependencies And Integration Points
Depends on `CONFIG_ERRATA_MIPS` and early alternatives config.

## Risks And Edge Cases
Wrong early code model can break pre-relocation errata code.

## Test Signals
Signals are builds with MIPS errata enabled and object inclusion in vmlinux/modules.

Source read size: 5 lines, 97 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/mips/errata.c

## Purpose
Applies MIPS P8700 pause-opcode erratum alternatives when the required vendor ISA extension is present.

## Important APIs, Types, And Functions
Functions are `errata_probe_pause()`, `mips_errata_probe()`, and `mips_errata_patch_func()`. It checks `CONFIG_ERRATA_MIPS_P8700_PAUSE_OPCODE` and vendor extension `XMIPSEXECTL`.

## Control Flow
The patch function skips early boot, computes required errata bits, iterates `.alternative` entries for `MIPS_VENDOR_ID`, validates patch IDs, and patches old text with alternative text under `text_mutex`.

## State And Persistence
Persistent state is the patched kernel text. Probe state is recomputed per call.

## Dependencies And Integration Points
Integrated with RISC-V alternative entries, text patching, MIPS vendor extension detection, and errata ID lists.

## Risks And Edge Cases
Patch IDs must remain within `ERRATA_MIPS_NUMBER`. Applying patches after boot requires synchronization through `text_mutex`; early stage intentionally does nothing.

## Test Signals
Signals are alternative patch application on affected CPUs, warnings for invalid IDs, and correct pause behavior in CPU idle/spin paths.

Source read size: 67 lines, 1537 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/errata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/Makefile

## Purpose
Builds SiFive errata support and the optional CIP-453 trap shim.

## Important APIs, Types, And Functions
Adds `errata_cip_453.o` when `CONFIG_ERRATA_SIFIVE_CIP_453` is enabled and always includes `errata.o`.

## Control Flow
Kbuild links the generic SiFive errata probe/patch code and optional assembly trap handlers.

## State And Persistence
State is object inclusion only.

## Dependencies And Integration Points
Depends on SiFive errata Kconfig symbols and alternative users that reference CIP-453 handlers.

## Risks And Edge Cases
Omitting `errata_cip_453.o` while alternatives reference its symbols would produce link errors.

## Test Signals
Signals are builds with CIP-453 enabled/disabled and symbol resolution for trap replacement handlers.

Source read size: 2 lines, 74 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata.c

## Purpose
Detects and patches SiFive CIP-453 and CIP-1200 errata.

## Important APIs, Types, And Functions
Defines `struct errata_info_t`, check functions for CIP-453 and CIP-1200, `errata_list`, `sifive_errata_probe()`, and `sifive_errata_patch_func()`. CIP-1200 can set `tlb_flush_all_threshold = 0` under MMU.

## Control Flow
The patch function skips early boot, probes CPU arch/implementation IDs, iterates SiFive alternative entries, validates patch IDs, and applies matching alternative text under `text_mutex`.

## State And Persistence
Persistent state is patched text and, for CIP-1200, changed TLB flush threshold policy.

## Dependencies And Integration Points
Integrated with RISC-V alternatives, text patching, vendor IDs, errata IDs, TLB flush behavior, and optional CIP-453 assembly handlers.

## Risks And Edge Cases
CPU ID range checks are the core correctness boundary. Too broad a match can apply unnecessary workarounds; too narrow can leave affected CPUs broken. Patch length and IDs must match alternative entries.

## Test Signals
Signals are boot-time alternative patching on affected SiFive cores, TLB flush threshold change for CIP-1200, and page/insn fault behavior for CIP-453.

Source read size: 109 lines, 2601 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata_cip_453.S -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata_cip_453.S

## Purpose
Provides replacement trap handlers for SiFive CIP-453 bad-address sign extension.

## Important APIs, Types, And Functions
`ADD_SIGN_EXT` loads `PT_BADADDR`, checks bit 0x26, sign-extends from bit 0x27 when needed, and stores it back. Entry points are `sifive_cip_453_page_fault_trp` and `sifive_cip_453_insn_fault_trp`.

## Control Flow
Each handler fixes the bad address in pt_regs, then jumps to `do_page_fault` or `do_trap_unknown` for page faults depending on MMU, or to `do_trap_insn_fault` for instruction faults.

## State And Persistence
Persistent state is the corrected `PT_BADADDR` field in the exception frame before the generic trap handler sees it.

## Dependencies And Integration Points
Integrated with SiFive alternative patching, trap entry code, asm offsets, and generic fault handlers.

## Risks And Edge Cases
Register clobbering and sign-extension bit positions are critical. The jump target differs with MMU config.

## Test Signals
Signals are fault tests on affected cores showing correctly sign-extended bad addresses and normal generic fault handling afterward.

Source read size: 38 lines, 835 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata_cip_453.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/thead/Makefile

## Purpose
Builds T-Head errata support with early-boot-safe instrumentation restrictions.

## Important APIs, Types, And Functions
For early alternatives it sets `-mcmodel=medany`, removes ftrace flags from `errata.o`, disables KASAN instrumentation, and includes `errata.o`.

## Control Flow
Kbuild applies these flags before compiling the T-Head errata object.

## State And Persistence
State is build flags and object inclusion.

## Dependencies And Integration Points
Depends on RISC-V early alternatives, ftrace, KASAN, and top-level T-Head errata gating.

## Risks And Edge Cases
Early errata code must run before instrumentation and full relocation are safe; accidental ftrace/KASAN instrumentation can break boot.

## Test Signals
Signals are builds with early alternatives plus ftrace/KASAN enabled and no instrumentation in the errata object.

Source read size: 11 lines, 221 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/thead/errata.c

## Purpose
Detects and applies T-Head C9xx errata for MAE, cache management operations, PMU behavior, and GhostWrite vulnerability marking.

## Important APIs, Types, And Functions
Important pieces include CSR `CSR_TH_SXSTATUS`, MAE bit `SXSTATUS_MAEE`, raw T-Head cache op encodings, `THEAD_CMO_OP`, cache operation callbacks, `errata_probe_mae()`, `errata_probe_cmo()`, `errata_probe_pmu()`, `errata_probe_ghostwrite()`, `thead_errata_probe()`, and `thead_errata_patch_func()`.

## Control Flow
Probe functions match T-Head-style zero arch/implementation IDs and stage constraints. CMO boot stage registers nonstandard cache ops and marks noncoherent support. The patch function iterates T-Head alternatives and either memcpy-patches during early boot or uses `patch_text_nosync()` later, flushing icache after early patches.

## State And Persistence
Persistent state includes patched text, registered nonstandard cache ops, `riscv_cbom_block_size`, noncoherent support flags, and GhostWrite vulnerability state.

## Dependencies And Integration Points
Integrated with RISC-V alternatives, vendor IDs, cacheflush, DMA noncoherent support, hwprobe/bugs reporting, text patching, and early boot CSR access.

## Risks And Edge Cases
Stage handling is delicate: early boot cannot use normal text patching, and late code must use `text_mutex`. The raw encoded cache instructions are vendor-specific and require correct block size. GhostWrite marking intentionally assumes broad vulnerability when xtheadvector is enabled.

## Test Signals
Signals are alternative patching on T-Head C9xx systems, registered cache maintenance callbacks, DMA coherency behavior, vulnerability reporting, and PMU workaround behavior.

Source read size: 224 lines, 6170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/errata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/Kbuild

## Purpose
Declares generated syscall headers and generic asm header fallbacks for RISC-V.

## Important APIs, Types, And Functions
Adds `syscall_table_32.h` and `syscall_table_64.h` to syscall generation and maps generic headers such as `early_ioremap.h`, `flat.h`, `fprobe.h`, `kvm_para.h`, spinlock/qrwlock/qspinlock headers, `user.h`, and `vmlinux.lds.h`.

## Control Flow
During header generation, kbuild creates syscall table headers and links or exposes generic asm headers where RISC-V has no custom implementation.

## State And Persistence
State is generated/exported header layout under the build tree.

## Dependencies And Integration Points
Integrated with syscall table generation, generic asm header infrastructure, and consumers including modules and UAPI-adjacent arch code.

## Risks And Edge Cases
Removing a generic mapping can break includes; adding one can mask a needed RISC-V-specific implementation.

## Test Signals
Signals are `make headers_install`, generated syscall tables, and clean compilation of users of generic spinlock/fprobe/KVM para headers.

Source read size: 18 lines, 453 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/acenv.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/acenv.h

## Purpose
Provides the required RISC-V ACPICA environment header hook.

## Important APIs, Types, And Functions
The file intentionally exports no types or functions beyond its include guard; its presence satisfies unconditional ACPI core includes.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated with ACPICA/Linux ACPI include paths.

## Risks And Edge Cases
Adding definitions here should be done only when RISC-V ACPI needs architecture-specific ACPICA behavior; unnecessary content can diverge from generic ACPI assumptions.

## Test Signals
Signals are ACPI-enabled RISC-V builds including this header without needing architecture overrides.

Source read size: 11 lines, 243 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/acenv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/acpi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/acpi.h

## Purpose
Defines RISC-V ACPI architecture interfaces and stubs.

## Important APIs, Types, And Functions
For `CONFIG_ACPI`, it defines `phys_cpuid_t`, `PHYS_CPUID_INVALID`, `acpi_os_ioremap`, `acpi_strict`, ACPI disable/enable helpers, `cpu_physical_id`, `acpi_has_cpu_in_madt()`, `arch_fix_phys_package_id()`, RINTC mapping APIs, ISA extraction, and CBO block-size extraction. Without ACPI, it provides no-op or `-EINVAL` stubs. It also declares `acpi_map_cpus_to_nodes()` when ACPI NUMA is enabled.

## Control Flow
ACPI core and RISC-V setup code use these helpers to map firmware CPU IDs to harts, control ACPI availability, map ACPI tables, parse RISC-V ISA data, and get cache-block operation sizes.

## State And Persistence
Persistent state is global ACPI enable/disable flags and CPU/hart/NUMA mappings maintained by implementation files.

## Dependencies And Integration Points
Integrated with ACPI MADT/RINTC parsing, RISC-V hart ID maps, PCI/IRQ disable flags, CBO extension setup, and ACPI NUMA.

## Risks And Edge Cases
ACPI on RISC-V is strict; out-of-spec workarounds are disabled. Bad CPU mapping or ISA parsing can break boot CPU enumeration, interrupt routing, or extension detection.

## Test Signals
Signals are ACPI boot on RISC-V platforms, MADT RINTC CPU discovery, ACPI NUMA node mapping, ISA/CBO table parsing, and non-ACPI builds compiling through stubs.

Source read size: 95 lines, 2460 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative-macros.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative-macros.h

## Purpose
Defines assembly and C inline-assembly macros for RISC-V runtime alternatives.

## Important APIs, Types, And Functions
Important macros include `ALT_ENTRY`, `ALT_NEW_CONTENT`, `ALTERNATIVE_CFG`, `ALTERNATIVE_CFG_2`, `__ALTERNATIVE_CFG`, `_ALTERNATIVE_CFG`, `ALTERNATIVE`, and `ALTERNATIVE_2`. When alternatives are disabled, they collapse to the old instruction content.

## Control Flow
When enabled, macros emit old code at labels 886/887, alternative metadata in `.alternative`, replacement code in subsection 1 at labels 888/889, disable RVC/relaxation around patchable content, and use `.org` checks to keep old and new content lengths compatible.

## State And Persistence
Persistent state is the `.alternative` metadata and replacement instruction sections linked into the kernel or module. Runtime patching code later consumes those entries.

## Dependencies And Integration Points
Integrated with `asm/alternative.h`, vendor errata patch functions, cpufeature alternatives, module loading, and text patching.

## Risks And Edge Cases
Length mismatches, relaxed instructions, or compressed encodings can make runtime patching unsafe, hence `norvc` and `norelax`. `ALTERNATIVE_2` must preserve ordering when multiple vendors patch the same site.

## Test Signals
Signals are objdump inspection of `.alternative`, successful builds with alternatives on/off, boot-time patch application, and module alternative patching.

Source read size: 161 lines, 5123 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative-macros.h -->
