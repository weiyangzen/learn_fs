# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cecctrl.c

## Purpose
This file implements low-level register access for the Samsung S5P/Exynos HDMI CEC hardware. It handles clock divider programming, reset, interrupt masking, transmit buffer setup, logical address programming, status aggregation, and RX buffer reads.

## Important APIs, Types, and Functions
The public helper functions are declared in `exynos_hdmi_cec.h`. `s5p_cec_set_divider` programs the HDMI PHY PMU divider through `cec->pmu` and local CEC divisor registers. `s5p_cec_copy_packet` writes TX bytes at 4-byte-spaced registers, sets byte count, retry count, start bit, and broadcast mode. `s5p_cec_get_status` folds multiple 8-bit status registers into a 32-bit driver status word.

## Control Flow
Adapter enable calls divider setup, threshold setup, interrupt unmasking, and RX enable. Transmit writes the packet and starts hardware. IRQ handling reads status through `s5p_cec_get_status`, clears TX/RX pending bits with `s5p_clr_pending_tx/rx`, and for successful RX reads bytes using `s5p_cec_get_rx_buf`.

## State and Persistence
State lives in hardware registers. The PMU register `EXYNOS_HDMI_PHY_CONTROL` stores divider bits; CEC registers hold logical address, filter threshold, TX/RX control, IRQ masks, status, and buffers. No persistent storage is written.

## Dependencies and Integration Points
The implementation depends on local register offsets in `regs-cec.h`, `struct s5p_cec_dev` in `s5p_cec.h`, `regmap` for PMU syscon access, and byte MMIO accessors.

## Risks and Test Signals
`s5p_cec_get_rx_buf` uses a fixed 40-byte debug buffer and `sprintf` while reading up to 16 bytes, which is tight but fits the formatted data. The divider code uses floating literal arithmetic (`CEC_DIV_RATIO * 0.00005`) in C, yielding a small divisor value; clock validation is important. Test reset, RX filter threshold, broadcast vs directed TX, retry encoding, status-bit mapping, and PMU access failure logging.
