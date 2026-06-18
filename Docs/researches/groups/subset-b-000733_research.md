# subset-b-000733 Research

Grouped research for OCTEON MIPS CSR definition headers under `sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-lmcx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-lmcx-defs.h

## Purpose
`cvmx-lmcx-defs.h` is a generated OCTEON SDK register-definition header for the LMC memory-controller blocks. It gives C code the physical CSR address formulas and 64-bit union overlays needed to initialize, tune, monitor, and diagnose DDR/DDR2/DDR3 memory-controller state on multiple OCTEON chip families. The file does not implement a driver by itself; it is the ABI surface consumed by platform, boot, EDAC, memory-training, and low-level MIPS/OCTEON code that reads or writes LMC CSRs through the broader CVMX CSR access layer.

## Important APIs, Types, And Functions
The address macros are the main API. They map controller `block_id` values, and occasionally rank or DIMM offsets, into IO-segment CSR addresses via `CVMX_ADD_IO_SEG(...)`. The exported register families cover BIST (`CVMX_LMCX_BIST_CTL`, `CVMX_LMCX_BIST_RESULT`), memory setup (`MEM_CFG0`, `MEM_CFG1`, `CONFIG`, `CONTROL`, `CTL`, `CTL1`, `DDR2_CTL`, `RESET_CTL`), PLL/DLL/clocking (`PLL_CTL`, `PLL_STATUS`, `PLL_BWCTL`, `DDR_PLL_CTL`, `DLL_CTL*`, `DCLK_*`), ECC and fault capture (`ECC_SYND`, `FADR`, `SCRAMBLED_FADR`, `INT`, `INT_EN`, `NXM`), training and leveling (`READ_LEVEL_*`, `RLEVEL_*`, `WLEVEL_*`, `CHAR_*`, `TRO_*`), DIMM and mode-register programming (`DIMMX_PARAMS`, `DIMM_CTL`, `MODEREG_PARAMS*`), performance counters (`IFB_CNT*`, `OPS_CNT*`, `DCLK_CNT*`), and on-die termination or compensation (`COMP_CTL*`, `RODT_*`, `WODT_*`).

Most registers are defined as `union cvmx_lmcx_*` with a raw `uint64_t u64` member plus a named bitfield struct `s`. Many unions also expose chip-specific overlays such as `cn30xx`, `cn38xx`, `cn50xx`, `cn52xx`, `cn58xx`, `cn61xx`, `cn63xx`, `cn63xxp1`, `cn66xx`, `cn68xx`, and `cn56xxp1`. These overlays preserve register names while reflecting different reserved ranges, field widths, or fields that exist only on particular silicon revisions.

Four static inline address helpers, `CVMX_LMCX_DUAL_MEMCFG()`, `CVMX_LMCX_ECC_SYND()`, `CVMX_LMCX_FADR()`, and `CVMX_LMCX_NXM()`, dispatch on `cvmx_get_octeon_family()`. They adjust the controller stride for CN68XX versus older families, using `0x1000000` for CN68XX and usually `0x60000000` otherwise. This family switch is the only real executable logic in the header.

## Control Flow
There is no runtime control flow beyond the four inline address helpers. Normal users compute a CSR address with a `CVMX_LMCX_*` macro or helper, read the 64-bit value through the CVMX CSR access functions, interpret or modify fields through the matching `union cvmx_lmcx_*`, and write it back if needed. Initialization code would typically program PLL/DLL and delay values, set memory geometry and timing registers, assert or clear reset/init bits, configure mode-register and ODT behavior, then poll status or interrupt fields such as `init_status`, `pll_status`, `sec_err`, `ded_err`, and training `status` fields.

The union bitfield layout uses `#ifdef __BIG_ENDIAN_BITFIELD` in every meaningful struct. This produces reversed declaration order for little-endian builds while keeping field names stable for callers. The generated layout assumes a compiler and ABI where these 64-bit bitfields match hardware CSR bit numbering under the selected endianness mode.

