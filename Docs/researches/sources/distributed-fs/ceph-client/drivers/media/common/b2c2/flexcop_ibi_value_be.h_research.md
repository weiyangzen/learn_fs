# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_be.h

Purpose: generated big-endian layout for the `flexcop_ibi_value` union, allowing named access to every 32-bit FlexCop IBI register field.

Important APIs/types: defines `typedef union flexcop_ibi_value` with raw `u32` access and register-specific structs for DMA, I2C two-wire state, LNB/misc/control/IRQ/reset, PID filters, MAC/card IDs, CI/PI/DVB registers, SRAM buffers, destination routing, and WAN control.

Control flow: no executable logic; consumers read/write `raw` or named bitfields after `flexcop-reg.h` selects this file under `__BIG_ENDIAN`.

State/persistence: describes volatile hardware register layout only. Runtime state is the `u32 raw` value returned by bus-specific register IO.

Dependencies/integration: every FlexCop register operation in common/bus code depends on these bit positions matching hardware on big-endian builds.

Risks/test signals: C bitfield layout is implementation-sensitive and this file is explicitly generated. Any manual edit or compiler assumption mismatch corrupts register programming. Cross-endian compile coverage, comparing raw encodings for key fields against datasheet constants, and tests for I2C/control/PID/SRAM fields are critical.
