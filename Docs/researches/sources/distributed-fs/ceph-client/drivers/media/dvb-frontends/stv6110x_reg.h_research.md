<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_reg.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_reg.h

`stv6110x_reg.h` is the compact register map for the STV6110x tuner. It defines the eight register addresses (`CTRL1`, `CTRL2`, `TNG0`, `TNG1`, `CTRL3`, `STAT1`, `STAT2`, `STAT3`) and per-field offset/width constants consumed by `STV6110x_SETFIELD()` and `STV6110x_GETFIELD()`.

The register groups map directly to implementation behavior. `CTRL1` contains reference-clock `K`, low-power/loop-through, receiver, and synthesizer bits. `CTRL2` contains output divider, reference output select, and baseband gain. `TNG0/TNG1` hold PLL divider fields, reference divider, prescaler, and divide-by-four selection. `CTRL3` controls DC loop, RC calibration clock, charge pump, and channel filter. `STAT1` exposes VCO calibration start, RC calibration start, and PLL lock status. `STAT2/STAT3` are address placeholders without field definitions in this header.

There is no runtime state or control flow in the header; it is a data contract for register shadow manipulation in `stv6110x.c`. Persistent effects occur only when the implementation writes shadow bytes to hardware.

Dependencies are private macros in `stv6110x_priv.h`. Integration risk is high because field names are built into macro invocations such as `STV6110x_SETFIELD(regs[STV6110x_CTRL1], CTRL1_K, value)`. Any rename or width/offset error breaks compilation or corrupts tuner programming.

Risks include missing range validation for raw bitfields, silent hardware misconfiguration from wrong offsets, and lack of documentation for STAT2/STAT3. Test signals should include compile coverage, bitfield unit-style checks over all defined fields, frequency/bandwidth programming on hardware, and lock-status readback through `STAT1_LOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_reg.h -->
