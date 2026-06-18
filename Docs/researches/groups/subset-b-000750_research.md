# subset-b-000750 research



<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp32.c -->
# sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp32.c

## Purpose
Implements the MIPS o32, 32-bit CPU backend for the shared eBPF JIT compiler. It translates verifier-accepted eBPF instructions into MIPS32 instruction streams while preserving 64-bit eBPF register semantics with native register pairs.

## Important APIs, Types, And Functions
The externally used JIT hooks are `build_prologue`, `build_epilogue`, and `build_insn` from the shared MIPS JIT framework. The central mapping is `bpf2mips32[][2]`, with helpers `lo()` and `hi()` selecting the low/high native register by endianness. Arithmetic emitters include `emit_alu_i64`, `emit_alu_r64`, `emit_shift_i64`, `emit_shift_r64`, `emit_mul_i64`, `emit_mul_r64`, `emit_divmod_r64`, `emit_bswap_r64`, and `emit_trunc_r64`. Memory and atomic paths are `emit_ldx`, `emit_stx`, `emit_atomic_r32`, `emit_atomic_r64`, `emit_cmpxchg_r32`, and `emit_cmpxchg_r64`. Branching and calls are handled by `emit_jmp_i64`, `emit_jmp_r64`, `emit_call`, and `emit_tail_call`.

## Control Flow
`build_insn` dispatches on the eBPF opcode class and emits one or more native instructions. 32-bit ALU opcodes operate on the low register and then rely on verifier-provided or local zero extension. 64-bit opcodes route through register-pair helpers for carry/borrow, cross-word shifts, multiply, divide/modulo helper calls, byte swaps, and comparisons. Calls resolve a fixed helper address through `bpf_jit_get_func_addr`, push stack-passed o32 arguments and caller-saved registers as needed, and emit `jalr`. Tail calls check array bounds, decrement the tail-call counter stored in the caller-reserved stack area, fetch the target program's `bpf_func`, skip the prologue initialization bytes, and jump through the normal epilogue path.

## State And Persistence
Generated code state is held in `struct jit_context`: clobbered/accessed register bitmaps, stack sizing, BPF instruction index, and emitted offsets. Runtime state is only the generated stack frame, including saved callee registers, local eBPF stack, spill space for caller-saved registers and stack arguments, and a tail-call counter stored at the top of the inherited o32 frame. No filesystem or durable persistence is involved.

## Dependencies And Integration Points
Depends on `linux/filter.h`, `linux/bpf.h`, `linux/math64.h`, MIPS CPU feature probes, uasm emit macros, and common helpers in `bpf_jit_comp.h`. It integrates with the eBPF verifier's `verifier_zext` contract, generic BPF helper address resolution, kernel atomic APIs, `div64_u64`, `atomic64_*`, and MIPS ABI rules for o32 argument passing, return registers, delay slots, and stack alignment.

## Risks And Edge Cases
The highest-risk areas are register-pair endianness, o32 stack argument layout, callee/caller save masks, branch-distance handling via `finish_jmp`, and tail-call prologue skip constants. CPUs without MIPS II load-delay behavior need explicit `nop`s. CPUs without LL/SC fall back to C atomic helpers, requiring correct caller-saved preservation and result exclusion. 64-bit div/mod helper calls must not clobber live eBPF state. Atomic compare-exchange has big-endian result-register special handling. Invalid or unsupported opcodes return `-EINVAL`, `-EFAULT`, or `-E2BIG`, which should force interpreter fallback rather than unsafe code.

## Test Signals
Useful signals are BPF selftests on 32-bit MIPS for ALU64 carry/borrow, unaligned-sized loads/stores within verifier constraints, atomics with and without fetch, `cmpxchg`, tail calls, helper calls with more than two 64-bit arguments, endian conversion, and long branches. Build coverage must include big- and little-endian MIPS32, LL/SC and non-LL/SC configurations, and older ISA variants with load delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp64.c -->
# sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp64.c

## Purpose
Implements the MIPS n64, 64-bit CPU backend for the shared eBPF JIT compiler. Unlike the 32-bit backend, each eBPF register maps to one native 64-bit MIPS register, with extra JIT registers for tail-call count and zero-extension masks.

## Important APIs, Types, And Functions
The exported JIT hooks are `build_prologue`, `build_epilogue`, and `build_insn`. `bpf2mips64[]` maps eBPF registers to native registers; `JIT_REG_TC` holds the tail-call counter and `JIT_REG_ZX` holds a 32-bit mask for zero extension on older MIPS64. Major emitters include `emit_sext`, `emit_zext`, `emit_mov_i64`, `emit_alu_i64`, `emit_alu_r64`, `emit_bswap_r64`, `emit_trunc_r64`, `emit_ldx`, `emit_stx`, `emit_atomic_r64`, `emit_cmpxchg_r64`, `emit_call`, and `emit_tail_call`.

## Control Flow
`build_insn` dispatches eBPF opcodes into native MIPS64 emissions. For BPF_ALU 32-bit arithmetic it explicitly sign-extends operands before operations that require it and zero-extends results when the verifier has not inserted zext. BPF_ALU64 routes directly through dword operations, including MIPS64r6-specific multiply/divide/modulo forms when available. Memory access uses byte/half/word/dword load-store opcodes. Atomics use LL/SC loops for 64-bit operations and common 32-bit LL/SC helpers for word atomics. Helper calls save JIT caller-saved registers, jump through a masked fixed address, then restore the zero-extension mask register if it was live. Tail calls use the in-register counter, fetch the target `bpf_prog`, skip the first prologue instruction, and jump via the epilogue.

## State And Persistence
State is contained in the generated native stack frame and `jit_context`. The stack frame saves only clobbered callee registers, local eBPF stack, and any reserved caller-saved spill area. Tail-call count is initialized into a caller-saved register rather than persisted on the stack unless the register is accessed and marked for preservation. No persistent storage is touched.