## State And Persistence
The file itself stores no software state. Its definitions describe persistent hardware state in memory-controller CSRs: memory geometry, rank masks, ECC enable and syndrome state, no-existent-memory write reporting, DDR timing, PLL/DLL configuration, read/write leveling results, ODT masks, counter values, and interrupt enable/pending bits. Writes through these definitions can affect live DRAM availability, refresh, ECC reporting, training margins, and reset behavior until the next hardware reset or reprogramming. Some registers are status or counter-like, while others are configuration latches that must be programmed in a silicon-prescribed sequence by external code.

## Dependencies And Integration Points
The header depends on OCTEON SDK infrastructure for `uint64_t`, `CVMX_ADD_IO_SEG`, `cvmx_get_octeon_family()`, `OCTEON_*` family constants, and `OCTEON_FAMILY_MASK`. It integrates with the MIPS/OCTEON CSR read/write helpers and any kernel subsystems that configure DRAM, handle ECC interrupts, expose memory-controller performance counters, or decode memory errors. Because the source is under `arch/mips/include/asm/octeon`, its consumers are architecture-specific and normally compiled only for Cavium/Marvell OCTEON platforms.

The LMC header also pairs with other generated CSR headers in the same directory. For example, interrupt controller code must route LMC interrupt causes exposed by `CVMX_LMCX_INT` and `CVMX_LMCX_INT_EN`; boot and board code must combine this file's memory geometry/timing with fuse, reset, and clock information from MIO and other OCTEON blocks.

## Risks
The highest risk is ABI drift: a wrong address stride, masked index width, chip-family case, bitfield width, or endian declaration order can write the wrong CSR bit or even the wrong controller instance. That is especially dangerous for `CONFIG`, `CONTROL`, `RESET_CTL`, PLL/DLL, and timing registers because incorrect writes can corrupt memory operation rather than fail cleanly.

The `block_id` macros mask different numbers of bits, usually `& 1` for older two-controller formulas and `& 3` for newer four-controller formulas. Passing an out-of-range block silently wraps; caller-side validation is required when the number of LMC instances differs by chip. The static inline helpers also fall back to the older `0x60000000` stride for unknown families, so adding silicon without updating this file can produce plausible but wrong addresses.

Bitfields over memory-mapped registers are compiler-layout-sensitive. The raw `u64` member is safer for masks in highly portable code, while field access is convenient but must be validated on both endian configurations. Several registers contain chip-revision-specific reserved fields; writing a generic overlay to a revision that reserves those bits may set undefined hardware state.

## Test Signals
Useful validation starts with compile coverage for both big-endian and little-endian MIPS/OCTEON configurations, ensuring all unions and helpers compile without bitfield-size overflow. Address tests can assert known CSR addresses for representative families, especially the CN68XX stride cases in `CVMX_LMCX_DUAL_MEMCFG`, `ECC_SYND`, `FADR`, and `NXM`, plus masked offset behavior for rank/DIMM macros.

Hardware or simulator tests should read stable status registers such as BIST result, counters, and PLL status; verify ECC interrupt mask/cause wiring; and exercise read/write leveling status fields during memory bring-up. Regression tests for generated headers should diff register names, address constants, family overlays, and reserved-bit widths against the vendor CSR database or a known-good SDK version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-lmcx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-mio-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-mio-defs.h

## Purpose
`cvmx-mio-defs.h` is a generated OCTEON SDK CSR-definition header for the MIO block, a broad miscellaneous I/O register bank. It exposes address macros and 64-bit register overlays for boot-bus/NAND access, boot DMA, eMMC/MMC control, efuse data and programming, PLL and GPIO compensation, PTP timekeeping, QLM configuration, reset and PCIe reset signaling, TWSI/I2C software access, and UART registers. It is a low-level hardware ABI header, not an implementation of those device drivers.

