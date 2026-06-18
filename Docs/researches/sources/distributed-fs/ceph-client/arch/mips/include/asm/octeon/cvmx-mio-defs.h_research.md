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
