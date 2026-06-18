# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.h

Purpose: Defines wl1251 WSPI command and initialization bit fields used by the SPI bus implementation.

Important APIs and types: Defines read/write command bits, byte length/address masks and shifts, init command fields, CRC length, command length, fixed busy length calculation, and init mask.

Control flow: No executable code. Constants are consumed by `spi.c` to build reset/wake/read/write transactions.

State and persistence: No state. Values encode hardware protocol requirements.

Dependencies and integration points: Includes `cmd.h`, `acx.h`, and `reg.h` for related firmware definitions. Used only by the SPI binding.

Risks: Bit masks must match the WSPI hardware protocol exactly. Mis-sizing `WL1251_BUSY_WORD_LEN` or command length changes SPI framing and can break all bus access.

Test signals: SPI reset/wake command success, correct register reads after wake, and stable firmware boot over SPI.
