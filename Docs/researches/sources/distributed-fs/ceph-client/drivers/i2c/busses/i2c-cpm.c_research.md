# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cpm.c

## Purpose
Freescale CPM1/CPM2 I2C controller adapter. It exposes a CPM communication processor I2C engine as a Linux `i2c_adapter`, using CPM parameter RAM, buffer descriptors, coherent DMA buffers, and OF platform resources.

## Important APIs, Types, And Functions
Key private state is `struct cpm_i2c`, holding the adapter, mapped I2C registers, CPM parameter RAM, DPRAM buffer descriptors, coherent TX/RX buffers, IRQ, command word, frequency, and CPM version. `struct i2c_ram` and `struct i2c_reg` model CPM parameter RAM and controller registers. The adapter algorithm is `cpm_i2c_algo` with `cpm_i2c_xfer()` and `cpm_i2c_func()`. Probe/remove are `cpm_i2c_probe()` and `cpm_i2c_remove()`. Hardware setup/teardown are `cpm_i2c_setup()` and `cpm_i2c_shutdown()`.

## Control Flow
Probe allocates `struct cpm_i2c`, binds OF data, copies `cpm_ops`, initializes hardware, then registers a numbered adapter using optional `linux,i2c-index`. Setup maps parameter RAM and registers, resolves CPM1 versus CPM2, allocates DPRAM BDs and coherent buffers, initializes parameter RAM, issues `CPM_CR_INIT_TRX`, programs address, baud, mode, and IRQ masks. Transfers reset BD pointers, prepare each message in `cpm_i2c_parse_message()`, enable interrupts, start the controller, wait for each TX/RX BD completion, then validate status in `cpm_i2c_check_message()`.

## State And Persistence
State is in RAM and hardware registers only. Persistent kernel-visible state is the registered adapter. The transfer path mutates CPM BD status bits, parameter RAM pointers, and coherent buffers. Error paths call `cpm_i2c_force_close()` and may clear enable for errata builds.

## Dependencies And Integration Points
Depends on CPM/MURAM APIs, OF address/IRQ parsing, DMA coherent allocation, IRQs, and Linux I2C core. Compatible strings are `fsl,cpm1-i2c` and `fsl,cpm2-i2c`.

## Risks
BD and DMA buffer alignment are delicate, especially read buffer alignment and CPM1 relocation handling. Timeout is fixed at one second per message. The code supports only four messages and read/write lengths up to `CPM_MAX_READ`. Hardware errata behavior is compile-time disabled by default. Failure cleanup spans IRQ, I/O maps, MURAM, and coherent memory, so partial allocation paths are risk-heavy.

## Test Signals
Useful checks include OF probe on CPM1/CPM2, successful adapter registration, basic read/write/repeated-start transactions, NACK mapping to `-ENXIO`, timeout recovery via force-close, max message/length quirk enforcement, and removal without leaked IRQ/DMA/MURAM resources.
