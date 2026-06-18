# Research: subset-b-004079

Grouped research for DVB frontend and tuner sources under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910.c

`stv0910.c` is the DVB core frontend driver for the ST STV0910 dual DVB-S/DVB-S2 demodulator. It exports `stv0910_attach()`, installs `dvb_frontend_ops`, probes chip id `0x51`, initializes shared chip registers, and then runs per-demod acquisition, status, statistics, I2C repeater, and DiSEqC flows.

Important state is split between `struct stv_base` and `struct stv`. `stv_base` is shared by both demod paths on one I2C address and holds `i2c`, `adr`, `i2c_lock`, `reg_lock`, reference count, external clock, and master clock. `struct stv` is per frontend and stores demod number, register offset, TS config, acquisition state, receive mode, lock timing, symbol rate, MODCOD/FEC metadata, VCM flags, PLS/ISI settings, BER scaling, and DVB-S Viterbi threshold cache. `match_base()` and the global `stvlist` let two attaches reuse one chip-level base; `release()` decrements the count and frees the base only when the last frontend exits.

Register access is through 16-bit-address I2C helpers: `write_reg()`, `i2c_read_regs16()`, `read_reg()`, `read_regs()`, `write_shared_reg()`, and `write_field()`. Shared register writes use `base->reg_lock`; tuner gate access uses `gate_ctrl()` and `base->i2c_lock` to serialize the single repeater bus across both demods. The `SET_FIELD`, `SET_REG`, and `GET_REG` macros select P1/P2 register aliases using `state->nr` and `state->regoff`.

Control flow starts in `stv0910_attach()`: allocate state, derive TS and repeater config from `struct stv0910_cfg`, choose `regoff`, initialize defaults, reuse or probe a base, copy ops, and initialize DVB statistics. `probe()` programs global chip setup, PLL master clock via `set_mclock()`, transport stream outputs, stream merger reset, I2C repeater level, TS insertion registers, and DiSEqC. Tuning flows through `set_parameters()` -> optional tuner `set_params()` -> `start()`. `start()` validates symbol rate, stops any existing acquisition, configures stream modes/PLS/ISI, computes demod and FEC timeouts from symbol rate, writes initial symbol rate, sets search standard, disables DSS, resets carrier and Viterbi tuning, configures carrier search range, and triggers acquisition through `DMDISTATE`.

Status and metrics are stateful. `read_status()` decodes demod/header state, transitions `receive_mode` from none to DVB-S or DVB-S2, captures first lock time, calls `get_signal_parameters()` and `tracking_optimization()`, resets TS FIFO on first lock, sets BER counter source and scale, and then updates `FE_HAS_*` flags. C/N lookup uses DVB-S and DVB-S2 tables with interpolation. BER uses adaptive `berscale` and preserves the last valid numerator/denominator while hardware counters are busy. Signal strength combines AGC and sampled I/Q power through `padc_lookup`. `get_frontend()` decodes current FEC, modulation, pilot, rolloff, and measured symbol rate.

Integration points are the DVB frontend API, tuner ops behind `fe->ops.tuner_ops`, STV0910 register definitions in `stv0910_regs.h`, I2C adapter transactions, and satellite SEC/DiSEqC operations (`set_tone()`, `send_master_cmd()`, `send_burst()`). Persistent behavior is only in kernel heap state and hardware registers; there is no filesystem persistence.

Risks include weak propagation of many register read/write failures, shared-chip race sensitivity if gate open/close is unbalanced, precise fixed-point math for symbol-rate/PLL/BER calculations, and dependence on undocumented hardware constants and tuning workarounds. Test signals should cover dual-frontend attach/release, failed probe, I2C transfer failures, PLS/ISI programming, DVB-S and DVB-S2 lock transitions, BER scale changes, VCM MODCOD updates, TS output reset, DiSEqC command timeout, and concurrent tuner I2C gate access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910.h

`stv0910.h` is the public in-tree interface for attaching the STV0910 DVB-S/S2 demodulator driver. It defines `struct stv0910_cfg`, which board drivers use to supply the demodulator clock, I2C address, transport stream mode, repeater level, single/dual operation mode, and optional TS speed.