## Dependencies And Integration Points
Depends on common MIPS JIT helpers in `bpf_jit_comp.h`, uasm emission macros, MIPS64 ISA feature probes, generic BPF helper resolution, LL/SC helper macros, Linux BPF verifier zero-extension behavior, and n64 ABI stack and register rules. It must line up with `struct bpf_array` and `struct bpf_prog` layouts for tail calls.

## Risks And Edge Cases
The main correctness risks are MIPS64 sign-extension semantics for 32-bit operations, conditional use of `JIT_REG_ZX`, helper-call address masking with `JALR_MASK`, tail-call skip length, and preserving caller-saved registers around helper calls. R4000 multiplication workarounds, MIPS64r6 instruction selection, branch-distance handling, and LL/SC retry offsets are CPU-sensitive. The epilogue sign-extends the 32-bit return value in the jump delay slot, so return-width behavior must match the shared JIT contract.

## Test Signals
BPF selftests should exercise 32-bit ALU zext and sign-sensitive operations, ALU64 multiply/divide/modulo on r6 and non-r6 CPUs, atomics, `cmpxchg`, tail-call chains, helper calls, endian conversion, and long conditional jumps. Cross-builds for MIPS64 r1/r2/r6 and configurations without verifier zext assumptions are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/pci/Makefile

## Purpose
Selects which MIPS PCI support objects are compiled for a kernel configuration. It is the integration manifest for generic PCI core glue, legacy controller glue, board-specific fixups, host-controller ops, MSI support, and SoC-specific drivers under `arch/mips/pci`.

## Important APIs, Types, And Functions
This file does not define C APIs. It uses Kbuild `obj-y` and `obj-$(CONFIG_...)` assignments to include objects such as `pci.o`, `pci-legacy.o`, `pci-generic.o`, `ops-bonito64.o`, `ops-gt64xxx_pci0.o`, `pci-bcm63xx.o`, `pci-alchemy.o`, `pci-ar2315.o`, `pci-ar71xx.o`, `pci-ar724x.o`, and matching fixup files.

## Control Flow
At build time, Kbuild evaluates the selected Kconfig symbols and appends matching objects. Several board symbols pull multiple files together, for example BCM63XX pulls controller, fixup, and ops files; Loongson boards pull fixup files plus `ops-loongson2.o`; SGI IP32 pulls fixup, ops, and platform PCI init files. Octeon MSI is gated by both `CONFIG_CAVIUM_OCTEON_SOC` and `CONFIG_PCI_MSI`.

## State And Persistence
No runtime state. Build outputs are determined by Kconfig state and object lists.

## Dependencies And Integration Points
Integrates MIPS platform Kconfig symbols with the Linux PCI subsystem. The object ordering matters because generic `pcibios_*` symbols and PCI fixup declarations are linked only for the active board family.

## Risks And Edge Cases
Wrong object selection can cause duplicate `pcibios_map_irq`/`pcibios_plat_dev_init` definitions or missing `pci_ops` symbols. Board combinations that accidentally enable incompatible legacy fixups are a build-time or link-time risk. MSI support for Octeon depends on nested `ifdef CONFIG_PCI_MSI`, so missing MSI objects are expected when MSI is disabled.

## Test Signals
Compile coverage across MIPS defconfigs is the primary signal. Link success for mutually exclusive board families and object presence checks in build logs validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ath79.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ath79.c

## Purpose
Provides ATH79 platform PCI hooks: a no-op device init callback and Open Firmware based interrupt mapping.

## Important APIs, Types, And Functions
Defines `pcibios_plat_dev_init` and `pcibios_map_irq`; the latter calls `of_irq_parse_and_map_pci(dev, slot, pin)`.

## Control Flow
During PCI enumeration the generic MIPS PCI code asks for platform init and IRQ mapping. Initialization returns success; IRQ mapping is delegated to the device tree PCI interrupt parser.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on `linux/of_pci.h`, `linux/pci.h`, and ATH79 platform builds selected by the Makefile.

## Risks And Edge Cases
Bad or missing DT interrupt-map data yields IRQ 0 or failed mapping. There is no fallback static swizzle.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ath79.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-bcm63xx.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-bcm63xx.c

## Purpose
Provides simple BCM63xx PCI platform hooks for legacy PCI interrupt routing.

## Important APIs, Types, And Functions
Defines `pcibios_map_irq`, returning `bcm63xx_get_irq_number(IRQ_PCI)`, and no-op `pcibios_plat_dev_init`.

## Control Flow
Every enumerated PCI device is routed to the SoC's single PCI IRQ. Device init does no additional programming.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on BCM63xx CPU IRQ helpers and the BCM63XX object group.

## Risks And Edge Cases
All devices share one IRQ, so interrupt sharing must work. Incorrect CPU IRQ tables break every PCI device.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-cobalt.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-cobalt.c

## Purpose
Implements Cobalt Qube/Raq PCI quirks, board ID discovery, and static IRQ routing tables.

## Important APIs, Types, And Functions
Key fixups are `qube_raq_galileo_early_fixup`, `qube_raq_via_bmIDE_fixup`, `qube_raq_galileo_fixup`, and `qube_raq_via_board_id_fixup`, registered via `DECLARE_PCI_FIXUP_*`. Exposes global `cobalt_board_id`, `pcibios_map_irq`, and `pcibios_plat_dev_init`.

## Control Flow
Early/header fixups correct the GT64111 class code, enable VIA IDE bus mastering, set latency/cache-line values, force Galileo retry timeouts, enable retry interrupts, and read the VIA-wired board ID. IRQ mapping selects one of three static tables based on `cobalt_board_id`.

## State And Persistence
Persists the detected board ID in global `cobalt_board_id` for later IRQ mapping. Hardware config registers are modified persistently until reset.

## Dependencies And Integration Points
Depends on PCI quirk infrastructure, GT64120 register macros, Cobalt board constants, and IRQ definitions.

## Risks And Edge Cases
The file writes magic legacy chipset registers. A failed board-ID read panics. Slot indexes are used directly, so unexpected topology can index invalid or zero IRQ entries. Galileo timeout changes are hardware-critical.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-cobalt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-fuloong2e.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-fuloong2e.c

