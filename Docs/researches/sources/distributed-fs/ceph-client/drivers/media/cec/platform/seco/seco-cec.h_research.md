# sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.h

## Purpose
This header defines SECO CEC microcontroller registers, SMBus I/O-port constants, status bits, enable bits, firmware requirement, and IR bit layout.

## Important APIs, Types, and Functions
There are no functions. Key constants include `SECOCEC_MICRO_ADDRESS`, `SECOCEC_VERSION`, `SECOCEC_ENABLE_REG_1`, `SECOCEC_STATUS`, read/write CEC data register ranges, `SECOCEC_IR_READ_DATA`, and masks for CEC RX/TX status and IR RC5 fields.

## Control Flow
`seco-cec.c` uses these constants for SMBus word reads/writes in adapter enable, logical address setting, transmit, receive, IRQ, IR, suspend, resume, and probe firmware validation.

## State and Persistence
The header maps microcontroller state and Braswell host status/control registers. Runtime persistence is in the external controller, not the Linux driver.

## Dependencies and Integration Points
The I/O-port constants target the Braswell SMBus host controller. The register map represents the STM32-based SECO microcontroller protocol used by the platform driver.

## Risks and Test Signals
`SECOCEC_STATUS_REG_1_IR_PASSTHR` references a misspelled/undefined macro-like name and should be compile-checked if used. Hardware tests should confirm register definitions against firmware documentation, especially status clearing masks and data word ordering.
