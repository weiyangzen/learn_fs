# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_ddc.c

## Purpose

This file implements fbdev DDC/EDID reading over an I2C bit-bang adapter. It performs legacy monitor line-wake sequencing and reads one EDID block from address `0x50`. The complete 127-line source was read.

## Important APIs, Types, and Functions

The exported API is `fb_ddc_read(struct i2c_adapter *adapter)`. The internal `fb_do_probe_ddc_edid()` allocates an EDID buffer and performs the two-message I2C transaction: write offset zero, read `EDID_LENGTH` bytes.

## Control Flow

`fb_ddc_read()` drives SCL high, then makes up to three attempts. Each attempt toggles SDA/SCL with sleeps to initialize old monitors, waits for SCL high if `getscl` is available, calls the EDID probe, drives stop/cleanup sequences, and breaks on success. At exit it releases both DDC lines high to avoid powering off Apple Cinema HD displays.

## State and Persistence Behavior

No persistent state is stored. On success the caller receives a heap-allocated EDID buffer and owns freeing it. The function mutates DDC line levels during probing.

## Dependencies and Integration Points

It depends on I2C core, `i2c-algo-bit` callbacks, EDID length definitions, delays, and fbdev drivers that expose DDC GPIO/I2C adapters. It exports `fb_ddc_read()` GPL-only.

## Risks and Edge Cases

The function assumes `adapter->algo_data` is a valid `struct i2c_algo_bit_data` with required line callbacks. DDC bus timing is sleep-heavy and can fail on monitors that hold SCL low. Only one 128-byte EDID block is read; extensions require higher-level handling elsewhere. Callers must free the returned buffer.

## Test Signals

Test successful EDID read, NACK/failure cleanup, SCL-stuck retries, adapters without `getscl`, allocation failure, line-release verification, and integration with drivers parsing the returned EDID.