## Purpose
Provides Lemote Fuloong2E IRQ routing and VIA686B/NEC USB PCI header fixups.

## Important APIs, Types, And Functions
Defines `pcibios_map_irq`, `pcibios_plat_dev_init`, fixups for VIA functions 0/1/2/3/5, and `loongson2e_nec_fixup`, registered with `DECLARE_PCI_FIXUP_HEADER`.

## Control Flow
The VIA ISA bridge fixup records `sb_slot`, programs ISA refresh, line buffers, delay transaction, IRQ trigger/routing bytes, legacy peripheral routing, and enables audio/modem functions. IDE, USB, and audio functions receive fixed interrupt lines and controller configuration. Non-southbridge devices map to `LOONGSON_IRQ_BASE + 25 + pin`.

## State And Persistence
Persists southbridge slot number in static `sb_slot` and writes multiple chipset PCI config bytes that remain active until reset.

## Dependencies And Integration Points
Depends on Loongson IRQ constants, VIA/NEC PCI IDs, port I/O, and the Loongson2 PCI ops selected for this board.

## Risks And Edge Cases
Magic VIA registers and hard-coded IRQs are board-specific. Interrupt routing depends on the ISA bridge fixup running before `pcibios_map_irq` needs `sb_slot`. Some disabled alternative IDE tuning indicates fragile hardware behavior.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-fuloong2e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ip32.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ip32.c

## Purpose
Provides SGI O2/IP32 MACE PCI interrupt routing for onboard SCSI controllers and the expansion slots.

## Important APIs, Types, And Functions
Defines `irq_tab_mace`, `pcibios_map_irq`, and no-op `pcibios_plat_dev_init`.

## Control Flow
Enumeration maps the PCI slot and interrupt pin directly through `irq_tab_mace`; onboard SCSI slots are fixed to SCSI IRQs and expansion slots swizzle shared IRQs.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on IP32 interrupt definitions and the MACE PCI controller files.

## Risks And Edge Cases
The table assumes O2's fixed five-device wiring and has no bounds checks. Unexpected slot/pin values can return wrong or zero IRQs.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ip32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lantiq.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lantiq.c

## Purpose
Provides Lantiq PCI platform hooks with device-tree interrupt mapping.

## Important APIs, Types, And Functions
Defines no-op `pcibios_plat_dev_init` and `pcibios_map_irq` using `of_irq_parse_and_map_pci`.

## Control Flow
The MIPS PCI core calls the platform hooks during device setup; this file delegates IRQ mapping to OF data and otherwise leaves devices unchanged.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on `linux/of_pci.h` and the Lantiq PCI controller stack.

## Risks And Edge Cases
Correctness depends entirely on board DT interrupt-map data. There is no static fallback.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lemote2f.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lemote2f.c

## Purpose
Provides Lemote 2F IRQ routing and CS5536/NEC fixups for Loongson2F boards.

## Important APIs, Types, And Functions
Defines `irq_tab`, `pcibios_map_irq`, no-op `pcibios_plat_dev_init`, CS5536 ISA/IDE/audio/OHCI/EHCI fixups, and `loongson_nec_fixup` registered as PCI header fixups.

## Control Flow
Non-CS5536 devices route through a static slot/pin table plus `LOONGSON_IRQ_BASE`. CS5536 functions get explicit IDE/audio/USB interrupts and write `PCI_INTERRUPT_LINE`. Fixups enable UART, IDE muxing, audio/OHCI interrupts, EHCI USB config MSRs and FLADJ, and reduce NEC USB ports.

## State And Persistence
Writes device config registers and CS5536 MSRs that persist until reset. No software state beyond static tables.

## Dependencies And Integration Points
Depends on Loongson, CS5536 PCI/MSR helpers, `_rdmsr/_wrmsr` from `ops-loongson2.c`, and PCI quirk registration.

## Risks And Edge Cases
Hard-coded slot numbers and CS5536 function assumptions are board-specific. MSR writes and USB/EHCI tuning can break peripherals if applied to the wrong revision. IRQ 0 returns indicate unsupported slots.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lemote2f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-malta.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-malta.c

## Purpose
Implements MIPS Malta PIIX4 IRQ discovery and chipset compatibility fixups.

## Important APIs, Types, And Functions
Defines static `pci_irq`, `irq_tab`, `pcibios_map_irq`, no-op `pcibios_plat_dev_init`, and PIIX4 fixups `malta_piix_func3_base_fixup`, `malta_piix_func0_fixup`, `malta_piix_func1_fixup`, and `quirk_dlcsetup`.

## Control Flow
PIIX function 0 fixup reads PIRQ routing registers and fills `pci_irq`, then enables SERIRQ and special cycles. Function 3 sets PM I/O base and enable. Function 1 enables IDE decode on expected slot. Final quirk enables passive release and delayed transaction. IRQ mapping uses board slot/pin swizzle to index the discovered PIRQ-to-IRQ table.

## State And Persistence
Persists PIRQ mappings in static `pci_irq` and modifies PIIX config registers. No durable state.

## Dependencies And Integration Points
Depends on Malta PIIX4 register definitions and PCI quirk infrastructure.

## Risks And Edge Cases
IRQ mapping is invalid until PIIX fixup fills `pci_irq`. Slot table assumes Malta topology. Hard-coded PIIX settings interact with firmware versions noted in comments.

## Test Signals
Malta QEMU or hardware boot with PCI devices should show correct IRQs, IDE/USB enumeration, and no PIIX regressions. Build coverage for `CONFIG_MIPS_MALTA` is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-malta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rbtx4927.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rbtx4927.c

## Purpose
Provides Toshiba RBTX4927 board-specific PCI interrupt rotation.

## Important APIs, Types, And Functions
Defines `rbtx4927_pci_map_irq`, using TXX9 option flags and RBTX4927 IOC IRQ constants.

## Control Flow
The function rotates INTA-D based on slot number, with separate handling for the card slot and backplane, then converts the logical pin to IOC PCIA-D IRQ numbers.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on TXX9 PCI option state and RBTX4927 board IRQ definitions. It is called by board PCI setup rather than generic `pcibios_map_irq` in this file.

