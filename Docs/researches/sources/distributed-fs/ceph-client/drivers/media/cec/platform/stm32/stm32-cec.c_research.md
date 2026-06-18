# sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/stm32-cec.c

## Purpose
This is the STMicroelectronics STM32 CEC controller driver. It registers a CEC adapter over a small regmap-backed MMIO block and streams TX/RX bytes through data registers under interrupt control.

## Important APIs, Types, and Functions
`struct stm32_cec` stores adapter, device, CEC and HDMI-CEC clocks, reset pointer, regmap, IRQ status, RX/TX messages, and TX byte index. Important functions are `cec_hw_init`, `stm32_tx_done`, `stm32_rx_done`, `stm32_cec_adap_enable`, `stm32_cec_adap_log_addr`, and `stm32_cec_adap_transmit`.

## Control Flow
Probe maps MMIO through `devm_regmap_init_mmio_clk`, requests a threaded IRQ, prepares the `cec` and optional `hdmi-cec` clocks, allocates/registers a CEC adapter with physical-address capability, initializes hardware, and stores drvdata. Enable turns on clocks and `CECEN`; disable turns them off. Transmit copies the message, sets `TXEOM` for one-byte messages, starts TX with `TXSOM`, and writes the header. IRQ snapshots/clears status; the thread writes additional bytes on `TXBR`, reports completion/error, collects RX bytes on `RXBR`, and reports on `RXEND`.

## State and Persistence
Driver state includes current TX message/count and current RX message. Logical addresses live in `CEC_CFGR.OAR`, and the controller is temporarily disabled while the address field is updated. No persistent storage is used.

## Dependencies and Integration Points
DT compatible is `st,stm32-cec`. The driver depends on regmap, clock framework, platform IRQ/MMIO, and CEC core. It currently does not use a notifier and therefore keeps `CEC_CAP_PHYS_ADDR` for userspace physical address control.

## Risks and Test Signals
`stm32_cec_adap_log_addr` ignores the return value of `regmap_read_poll_timeout`, so timeout behavior deserves review. RX length is incremented without an explicit `CEC_MAX_MSG_SIZE` guard. Test one-byte TX, multi-byte TXBR sequencing, TX error/NACK/arbitration mapping, RX overflow reset, logical address update during busy TX, optional clock absence, and remove cleanup.