The important API is `stv0910_attach(struct i2c_adapter *i2c, struct stv0910_cfg *cfg, int nr)`. When `CONFIG_DVB_STV0910` is reachable, this is the external symbol implemented in `stv0910.c`; otherwise the header provides a static inline stub that warns through `pr_warn()` and returns `NULL`. This pattern lets board drivers compile whether the frontend is built-in, modular, or disabled.

The header carries no runtime control flow beyond the Kconfig conditional. Its state contract is entirely through `struct stv0910_cfg`: `clk` defaults to the implementation fallback when zero, `adr` selects the chip address, `parallel` affects TS serial/parallel setup, `rptlvl` controls I2C repeater level, `single` changes the chip GENCFG setup, and `tsspeed` falls back to a safe default if zero.

Dependencies are Linux I2C types, Linux integer types, and the DVB frontend type declaration supplied by included kernel media headers in users of this header. Integration is with board/bridge drivers that instantiate an STV0910 frontend and then attach a tuner through the demodulator's I2C gate.

Risks are mostly configuration risks: invalid clock, repeater level, TS mode, demod index, or I2C address values are not validated in the header and are only partly handled by the implementation. Test signals are compile coverage with `CONFIG_DVB_STV0910` enabled/disabled and board-level attach tests verifying that zero/default config fields produce expected hardware register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910_regs.h

`stv0910_regs.h` is a generated-style register and bit-field map for the STV0910/STV0900-family demodulator. It has no executable code, but it is central to all register access in `stv0910.c`. Register macros use `RSTV0910_*` names with 16-bit addresses; field macros use `FSTV0910_*` packed values where high bits encode the register address and lower bits encode field offset and mask.

The header is organized by chip/global registers, P2 demodulator register bank, P1 demodulator register bank, stream merger/transport registers, DiSEqC registers, LDPC/BCH metrics, iteration controls, and test registers. P1 and P2 sections are mostly mirrored, which allows `stv0910.c` to select a base P2 macro plus `state->regoff` or use `SET_FIELD()` token-pasting against P1/P2 field names.

Important integration points include `RSTV0910_MID` for probe identity, `RSTV0910_Px_I2CRPT` for tuner repeater control, PLL registers (`NCOARSE*`, `SYNTCTRL`), demod acquisition registers (`DMDISTATE`, `DMDCFGMD`, `DSTATUS`, `DMDMODCOD`), timing/symbol-rate registers (`SFR*`, `TMGREG*`), C/N and power registers, Viterbi/FEC registers, packet delineator and stream-ID registers, TS output registers, BER counter registers, and DiSEqC FIFO/status/config registers.

State and persistence are hardware-facing: the header defines addresses only, while the implementation writes those addresses into device registers and maintains local shadow state separately. There is no persistent software storage.

Risks are definition drift and packed-field correctness. A single bad address, offset, or mask can corrupt unrelated demodulator state, especially because `write_field()` derives register, shift, and mask directly from these constants. Mirrored P1/P2 definitions must stay consistent for `state->regoff` and token-pasted macros to work. Test signals include compile-time use by `stv0910.c`, spot checks against datasheet values where available, runtime probe/tune success, and targeted tests of field writes for representative P1, P2, shared, TS, and DiSEqC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110.c

`stv6110.c` is a DVB tuner driver for the ST STV6110 satellite tuner. It exports `stv6110_attach()`, validates communication with an initial register write, allocates `struct stv6110_priv`, installs `dvb_tuner_ops` into the frontend, and drives tuner frequency, bandwidth, sleep, and readback operations.

`struct stv6110_priv` holds I2C address, I2C adapter, master clock, output clock divider, baseband gain, and an eight-byte register shadow. The shadow is updated by reads and modified before writes, making it the driver's only persistent software state. The implementation uses the demodulator's optional `i2c_gate_ctrl()` around all tuner I2C transfers.

Control flow is straightforward. `stv6110_attach()` writes default register bytes with the requested clock divider, then stores config fields and tuner ops. `stv6110_init()` reinitializes default registers, writes the reference-clock `K` field and output divider, writes all eight registers, sleeps briefly, and sets maximum bandwidth. `stv6110_set_params()` computes carrier width from DVB symbol rate and rolloff, then calls `stv6110_set_frequency()` and `stv6110_set_bandwidth()`.

