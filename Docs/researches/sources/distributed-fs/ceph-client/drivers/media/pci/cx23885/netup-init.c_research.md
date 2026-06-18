# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.c

Purpose: performs NetUP Dual DVB-S2 CI board-specific initialization by programming the cx23885 A/V core over I2C to set AUX clock output to 27 MHz.

Important APIs and functions: public `netup_initialize(struct cx23885_dev *dev)` uses static helpers `i2c_av_write`, `i2c_av_write4`, `i2c_av_read`, and `i2c_av_and_or` to access 8-bit and 32-bit A/V core registers at I2C address `0x88 >> 1`.

Control flow: `netup_initialize` selects `dev->i2c_bus[2]`, stops the microcontroller by clearing bit `0x10` in register `0x803`, writes AUX PLL fractional value `0xea0eb3` to `0x114`, writes AUX PLL integer value `0x090319` to `0x110`, and restarts the microcontroller by setting bit `0x10`. The read-modify-write helper reads a byte register and writes back masked/or'ed data.

State and persistence: programmed state is hardware register state in the A/V core. There is no software cache and no retry/recovery beyond logging transfer errors. Helper writes use little-endian byte order for 32-bit values as expected by the target register protocol.

Dependencies and integration points: depends on `cx23885.h`, the cx23885 I2C bus array, Linux I2C transfer API, and `netup-init.h`. It is called from NetUP-specific board initialization before DVB/CI components rely on the 27 MHz AUX clock.

Risks: I2C helper functions log failures but do not return errors, so `netup_initialize` cannot report partial PLL programming failure. The function assumes bus 2 exists and that the A/V core is reachable at address `0x44`. Register constants are magic values with no local symbolic definitions. The read helper logs "write error" on its initial address phase, which can confuse diagnostics.

Test signals: board bring-up should verify the AUX clock frequency, successful I2C transactions, and downstream tuner/demod stability. No local unit tests are present.
