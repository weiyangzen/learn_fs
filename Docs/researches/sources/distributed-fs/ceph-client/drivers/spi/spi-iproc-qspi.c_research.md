# sources/distributed-fs/ceph-client/drivers/spi/spi-iproc-qspi.c

## Purpose

`spi-iproc-qspi.c` is the Broadcom iProc integration layer for the shared Broadcom QSPI controller. It adapts iProc-specific level-2 interrupt registers to the common `spi-bcm-qspi` core by providing interrupt status, acknowledge, and mask callbacks, then delegates probing/removal and PM to the common core.

## Important APIs, Types, and Functions

`struct bcm_iproc_intc` wraps `struct bcm_qspi_soc_intc` with platform device, interrupt mask/status MMIO windows, a spinlock, and endian flag. The callback implementations are `bcm_iproc_qspi_get_l2_int_status()`, `bcm_iproc_qspi_int_ack()`, and `bcm_iproc_qspi_int_set()`. `bcm_iproc_probe()` allocates the wrapper, maps named resources, detects big-endian mode, initializes and disables interrupts, installs callbacks, and calls `bcm_qspi_probe()`.

## Control Flow

On probe, the driver maps `intr_regs` and `intr_status_reg`, acknowledges pending MSPI/BSPI done bits, masks done interrupts, fills the common interrupt callback table, and hands control to the shared Broadcom QSPI probe. The status callback reads seven status registers and translates raw bit positions into common `MSPI_DONE`, `BSPI_DONE`, and `BSPI_ERR` flags. Ack writes `1` to each status register selected by a common interrupt mask. Set updates the iProc interrupt-enable register under a spinlock, shifting the common mask by `INTR_BASE_BIT_SHIFT`.

## State and Persistence Behavior

State is volatile interrupt-controller adapter state. The QSPI flash/device state is owned by `spi-bcm-qspi`. Interrupt mask bits persist in hardware while the device is active and are modified by common-core calls.

## Dependencies and Integration Points

The driver depends on OF compatibles `brcm,spi-nsp-qspi` and `brcm,spi-ns2-qspi`, named platform MMIO resources, endian-aware Broadcom QSPI accessors, common interrupt masks from `spi-bcm-qspi.h`, and the shared `bcm_qspi_probe/remove/pm_ops`.

## Risks and Edge Cases

Correct named resources are mandatory. Interrupt translation depends on the common mask definitions matching the seven iProc status registers. The mask update is locked, but status/ack loops are not; this matches typical interrupt-controller usage but should be validated under high IRQ load. Big-endian access must match DT, or interrupt bits will be misread.

## Test Signals

Test both compatibles, big- and little-endian MMIO access, missing named resources, pending IRQ ack at probe, interrupt enable/disable races, MSPI done, BSPI done, BSPI error status translation, and integration smoke tests through the common Broadcom QSPI flash read/write paths.