## Risks And Edge Cases
PICMG option and slot arithmetic must match physical backplane wiring. Out-of-range pins would produce nonsensical rotations.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rbtx4927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rc32434.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rc32434.c

## Purpose
Provides IDT RC32434/RB532 PCI IRQ mapping and an early bridge fixup.

## Important APIs, Types, And Functions
Defines `irq_map`, `pcibios_map_irq`, `rc32434_pci_early_fixup`, and no-op `pcibios_plat_dev_init`.

## Control Flow
Devices on bus 0 or 1 and slots below 12 map through `irq_map` plus `GROUP4_IRQ_BASE + 4`. Header fixup for slot 6 bus 0 disables prefetch memory range and sets cache line size.

## State And Persistence
No software persistence except static table. Config writes persist until reset.

## Dependencies And Integration Points
Depends on RC32434 board IRQ definitions and PCI fixup infrastructure.

## Risks And Edge Cases
The fixup is registered for `PCI_ANY_ID`, so guard conditions must remain correct. Table lookup lacks pin use and assumes two buses/twelve slots.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rc32434.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sb1250.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sb1250.c

## Purpose
Defines SiByte BCM1250/HT/SP1011 PCI quirks for timeout, class, and DMA addressing limitations.

## Important APIs, Types, And Functions
Fixups are `quirk_sb1250_pci`, `quirk_sb1250_pci_dac`, `quirk_sb1250_ht`, and `quirk_sp1011`. Helper `sb1250_bus_dma_limit` walks devices under the host bridge.

## Control Flow
Early quirks set TRDY timeouts and reclassify the HT bridge as normal PCI bridge. Final DAC quirk walks the bus and limits devices to 32-bit DMA except the HT bridge's subordinate bus range, which supports wider addressing.

## State And Persistence
Persists device DMA limits in `dev->dev.bus_dma_limit` and writes bridge timeout registers. Temporary exclude state is stack-local during bus walk.

## Dependencies And Integration Points
Depends on PCI fixup registration, DMA mask definitions, and SiByte/SP1011 device IDs.

## Risks And Edge Cases
DMA limit propagation is subtle: incorrect exclusion of HT subordinate buses can either break 64-bit-capable devices or allow unsafe DAC on a 32-bit bus. Assumes `dev->subordinate` exists for the HT bridge.

## Test Signals
PCI enumeration with devices behind native PCI and HT bridges, DMA mask checks, and driver DMA tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sb1250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sni.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sni.c

## Purpose
Provides SNI RM200/RM300 PCI IRQ routing tables for PCIMT and PCIT variants.

## Important APIs, Types, And Functions
Defines multiple static IRQ tables, `is_rm300_revd`, `pcibios_map_irq`, and no-op `pcibios_plat_dev_init`.

## Control Flow
`pcibios_map_irq` switches on `sni_brd_type`, applies a special PCI Tower C Plus slot-4 bus-1 workaround, distinguishes RM300 revision D via `PCIMT_CSMSR`, and returns the selected table entry.

## State And Persistence
No software persistence; board type is external global platform state.

## Dependencies And Integration Points
Depends on SNI board type constants, memory-mapped SNI registers, and platform IRQ definitions.

## Risks And Edge Cases
Tables are topology-specific and unchecked. The C Plus workaround walks parent bridges and depends on bus numbering and devfn thresholds. Direct volatile register access must be valid on PCIMT systems.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/msi-octeon.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/msi-octeon.c

## Purpose
Implements Octeon architecture MSI allocation, teardown, interrupt masking, dispatch, and initialization.

## Important APIs, Types, And Functions
Public hooks are `arch_setup_msi_irq`, `arch_teardown_msi_irq`, and `octeon_msi_initialize`. State is tracked in `msi_free_irq_bitmask`, `msi_multiple_irq_bitmask`, `msi_irq_size`, `msi_rcv_reg`, and `mis_ena_reg`. IRQ chips are `octeon_irq_chip_msi_pcie` and `octeon_irq_chip_msi_pci`.

## Control Flow
Setup rejects MSI-X, reads MSI capability sizing, allocates aligned contiguous MSI bits under spinlock, writes the MSI message address based on `octeon_dma_bar_type`, updates QSIZE, attaches the descriptor, and writes the MSI message. Teardown computes the owned range using the multiple bitmap and clears allocation bits. Initialization selects PCIe or PCI CSR registers, installs irq chips for all MSI IRQs, and requests parent MSI interrupt lines. Runtime handlers ack the pending CSR bit and invoke `do_IRQ` for the logical MSI.

## State And Persistence
Global bitmaps persist allocation ownership for the boot lifetime. Hardware MSI enable/receive CSRs are programmed and updated under locks. No durable storage.

## Dependencies And Integration Points
Depends on Octeon PCI/PCIe BAR type globals, CVMX CSR definitions, Linux MSI core, IRQ chip APIs, and Octeon feature/host-mode probes.

## Risks And Edge Cases
Bitmap allocation has panic-on-exhaustion behavior for single IRQ failure. Multi-MSI range accounting must remain aligned. PCI mode lacks per-vector mask support. Incorrect BAR type produces invalid MSI addresses or panic. Register arrays for invalid lanes deliberately use addresses that fault if misused.

## Test Signals
MSI-capable PCI/PCIe device tests on Octeon, allocation/teardown stress, multi-MSI devices, interrupt delivery/disable tests, and boot logs for requested parent IRQs are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/msi-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-bcm63xx.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-bcm63xx.c

## Purpose
Provides BCM63xx PCI, CardBus emulation, and PCIe config-space operations.

## Important APIs, Types, And Functions
Defines `bcm63xx_pci_ops`, optional `bcm63xx_cb_ops`, and `bcm63xx_pcie_ops`. Core helpers are `postprocess_read`, `preprocess_write`, `bcm63xx_setup_cfg_access`, `bcm63xx_do_cfg_read/write`, fake CardBus bridge read/write handlers, `bcm63xx_fixup`, and PCIe access gating functions.

