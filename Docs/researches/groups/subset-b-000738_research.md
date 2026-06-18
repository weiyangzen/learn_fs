# subset-b-000738 Research

Grouped research report for the requested SiByte MIPS platform header subset. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_mc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_mc.h

Purpose: defines BCM1280/BCM1480 memory-controller register bitfields and canned values. It is the high-level contract used by early platform firmware/kernel setup code to program DRAM channel layout, chip-select windows, address muxing, DRAM mode commands, memory clocking, delay-locked-loop tuning, drive strength, ECC diagnostics, and global interleave/ECC control.

Important APIs/types/functions: this header has no C functions or types; its API is macro families. `S_BCM1480_MC_*` macros define shifts, `M_BCM1480_MC_*` masks, `V_BCM1480_MC_*(x)` encoded values, `G_BCM1480_MC_*(x)` extractors, and `K_BCM1480_MC_*` symbolic enumerants. Important composite defaults include `V_BCM1480_MC_CONFIG_DEFAULT`, `V_BCM1480_MC_DRAMMODE_DEFAULT`, `V_BCM1480_MC_TIMING_DEFAULT`, and default DLL/clock/timing encodings.

Control flow: runtime control flow is external; callers write the generated values into addresses from `bcm1480_regs.h`. The encoded flow is the hardware initialization sequence: configure chip-select/interleave/address selectors, issue DRAM commands such as EMRS/MRS/precharge/refresh/power-down, then program mode, clock, DLL, drive, timing, and ECC/global status registers.

State and persistence: all state represented here is persistent hardware register state until reset or reprogramming. ECC status/correction fields expose latched error information; global interleave and chip-select fields affect the physical memory map and cannot be treated as transient software state.

Dependencies and integration: depends on `sb1250_defs.h` for 64-bit mask/value helpers and on `SIBYTE_HDR_FEATURE(1480, PASS2)` to expose DDR2, ODT, extra commands, timing2, and ECC RMW fields. It integrates with `bcm1480_regs.h` address macros, boot memory sizing, ECC handlers, and low-level board bring-up.

Risks and test signals: incorrect constants can produce unbootable memory or silent ECC/addressing corruption. Several duplicate definitions are present (`V_BCM1480_MC_COL03`, `S_BCM1480_MC_PG_POLICY`, `S_BCM1480_MC_PVT_BYP_C1_PULLUP`), and `M_DATA_ECC_INVERT` appears to reference the ECC shift rather than the data-invert shift name. Useful tests are compile coverage with constrained `SIBYTE_HDR_FEATURES`, static macro expansion checks for default values, and hardware/boot tests that exercise DRAM init, ECC injection/status, and multi-channel interleave.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_regs.h

Purpose: maps BCM1255/BCM1280/BCM1455/BCM1480 on-chip peripheral register addresses. It intentionally includes `sb1250_regs.h` and then adds or overrides the register layout that changed for the BCM1480 family.

Important APIs/types/functions: no functions or structs are defined. The exported interface is address and offset macros: `A_BCM1480_MC_*`, `A_BCM1480_L2_*`, `A_BCM1480_MAC_*`, `A_BCM1480_DUART*`, `A_BCM1480_IMR_*`, `A_BCM1480_SCD_*`, `A_BCM1480_HT_*`, `A_BCM1480_NC_*`, packet-manager/high-speed-port registers, and `A_BCM1480_PHYS_*` physical map ranges. Parameterized macros such as `A_BCM1480_MC_REGISTER(ctlid, reg)`, `A_BCM1480_IMR_REGISTER(cpu, reg)`, and mailbox helpers encode per-instance spacing.

Control flow: callers use these macros to sequence MMIO access. The file encodes routing decisions such as four memory controllers, extra MACs, two DUART blocks, 128-bit interrupt mapper registers split into non-contiguous halves, additional watchdogs/compare registers, and per-port HyperTransport/node-controller/packet-manager blocks.

State and persistence: the header itself stores no state; every address resolves to memory-mapped hardware state. Some aliases target write-only set/clear mailbox registers, status registers, or physical windows whose effects persist in the device.