## Important APIs, Types, And Functions
The top-level `CVMX_MIO_*` macros compute CSR addresses through `CVMX_ADD_IO_SEG`. Major address groups include `CVMX_MIO_BOOT_*` for boot bus, chip-select timing, local boot window, and boot DMA; `CVMX_MIO_EMM_*` for eMMC command, DMA, response, status, mode, switch, buffer, and interrupt handling; `CVMX_MIO_FUS_*` for fuse read/program/timing/repair/result state; `CVMX_MIO_PTP_*` for PTP clock, timestamp, event count, 1PPS, and clock-output threshold/increment registers; `CVMX_MIO_RST_*` for reset straps, BIST clearing, reset delays, link reset control, PERST and reset interrupts; `CVMX_MIO_TWSX_*` for two TWSI controllers; and `CVMX_MIO_UARTX_*` plus `CVMX_MIO_UART2_*` for DesignWare-style UART register access.

Each register has a matching `union cvmx_mio_*` with raw `u64` access and endian-adjusted bitfield struct `s`. Many unions contain family-specific layouts. Boot registers vary across CN30XX, CN38XX, CN50XX, CN52XX, CN56XX, CN61XX, CN63XX, CN66XX, and CN68XX. Fuse registers carry the broadest family matrix, including CN70XX, CN73XX, CN78XX, CN78XX pass 2, and CNF75XX overlays. PTP, QLM, reset, and TWSI definitions also include selected chip-family specializations.

Important register unions include `cvmx_mio_boot_reg_cfgx` and `cvmx_mio_boot_reg_timx` for boot-bus address/timing windows; `cvmx_mio_boot_dma_cfgx`, `cvmx_mio_boot_dma_intx`, and `cvmx_mio_ndf_dma_cfg` for DMA descriptors and completion interrupts; `cvmx_mio_emm_cmd`, `cvmx_mio_emm_dma`, `cvmx_mio_emm_rsp_sts`, and `cvmx_mio_emm_int` for MMC command/DMA lifecycle; `cvmx_mio_fus_dat2` and `cvmx_mio_fus_dat3` for feature-disable, chip ID, power, PLL, cache, and accelerator fuse state; `cvmx_mio_ptp_clock_cfg` and companion clock/increment/threshold unions for timekeeping; `cvmx_mio_rst_boot`, `cvmx_mio_rst_ctlx`, and `cvmx_mio_rst_cntlx` for boot straps and PCIe/QLM reset control; and the UART line/fifo/status unions such as `cvmx_mio_uartx_lcr`, `lsr`, `ier`, `iir`, `mcr`, `msr`, `rbr`, and `thr`.

## Control Flow
There are no functions and no dynamic control flow in this header. Consumers select an address macro, use a CVMX CSR read/write primitive, and interpret the returned 64-bit value using the matching union. Typical flows are implemented externally: boot code configures boot chip-select timing before accessing flash/NAND; eMMC drivers issue `EMM_CMD` or `EMM_DMA` and poll or handle `EMM_INT`/`EMM_RSP_STS`; fuse code unlocks and times efuse reads or programming; PTP code enables `PTP_CLOCK_CFG` and maintains clock compensation and event/timestamp registers; reset/PCIe code drives link reset bits and watches `rst_done` or interrupt bits; UART drivers program divisor and FIFO/line-control registers and read line status or data registers.

Every bitfield struct uses the `__BIG_ENDIAN_BITFIELD` pattern to keep field names semantically consistent while reversing declaration order. UART2 definitions intentionally duplicate the UARTX register shape for a fixed third UART address range rather than using an `offset` macro.

## State And Persistence
The header has no software-owned persistent data. It describes hardware state that can be persistent within the running SoC: boot-bus mappings, DMA enable/clear bits, eMMC command and response state, interrupt pending and enable bits, efuse contents and programming controls, reset straps, clock/time counters, and UART FIFO/status state. Fuse fields are especially persistent because they reflect or can program one-time hardware configuration. Reset and boot fields may be latched at reset and should not be treated as ordinary mutable software state without consulting the hardware manual.

Writes to `MIO_FUS_*` programming and unlock registers can have irreversible hardware effects on real devices. Writes to reset, PLL, boot, and QLM configuration can disrupt boot media, PCIe/SerDes links, clocks, or debug access. The definitions make those writes syntactically easy; safe sequencing and policy live in the external platform code.