## Control Flow
Legacy PCI config cycles program MPI L2 PCI config registers, access `pci_iospace_start`, then restore normal I/O behavior. CardBus support fakes a bridge at slot 0x1e, stores bridge config in software, remaps a single real CardBus device as type-0 access, and uses a fixup to assign the one hardware I/O window to PCI or CardBus. PCIe access only allows bridge slot 0 and endpoint slot 0 when link is up, with endpoint config offset adjustment.

## State And Persistence
Stores fake CardBus bridge config in static `fake_cb_bridge_regs`, bus tracking in `fake_cb_bridge_bus_number`, and one-time I/O window choice in `bcm63xx_fixup`. Hardware MPI/PCIe registers are programmed per access.

## Dependencies And Integration Points
Depends on `pci-bcm63xx.h`, BCM MPI/PCIe register helpers, CardBus config symbols, PCI fixup infrastructure, and shared `pci_iospace_start` from the BCM63xx controller setup.

## Risks And Edge Cases
The single I/O window means mixed PCI/CardBus I/O users are unsupported. Config write waits with fixed `udelay(500)`. Bus number handling for type 1 is noted as incomplete. Fake bridge state must match Linux PCI enumeration expectations.

## Test Signals
BCM63xx boot with PCI, CardBus, and PCIe devices; config-space byte/word/dword access tests; CardBus bridge enumeration; and link-down PCIe probes are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-bonito64.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-bonito64.c

## Purpose
Implements Bonito64 PCI config-space operations for MIPS boards.

## Important APIs, Types, And Functions
Exports `bonito64_pci_ops`; core helper `bonito64_pcibios_config_access` maps type 0/type 1 config cycles through Bonito registers, with read/write wrappers for byte, word, and dword sizes.

## Control Flow
Reads/writes validate alignment, compose type-0 IDSEL or type-1 bus/device/function addresses, clear Bonito abort status, program `BONITO_PCIMAP_CFG`, access the CKSEG1 config window, wait for writes, then detect and clear master/target aborts.

## State And Persistence
No software state. Hardware abort bits and mapping registers are mutated per access.

## Dependencies And Integration Points
Depends on Bonito64 board register macros, PCI core `struct pci_ops`, CKSEG1 uncached access, endian conversion helpers, and MIPS board builds.

## Risks And Edge Cases
Device range is limited by IDSEL mapping. Abort returns sometimes use `-1` rather than a PCIBIOS code in wrappers. Byte/word writes require read-modify-write, so abort handling must be correct.

## Test Signals
Bonito64/Malta-style config-space enumeration, byte/word/dword access, absent-device probes, and alignment error tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-bonito64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-gt64xxx_pci0.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-gt64xxx_pci0.c

## Purpose
Implements GT64120/Galileo PCI0 config-space operations.

## Important APIs, Types, And Functions
Exports `gt64xxx_pci0_ops`; `gt64xxx_pci0_pcibios_config_access` performs the actual config cycle and wrappers handle byte/word/dword extraction and read-modify-write.

## Control Flow
The access helper rejects Galileo slot 31 on bus 0, clears master/target abort causes, writes config address with enable bit, accesses config data with special raw/nonraw handling for the host controller at bus 0 slot 0, then checks and clears aborts.

## State And Persistence
No persistent software state; hardware config address/data and interrupt cause registers are modified for each access.

## Dependencies And Integration Points
Depends on `asm/gt64120.h`, GT register access macros, and PCI core ops.

## Risks And Edge Cases
Host bridge slot 0 special handling and slot 31 hardware bug are easy to regress. Wrappers do not explicitly validate alignment. Abort detection controls absent-device behavior.

## Test Signals
GT64xxx board enumeration, absent slot probes, host bridge config access, and byte/word writes validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-gt64xxx_pci0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-lantiq.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-lantiq.c

## Purpose
Provides Lantiq PCI config-space read/write callbacks used by the Lantiq PCI controller.

## Important APIs, Types, And Functions
Defines `ltq_pci_read_config_dword` and `ltq_pci_write_config_dword`; internal `ltq_pci_config_access` maps config accesses through `ltq_pci_mapped_cfg` under `ebu_lock`.

## Control Flow
Access rejects non-bus-0, invalid slots, slot 0, and the SoC's own AD29 devfn. It builds a config address, performs swapped 32-bit reads/writes, executes a write barrier, clears possible master abort status through a status-command register sequence, and treats all-ones reads as not found.

## State And Persistence
No persistent software state; uses external Lantiq mapped config base and EBU lock. Hardware error status is cleared per access.

## Dependencies And Integration Points
Depends on Lantiq SoC helpers, `pci-lantiq.h`, `ltq_pci_mapped_cfg`, and global `ebu_lock`.

## Risks And Edge Cases
Endianness swabbing and master-abort cleanup are hardware-sensitive. Slot filtering is strict and may hide devices if topology differs. Uses exported-looking function names rather than a local `struct pci_ops` in this file.

## Test Signals
Lantiq PCI enumeration, all byte/word/dword config access sizes, absent-device probing, and concurrent config access stress under interrupt load are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-loongson2.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-loongson2.c

## Purpose
Implements Loongson2 PCI config-space operations and CS5536 MSR access helpers.

## Important APIs, Types, And Functions
Exports `loongson_pci_ops`, `_rdmsr`, and `_wrmsr` under `CONFIG_CS5536`. `loongson_pcibios_config_access` handles type 0/type 1 cycles and special CS5536 config reads/writes.

## Control Flow
On bus 0, CS5536 config registers below `PCI_MSR_CTRL` are handled by CS5536 helper functions to avoid recursive MSR access. Other accesses program Loongson PCI map registers, use CKSEG1 config windows, and detect master/target aborts. `_rdmsr/_wrmsr` serialize via `msr_lock` and perform PCI config cycles to the CS5536 MSR address/data registers.

## State And Persistence
No general persistent state except `msr_lock`. Hardware PCI map and command registers are touched per access.

## Dependencies And Integration Points
Depends on Loongson register macros, optional CS5536 headers, PCI core ops, raw spinlocks, and exported MSR helpers consumed by Loongson fixups.