Dependencies and integration: depends on `sb1250_defs.h` and `sb1250_regs.h`. It is a compatibility bridge: common SB1250 symbols remain available, while BCM1480-specific blocks use `_BCM1480_` names to avoid accidentally programming incompatible SCD/IMR/L2/MC layouts.

Risks and test signals: the primary risk is using an SB1250 `A_*` symbol for a block whose BCM1480 layout diverges, especially SCD and interrupt mapper registers. Address arithmetic should be checked for CPU, MAC, MC, PM, HT, and high-speed-port instance bounds. Test signals include build coverage for platform code using all macros, sparse/checkpatch-style detection of pointer-width truncation, and hardware smoke tests for UART, timers, interrupts, MAC DMA, and memory-controller probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_scd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_scd.h

Purpose: defines BCM1480-family System Control and Debug bitfields. It is the chip-specific supplement to `sb1250_scd.h`, adding new part IDs and the changed SCD layouts for system configuration, watchdog reset targets, performance counters, address traps, and trace control.

Important APIs/types/functions: the file exports only macros. Key constants are `K_SYS_PART_BCM1480`, `K_SYS_PART_BCM1280`, `K_SYS_PART_BCM1455`, `K_SYS_PART_BCM1255`, and `K_SYS_PART_BCM1158`; `M_BCM1480_SYS_*`/`V_BCM1480_SYS_*` fields for PLL, boot mode, node ID, CPU reset/disable, ccNUMA, and reset flags; watchdog reset-type encodings; performance-counter source fields `SRC4` through `SRC7`; address-trap agent IDs; and trace sequence/config additions.

Control flow: platform code reads revision/manufacturing registers, derives SoC identity, configures clocks/boot-mode-dependent peripherals, masks or resets CPUs, arms watchdogs, selects performance-counter events, installs address traps, and configures trace collection. This header supplies the bit encodings for those flows while the actual MMIO addresses come from `bcm1480_regs.h`.

State and persistence: all represented state lives in SCD hardware registers. Some bits are latched status from reset or bus errors; others trigger resets, counter clear/enable operations, watchdog behavior, or trace capture state.

Dependencies and integration: depends on `sb1250_defs.h` plus `sb1250_scd.h` for shared fields. The comments explicitly warn that BCM1480 SCD symbols are distinct from SB1250 `A_SCD_*`/field names; integration should use `_BCM1480_` names when targeting the newer family.

Risks and test signals: reset, watchdog, and CPU-disable masks are high impact. Wrong reset-type or CPU bit selection can reset the wrong core or whole system. Compile tests should cover `SIBYTE_HDR_FEATURE_CHIP(1480)`, and runtime tests should validate part ID decode, timer/watchdog interrupts, per-core reset/mask behavior, performance counter clear/enable, address trap matching, and trace register programming on actual hardware or an accurate simulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_scd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bigsur.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bigsur.h

Purpose: describes board-level constants for the BCM91x80A/B BigSur platform. It selects the board name and declares fixed generic-bus chip-select assignments and physical addresses for LEDs, IDE, and PCMCIA support.

Important APIs/types/functions: no functions or types are defined. Important symbols are `SIBYTE_BOARD_NAME`, `SIBYTE_HAVE_PCMCIA`, `SIBYTE_HAVE_IDE`, `LEDS_CS`, `LEDS_PHYS`, `IDE_CS`, `IDE_PHYS`, `K_GPIO_GB_IDE`, `K_INT_GB_IDE`, `PCMCIA_CS`, `PCMCIA_PHYS`, `K_GPIO_PC_READY`, and `K_INT_PC_READY`.

Control flow: the file is selected when `CONFIG_SIBYTE_BIGSUR` is enabled, usually through `board.h`. Feature macros gate whether IDE and PCMCIA definitions are visible. Interrupt constants are composed from GPIO lines and `K_INT_GPIO_0`, tying board wiring into the interrupt mapper.

State and persistence: there is no software state. The constants point to persistent board hardware mappings on the generic bus and GPIO interrupt lines.

Dependencies and integration: includes `sb1250.h` for common platform declarations and `bcm1480_int.h` for BCM1480 interrupt source numbering. It integrates with generic bus setup, IDE/PCMCIA platform devices, LED diagnostics, and board setup code.

