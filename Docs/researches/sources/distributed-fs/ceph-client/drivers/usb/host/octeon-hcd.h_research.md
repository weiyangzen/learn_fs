# sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.h

## Purpose
`octeon-hcd.h` is the hardware register map for the OCTEON USB host driver. It defines the USBC and USBN MMIO address macros plus C bitfield unions used by `octeon-hcd.c` to configure clocks, PHY mode, FIFOs, interrupts, host channels, split transactions, frame timing, port state, DMA-related behavior, and PHY control/status.

## Important APIs, types, and functions
The header exports no callable functions; its API is a set of address macros and typed register layouts. `CVMX_USBCXBASE`, `CVMX_USBCXREG1()`, and `CVMX_USBCXREG2()` derive USBC register addresses by block id and channel offset. `CVMX_USBNXREG1()` and `CVMX_USBNXREG2()` derive USBN control and DMA pointer addresses. Named register macros include global/core registers such as `CVMX_USBCX_GAHBCFG`, `GINTMSK`, `GINTSTS`, `GUSBCFG`, `GRSTCTL`, FIFO registers, host-channel registers such as `HCCHARX`, `HCINTX`, `HCINTMSKX`, `HCSPLTX`, `HCTSIZX`, frame/port registers, and USBN `CLK_CTL`, `DMA0_INB_CHN0`, `DMA0_OUTB_CHN0`, and `USBP_CTL_STATUS`.

Register unions include `cvmx_usbcx_gahbcfg`, `cvmx_usbcx_ghwcfg3`, `cvmx_usbcx_gintmsk`, `cvmx_usbcx_gintsts`, `cvmx_usbcx_gnptxfsiz`, `cvmx_usbcx_gnptxsts`, `cvmx_usbcx_grstctl`, `cvmx_usbcx_grxfsiz`, `cvmx_usbcx_grxstsph`, `cvmx_usbcx_gusbcfg`, `cvmx_usbcx_haint`, `cvmx_usbcx_haintmsk`, `cvmx_usbcx_hccharx`, `cvmx_usbcx_hcfg`, `cvmx_usbcx_hcintx`, `cvmx_usbcx_hcintmskx`, `cvmx_usbcx_hcspltx`, `cvmx_usbcx_hctsizx`, `cvmx_usbcx_hfir`, `cvmx_usbcx_hfnum`, `cvmx_usbcx_hprt`, `cvmx_usbcx_hptxfsiz`, `cvmx_usbcx_hptxsts`, `cvmx_usbnx_clk_ctl`, and `cvmx_usbnx_usbp_ctl_status`.

## Control flow
This header does not execute control flow, but it directly shapes the control flow in `octeon-hcd.c`. Initialization writes `cvmx_usbnx_clk_ctl` and `cvmx_usbnx_usbp_ctl_status` to bring the PHY/core out of reset, programs `cvmx_usbcx_gahbcfg`, `cvmx_usbcx_gusbcfg`, `cvmx_usbcx_gintmsk`, `cvmx_usbcx_hcfg`, and FIFO sizing registers, and then uses host-channel unions for per-transfer setup. Interrupt control flow reads `cvmx_usbcx_gintsts`, `cvmx_usbcx_haint`, and `cvmx_usbcx_hcintx`; transfer accounting reads `cvmx_usbcx_hctsizx` and `cvmx_usbcx_hccharx`; root-hub behavior reads and writes `cvmx_usbcx_hprt`.

## State and persistence behavior
The unions are transient views over MMIO register values. They do not store persistent software state; persistence lives in hardware registers and the driver state in `octeon-hcd.c`. The `__BITFIELD_FIELD` layout is architecture-sensitive and represents the on-chip bit order expected by OCTEON. Address macros are deterministic from block id and channel id.

## Dependencies and integration points
The header depends on `<asm/bitfield.h>` for bitfield declarations and on OCTEON address translation through `CVMX_ADD_IO_SEG`, which is supplied elsewhere in the OCTEON platform headers. Its sole in-tree consumer in this work item is `octeon-hcd.c`, but the register names mirror the OCTEON USB core documentation and the DWC OTG-style host register model.

## Risks and edge cases
The main risks are bitfield layout correctness, 32-bit versus 64-bit register access width, block-id address selection, and channel offset calculations. A single incorrect field width or reserved-bit placement can cause writes to affect unrelated hardware controls. Several comments document fields that must only change during reset or before normal operation; driver changes must preserve those sequencing constraints. Endianness-related fields such as `usbc_end` and the C bitfield ordering make cross-architecture reuse unsafe without platform validation.

## Test signals
Compilation of `octeon-hcd.c` is the first signal because all field names are exercised through these unions. Runtime signals include successful PHY/core reset, valid FIFO depth reads from `GHWCFG3`, correct interrupt masks, working host-channel interrupts, correct port-speed reporting from `HPRT`, and stable DMA pointer behavior through USBN DMA registers. Hardware register dump comparison against vendor documentation is the most direct validation for address and field layout changes.