## Risks And Edge Cases
CS5536 recursion avoidance is critical. Abort wrappers return `-1` in some failure paths. MSR helpers synthesize a local `pci_bus` and assume CS5536 bus/devfn constants are correct.

## Test Signals
Loongson2E/2F PCI enumeration, CS5536 peripheral fixups, MSR read/write tests, absent-device probes, and byte/word alignment checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-loongson2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-mace.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-mace.c

## Purpose
Implements SGI IP32 MACE PCI config-space operations.

## Important APIs, Types, And Functions
Exports `mace_pci_ops`; helper `mkaddr` builds config addresses, and read/write callbacks access `mace->pci.config_data` byte/word/long views.

## Control Flow
Reads temporarily disable master-abort interrupts, program config address, read the requested size with big-endian byte/word lane adjustment, acknowledge possible master abort, restore control, and fake the ultra bit for onboard SCSI devices. Writes program the config address and size-specific data lane.

## State And Persistence
No software persistence. MACE control/error registers are modified around reads.

## Dependencies And Integration Points
Depends on IP32 MACE register definitions and PCI ops used by `pci-ip32.c`.

## Risks And Edge Cases
Suppressing master-abort interrupts around reads must be balanced. The SCSI ultra-bit fakery is device/devfn-specific. No explicit invalid-device rejection is present here.

## Test Signals
SGI O2 PCI enumeration, onboard SCSI behavior, and config access to absent slots are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-mace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-msc.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-msc.c

## Purpose
Implements MIPS MSC01 PCI config-space operations.

## Important APIs, Types, And Functions
Exports `msc_pci_ops`; `msc_pcibios_config_access` programs MSC01 config address/data and wrappers perform size extraction and read-modify-write.

## Control Flow
Before each access it clears master/target abort status, writes bus/device/function/register fields to `MSC01_PCI_CFGADDR`, performs read or write through `MSC01_PCI_CFGDATA`, reads interrupt status, and clears abort bits on error.

## State And Persistence
No persistent software state. Hardware config and status registers are updated per access.

## Dependencies And Integration Points
Depends on MSC01 PCI register macros and generic PCI ops.

## Risks And Edge Cases
Alignment checks exist in wrappers, but config-access failures return `-1` rather than canonical PCIBIOS error in some paths. Abort handling defines absent-device semantics.

## Test Signals
MSC platform config enumeration and absent-device probes should validate read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-msc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-rc32434.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-rc32434.c

## Purpose
Implements IDT RC32434 PCI config-space operations.

## Important APIs, Types, And Functions
Exports `rc32434_pci_ops`; helpers include `config_access`, byte/word/dword readers and writers, and public `pci_config_read/write` callbacks.

## Control Flow
`config_access` writes an enabled config address to `pcicfga`, synchronizes, and reads or writes `pcicfgd`. Dword vendor-ID reads retry with increasing sleep when values look invalid. Bus 0 scans above slot 21 are suppressed to avoid errors with daughterboards.

## State And Persistence
No persistent software state. RC32434 PCI config registers are touched on each access.

## Dependencies And Integration Points
Depends on RC32434 PCI register globals, `rc32434_sync`, MIPS CPU/board headers, and PCI core ops.

## Risks And Edge Cases
The retry loop returns success with invalid all-ones/all-zero data after delay exhaustion, which matches scanning behavior but can hide faults. Slot limit is board-specific. Byte/word writes use read-modify-write.

## Test Signals
RB532/RC32434 enumeration with slow devices, absent slot scans, and daughterboard configurations validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-rc32434.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-sni.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-sni.c

## Purpose
Provides SNI PCIMT and PCIT PCI config-space operations.

## Important APIs, Types, And Functions
Exports `sni_pcimt_ops` and `sni_pcit_ops`. Helpers are `set_config_address`, `pcimt_read/write`, `pcit_set_config_address`, and `pcit_read/write`.

## Control Flow
PCIMT validates devfn/register, rejects bus-0 devfns beyond the decoded range, writes an ASIC config address, and uses port I/O for data. PCIT uses CF8/CFC-style type-1 addresses and, for bus 0 reads, performs a guarded write/probe sequence to avoid data bus errors before doing the requested access.

## State And Persistence
No persistent software state; direct ASIC or port I/O registers are programmed per access.

## Dependencies And Integration Points
Depends on SNI address constants and PCI core ops.

## Risks And Edge Cases
The bus-0 PCIT existence probe is invasive but protects against bus errors. Return values are sometimes raw zero instead of `PCIBIOS_SUCCESSFUL`, which is equivalent here but inconsistent. Device decode assumptions differ between PCIMT and PCIT.

## Test Signals
SNI RM200/RM300 hardware enumeration and absent-device reads are the only realistic signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-sni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-tx4927.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/ops-tx4927.c

## Purpose
Implements Toshiba TX4927/TX4938 PCI controller config ops, setup, diagnostics, and PCI error interrupt handling.

## Important APIs, Types, And Functions
Key APIs are `get_tx4927_pcicptr`, `tx4927_pcibios_setup`, `tx4927_pcic_setup`, `tx4927_report_pcic_status`, `tx4927_dump_pcic_settings`, and `tx4927_pcierr_interrupt`. It installs a private `tx4927_pci_ops` and optionally declares an SLC90E66 bridge quirk.

## Control Flow
Setup records controller-to-register mappings, assigns `pci_ops`, disables initiator spaces, configures GB-to-PCI and PCI-to-GB windows, endian swap flags, timeout options, interrupt/status masks, optional internal arbiter, and command bits. Config reads/writes derive the controller from `bus->sysdata`, program config address, access endian-correct data lanes, and check/clear master abort. Error interrupt handling reports status, clears errors, or panics depending on `txx9_pci_err_action`.

## State And Persistence
Persists controller mappings in static `pcicptrs` and boot options in `tx4927_pci_opts`. Hardware window, mask, status, and arbiter registers are programmed for the boot lifetime.