Risks and test signals: hard-coded chip-select and physical address constants must match board strapping and generic-bus setup. Wrong GPIO-to-interrupt mapping breaks IDE/PCMCIA readiness signaling. Test signals are BigSur config build coverage, early LED writes, generic-bus resource registration, and interrupt delivery tests for IDE and PCMCIA ready GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bigsur.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/board.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/board.h

Purpose: centralizes SiByte board header selection and exposes the LED helper contract used by assembly and C code during early boot and diagnostics.

Important APIs/types/functions: for C callers it declares `void swarm_setup(void);` and either `extern void setleds(char *str);` or a no-op `setleds(s)` macro depending on whether the selected board defines `LEDS_PHYS`. For assembler it defines a `setleds(t0, t1, c0, c1, c2, c3)` macro that writes four bytes to LED offsets from the uncached LED physical address.

Control flow: preprocessor selection includes `swarm.h`, `sentosa.h`, or `bigsur.h` based on `CONFIG_SIBYTE_*` options. The LED helper becomes active only when the included board header supplies `LEDS_PHYS`; otherwise both assembly and C LED calls compile away.

State and persistence: no ordinary software state is stored. Active LED operations write board hardware registers and persist visually until overwritten or reset.

Dependencies and integration: depends on board-specific headers for constants. It is used by early boot assembly, board setup, and platform diagnostics that need common names while still allowing board-specific resource maps.

Risks and test signals: configuration overlap can include multiple board headers if Kconfig is inconsistent, which could collide on board constants. The assembly LED macro assumes scratch registers and specific byte offsets. Test signals include all supported SiByte board defconfig builds, assembly preprocessing, boot logs that call `swarm_setup`, and visible/no-op LED behavior depending on board support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/board.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250.h

Purpose: provides the top-level SiByte SB1250/BCM1480 platform constants and low-level declarations shared by C platform code. It records release metadata, IRQ counts, DUART numbering, SoC revision globals, interrupt mask helpers, BCM1480 timer/IRQ entry points, and MMIO address conversion.

Important APIs/types/functions: important constants are `SIBYTE_RELEASE`, `SB1250_NR_IRQS`, `BCM1480_NR_IRQS`, `BCM1480_NR_IRQS_HALF`, and `SB1250_DUART_MINOR_BASE`. Extern globals include `sb1_pass`, `soc_pass`, `soc_type`, `periph_rev`, and `zbbus_mhz`. Extern functions include `sb1250_mask_irq`, `sb1250_unmask_irq`, `bcm1480_time_init`, `bcm1480_mask_irq`, and `bcm1480_unmask_irq`. `IOADDR(a)` maps a physical offset through `IO_BASE`, and `AT_spin` is an inline assembly spin trap using `$at`.

Control flow: platform initialization discovers SoC/pass information, initializes timers, and routes interrupt masking through SB1250 or BCM1480-specific helpers. The `AT_spin` macro is a deliberate infinite loop for debug/halt paths.

State and persistence: revision globals and `zbbus_mhz` are process-wide kernel state initialized by platform probing. Interrupt mask helpers mutate interrupt-controller hardware state. `IOADDR` produces an MMIO pointer but stores no state itself.

Dependencies and integration: includes `addrspace.h`, `sb1250_scd.h`, and `bcm1480_scd.h` for address and revision constants. It is a common include for board files, interrupt code, timer code, UART setup, and low-level drivers.

Risks and test signals: using the wrong IRQ count or mask helper for a chip family can drop interrupts above 63 on BCM1480 or touch wrong registers. `AT_spin` clobbers assembler temporary state by design and must remain debug-only. Test signals are platform build coverage, boot-time SoC/pass identification, timer tick validation, and interrupt mask/unmask tests for both 64- and 128-source controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_defs.h

Purpose: supplies the shared preprocessor and bitfield machinery used by all SiByte hardware headers. It also defines the compile-time feature-selection model for chip families and revisions.

