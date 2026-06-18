# subset-b-004076 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_regs.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_regs.h

### Purpose
`stv0367_regs.h` is the static register and bitfield catalog for the STV0367 DVB-T/DVB-C demodulator driver. It does not execute logic; it gives the companion driver code symbolic names for every memory-mapped/I2C-accessed hardware register and field used to configure terrestrial COFDM and cable QAM operation.

### Important APIs, Types, And Functions
The file exports preprocessor constants only. Register constants use the `R367TER_*` and `R367CAB_*` prefixes, while bitfield constants use `F367TER_*` and `F367CAB_*`. The encoded field format places the 16-bit register address in the high part and the field mask in the low byte, for example `F367TER_I2CT_ON` is tied to `R367TER_I2CRPT` and mask `0x80`. This matches common ST frontend helper patterns where code extracts the target register from `field >> 16` and the mask from `field & 0xff`.

### Control Flow
There is no runtime control flow. The file is organized as a long register map. The first region is the terrestrial core around addresses `0xf000` and covers chip ID, I2C repeater, top control, GPIO/IO configuration, AGC, derotator, timing recovery, TPS/FFT/SYR/CHC controls, equalizer, Viterbi/FEC, Reed-Solomon, transport stream output, and error counters. The later cable region uses `R367CAB_*`/`F367CAB_*` names around the `0xf4xx` range and covers QAM demodulation, AGC, equalizer, carrier/timing recovery, FEC, Reed-Solomon counters, BERT, output formatting, and TSMF/status registers.

### State, Persistence, And Dependencies
The header has no state and no persistence behavior. The persistent effect happens only when a driver uses these constants to perform I2C register writes to the STV0367 chip. Its only dependency is C preprocessor inclusion through an include guard. Driver code that includes it depends on the exact numeric values matching the STV0367 datasheet and the helper encoding convention.

### Integration Points
This file integrates with the STV0367 DVB frontend implementation in the same media driver directory. Register-level helper functions in that driver can use `R367*` constants for full-byte reads/writes and `F367*` constants for masked bit updates. The terrestrial/cable prefix split is the key integration boundary: wrong prefix use can program the wrong functional block or address range.

### Risks
The largest risk is silent hardware misconfiguration from an incorrect address or mask. Because these are macros, the compiler cannot validate register ownership, field width, or valid values. The shared encoded-field convention is also implicit; if helper code interprets `F367*` values differently, masked writes will target bad registers. The file contains hundreds of constants, so copy/paste drift, duplicate bit names, or datasheet revision differences are practical maintenance risks.

### Test Signals
Useful validation signals are successful STV0367 probe/chip-ID reads, correct I2C repeater behavior, lock acquisition for both DVB-T and DVB-C channels, stable AGC readings, correct BER/uncorrected block counters, transport-stream output under serial/parallel modes, and regression tests or hardware traces confirming that masked field writes preserve unrelated bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0367_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900.h

### Purpose
`stv0900.h` is the public kernel-driver interface for the ST STV0900 satellite demodulator frontend. Board drivers include it to describe chip wiring and to attach one of the demodulator paths to the Linux DVB frontend core.

### Important APIs, Types, And Functions
`struct stv0900_reg` represents one register/value pair and is used for optional transport-stream configuration tables. `struct stv0900_config` is the board-provided configuration: demodulator I2C address, single/dual demod mode, crystal frequency, clock source mode, DiSEqC mode, per-path transport stream modes, optional TS register table, tuner I2C addresses, ADC/tuner type hints, and two board hooks. `set_ts_params()` lets the board start DMA or adjust TS plumbing when tuning starts. `set_lock_led()` lets the demod driver report lock state to board LED logic. `stv0900_attach()` is the exported attach point when `CONFIG_DVB_STV0900` is reachable; otherwise an inline stub warns and returns `NULL`.

### Control Flow
There is no implementation control flow beyond the Kconfig wrapper. At compile time, `IS_REACHABLE(CONFIG_DVB_STV0900)` decides whether callers link against the real module symbol or the disabled-driver stub. At runtime, board code populates `stv0900_config`, passes it with an `i2c_adapter` and demod index to `stv0900_attach()`, and receives a `struct dvb_frontend *` or `NULL`.

### State, Persistence, And Dependencies
The header owns no mutable state. Configuration data is persistent only as board-driver storage referenced by attached frontend state in `stv0900_core.c`. It depends on Linux DVB frontend headers for `struct dvb_frontend`, `struct i2c_adapter`, frontend operation types, and kernel logging in the disabled stub.