Frequency programming chooses divider/prescaler ranges from the requested LO, finds the best reference divider against a target phase detector value, computes NDIV with rounding, writes register shadow bytes, starts VCO calibration, polls `STAT1.CALVCOSTRT`, and reads back frequency for debug. Bandwidth programming clamps half-bandwidth to 5-36 MHz, writes the LPF field in `CTRL3`, starts RC calibration, polls `STAT1.CALRCSTRT`, and disables the calibration clock. `get_frequency()` and `get_bandwidth()` decode hardware/shadow register values.

Dependencies are the DVB frontend API, Linux I2C, STV6110 register constants in `stv6110.h`, and optional demodulator I2C-gate serialization. Risks include transfer helpers returning success even after failed `i2c_transfer()` in some paths, register shadow divergence after failed writes, fixed-point PLL rounding edge cases, and lack of timeout errors when calibration bits never clear. Test signals should include attach failure on missing tuner, gate open/close pairing, frequency range boundaries around 1023/1300/2046 MHz, bandwidth clamp boundaries, readback decode, sleep behavior, and debug/error paths for I2C failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110.h

`stv6110.h` is the public attach/configuration header for the STV6110 satellite tuner driver. It defines the eight register indexes used by `stv6110.c` (`CTRL1`, `CTRL2`, `TUNING1`, `TUNING2`, `CTRL3`, `STAT1`, `STAT2`, `STAT3`) and `struct stv6110_config`.

`struct stv6110_config` carries the tuner I2C address, reference/master clock, baseband gain, and output clock divider. Board drivers pass this with a `dvb_frontend` and `i2c_adapter` to `stv6110_attach()`. If `CONFIG_DVB_STV6110` is reachable, the exported implementation is declared; otherwise a static inline stub logs a Kconfig-disabled warning and returns `NULL`.

The header has no runtime persistence or control flow aside from the Kconfig stub. It establishes the ABI between board code and the implementation and exposes register index constants that couple directly to the driver's eight-byte shadow array.

Dependencies are Linux I2C and media DVB frontend definitions. Integration is with demodulator drivers whose frontend ops can provide `i2c_gate_ctrl()` and with bridge/board code that knows the tuner clocking and address.

Risks are ABI/configuration mismatch: `clk_div` and `gain` are raw bitfield values consumed with little validation, and the register index constants must remain aligned with the hardware register order and implementation array size. Test signals include compile coverage with the Kconfig option enabled/disabled, attach with valid and invalid I2C addresses, and board tests confirming `mclk`, gain, and divider values are reflected in tuner register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x.c

`stv6110x.c` is an STV6110(A) silicon tuner driver with two integration paths: a legacy exported `stv6110x_attach()` helper returning a `struct stv6110x_devctl` table, and a normal `i2c_driver` probe path that obtains `struct stv6110x_config` from platform data. It installs minimal DVB tuner ops for release and exposes the real tuner controls through `devctl`.

Runtime state is `struct stv6110x_state` from `stv6110x_priv.h`: frontend, adapter, config pointer, eight-byte register shadow, and `devctl`. `st6110x_init_regs()` seeds default registers; `stv6110x_setup_divider()` applies the configured clock output divider. `stv6110x_set_frontend_opts()` stores the state in `fe->tuner_priv` and installs `stv6110x_ops`.

Control functions include `tuner_init`, `tuner_sleep`, `tuner_set_mode`, `tuner_set_frequency`, `tuner_get_frequency`, `tuner_set_bandwidth`, `tuner_get_bandwidth`, `tuner_set_bbgain`, `tuner_get_bbgain`, `tuner_set_refclk`, and `tuner_get_status`. Frequency setup programs the `K`, divider, prescaler, reference divider, and NDIV fields, starts VCO calibration, and polls `STAT1.CALVCO_STRT`. Bandwidth setup clamps half-bandwidth, programs LPF `CF`, starts RC calibration, polls `STAT1.CALRC_STRT`, and turns the calibration clock off. Mode toggles synthesizer, receiver, and loop-through bits; status maps the lock bit to `TUNER_PHASELOCKED`.

Dependencies are Linux I2C, module/i2c-driver infrastructure, DVB frontend types, and local register/field macros. Unlike `stv6110.c`, this driver does not use the frontend's I2C gate around its own I2C transfers, so integration assumes the adapter path presented to it is already appropriate or externally serialized.