Important APIs/types/functions: key feature masks are `SIBYTE_HDR_FMASK_*`, `SIBYTE_HDR_FEATURES`, `SIBYTE_HDR_FEATURE_CHIP`, `SIBYTE_HDR_FEATURE`, `SIBYTE_HDR_FEATURE_EXACT`, `SIBYTE_HDR_FEATURE_UP_TO`, and `SIBYTE_HDR_FEATURE_1250_112x`. Bitfield helpers include `_SB_MAKE64`, `_SB_MAKEMASK1`, `_SB_MAKEMASK`, `_SB_MAKEVALUE`, `_SB_GETVALUE`, and 32-bit variants. On MIPS64 C builds it also defines register access macros `SBWRITECSR(csr, val)` and `SBREADCSR(csr)`.

Control flow: most dependent headers branch at preprocessing time based on `SIBYTE_HDR_FEATURES`, exposing only fields valid for selected chip revisions. Runtime code then uses the bitfield helpers to assemble or decode MMIO register values.

State and persistence: the header has no runtime state. `SBWRITECSR` and `SBREADCSR` are direct volatile MMIO accessors and therefore read/write persistent hardware register state selected by callers.

Dependencies and integration: requires ANSI C89 preprocessing and 64-bit integer support; C users must have `uint32_t` and `uint64_t` defined. It is included by the register, DMA, MAC, memory-controller, generic-bus, interrupt, L2, and LDT headers.

Risks and test signals: incorrect `SIBYTE_HDR_FEATURES` settings can hide needed macros or expose invalid ones, causing either build failures or wrong register programming. The helper macros rely on correct integer widths and should be checked in assembler and C preprocessing contexts. Test signals include compile matrices for all feature masks, macro expansion tests for masks crossing bit 31, and sparse/`-Wshift-*` builds on 32- and 64-bit toolchains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_dma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_dma.h

Purpose: defines SB1250 Ethernet/serial DMA and generic data-mover register and descriptor bitfields. It is the contract between network/serial/data-mover drivers and the descriptor formats consumed by the DMA engines.

Important APIs/types/functions: there are no C functions or structs. Key macro groups cover `DMA_CONFIG0/1` control bits, descriptor base/current/count fields, receive drop counters, Ethernet/serial descriptor doubleword A/B layouts, Ethernet RX/TX status and option encodings, serial RX/TX status/options, data-mover descriptor base/current/partial-result registers, CRC/TCP checksum definition registers, and data-mover descriptor source/destination direction and checksum/CRC options.

Control flow: drivers construct descriptor rings, program descriptor base/count registers, enable DMA channels, then poll or handle interrupts using status bits. Descriptor control flow is split across valid/address/size/status fields and interrupt flags; data-mover descriptors additionally encode source/destination direction, zeroing, prefetch, L2 hints, read/write backoff, CRC, and TCP checksum behavior.

State and persistence: descriptor rings live in DMA-visible memory owned by drivers. The channel registers and current descriptor pointers are hardware state; status bits are written by hardware and consumed by interrupt/poll paths.

Dependencies and integration: depends on `sb1250_defs.h`; feature gates expose later pass/BCM1480 additions such as enhanced addressing, pause/status bits, VLAN/CRC flags, partial CRC/checksum results, and data-mover checksum options. It integrates with `sb1250_regs.h`/`bcm1480_regs.h` address macros and MAC/serial drivers.

Risks and test signals: address masks, ring sizes, and descriptor ownership bits are high risk because mistakes can DMA to wrong memory. `M_DMA_DSCRB_STATUS` is duplicated, and several bits have different meanings for read versus write or RX versus TX. Test signals include compile coverage for pass1/pass2/pass3 feature gates, descriptor layout unit checks, DMA ring wrap tests, Ethernet RX/TX checksum/VLAN tests, serial DMA transfer tests, and data-mover CRC/checksum validation on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_genbus.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_genbus.h

Purpose: defines generic bus, PCMCIA, and GPIO interrupt configuration bitfields for SiByte SoCs. It is used by board setup and platform device code to describe external chip-select timing, sizing, interrupt capture, drive strength, PCMCIA behavior, and GPIO interrupt mode.

Important APIs/types/functions: exported macro groups include `M_IO_*`/`V_IO_*` fields for generic-bus region configuration, size, start address, timing0/timing1, interrupt status/data/address/parity, and output drive registers; `M_PCMCIA_*` fields for configuration and card status; and `K_GPIO_INTR_*`, `V_GPIO_INTR_TYPE`, `G_GPIO_INTR_TYPE`, plus BCM1480 additional GPIO interrupt type fields.

