# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/opera1.c

## Purpose
This driver supports Opera1 DVB-S USB2 hardware. It implements an Xilinx/FX2 vendor protocol, I2C over USB, STV0299 frontend setup, tuner attach, LNB voltage, PID filter programming, remote-control decoding, MAC reading, FPGA firmware loading, and USB registration.

## Important APIs, types, and functions
`struct opera1_state` stores the last remote key. `opera1_xilinx_rw()` performs vendor control transfers and special tuner request status checks. `opera1_usb_i2c_msgxfer()` maps pseudo I2C addresses to voltage, stream, remote, or tuner USB requests. `opera1_i2c_xfer()` exposes this as an I2C adapter. Frontend code uses `opera1_stv0299_config`, `opera1_stv0299_set_symbol_rate()`, `opera1_frontend_attach()`, and `opera1_tuner_attach()`.

## Control flow and state
On warm Opera1 devices, `opera1_probe()` loads FPGA firmware before `dvb_usb_device_init()`. Power control writes request `0xb7`. Streaming and PID filter control are encoded as I2C messages to the stream-control pseudo address. Remote polling reads 32 bytes, rebuilds a bitstream, searches for start markers, maps RC5-like values, and emits legacy events.

## Dependencies and integration
The driver depends on DVB USB, `stv0299`, DVB PLL `DVB_PLL_OPERA1`, Cypress FX2 firmware, optional FPGA firmware `dvb-usb-opera1-fpga-01.fw`, and bulk streaming endpoint `0x82`.

## Risks and test signals
Risks include nested USB/I2C locking, Xilinx status expectations, inferred remote bit alignment, PID table address programming, and firmware pointer cleanup. Test firmware and FPGA load paths, STV0299 attach, LNB 13/18V switching, stream start/stop, PID filter programming across indices, MAC read, and RC repeat behavior.