## Dependencies And Integration Points
The file depends on `uint64_t`, `CVMX_ADD_IO_SEG`, `__BIG_ENDIAN_BITFIELD`, and the OCTEON CSR access environment. It is consumed by MIPS/OCTEON boot code, platform setup, flash/NAND/boot-bus drivers, MMC/eMMC support, efuse and feature-detection logic, PTP or network timestamping code, reset/PCIe/QLM management, I2C/TWSI support, and serial/UART support.

Integration is intentionally flat: the header only names addresses and bitfields. Higher-level code must know which chip family is present and choose the correct family overlay when generic `s` does not match the silicon. The fuse overlays provide feature availability signals that other blocks depend on, such as disabled cores, crypto/ZIP/DFA/HNA availability, power limits, chip ID, PLL configuration, and platform strap details.

## Risks
The primary risks are incorrect register interpretation, irreversible fuse writes, and accidental reset/clock disruption. The MIO block spans many unrelated devices, so a broad include can tempt code to manipulate sensitive CSRs outside its subsystem. Register fields often differ by chip family and pass; using the generic `s` overlay where a `cn*` overlay is required can misread reserved bits as capabilities or program bits that do not exist on that chip.

Address macros with `offset` parameters mask indexes, for example boot DMA channel `& 3`, boot register `& 7`, TWSI controller `& 1`, QLM `& 7`, UARTX `& 1`, and reset control indexes. Out-of-range indexes silently wrap to another hardware instance. Tests and callers need explicit instance-count validation outside this header.

The UART register model is 64-bit CSR-wrapped around mostly 8-bit UART semantics. Code that assumes byte-addressable 16550 registers without the CVMX CSR accessor can use the wrong access width or address. PTP clock registers split fractional and integer nanosecond fields across high/low and increment/threshold registers; update ordering is driver responsibility and not encoded here.

## Test Signals
Compile tests should cover all MIPS/OCTEON endian configurations and ensure the generated union bit widths sum to 64 bits. Address tests should assert the known constants and offset strides for boot DMA, boot chip selects, eMMC modes, fuse bank data, QLM configuration, reset control arrays, TWSI controllers, UARTX, and fixed UART2.

Subsystem tests should exercise safe read-only paths first: fuse data decode, reset strap decode, boot BIST status, PTP counter reads, UART line status reads, and TWSI interrupt status. Driver-level tests can validate eMMC command completion and error bits, boot/NAND DMA completion interrupts, UART FIFO status transitions, PTP event/timestamp updates, and reset/link interrupt masks. For efuse programming definitions, validation should use simulation, read-only hardware, or explicit board-lab procedures rather than generic automated writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-mio-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-mixx-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-mixx-defs.h

## Purpose
`cvmx-mixx-defs.h` is a generated OCTEON SDK CSR-definition header for the MIXX management-interface blocks. It defines addresses and 64-bit overlays for two MIXX instances, including input/output rings, ring counters and high-water marks, interrupt cause/enable bits, BIST status, timestamp control, and timestamp data. The header gives management Ethernet or management I/O code a stable way to configure ring memory and monitor MIXX hardware state.

## Important APIs, Types, And Functions
The address macros are `CVMX_MIXX_BIST`, `CVMX_MIXX_CTL`, `CVMX_MIXX_INTENA`, `CVMX_MIXX_IRCNT`, `CVMX_MIXX_IRHWM`, `CVMX_MIXX_IRING1`, `CVMX_MIXX_IRING2`, `CVMX_MIXX_ISR`, `CVMX_MIXX_ORCNT`, `CVMX_MIXX_ORHWM`, `CVMX_MIXX_ORING1`, `CVMX_MIXX_ORING2`, `CVMX_MIXX_REMCNT`, `CVMX_MIXX_TSCTL`, and `CVMX_MIXX_TSTAMP`. Each takes `offset` and maps it to one of two hardware instances with `((offset) & 1) * 2048`.