Control flow: board code programs chip-select regions with bus width, multiplexing, timing, and caching attributes, then handles bus errors or external interrupts through status registers. PCMCIA setup uses config/status bits to control power/reset/card enable and detect card-ready/status. GPIO interrupt flow configures edge/level/high/low behavior and later routes GPIO lines into the interrupt mapper.

State and persistence: region config/timing/drive registers persist in hardware and define external device access behavior. Interrupt status registers expose latched event/error state. PCMCIA/GPIO status reflects board hardware inputs.

Dependencies and integration: depends on `sb1250_defs.h` for bit helpers and feature gates. It integrates with board headers such as `bigsur.h`, generic bus address macros in register headers, PCMCIA/IDE platform drivers, and interrupt mapper constants.

Risks and test signals: wrong timing or bus width can hang external bus cycles; wrong cacheability or address-base programming can corrupt device access. GPIO interrupt mode mismatches cause lost or stuck interrupts. Test signals include per-board resource setup builds, LED/IDE/PCMCIA access smoke tests, external bus error interrupt tests, and GPIO edge/level interrupt tests including BCM1480 additional type registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_genbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_int.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_int.h

Purpose: defines SB1250 interrupt source numbers, per-source masks, interrupt mapper values, LDT interrupt set fields, and interrupt vector format.

Important APIs/types/functions: important constants include `K_INT_SOURCES`, source IDs for watchdogs, timers, SMBus, UARTs, serial, PCMCIA, address trap, performance counter, ECC, IO bus, MACs, data mover channels, mailboxes, GPIO 0-15, and LDT classes. `M_INT_*` masks mirror those source IDs. Mapper fields encode interrupt destination and delivery mode, while vector fields provide interrupt number and pending bits.

Control flow: interrupt setup code maps hardware sources to CPU interrupt lines, masks/unmasks sources, reads source status, and decodes vectors. Drivers use the numeric constants to request or route platform interrupts.

State and persistence: the header has no state, but its masks operate on interrupt mapper registers that persist until changed. Source status and vector fields reflect hardware pending state.

Dependencies and integration: depends on `sb1250_defs.h` and feature gates for pass2/112x additions such as cycle counter interrupts and LDT error/eject sources. It integrates with `sb1250.h` IRQ counts, `sb1250_regs.h` IMR addresses, board GPIO interrupt assignments, and device drivers.

Risks and test signals: source-number drift is high impact because it silently routes handlers to the wrong hardware. Feature-gated sources must align with the selected SoC revision. Test signals include build coverage for old/new feature masks, interrupt-controller initialization checks, per-source mask bit validation, GPIO interrupt tests, timer/watchdog interrupt tests, and LDT interrupt injection where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_l2c.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_l2c.h

Purpose: defines SB1250/112x L2 cache tag and management-address bitfields. It supports low-level cache diagnostics, way management, ECC inspection, and cache disable/read-misc control.

Important APIs/types/functions: exported macros describe L2 tag register fields (`M_L2C_TAG_INDEX`, `M_L2C_TAG_TAG`, `M_L2C_TAG_ECC`, `M_L2C_TAG_WAY`, dirty/valid bits), management-address fields (`M_L2C_MGMT_INDEX`, quadrant, half, way, ECC diagnostic mode, tag, dirty/valid bits), the management tag base address `A_L2C_MGMT_TAG_BASE`, and read-misc register bits for way-local/remote/agent state and cache disable support on later revisions.

Control flow: diagnostic or cache-management code constructs management addresses from index/quadrant/way fields, reads tag/ECC/dirty/valid state, and may disable ways or inspect read-misc state. Normal cache behavior is hardware-managed; software flow is limited to bring-up, diagnostics, and error handling.

State and persistence: L2 tag and management registers expose persistent cache state. Dirty/valid/tag/ECC fields are volatile from software's perspective because hardware changes them as cache traffic occurs.

