# sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/tegra_cec.h

## Purpose
This private header defines Tegra CEC register offsets, hardware-control bits, TX/RX register bit layouts, timing field shifts, interrupt status/mask bits, and debug register fields.

## Important APIs, Types, and Functions
There are no functions. Key definitions include `TEGRA_CEC_HW_CONTROL`, `TEGRA_CEC_TX_REGISTER`, `TEGRA_CEC_RX_REGISTER`, timing registers, `TEGRA_CEC_INT_STAT/MASK`, `TEGRA_CEC_HWCTRL_RX_LADDR`, `TEGRA_CEC_HWCTRL_RX_SNOOP`, TX start/EOM/retry/broadcast bits, and interrupt flags.

## Control Flow
`tegra_cec.c` uses the constants to program timing during enable, encode each transmitted byte, detect RX EOM, mask/unmask interrupts, and recover from TX failures.

## State and Persistence
The file describes hardware state only. Runtime values are in MMIO registers and driver buffers.

## Dependencies and Integration Points
It is consumed by the Tegra CEC platform driver and must match Tegra114/124/210 hardware documentation.

## Risks and Test Signals
Incorrect shift constants would corrupt timing configuration, which can look like flaky CEC signaling. Hardware register tests should validate bitfield encodings for logical-address masks, snoop mode, TX byte flags, RX EOM, and interrupt masks.
