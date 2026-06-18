# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/s5p_cec.h

## Purpose
This header defines the Samsung S5P CEC driver state, status-bit meanings, buffer sizing, and TX/RX state enum.

## Important APIs, Types, and Functions
Key definitions are `CEC_STATUS_TX_*`, `CEC_STATUS_RX_*`, `CEC_RX_BUFF_SIZE`, `CEC_TX_BUFF_SIZE`, `enum cec_state`, and `struct s5p_cec_dev`. The state structure contains the CEC adapter, clock, device, mutex, PMU regmap, notifier, IRQ, MMIO base, RX/TX state, and current RX message.

## Control Flow
The status bits are produced by `s5p_cec_get_status` and consumed by `s5p_cec_irq_handler`. The state enum gates threaded IRQ reporting through `cec_transmit_done` and `cec_received_msg`.

## State and Persistence
This file defines volatile driver state only. `rx`, `tx`, and `msg` are transient interrupt-processing state; hardware and runtime PM own actual device state.

## Dependencies and Integration Points
The header includes Linux platform, clock, interrupt, runtime PM, media CEC, and the local low-level headers. It is private to the S5P driver build.

## Risks and Test Signals
The header includes itself indirectly through `exynos_hdmi_cec.h`, relying on guards. Status-bit definitions must match how `exynos_hdmi_cecctrl.c` packs hardware registers. Compile tests and IRQ status mapping tests are the main signals.
