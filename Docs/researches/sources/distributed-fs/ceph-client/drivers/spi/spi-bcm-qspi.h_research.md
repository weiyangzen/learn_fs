# sources/distributed-fs/ceph-client/drivers/spi/spi-bcm-qspi.h

## Purpose
Declares the shared interface and interrupt definitions used by the Broadcom QSPI common driver and its SoC-specific wrappers. It provides interrupt mask constants, the SoC interrupt-controller callback structure, endian-aware MMIO helpers, and exported common probe/remove/PM declarations.

## Important APIs, Types, And Functions
`struct bcm_qspi_soc_intc` is the wrapper-facing adapter for SoC interrupt integration, with callbacks to acknowledge interrupt groups, enable/disable groups, and read muxed status. Interrupt group constants identify `MSPI_DONE`, `BSPI_DONE`, `BSPI_ERR`, and combined `MSPI_BSPI_DONE`. `get_qspi_mask()` maps those logical groups to hardware interrupt masks. `bcm_qspi_readl()` and `bcm_qspi_writel()` choose big-endian or relaxed little-endian access. The file declares `bcm_qspi_probe()`, `bcm_qspi_remove()`, and `bcm_qspi_pm_ops`.

## Control Flow
The header has no independent runtime flow. It supports flow in `spi-bcm-qspi.c` by letting wrapper drivers pass a `bcm_qspi_soc_intc`, allowing the common L1 ISR to read SoC status, dispatch to MSPI/BSPI handlers, acknowledge events, and mask/unmask BSPI completion/error sources.

## State And Persistence
The header defines no storage except callback contracts. Persistent state is supplied by wrapper-specific implementations of `struct bcm_qspi_soc_intc` and by the common driver’s `struct bcm_qspi`, which stores the pointer passed to `bcm_qspi_probe()`.

## Dependencies And Integration Points
It depends on Linux `types.h` and `io.h`, plus forward declarations for `platform_device` and `dev_pm_ops`. It is included by the common QSPI core and wrappers such as `spi-brcmstb-qspi.c`. The endian helpers integrate with device-tree `big-endian` selection in the common driver.

## Risks And Edge Cases
Incorrect interrupt mask mapping can cause lost completions or unhandled BSPI errors. Wrappers passing a partially implemented `bcm_qspi_soc_intc` can make muxed IRQ handling fail at runtime. Endian access helpers centralize byte order, so any future register that requires different access width or ordering should not blindly use these helpers.

## Test Signals
Validation comes from wrapper probe success, correct interrupt dispatch in both muxed and non-muxed IRQ modes, BSPI error handling, and big-endian platform smoke tests. Static checks should confirm every logical interrupt group used by wrappers is represented in `get_qspi_mask()`.
