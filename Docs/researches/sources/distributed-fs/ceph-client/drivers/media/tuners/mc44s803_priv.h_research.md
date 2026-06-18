# sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803_priv.h

Purpose: private MC44S803 register/bitfield definitions and state. It documents the tuner register map, defines oscillator and IF constants, register numbers, bit masks/shifts, field pack/unpack macros `MC44S803_REG_SM` and `MC44S803_REG_MS`, and `struct mc44s803_priv`.

The constants drive all init and tuning writes in `mc44s803.c`: oscillator/power/reference/mixer/reset/LO/circuit/digital tune/AGC/data/id fields are packed into 24-bit register values. Private state stores public config, I2C adapter, frontend pointer, and cached frequency.

Dependencies are the public config type and kernel integer types through includers. Risks: field macro correctness is critical because every write packs raw bitfields; comments contain hardware datasheet assumptions; IF constants directly shape LO math; and cached state is minimal. Test signals: field macro pack/unpack sanity checks, ID extraction from read value, frequency calculations around range limits, and static review of mask/shift overlaps.
