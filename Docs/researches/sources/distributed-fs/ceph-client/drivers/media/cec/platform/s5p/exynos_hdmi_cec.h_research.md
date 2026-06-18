# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/exynos_hdmi_cec.h

## Purpose
This header declares the low-level Samsung Exynos HDMI CEC helper API used by the S5P CEC framework driver.

## Important APIs, Types, and Functions
It includes `s5p_cec.h` and declares helpers for divider setup, RX enable, TX/RX interrupt masking, full/TX/RX reset, RX filter threshold setup, TX packet copy/start, logical address programming, status reading, pending interrupt clearing, and RX buffer extraction.

## Control Flow
The header provides the call contract from `s5p_cec.c` into `exynos_hdmi_cecctrl.c`. Adapter enable calls reset, divider, threshold, unmask, and RX enable helpers; transmit calls `s5p_cec_copy_packet`; IRQ paths call status, clear-pending, reset, and RX buffer helpers.

## State and Persistence
It does not define storage. All state is passed through `struct s5p_cec_dev *cec`, which carries MMIO base, PMU regmap, CEC adapter, and TX/RX state.

## Dependencies and Integration Points
The header depends on Linux regmap through the implementation and on local `s5p_cec.h`/`regs-cec.h` definitions. It is a private in-directory interface, not a global kernel API.

## Risks and Test Signals
The include cycle with `s5p_cec.h` is unusual but works through include guards. Prototype changes must be kept synchronized with `exynos_hdmi_cecctrl.c`; compile testing is the primary signal.