The union overlays include `cvmx_mixx_bist` for RAM self-test status, `cvmx_mixx_ctl` for enable/reset/busy/endian/arbitration/CRC strip/timestamp threshold controls, `cvmx_mixx_intena` and `cvmx_mixx_isr` for interrupt masks and causes, `cvmx_mixx_iring1`/`iring2` and `oring1`/`oring2` for ring base, size, doorbell, and tail-pointer state, `cvmx_mixx_ircnt`/`orcnt` and `irhwm`/`orhwm` for occupancy and high-water marks, `cvmx_mixx_remcnt` for remaining input/output counts, and `cvmx_mixx_tsctl`/`tstamp` for timestamp availability/timeout/count and timestamp value.

Several unions contain a `cn52xx` overlay. Those variants reduce available fields or base-address width compared with the generic layout, such as 33-bit ring bases instead of 37-bit bases and missing timestamp interrupt/threshold fields. All unions provide `u64` raw access and endian-aware bitfields under `__BIG_ENDIAN_BITFIELD`.

## Control Flow
The header has no functions and no internal control flow. External MIXX setup code computes per-instance CSR addresses, programs ring bases and sizes in `IRING1` and `ORING1`, initializes doorbell and tail-pointer registers in `IRING2` and `ORING2`, configures high-water marks and interrupts, clears or observes BIST status, then enables the block through `CTL.en` while polling `CTL.busy` or interrupt/status fields.

Operational control is ring-driven: software and hardware exchange producer/consumer state through doorbell, tail-pointer, count, and high-water registers. Interrupt handlers read `ISR`, check overflow, threshold, underrun, data-drop, and timestamp bits, service the rings, and use `INTENA` to mask or unmask those events. Timestamp handling reads or configures `TSCTL` and consumes `TSTAMP` when timestamp availability signals are raised.

## State And Persistence
No C state is stored in the file. The described hardware state includes ring base addresses, ring sizes, doorbell counters, tail pointers, occupancy counters, interrupt pending and enable bits, reset/enable/busy status, and timestamp counters. Those CSRs persist until software reprograms them or the block/SoC resets. Ring base fields point to external memory owned by the MIXX driver; this header only defines the CSR bit layout for those pointers and sizes.

## Dependencies And Integration Points
The header depends on OCTEON CSR infrastructure for `CVMX_ADD_IO_SEG`, `uint64_t`, and endian bitfield selection. It integrates with the management interface driver and interrupt handling code for OCTEON chips that expose MIXX blocks. Because ring setup includes physical base addresses, consumers must also integrate with DMA-safe memory allocation, cache coherency rules, and any OCTEON-specific ordering barriers required around CSR writes and ring memory updates.

The MIXX interrupt cause and enable bits are expected to connect to the platform interrupt controller outside this file. The timestamp fields may integrate with network time stamping or management-port receive metadata depending on the driver design.

## Risks
The `offset` parameter silently wraps with `& 1`, so using instance 2 or higher aliases instance 0 or 1. Ring base fields differ between generic and CN52XX layouts; using the wrong overlay can truncate DMA addresses or set reserved bits. Endian selection matters for every bitfield. Code that writes individual fields must ensure the raw `u64` value preserves reserved bits where the hardware requires read-modify-write behavior.

Ring registers are concurrency-sensitive. Incorrect ordering between memory ring updates, doorbell writes, and interrupt acknowledgement can cause dropped data, false underrun/overrun interrupts, or stuck busy state. The header exposes status bits such as `data_drp`, `irun`, `orun`, `idblovf`, and `odblovf`, but policy for clearing and recovery must be implemented by the caller.

## Test Signals
Compile tests should verify both generic and CN52XX overlays build and remain 64-bit. Address tests should assert the 2048-byte per-instance stride and wrapping behavior. Driver tests should program minimal input and output rings, verify base/size encoding, ring count changes, doorbell/tail-pointer behavior, and high-water interrupt generation. Fault-injection tests should cover overflow, underrun, data-drop, BIST status interpretation, reset/enable transitions, and timestamp availability through `TSCTL` and `TSTAMP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-mixx-defs.h -->