Dependencies and integration: depends on `sb1250_defs.h`; later read-misc features are gated by `SIBYTE_HDR_FEATURE(1250, PASS3)` or `SIBYTE_HDR_FEATURE(112x, PASS1)`. Address macros in `sb1250_regs.h` and BCM1480-specific L2 macros in `bcm1480_regs.h` are the access points.

Risks and test signals: incorrect management-address construction can inspect or alter the wrong cache line/way. Runtime tests need strong serialization around cache diagnostics. Test signals include compile coverage for feature gates, cache tag read diagnostics, ECC error path exercises, and boot tests on pass levels with and without read-misc/cache-disable fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_l2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_ldt.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_ldt.h

Purpose: defines SB1250 Lightning Data Transport/HyperTransport bridge configuration-space offsets and bitfields. It lets platform PCI/HT setup and error handling code program the on-chip LDT interface.

Important APIs/types/functions: important symbols include vendor/device IDs `K_LDT_VENDOR_SIBYTE` and `K_LDT_DEVICE_SB1250`, type-1 config header offsets (`R_LDT_TYPE1_*`), device ID/class/header fields, command/status and bridge-control masks, LDT command fields, link control/frequency fields, SRI command/control and buffer count fields, error status/control bits, CRC counters, and additional status bits for later revisions.

Control flow: platform code reads config header identity, enables I/O/memory/mastering, configures bridge windows and bus numbers, programs link control/frequency, handles CRC/error/status registers, and configures SRI flow-control behavior. Some macros assume a 32-bit read of combined command/status-style registers, which shapes how callers must access config space.

State and persistence: all represented values live in LDT/PCI configuration or status registers. Command/bridge/link settings persist until reset or reconfiguration; error/status bits may be latched and require explicit clearing.

Dependencies and integration: depends on `sb1250_defs.h` and feature gates for pass2/112x fields. It integrates with `sb1250_regs.h` LDT/PCI base addresses, PCI subsystem setup, interrupt mapper LDT sources, and error-reporting paths.

Risks and test signals: register-width assumptions are important; reading or writing only 16 bits where macros expect a combined 32-bit value can misplace bits. Link frequency/control mistakes can break bus enumeration. Test signals include config-space read/write tests, PCI/HT enumeration, link training/status checks, injected fatal/nonfatal LDT errors, and compile coverage for pass1 versus pass2 fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_ldt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mac.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mac.h

Purpose: defines Ethernet MAC register bitfields shared by SB1250-compatible SiByte MAC blocks. It supports MAC configuration, enable/reset, DMA control, FIFO thresholds, frame timing, VLAN, interrupt/status, debug counters, address filters, packet-type filters, receive channel selection, and MII/MDIO control.

Important APIs/types/functions: the API is macro families for `MAC_CFG`, `MAC_ENABLE`, reset info, `MAC_TXD_CTL`, FIFO threshold registers, frame configuration, VLAN tag, status/interrupt mask, FIFO pointers/EOP counts, exact/hash/mask address filter registers, source address, packet type config, address-filter control, RX channel select, and MDIO pins. Enumerants cover speed, bypass modes, flow-control commands, IFG defaults per speed, slot/min/max frame sizes, and jumbo frame maximums.

Control flow: drivers program configuration and frame timing, set filters and addresses, enable RX/TX paths, configure DMA thresholds, handle MAC status interrupts by channel, and bit-bang or drive MDIO to access PHYs. Status-channel offset macros allow common ISR logic across RX/TX channel groups.

State and persistence: MAC configuration, filters, VLAN, thresholds, and MDIO output state persist in hardware. Status, FIFO pointers, counters, and interrupt bits reflect live device state.

Dependencies and integration: depends on `sb1250_defs.h`; many fields are feature-gated for pass2/pass3/112x/BCM1480. It integrates with DMA descriptors from `sb1250_dma.h`, MAC register addresses from `sb1250_regs.h`/`bcm1480_regs.h`, PHY/MDIO code, and network drivers.

Risks and test signals: wrong feature gating can expose fields unavailable on older silicon. RX/TX status bits share positions with different meanings, so ISR code must apply the correct channel context. The FIFO pointer getters for RX use TX masks in this header, a compatibility risk for any debug code depending on those helpers. Test signals include Ethernet link bring-up at 10/100/1000, RX/TX with checksum/VLAN/flow control, multicast/hash/exact filter tests, interrupt-per-channel tests, MDIO PHY access, and compile coverage across feature masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mc.h

