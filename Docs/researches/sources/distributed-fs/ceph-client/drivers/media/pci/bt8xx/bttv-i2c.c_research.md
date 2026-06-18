# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-i2c.c

## Purpose
`bttv-i2c.c` implements the Bt848/Bt878 I2C adapter used to discover and control EEPROMs, tuners, audio processors, IR receivers, and other board subdevices. It supports both software bit-bang I2C over the chip pins and Bt878 hardware I2C transactions.

## Important APIs, Types, And Functions
Module parameters are `i2c_debug`, `i2c_hw`, `i2c_scan`, and `i2c_udelay`. Bit-bang callbacks are `bttv_bit_setscl()`, `bttv_bit_setsda()`, `bttv_bit_getscl()`, and `bttv_bit_getsda()` through `bttv_i2c_algo_bit_template`. Hardware transfer routines are `bttv_i2c_wait_done()`, `bttv_i2c_sendbytes()`, `bttv_i2c_readbytes()`, and `bttv_i2c_xfer()` through `bttv_algo`. Public helpers are `bttv_I2CRead()`, `bttv_I2CWrite()`, `bttv_readee()`, `init_bttv_i2c()`, and `fini_bttv_i2c()`.

## Control Flow
`init_bttv_i2c()` chooses hardware mode if forced or configured by the board; otherwise it installs an `i2c-algo-bit` adapter after raising SCL/SDA. Hardware transfers program `BT848_I2C`, clear/observe `BT848_INT_I2CDONE` and `BT848_INT_RACK`, and wait on `btv->i2c_queue`, which is woken by `bttv_irq()` when an I2CDONE interrupt arrives. Optional scan probes all 7-bit addresses and reports known mappings. `fini_bttv_i2c()` deletes the adapter when registration succeeded.

## State And Persistence
State is kept in `btv->c.i2c_adap`, `btv->i2c_client`, `btv->i2c_algo`, `btv->i2c_state`, `btv->i2c_rc`, `btv->i2c_done`, and `btv->i2c_queue`. It is initialized during PCI probe and destroyed on remove. EEPROM reads are caller-supplied buffers only; no persistent storage is modified.

## Dependencies And Integration Points
The file integrates with Linux I2C core, `i2c-algo-bit`, V4L2 device private data, the bttv IRQ handler, `tveeprom_read()`, tuner/audio/IR clients, and board identification in `bttv-cards.c`. The hardware adapter depends on I2CDONE interrupts being enabled by `init_irqreg()`.

## Risks
Hardware I2C waits are interrupt-driven and can fail if IRQs are masked or the chip is wedged. `bttv_i2c_wait_done()` treats RACK as success and timeout/no-RACK as failure; subtle changes could break device probing. The helper functions mutate the shared `btv->i2c_client.addr`, so concurrent users need serialization at higher layers. Too-small `i2c_udelay` is clamped, but unusual boards may still be timing-sensitive.

## Test Signals
Signals include adapter registration under `/sys/bus/i2c`, optional `i2c_scan` discoveries, successful EEPROM reads, tuner/audio subdevice binding, IR receiver probing, no `i2c read/write error` warnings during probe, and working frequency/audio controls through V4L2.
