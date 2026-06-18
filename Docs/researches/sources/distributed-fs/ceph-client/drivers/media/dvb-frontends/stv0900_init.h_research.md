# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_init.h

### Purpose
`stv0900_init.h` provides static calibration and initialization data for the STV0900 demodulator core. It supplies C/N and RF lookup tables, carrier-loop optimization tables for different DVB-S2 modcodes/modulations/chip cuts/symbol rates, the main startup register script, and a cut-2.0 add-on register script.

### Important APIs, Types, And Functions
The header defines no functions. It defines `stv0900_s2_cn` and `stv0900_rf` as `struct stv0900_table` lookup tables used by metric interpolation. It defines carrier-loop table row types: `struct stv0900_car_loop_optim`, `struct stv0900_short_frames_car_loop_optim`, and `struct stv0900_short_frames_car_loop_optim_vs_mod`. Major static arrays include `FE_STV0900_S2CarLoop`, `FE_STV0900_S2CarLoopCut20`, `FE_STV0900_S2APSKCarLoopCut20`, low-rate QPSK cut-20/cut-30 tables, short-frame tables, `STV0900_InitVal[181][2]`, and `STV0900_Cut20_AddOnVal[32][2]`.

### Control Flow
There is no standalone control flow, but `stv0900_core.c` consumes the arrays in deterministic loops. `stv0900_initialize()` writes all 181 base initialization register/value pairs, then writes 32 cut-2.0 add-on pairs for chip IDs at or above `0x20`. Carrier-loop helper functions select one of the optimization tables by chip ID, modcode/modulation, pilot state, frame type, and symbol-rate bucket, then return the register value to program into acquisition/tracking loops. Metric helpers interpolate raw AGC/noise register values through the lookup tables.

### State, Persistence, And Dependencies
All data is `static const`; it is read-only kernel module data. Persistent effects occur when the core writes these table values into hardware registers or when metric routines use them to convert raw readings. The file depends on `stv0900_priv.h` for table and enum definitions and on `stv0900_reg.h` being included by consumers for register constants referenced in the arrays.

### Integration Points
`stv0900_core.c` includes this header directly, so the arrays are compiled into the core translation unit. Initialization tables are a hardware bring-up contract with the STV0900 chip. Carrier-loop tables integrate with DVB-S2 acquisition/tracking decisions. RF and C/N tables feed DVB frontend `read_signal_strength` and `read_snr` callbacks.

### Risks
These constants encode hardware tuning knowledge and are difficult to validate by inspection. A wrong table value can degrade acquisition, lock stability, or reported metrics without causing a compile error. Table sizes are assumed by loops and array-size expressions in the core; manual size changes must remain consistent. Several APSK entries are placeholder-like repeated `0x0C`/`0x0A` values, so support quality may depend on chip revision and modulation mix. Register scripts are order-dependent and include reset/timing-sensitive values.

### Test Signals
Signals include successful initialization on chip cuts below `0x20`, exactly `0x20`, and `>= 0x30`; stable lock over symbol-rate buckets around 3, 7, 15, and 25 Msps; DVB-S2 C/N readings that track lab signal level; RF strength readings that vary monotonically with attenuator changes; and no regressions in transport output or DiSEqC frequency after master-clock setup.