Purpose: defines SB1250 memory-controller bitfields and default encodings. It covers memory channel configuration, memory clock configuration, DRAM commands/mode, SDRAM timing, chip-select windows, address-bit selection, chip-select page policy, and ECC test control.

Important APIs/types/functions: there are no functions or structs. Key macros include `V_MC_CONFIG_DEFAULT`, `V_MC_CLKCONFIG_DEFAULT`, `V_MC_TIMING_DEFAULT`, command encodings such as `V_MC_COMMAND_MRS`/`PRE`/`AR`, DRAM type values, chip-select modes, start/end/interleave encodings, row/column/bank address selectors, `K_MC_CS_ATTR_*` page policies, and `M_MC_ECC_INVERT`.

Control flow: early memory initialization programs channel map, queue/age/write limits, chip-select mode, clock ratio/refresh/skew/DLL settings, then issues DRAM commands and sets timing and chip-select address decode. Later diagnostic code may use ECC inversion/test fields.

State and persistence: all fields map to memory-controller hardware state. Chip-select windows and address selectors define the physical memory map; timing and clock fields remain active until reset/reprogramming.

Dependencies and integration: depends on `sb1250_defs.h`; pass3/112x feature gates add refresh disable, precharge/A13 behavior, and extended `tRFC`. Register addresses come from `sb1250_regs.h`; high-level platform code consumes defaults during DRAM bring-up.

Risks and test signals: mistakes can prevent boot or cause intermittent memory corruption. Duplicate `V_MC_EMODE_DEFAULT` is harmless but indicates macro hygiene risk. Errata comments explicitly note timing default differences, so changing defaults requires hardware validation. Test signals include macro expansion checks, early boot memory sizing, stress tests across chip selects, ECC test injection, and feature-mask builds for pass1/pass3/112x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_regs.h

Purpose: maps SB1250 on-chip peripheral register addresses and physical address windows. It is the base address/offset catalog used by platform code and low-level drivers for memory controller, L2 cache, PCI/LDT, MAC/DMA, DUART, synchronous serial, generic bus, GPIO, SMBus, timers, SCD, address traps, interrupt mapper, performance counters, bus watcher, debug/trace, data mover, and the physical map.

Important APIs/types/functions: the API consists of `A_*` absolute address macros, `R_*` register offsets, and parameterized helpers such as `A_MC_REGISTER`, `A_MAC_REGISTER`, `A_MAC_DMA_REGISTER`, `A_DUART_CHANREG`, `A_SER_REGISTER`, `A_IO_EXT_REG`, `A_SMB_REGISTER`, `A_SCD_TIMER_REGISTER`, `A_ADDR_TRAP_UP`, `A_IMR_REGISTER`, `A_MAILBOX_REGISTER`, `A_SCD_PERF_CNT`, and `A_DM_REGISTER`. Physical map constants include memory windows, system control, generic bus, LDT/PCI windows, cache test space, and cache way ranges.

Control flow: callers compose base-plus-offset addresses, then use MMIO helpers to initialize devices, route interrupts, access UARTs, drive timers, configure external buses, and control DMA. Feature gates remove blocks not present on 112x/1250 variants, such as memory controllers, sync serial, PCI/HT, and newer counters.

State and persistence: the file stores no state; all addresses target hardware state. Some macros target write-side set/clear aliases or debug/status views that must be used with the correct access semantics.

Dependencies and integration: depends on `sb1250_defs.h` and underpins nearly every other SiByte header. `bcm1480_regs.h` includes this file for shared blocks and adds BCM1480-specific addresses where layouts changed.

Risks and test signals: off-by-spacing errors or using feature-gated addresses on the wrong SoC can hang MMIO. The file includes compatibility aliases that comments discourage, so new code should prefer specific register names. Test signals include all-platform compile coverage, boot-time UART/timer/interrupt smoke tests, MAC/DMA and SMBus probing, generic-bus resource checks, and address-map validation against SoC documentation or hardware reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_regs.h -->