Risks include register shadow divergence on failed writes, attach/probe duplication, platform-data lifetime assumptions, no explicit calibration timeout error if polling expires, and possible bus-access issues when used behind a demodulator gate that the caller does not open. Test signals should cover attach and i2c-driver probe/remove, config callback `get_devctl`, all frequency band thresholds, bandwidth clamps, gain/refclock setters, status lock decode, I2C error propagation, and release idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x.h

`stv6110x.h` is the public interface for the STV6110x tuner. It defines `struct stv6110x_config`, tuner mode/status enums, `struct stv6110x_devctl`, and the Kconfig-gated `stv6110x_attach()` API.

`struct stv6110x_config` provides tuner I2C address, reference clock, output clock divider, frontend pointer, and a callback slot `get_devctl` used by the i2c-driver probe path. `enum tuner_mode` exposes sleep/wake control; `enum tuner_status` currently defines `TUNER_PHASELOCKED`. `struct stv6110x_devctl` is a function table for tuner initialization, sleep, mode, frequency, bandwidth, baseband gain, reference clock, and lock status.

The header's control flow is only Kconfig selection: when `CONFIG_DVB_STV6110x` is reachable, the exported attach function is declared; otherwise an inline stub warns and returns `NULL`. State is owned by the implementation and reached through `fe->tuner_priv` or the returned devctl callbacks.

Dependencies are DVB frontend and I2C client types supplied by includers. Integration is unusual compared with standard DVB tuner ops because most operations are not installed in `fe->ops.tuner_ops`; consumers must keep and call the returned `devctl` table or retrieve it through `config->get_devctl` after I2C probing.

Risks include API misuse when callers expect ordinary tuner ops, config lifetime issues because the implementation stores a config pointer, and raw clock/divider fields with limited validation. Test signals include disabled-Kconfig compile behavior, attach returning non-NULL devctl, probe-populated `get_devctl`, and consumer code calling each callback through the table rather than through absent tuner ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_priv.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_priv.h

`stv6110x_priv.h` contains private logging, bitfield, clock, and state definitions for `stv6110x.c`. It is not a public board-driver interface.

The logging section defines verbosity levels and `dprintk()`, which selects kernel log levels based on the module parameter `verbose` declared in the C file. Bitfield helpers `STV6110x_SETFIELD()` and `STV6110x_GETFIELD()` depend on field offset/width macros from `stv6110x_reg.h`; they are used throughout the tuner code to update shadow registers. Utility macros include `MAKEWORD16`, `LSB`, `MSB`, `TRIALS`, `R_DIV`, and reference clock conversions.

`struct stv6110x_state` is the driver's runtime state: DVB frontend pointer, I2C adapter, config pointer, eight-byte register cache, and devctl pointer. This state persists for the lifetime of the attached tuner or I2C client and is freed by release/remove.

Dependencies are the public `stv6110x_config`/`devctl` declarations, register layout macros, and the `verbose` variable in the implementation. Integration is tight: the setter/getter macros assume identifiers such as `STV6110x_WIDTH_CTRL1_K` and `STV6110x_OFFST_CTRL1_K` exist, and `REFCLOCK_kHz` assumes local functions name their state pointer `stv6110x`.

Risks are macro side effects and type width limits. `STV6110x_SETFIELD()` evaluates its `mask` lvalue more than once and does not range-check `val`; oversized values can spill into neighboring bits before masking behavior is considered. The clock macros are context-sensitive and fragile outside the existing implementation style. Test signals include compile coverage after register macro changes, field set/get round trips for each register field, frequency calculations with unusual refclocks, and verbose logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_reg.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_reg.h

`stv6110x_reg.h` is the compact register map for the STV6110x tuner. It defines the eight register addresses (`CTRL1`, `CTRL2`, `TNG0`, `TNG1`, `CTRL3`, `STAT1`, `STAT2`, `STAT3`) and per-field offset/width constants consumed by `STV6110x_SETFIELD()` and `STV6110x_GETFIELD()`.