## Dependencies And Integration Points
Depends on TXX9 PCI globals/options, TX4927 register layout, MIPS IRQ APIs, and board setup code that calls `tx4927_pcic_setup`.

## Risks And Edge Cases
Window size/offset calculations, endian flags, abort handling, and interrupt action policy are hardware-critical. `pcicptrs` supports only two controllers. Boot option parsing silently ignores invalid values.

## Test Signals
TX4927/TX4938 boot, PCI config scanning, PCI error interrupt injection, endian build coverage, and boot options `trdyto=`, `retryto=`, `gbwc=` validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/ops-tx4927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-alchemy.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-alchemy.c

## Purpose
Implements Au1500/Au1550 Alchemy PCI host-mode controller support, including config-space access through a wired TLB entry, platform probing, IRQ delegation, and suspend/resume register save/restore.

## Important APIs, Types, And Functions
Defines `struct alchemy_pci_context`, `alchemy_pci_ops`, `alchemy_pci_probe`, `alchemy_pci_init`, `pcibios_map_irq`, and syscore suspend/resume hooks. Helpers include `mod_wired_entry`, `alchemy_pci_wired_entry`, `config_access`, and board IDSEL callback support.

## Control Flow
Probe validates platform data, claims and maps controller registers, enables the PCI clock, maps I/O space, handles old Au1500 noncoherent mode, installs board IRQ/IDSEL callbacks, allocates a VM area for config space, creates a wired TLB mapping, applies board config bit masks, registers syscore ops, and registers the PCI controller. Config access asserts board IDSEL, creates or reuses a wired TLB mapping for the target config page, reads/writes through the VM window, checks/clears PCI errors, and deasserts IDSEL.

## State And Persistence
Global `__alchemy_pci_ctx` stores the single controller for syscore operations. `alchemy_pci_context` caches last TLB entry values and saves twelve PCI controller registers across suspend. Hardware PCI config and TLB state persist until changed or reset.

## Dependencies And Integration Points
Depends on Alchemy platform data, clock framework, MIPS TLB helpers, PCI controller registration, DMA coherency state, syscore ops, and board-provided IRQ/IDSEL callbacks.

## Risks And Edge Cases
Wired TLB manipulation is fragile, especially across firmware resume paths that reset C0_wired. Config access runs with interrupts disabled and assumes board IDSEL callbacks are safe. Old Au1500 coherency workaround changes PCI config behavior. Only one controller is supported by the global context.

## Test Signals
Au1500/Au1550 boot, suspend/resume, PCI config scanning from atomic contexts, DMA coherency tests, and board-specific IRQ routing are needed signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-alchemy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar2315.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar2315.c

## Purpose
Implements AR2315/AR2316 PCI host controller support for a limited single-board use case, including custom DMA offset translation and interrupt-domain handling.

## Important APIs, Types, And Functions
Defines `struct ar2315_pci_ctrl`, overrides `phys_to_dma` and `dma_to_phys`, installs `ar2315_pci_ops`, and provides `ar2315_pci_probe`, `ar2315_pci_host_setup`, IRQ domain ops, `pcibios_map_irq`, and `pcibios_plat_dev_init`.

## Control Flow
Probe maps controller and external config windows, resets the PCI bus, configures uncached access, delays for hardware stabilization, validates/programs host BARs and command bits, creates an IRQ domain, enables abort/external interrupts, and registers the PCI controller. Config access toggles CFG_SEL, reads the config window, checks abort status, optionally writes masked values, clears aborts, and restores memory access mode. IRQ handling dispatches the first pending bit through the domain.

## State And Persistence
Controller state is in `ar2315_pci_ctrl`; IRQ mappings persist in the irq domain. DMA translation uses a fixed 0x20000000 offset for PCI devices. Hardware reset, BAR, interrupt, and uncached config registers persist until reset.

## Dependencies And Integration Points
Depends on platform resources named `ar2315-pci-ctrl` and `ar2315-pci-ext`, IRQ domain APIs, MIPS physical access behavior, and PCI controller registration.

## Risks And Edge Cases
Global `phys_to_dma`/`dma_to_phys` overrides affect DMA translation on this build. Only devices up to slot 18 are accepted, and host slot 3 is hidden. CFG_SEL toggling must be restored after every access. IRQ handler handles one pending bit per parent interrupt.

## Test Signals
Fonera/AR2315 boot with USB EHCI device, DMA address tests, config abort probes, and external interrupt delivery are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar2315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar71xx.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar71xx.c

## Purpose
Implements Atheros AR71xx PCI host controller config access, reset, resource registration, and chained interrupt handling.

## Important APIs, Types, And Functions
Defines `struct ar71xx_pci_controller`, `ar71xx_pci_ops`, `ar71xx_pci_probe`, `ar71xx_pci_reset`, IRQ chip callbacks, and `postcore_initcall(ar71xx_pci_init)`.

## Control Flow
Probe maps the config register block and resources, resets PCI bus/core through ATH79 reset helpers, programs the local PCI command register, clears bus errors, installs IRQ chips for the ATH79 PCI IRQ range, fills the PCI controller, and registers it. Config reads/writes build type-0/type-1 addresses, program byte-lane enables, check PCI/AHB error registers, and access config read/write data registers. Chained IRQ handling reads ATH79 reset interrupt pending/enabled bits and dispatches device/core IRQs.

## State And Persistence
State is per-controller in the platform device object: resource descriptors, IRQ base, and config base. Hardware reset, command, error, and interrupt-enable registers are modified during boot and IRQ operations.

## Dependencies And Integration Points
Depends on ATH79 reset/DDR helpers, platform resources `cfg_base`, `io_base`, `mem_base`, and Linux PCI/IRQ APIs.

## Risks And Edge Cases
Byte-lane table has BUG_ON for invalid size/offset combinations. Error handling logs critical bus errors when not quiet. IRQ dispatch uses an else-if chain, so one parent interrupt handles one pending source at a time. Reset timing uses fixed delays.

