# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-bcm-iproc.c

## Purpose
Broadcom iProc SMBus/I2C controller driver with master support, optional slave support, IRQ or polling completion, NIC indirect-access handling, and sleep PM reinitialization.

## APIs, Control Flow, and State
`struct bcm_iproc_i2c_dev` stores direct or IDM-mediated MMIO, adapter, speed, completion, current message, FIFO counters, slave state, tasklet, and interrupt masks. `iproc_i2c_rd_reg()`/`wr_reg()` optionally serialize indirect NIC access through `idm_lock` and `ape_addr_mask`. Master flow initializes/reset FIFOs with `bcm_iproc_i2c_init()`, formats address/data into TX FIFO in `bcm_iproc_i2c_xfer_internal()`, supports a two-message write-then-read process call, dynamically sets RX thresholds, and waits in IRQ or polling mode through `bcm_iproc_i2c_xfer_wait()`. Status codes map lost arbitration, NACK, timeout, underrun, and RX full to Linux errno. Slave flow programs address slot 3, handles RX FIFO data in a tasklet, and services TX underruns to feed read data to an external master.

## Dependencies and Integration
Uses OF compatibles `brcm,iproc-i2c` and `brcm,iproc-nic-i2c`, platform IRQ/MMIO, I2C adapter quirks, tasklets, completions, and PM suspend_late/resume_early. NIC type disables slave callbacks on the shared algorithm.

## Risks and Test Signals
Risks include global mutation of the algorithm callbacks for NIC instances, interrupt disable/synchronize ordering, long 50-second transfer timeout masking hangs, slave tasklet races with unregister, threshold changes for large reads, and indirect register serialization. Test IRQ and poll mode, combined transfers, reads over the 50-byte threshold and 255-byte max, no-IRQ fallback, NIC DT resources, slave write/read/write-read cases, suspend/resume, and removal with pending interrupts.