### Integration Points
This is the boundary between board-specific device setup and the generic STV0900 demodulator implementation. It is consumed by PCI/USB/media bridge drivers that know the physical tuner wiring, TS routing, DiSEqC electrical mode, and optional LED/DMA hooks. `stv0900_core.c` copies the frontend ops, calls the hooks, and interprets the path/tuner fields during initialization.

### Risks
The config fields are low-level hardware policy. A wrong `xtal`, `clkmode`, tuner address, tuner type, IQ inversion assumption, or TS mode can produce failed lock, broken transport output, or I2C access to the wrong downstream tuner. The optional `ts_config_regs` table must be sentinel-terminated by address `0xffff` because the core iterates until that value. The disabled Kconfig stub fails at attach time, so board code must handle `NULL`.

### Test Signals
Good signals are a non-NULL attach, correct frontend name/caps registration, successful tuning on both demod indices, lock LED transitions, DMA/TS activation through `set_ts_params()`, correct serial/parallel TS output, and absence of the disabled-driver warning when STV0900 support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_core.c -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_core.c

### Purpose
`stv0900_core.c` implements the Linux DVB frontend driver for the STV0900 satellite demodulator. It handles chip allocation, shared dual-demod internal state, low-level I2C register access, chip initialization, tuner setup, DVB-S/DVB-S2/DSS search, status and metric callbacks, DiSEqC commands, transport stream control, and module registration metadata.

### Important APIs, Types, And Functions
The file exports `stv0900_attach()` and internal helpers declared in `stv0900_priv.h`. The global `stvdebug` module parameter gates debug printing. `struct stv0900_inode` links shared `struct stv0900_internal` objects by I2C adapter/address so two frontend instances can share one physical dual-demod chip. Register helpers are `stv0900_write_reg()`, `stv0900_read_reg()`, `stv0900_write_bits()`, and `stv0900_get_bits()`. Initialization helpers include `stv0900_initialize()`, `stv0900_set_mclk()`, `stv0900_set_ts_parallel_serial()`, `stv0900_st_dvbs2_single()`, and `stv0900_init_internal()`. Runtime frontend callbacks are collected in `stv0900_ops`: `init`, `sleep`, `search`, `read_status`, BER/SNR/strength/uncorrected-block reads, DiSEqC send/receive, tone control, I2C gate control, and `get_frontend`.

### Control Flow
Attach allocates `struct stv0900_state`, copies `stv0900_ops`, stores board config and I2C adapter, builds `stv0900_init_params`, and calls `stv0900_init_internal()`. Internal initialization either reuses an existing shared chip object in dual mode or allocates and appends a new one, runs the startup register sequence from `stv0900_init.h`, configures rolloff, TS routing or custom TS registers, tuner type/address/ADC settings, IQ swap, and master clock.

Tuning uses the DVB custom-search flow. `stv0900_search()` validates symbol rate, calls the board TS hook, configures MIS filtering from `stream_id`, fills `intp` search state, narrows DVB-S searches to `STV0900_SEARCH_DVBS1`, and delegates acquisition to `stv0900_algo()` from the algorithm code. Search success is reported only when the algorithm returns range OK and the per-demod result is locked. `stv0900_start_search()` programs acquisition registers based on chip cut, symbol rate, search range, and warm/cold/blind search mode. Lock polling in `stv0900_get_demod_lock()` watches `HEADER_MODE`, then `LOCK_DEFINITIF`.

Status and metrics read hardware fields after tuning. `stv0900_status()` distinguishes DVB-S2 and DVB-S lock paths using packet delineator/Viterbi and TS FIFO flags. Strength and C/N use interpolation against lookup tables from `stv0900_init.h`. BER samples error counters several times and scales them when the relevant lock flag is set. DiSEqC control writes mode/reset bits, pushes FIFO bytes, waits for TX idle or RX end, and implements mini-burst and 22 kHz tone operations.

### State, Persistence, And Dependencies
Persistent driver state lives in memory in `struct stv0900_internal` and per-frontend `struct stv0900_state`. The internal object tracks clock, chip id, demod mode, per-path frequency/bandwidth/symbol-rate/search settings, tuner type, result structures, error state, I2C adapter/address, optional TS config, and a reference count `dmds_used`. The global inode list persists shared chips until release. Hardware state persists in demodulator registers until reset, sleep, retune, or module unload. Dependencies include Linux kernel module/I2C/slab APIs, DVB frontend APIs, `stv0900_reg.h` register labels, private enums/types, static init tables, and external acquisition helpers such as `stv0900_algo()` and `stv0900_get_standard()`.

