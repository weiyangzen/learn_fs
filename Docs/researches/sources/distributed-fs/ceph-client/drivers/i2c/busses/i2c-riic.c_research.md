# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-riic.c

Purpose: Renesas RIIC platform driver. It exposes a full I2C/SMBus-emulation adapter for RIIC variants with different register layouts and interrupt mappings, including fast-mode-plus capable RZ devices and alternate RZ/T2H interrupt aggregation.

Important APIs/types/functions: `struct riic_dev` stores MMIO base, current buffer/message, byte counter, completion, timing data, clock, reset, and variant info. `struct riic_of_data` supplies register-offset tables, IRQ descriptors, IRQ count, and fast-mode-plus capability. The algorithm is `riic_algo` with `riic_xfer()` and `riic_func()`. State-machine interrupts are `riic_tdre_isr()`, `riic_tend_isr()`, `riic_rdrf_isr()`, `riic_stop_isr()`, and `riic_eei_isr()`. Hardware setup and integration are in `riic_init_hw()`, `riic_i2c_probe()`, remove, and PM callbacks.

Control flow: `riic_xfer()` resumes runtime PM, verifies bus free through `riic_bus_barrier()`, clears status, then processes messages in order. Each message starts with TIE enabled and a START or repeated START. `riic_tdre_isr()` writes the address first, then either switches to receive interrupt for reads or streams write bytes until it enables TEIE. `riic_rdrf_isr()` performs the dummy read for reads, controls ACKBT before the last byte, and issues STOP for final reads. `riic_tend_isr()` handles NACK and write completion, either completing for repeated-start continuation or enabling stop interrupt and generating STOP. `riic_stop_isr()` clears status/interrupt enable and completes the message.

State and persistence: `bytes_left == RIIC_INIT_MSG` marks address phase. `err`, `is_last`, `buf`, and `msg` track active transfer state; `msg_done` bridges IRQ completion to the transfer caller. Runtime PM uses autosuspend delay zero by default. Reset is optional and deasserted for operation, asserted during suspend_noirq after disabling output.

Dependencies/integration: I2C core, OF match data, runtime PM, reset controller, firmware timing parser, `i2c_generic_scl_recovery`, platform IRQ resources, and byte-wide MMIO. Register maps are abstracted by indexed offsets, allowing RZ/A-style and RZ/V2H-style layouts.

Risks: transfer correctness depends on IRQ ordering and on using RDRFS/ACKBT for every received byte to avoid races. `riic_init_hw()` timing math must account for rise/fall times and 5-bit BRL/BRH bounds. Suspend/resume deliberately wakes the controller before late suspend because some devices need noirq I2C access. Error paths rely on ACPI-like package-independent IRQ clearing reads to ensure register writes propagate.

Test signals: verify quick/zero-length write behavior, read lengths of 1 and multiple bytes, NACK path through NAKIE/EEI, repeated starts across multi-message transfers, bus recovery when BBSY or pins are stuck low, FMP timing rejection/enablement, RZ/T2H EEI dispatch, runtime autosuspend, and suspend_noirq/resume_noirq reset restoration.
