# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-brcmstb.c

## Purpose
Broadcom set-top/peripheral BSC I2C master driver. It supports endian-aware MMIO, interrupt or polling completion, atomic transfers, 1-byte or 4-byte data register layouts, `NOSTART`, 10-bit addressing, and BCM2711 HDMI auto-I2C release.

## APIs, Control Flow, and State
`struct brcmstb_i2c_dev` stores MMIO, cached `struct bsc_regs`, adapter, completion, configured bus frequency, data register size, and atomic flag. `brcmstb_i2c_xfer()` chunks messages by the data-register window (`N_DATA_REGS * data_regsz`), computes START/STOP/RESTART/NOSTART conditions, writes the address, and calls `brcmstb_i2c_xfer_bsc_data()` for each chunk. Data packing/unpacking differs for 1-byte peripheral cores and 4-byte STB cores. `brcmstb_send_i2c_cmd()` enables BSC interrupts, starts the transfer, waits by IRQ or polling, checks NOACK unless ignored, then clears count/enable. `xfer_atomic()` disables the IRQ and forces polling. Probe handles optional IRQ fallback, clock-frequency selection from a fixed table, compatible-specific data width, and optional `auto-i2c` release for HDMI.

## Dependencies and Integration
Uses OF compatibles `brcm,brcmstb-i2c`, `brcm,brcmper-i2c`, and `brcm,bcm2711-hdmi-i2c`, platform MMIO/IRQ, I2C core atomic xfer hooks, and PM sleep adapter suspend markers.

## Risks and Test Signals
Risks include cached register state diverging from hardware, wrong endian/data-width packing, polling fallback behavior, `IGNORE_NAK` command selection, and chunk boundary START/STOP errors. Test 1-byte and 4-byte cores, interrupt and polling mode, atomic transfers from late contexts, long reads/writes across chunks, `NOSTART` sequences, 10-bit read setup, unsupported clock-frequency fallback, BCM2711 HDMI release, and suspend/resume register restoration.