## Test Signals
AR71xx board boot, PCI device config scanning, AHB/PCI error clearing, interrupt delivery for DEV0-2 and CORE, and build coverage for `CONFIG_SOC_AR71XX` are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar71xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar724x.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar724x.c

## Purpose
Implements AR724x PCIe host controller support, including local/root config access, endpoint config access, link bring-up, resources, and one-line chained IRQ handling.

## Important APIs, Types, And Functions
Defines `struct ar724x_pci_controller`, `ar724x_pci_ops`, `ar724x_pci_probe`, `ar724x_pci_hw_init`, `ar724x_pci_check_link`, IRQ chip callbacks, and `postcore_initcall(ar724x_pci_init)`.

## Control Flow
Probe maps control, endpoint config, and root-complex config windows, collects I/O and memory resources, optionally performs full PCIe reset/PLL/LTSSM initialization, records link status, installs one IRQ, initializes local command bits, and registers the controller. Config reads/writes allow only root bus slot 0/function 0 and endpoint bus slot 0, returning not found when link is down. Local writes program CRP config space; endpoint accesses use `devcfg_base` with BAR0 workaround handling for AR7240. IRQ mask/unmask uses the controller INT_MASK/STATUS registers.

## State And Persistence
Per-controller state stores mapped bases, resources, irq, irq_base, and `link_up`. Hardware reset/PLL/app-control, interrupt, and config registers persist for the boot session.

## Dependencies And Integration Points
Depends on ATH79 reset and PLL helpers, named platform resources `ctrl_base`, `cfg_base`, `crp_base`, `io_base`, `mem_base`, and PCI/IRQ core APIs.

## Risks And Edge Cases
The driver intentionally supports only one endpoint slot. Link-down handling hides endpoint config. BAR0 workaround and local/endpoint access distinction are hardware-specific. Fixed 100 ms link wait may be marginal on slow boards.

## Test Signals
AR724x PCIe board boot, link-up/link-down probes, endpoint BAR programming, interrupt delivery, and config read/write tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar724x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480.c

## Purpose
Implements Broadcom BCM1480/BCM1x55 native PCI-X host-controller glue.

## Important APIs, Types, And Functions
Defines `bcm1480_pci_ops`, `bcm1480_controller`, `pcibios_map_irq`, `pcibios_plat_dev_init`, and `bcm1480_pcibios_init`.

## Control Flow
Init sets probe-only mode, adjusts global I/O and memory limits, maps 16 MiB config space, detects host versus device mode from system config and bridge command bits, enables ExpMemEn, maps PCI I/O space, sets I/O port base, registers the PCI controller, and optionally takes over VGA console. Config access checks bus mode, reads/writes the mapped config window, and handles byte/word/dword extraction.

## State And Persistence
Global `cfg_space` and `bcm1480_bus_status` persist after init. Hardware config space, I/O mapping, and controller command bits are programmed for the boot lifetime.

## Dependencies And Integration Points
Depends on SiByte BCM1480 register definitions, CFE firmware resource assignment, MIPS I/O mapping, generic PCI controller registration, and optional VGA console support.

## Risks And Edge Cases
Assumes firmware assigned resources (`PCI_PROBE_ONLY`). The 16 MiB config mapping is large. Device mode hides bus 0. Writes to disallowed devices return bad-register rather than not-found. Global resource limit changes affect the whole PCI subsystem.

## Test Signals
BCM1480 host-mode boot with CFE-initialized PCI, device-mode boot, config scanning, I/O mapping, and VGA console takeover are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480ht.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480ht.c

## Purpose
Implements BCM1480/BCM1455 HyperTransport support exposed through the PCI subsystem.

## Important APIs, Types, And Functions
Defines `bcm1480ht_pci_ops`, `bcm1480ht_controller`, global `ht_eoi_space`, and `bcm1480ht_pcibios_init`.

## Control Flow
Init maps 16 MiB HT config space, marks the bus enabled, maps the 4 MiB HT EOI special region, maps HT I/O space, sets `io_map_base`, and registers a secondary PCI controller with `get_busno` returning 0. Config access mirrors the BCM1480 PCI path using the HT config mapping and access gating.

## State And Persistence
Global `ht_cfg_space`, `ht_eoi_space`, and `bcm1480ht_bus_status` persist for the boot lifetime. Hardware mappings remain active until reboot.

## Dependencies And Integration Points
Depends on SiByte BCM1480 HT register definitions, MIPS I/O mapping, and PCI controller registration.

## Risks And Edge Cases
Always scans because firmware may not initialize all HT paths, increasing reliance on absent-device behavior. Large config and EOI mappings consume kernel virtual space. Device-mode handling is minimal.

## Test Signals
BCM1480 HT devices, interrupt EOI users, config scanning, and secondary-controller registration are main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480ht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm47xx.c -->
# sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm47xx.c

## Purpose
Provides BCM47xx PCI platform device initialization and IRQ mapping delegation for SSB and BCMA bus variants.

## Important APIs, Types, And Functions
Defines `pcibios_map_irq`, SSB/BCMA-specific `bcm47xx_pcibios_plat_dev_init_*` helpers under config guards, and `pcibios_plat_dev_init`.

## Control Flow
Generic IRQ mapping returns 0, while platform device init dispatches by `bcm47xx_bus_type`. SSB path calls SSB PCI init, reads the PCI interrupt pin, maps IRQ through SSB, validates IRQ >= 2, and writes `dev->irq`. BCMA path calls BCMA init and IRQ mapping similarly.

## State And Persistence
No persistent software state beyond assigning `dev->irq` during device init. Uses external `bcm47xx_bus_type`.

## Dependencies And Integration Points
Depends on SSB and/or BCMA core PCI helpers, BCM47xx platform bus type, and PCI core callbacks.

## Risks And Edge Cases
Returning 0 from `pcibios_map_irq` means the real mapping must happen in platform init. IRQ values below 2 are rejected because they are software interrupts. Builds without matching SSB/BCMA support leave devices unchanged.

## Test Signals
BCM47xx SSB and BCMA board boot, PCI device init logs, IRQ assignment, and failed-map error paths are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm47xx.c -->
