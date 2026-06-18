# sources/distributed-fs/ceph-client/drivers/hwmon/sbtsi_temp.c

Purpose: I2C hwmon driver for AMD SB-TSI temperature sensors. It exposes CPU temperature plus writable min/max limits.

Important APIs/types/functions: `struct sbtsi_data` stores client, extended-range mode, and read order. `sbtsi_reg_to_mc()` and `sbtsi_mc_to_reg()` convert integer/decimal registers to millidegrees. `sbtsi_read()` and `sbtsi_write()` implement hwmon temp callbacks.

Control flow: probe reads `SBTSI_REG_CONFIG` to detect extended range and atomic-read order, then registers hwmon. Input reads follow configured integer/decimal order; limit reads use high/low registers; writes clamp values and write integer then decimal registers.

State and persistence: range/read-order flags persist from probe. Limit writes persist in device registers. No measurement cache exists.

Dependencies/integration: I2C SMBus byte operations, hwmon, OF/I2C matching, bitfield helpers.

Risks: no locking around multi-register reads/writes. Extended range adjusts all readings by 49 C. Writes clamp to encoded 0..255.875 C after range adjustment, which limits accepted user values.

Test signals: config bit decoding, read-order behavior, input/min/max conversions at fractional 0.125 C boundaries, writable limits, and OF match `amd,sbtsi`.