The register groups map directly to implementation behavior. `CTRL1` contains reference-clock `K`, low-power/loop-through, receiver, and synthesizer bits. `CTRL2` contains output divider, reference output select, and baseband gain. `TNG0/TNG1` hold PLL divider fields, reference divider, prescaler, and divide-by-four selection. `CTRL3` controls DC loop, RC calibration clock, charge pump, and channel filter. `STAT1` exposes VCO calibration start, RC calibration start, and PLL lock status. `STAT2/STAT3` are address placeholders without field definitions in this header.

There is no runtime state or control flow in the header; it is a data contract for register shadow manipulation in `stv6110x.c`. Persistent effects occur only when the implementation writes shadow bytes to hardware.

Dependencies are private macros in `stv6110x_priv.h`. Integration risk is high because field names are built into macro invocations such as `STV6110x_SETFIELD(regs[STV6110x_CTRL1], CTRL1_K, value)`. Any rename or width/offset error breaks compilation or corrupts tuner programming.

Risks include missing range validation for raw bitfields, silent hardware misconfiguration from wrong offsets, and lack of documentation for STAT2/STAT3. Test signals should include compile coverage, bitfield unit-style checks over all defined fields, frequency/bandwidth programming on hardware, and lock-status readback through `STAT1_LOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6111.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6111.c

`stv6111.c` is a DVB tuner driver for the STV6111 satellite tuner. It exports `stv6111_attach()`, installs standard DVB tuner ops, programs an eleven-byte register cache, tunes LO/bandwidth, and provides RF strength estimation through calibration lookup tables.

`struct stv` holds the I2C adapter/address, register shadow, reference frequency in kHz, and last tuned frequency. Several `struct slookup` tables convert LNA, RF AGC, and channel AGC register readings into gain estimates for NF and IIP3 modes. `muldiv32()` provides fixed-point fractional PLL math.

Attach flow allocates state, stores I2C info, copies tuner ops, initializes the register cache with `init_state()`, opens the demod I2C gate if available, writes all registers through `attach_init()`, closes the gate, and stores `fe->tuner_priv`. `set_params()` accepts only DVB-S/S2, converts frontend frequency from kHz to Hz, computes cutoff as `5 MHz + symbol_rate * 135 / 200`, opens the I2C gate, and calls `set_lof()`. `set_lof()` clamps cutoff index, selects divider mode by frequency, computes integer and fractional PLL values against the 16 MHz reference, selects charge pump by VCO frequency, starts VCO/filter calibration, waits for completion, optionally falls back from LNA IIP3 to NF mode, and records tuned frequency.

`set_bandwidth()` can adjust filter cutoff independently and triggers filter calibration. `get_rf_strength()` reads/uses AGC state, selects the correct lookup table depending on RF/channel and NF/IIP3 modes, applies frequency tilt and baseband gain correction, clamps gain, and returns inverted strength on a 0-10000 scale.

Dependencies are Linux I2C, DVB frontend/tuner ops, optional demodulator I2C gate control, and hardware calibration tables. Persistence is limited to `fe->tuner_priv`, the shadow register array, and hardware registers. Risks include many write/read calls not propagating all errors, assumptions about 16 MHz reference/default register values, lookup-table calibration accuracy, gate imbalance on unexpected failures, and strength estimates depending on stale shadow mode bits. Test signals should cover attach failure, DVB-S/S2 validation, PLL range boundaries, cutoff clamps, calibration timeout, LNA mode fallback, RF strength in NF/IIP3 and channel modes, and I2C gate pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6111.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6111.h

`stv6111.h` is the public attach header for the STV6111 satellite tuner. It exposes `stv6111_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, u8 adr)` when `CONFIG_DVB_STV6111` is reachable and otherwise provides a warning stub returning `NULL`.

The header contains no config structure; board drivers provide only the frontend, tuner I2C adapter, and tuner address. All default register values, reference clock assumptions, and tuner behavior live in `stv6111.c`. Runtime state is allocated by the implementation and stored in `fe->tuner_priv`.

Dependencies are DVB frontend and I2C adapter declarations supplied by includers. Integration is with satellite demodulator drivers that expose an I2C gate and with board code that knows the tuner address. The implementation installs standard tuner ops, so consumers use normal DVB tuning paths after attach.

Risks are mostly hidden defaults: because this header has no explicit clock or gain configuration, board designs that differ from the implementation assumptions cannot express those differences through the API. Disabled-Kconfig behavior must also be acceptable to callers. Test signals include compile with enabled/disabled Kconfig, attach on boards with expected 16 MHz reference configuration, and normal frontend tuning through installed tuner ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6111.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tc90522.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tc90522.c

`tc90522.c` is an I2C driver for Toshiba TC90522 ISDB-S and ISDB-T demodulator submodules. The file notes that the driver is incomplete: chip init/configuration is not public and is expected to be performed by a parent device before this frontend is initialized. The driver supplies DVB frontend ops, status/statistic decoding, tuning handoff to an attached tuner, IF AGC control, sleep/wake, and a child I2C adapter for tuner access through the demodulator.

`struct tc90522_state` embeds a copy of `struct tc90522_config`, a `dvb_frontend`, the parent `i2c_client`, a tuner `i2c_adapter`, and an LNA flag. `reg_write()` and `reg_read()` implement simple demod register transactions. Probe chooses satellite or terrestrial ops from the I2C device id, copies frontend ops, creates the tuner adapter with `tc90522_tuner_i2c_algo`, returns `cfg->fe` and `cfg->tuner_i2c` to the caller, and stores config as client data. Remove deletes the child adapter and frees state.

Satellite control includes TSID programming, status decoding from registers `0xc3`/`0xc5`, frontend decode of stream id, high/low layer modulation/FEC/slots, CNR polynomial conversion from register `0xbc`, and per-layer post-error counters from `0xeb`. Terrestrial control includes layer enable masking, status decoding from `0x96`/`0x80`, TMCC/layer decode from `0xb0`/`0xb2`, CNR conversion using `intlog10()` from `0x8b`, and per-layer counters from `0x9d`.

`tc90522_set_frontend()` first calls tuner `set_params()`, then programs TSID or terrestrial layer selection and resets the relevant demod block. `tc90522_init()` wakes the chip, optionally toggles LNA for terrestrial auto mode, defaults ISDB-T layer enable to all layers, and enables IF AGC. `tc90522_sleep()` writes sleep registers and may disable LNA in auto mode. Tune settings differ for ISDB-S and ISDB-T.

The child tuner adapter wraps each tuner message through register `0xfe`, rewriting target tuner address and data into demod pass-through transactions. It can split read transactions for parent devices that require that behavior. Risks include reliance on external firmware initialization, fixed register magic values, stack `wbuf[256]` capacity for rewritten I2C messages, split-transfer corner cases, possible stale LNA/property-cache manipulation, and statistics formulas sensitive to integer scaling. Test signals should cover both I2C IDs, probe/remove adapter lifetime, tuner pass-through writes/reads including split reads and overflow rejection, set_frontend failure paths, sleep/wake with LNA auto, ISDB-S/ISDB-T status thresholds, layer decode, CNR scaling, and per-layer counter lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tc90522.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tc90522.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tc90522.h

`tc90522.h` is the public interface for the Toshiba TC90522 demodulator driver. It documents the hardware model: a chip has four inputs, two ISDB-T and two ISDB-S, exposed as independent submodules with separate I2C addresses, so this driver treats each submodule as one demodulator device.

The header defines I2C device type strings `TC90522_I2C_DEV_SAT` and `TC90522_I2C_DEV_TER`, used by board/bridge drivers when creating I2C clients. `struct tc90522_config` is the platform-data contract: the driver writes back `fe` and `tuner_i2c`, and callers provide `split_tuner_read_i2c` to request separated read transactions through the demodulator's tuner pass-through adapter.

There is no executable control flow in this header. State is returned through output fields after `tc90522_probe()` copies platform data into its private state and creates the DVB frontend plus child tuner adapter.

Dependencies are Linux I2C and DVB frontend definitions. Integration is with parent bridge drivers that perform undisclosed chip initialization, instantiate satellite or terrestrial submodule I2C clients, then attach tuners through the returned `tuner_i2c` adapter.

Risks include the mutable platform-data contract: callers must keep a writable config structure and must read output fields only after successful probe. The `split_tuner_read_i2c` flag changes low-level I2C transfer grouping and must match parent adapter behavior. Test signals include client creation with both device strings, probe output field population, tuner attach through `tuner_i2c`, and split/non-split tuner read behavior on affected hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tc90522.h -->
