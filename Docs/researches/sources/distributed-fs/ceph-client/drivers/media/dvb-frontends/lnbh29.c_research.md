# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh29.c

## Purpose
`lnbh29.c` drives the STMicroelectronics LNBH29 LNB supply/control IC. It attaches a voltage-control SEC helper to an existing DVB frontend and validates output voltage through status reads.

## Important APIs, Types, and Functions
`struct lnbh29_priv` stores the I2C adapter, 7-bit address, and two-byte DATA register write buffer. `lnbh29_set_voltage()` updates only the `LNBH29_VSEL_MASK` bits for off, 13 V, or 18 V and writes register `0x01`. `lnbh29_read_vmon()` reads two status bytes from register `0x00` and treats OLF or VMON as failures. `lnbh29_release()` powers off and frees state; `lnbh29_attach()` allocates state, probes with voltage off, and installs SEC callbacks.

## Control Flow
Attach shifts the configured address, seeds the DATA register byte from board config, stores `sec_priv`, and powers off to detect the chip. Voltage changes perform one I2C write, wait 6-20 ms for soft-start, and read status unless turning off.

## State and Persistence
The driver keeps a mutable cached DATA byte so board option bits survive voltage changes while VSEL bits change. Release forces off. No persistent storage or suspend cache exists.

## Dependencies and Integration Points
It depends on Linux I2C, DVB frontend SEC operations, bit macros, and `struct lnbh29_config`. It exports `lnbh29_attach()`.

## Risks and Edge Cases
Only voltage control is implemented. Status bits for over-temperature, power-not-good, and power-down are defined but only OLF/VMON are used for failure decisions. Address shifting has the same 8-bit-vs-7-bit board convention risk as LNBH25.

## Test Signals
Validate attach, DATA option preservation, off/13/18 V writes, status-fault propagation, release power-off, and callback replacement on an existing frontend.
