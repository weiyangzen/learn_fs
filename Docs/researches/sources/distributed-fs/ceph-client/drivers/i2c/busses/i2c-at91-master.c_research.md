# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-master.c

## Purpose
Master-mode AT91 TWI implementation. It calculates bus timing, drives CPU and DMA transfers, handles RX/TX interrupts, supports limited repeated-start transactions through the internal address feature, configures optional FIFO/filter/alternative-command features, and wires bus recovery.

## APIs, Control Flow, and State
`at91_twi_probe_master()` installs `atmel_twi_interrupt()`, optionally configures DMA channels, reads `atmel,fifo-size`, filter properties, computes `twi_cwgr_reg`, and assigns `at91_twi_algorithm` plus quirks. `at91_twi_xfer()` accepts normal I2C messages, folds a two-message write-then-read/write sequence into `IADR`/`IADRSZ`, enables alternative command mode for short transfers, chooses DMA-safe buffers, and calls `at91_do_twi_transfer()`. The transfer routine clears stale status, resets FIFO thresholds, starts quick/read/write paths, waits on `cmd_complete`, maps hardware status to errno, cleans DMA, unlocks/flushes TX, and invokes `i2c_recover_bus()` on errors. ISR ordering intentionally drains RXRDY before TXCOMP/NACK to avoid stale RHR data; NACK/TXCOMP complete the transaction, while TXRDY feeds CPU writes. DMA callbacks unmap buffers and defer TXCOMP/STOP sequencing.

## Dependencies and Integration
Depends on DMAEngine, DMA mapping, I2C core quirks, runtime PM from the core file, GPIO/pinctrl recovery support, firmware timing parsing, and AT91 register definitions. It advertises `I2C_FUNC_I2C`, SMBus emulation, and SMBus block read.

## Risks and Test Signals
Highest risk is hardware-ordering drift around TXCOMP/NACK/LOCK, DMA callback races, last-byte read STOP timing, SMBus block length aborts, and CLEAR-vs-GPIO recovery selection. Test CPU and DMA reads/writes around the 8-byte threshold, short alt-command transfers, FIFO aligned/unaligned buffers, EEPROM NACKs, zero-length quick commands, combined messages with 1-3 byte internal addresses, stuck SDA recovery, filters from DT timings, and suspend/resume with active autosuspend.
