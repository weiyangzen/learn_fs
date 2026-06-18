# sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256-regs.h

Purpose: register and bitfield definition header for the Lantiq PEF2256/FALC56 framer.

Important APIs, types, and functions: defines offsets for command, interrupt mask/status, framer mode, transmit/receive control, line interface mode, system interface control, clock mode, global config, port config, global counter mode, version/status, receive status, global interrupt status, and wafer ID registers. Bit helpers use `BIT()`, `GENMASK()`, `FIELD_PREP_CONST()`, and `FIELD_PREP()` for coding modes, frame formats, clock rates, buffer depths, LOS thresholds, carrier status, interrupt bits, and version decoding.

Control flow: no executable flow. `pef2256.c` consumes these constants to identify chip version, program E1 line/system/signaling/errors, mask/unmask interrupts, read carrier status, and decode interrupt sources.

State and persistence: register definitions only. Hardware state is represented by the chip registers programmed through these offsets.

Dependencies and integration points: depends on Linux bitfield helpers. It is tightly coupled to the PEF2256 datasheet and to the register programming sequences in `pef2256.c`.

Risks: wrong bit masks or version-specific constants can silently misprogram clocks, line thresholds, coding, or interrupt handling. Some fields are split across registers, such as SSD in `FMR1` and `SIC1`; users must update both sides consistently.

Test signals: static compile of all macros, hardware register trace comparison against datasheet-recommended E1 setup, version detection for 1.2/2.1/2.2, LOS/AIS interrupt mask behavior, and tests for all supported mclk/sysclk/data-rate combinations.