### Integration Points
The file integrates upward with the DVB core through `struct dvb_frontend_ops` and downward with the STV0900 chip through I2C transfers. It also integrates sideways with board drivers through `struct stv0900_config` hooks, tuner operations in `fe->ops.tuner_ops`, and optional hardware/auto tuner register programming. DiSEqC and tone callbacks connect satellite equipment control to the DVB SEC API. The real attach symbol is exported with `EXPORT_SYMBOL_GPL`.

### Risks
The shared inode list is global and has no explicit locking, so concurrent attach/release paths would rely on broader DVB registration serialization. Several I2C helpers only log transfer failures and do not set a local error in the shown code, so later logic can continue with zero/stale values. `stv0900_diseqc_send()` busy-waits while FIFO full without a timeout, which can hang if hardware never drains. Search and TS setup are sensitive to chip cut (`chip_id`) and symbol-rate thresholds. Custom `ts_config_regs` must be correctly terminated. Release decrements shared `dmds_used`; mismatched attach/release lifetimes could free shared state still in use.

### Test Signals
High-value tests require hardware or emulation: attach both demods on one chip and release them in both orders, probe all supported chip cuts, tune DVB-S and DVB-S2 transponders across low/high symbol rates, verify MIS filtering and `FE_CAN_MULTISTREAM` on chip id `>= 0x30`, measure BER/SNR/strength monotonicity, exercise DiSEqC master commands, mini-bursts, slave replies, and tone toggles, confirm TS output in serial/parallel/DVBCI modes, and inject I2C failures to check graceful attach/search failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_init.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_init.h

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_priv.h -->
## sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_priv.h

### Purpose
`stv0900_priv.h` is the private type and helper contract for the STV0900 driver. It defines driver-local enums, search/result/internal state structures, utility macros, debug printing, and prototypes shared across the core and algorithm implementation files.

### Important APIs, Types, And Functions
Utility macros include `INRANGE`, `MAKEWORD`, `LSB`, `MSB`, boolean constants, and `dprintk()`. Lookup support is defined by `struct stv000_lookpoint` and `struct stv0900_table`. Enums describe error codes, TS clock modes, acquisition states, LDPC/demod modes, signal-presence states, demod path numbers, tracking/search standards, search algorithms, modulation, DVB-S2 modcodes, FEC, frame length, pilots, rolloff, IQ inversion/search policy, DiSEqC mode, and single/dual demod mode. `struct stv0900_init_params`, `struct stv0900_search_params`, `struct stv0900_signal_info`, `struct stv0900_internal`, and `struct stv0900_state` are the main state carriers. Prototypes expose register access, lock checking, signal search, tuner control, carrier-loop lookup, modcod control, standard detection, auto-tuner frequency access, and debug state.

### Control Flow
The header has no executable control flow, but it defines the states consumed by the search algorithm and frontend callbacks. A typical flow is: board attach builds `stv0900_init_params`; initialization fills `struct stv0900_internal`; tuning fills per-demod search fields and calls `stv0900_algo()`; the algorithm updates `struct stv0900_signal_info`; status/metric callbacks read those results and hardware state.

### State, Persistence, And Dependencies
`struct stv0900_internal` is the shared persistent chip state for one physical STV0900: clocks, rolloff, demod mode, per-demod tuning/search parameters, tuner type, result/error arrays, I2C adapter/address, clock mode, chip id, TS config, aggregate error state, and demod reference count. `struct stv0900_state` is per frontend and holds the shared internal pointer, I2C adapter, board config, embedded `dvb_frontend`, and demod index. The header depends on Linux I2C types and on public `stv0900.h` types being available through includers.

### Integration Points
This file connects `stv0900_core.c` with other STV0900 implementation units, especially the acquisition algorithm source that provides `stv0900_algo()`, `stv0900_check_signal_presence()`, and `stv0900_get_standard()`. It also codifies the contract with register labels from `stv0900_reg.h`: helpers take encoded labels and demod-specific code selects path-specific aliases. The DVB core sees only the public frontend object, while these private structures hold the implementation details.

### Risks
Enums and array indices must remain aligned: many internal arrays are size two and indexed by `enum fe_stv0900_demod_num`. Any invalid demod value can corrupt memory. The `TRUE`/`FALSE` macros and broad debug macro are legacy style and can mask type issues. The shared internal structure is mutable across both frontend paths, so algorithm code must avoid overwriting the other path's settings except for intentional single/dual LDPC changes. Function prototypes imply cross-file coupling; signature drift or mismatched enum semantics would break acquisition behavior.

### Test Signals
Compile coverage across all STV0900 translation units is the first signal. Runtime signals include correct per-demod isolation in dual mode, correct single-mode LDPC switching, valid search state transitions, sane result fields after lock, correct I2C register helper behavior for encoded labels, and debug logging that identifies search/lock failures without changing behavior when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_priv.h -->
