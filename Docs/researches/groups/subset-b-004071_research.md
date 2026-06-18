# subset-b-004071 research

This grouped report covers the requested DVB frontend driver files from the Ceph client source snapshot. Each file has its own source-path-titled section wrapped with reconciliation markers, and the corresponding per-file reports are emitted under the mirrored `Docs/researches/<source_path>_research.md` layout.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16.c

## Purpose
`mb86a16.c` implements the Fujitsu MB86A16 DVB-S/DSS frontend. It is an attach-style demodulator driver that programs the demodulator and integrated RF control registers over I2C, performs a custom satellite signal search, reports DVB frontend lock/statistics, and exposes DiSEqC tone/burst/message callbacks.

## Important APIs, Types, And Functions
The central state is `struct mb86a16_state`, holding the I2C adapter, board config, embedded `dvb_frontend`, current frequency/symbol rate, and symbol-rate-derived clock selection fields. `mb86a16_attach()` probes register `0x7f` for device id `0xfe`, installs `mb86a16_ops`, and passes through the board `set_voltage` callback. Low-level I/O is handled by `mb86a16_write()` and `mb86a16_read()`. Tuning is driven by `mb86a16_search()` and the large `mb86a16_set_fe()` state machine. Status/statistics callbacks include `mb86a16_read_status()`, `mb86a16_read_ber()`, `mb86a16_read_signal_strength()`, `mb86a16_read_snr()`, and `mb86a16_read_ucblocks()`. Satellite-control callbacks are `mb86a16_send_diseqc_msg()`, `mb86a16_send_diseqc_burst()`, and `mb86a16_set_tone()`.

## Control Flow
The search callback converts DVBv5 cached `frequency` and `symbol_rate` from Hz/symbols per second into MHz and ksymbols per second, then calls `mb86a16_set_fe()`. The tuning algorithm initializes demodulator filter/AGC/FEC defaults, derives decimation and master clock from the requested symbol rate, selects VCO divider mode, sweeps possible oscillator offsets around the requested transponder frequency, and records signal meter samples in a signed offset array. Candidate signal peaks are de-duplicated and checked by `signal_det()` using symbol-rate perturbation. Once a signal is found, the driver switches from external AFC search to AFC correction, refines frequency with AFC and DAGC measurements, then programs final carrier recovery, Viterbi thresholds, IQ inversion handling, FEC reset, and sequence mode before declaring lock. The algorithm retries the whole acquisition path up to three times.

The status path reads signal registers, carrier/sync bits, and frame sync before setting standard `FE_HAS_*` flags. Statistics are read directly from MB86A16 monitor registers. DiSEqC master messages validate length 4-5, copy bytes to DCC registers, and trigger transmission; tone and mini-burst callbacks toggle the demodulator's tone/DCC output bits.

## State And Persistence
The driver has no persistent storage. Runtime state is the allocated `mb86a16_state`, with `frequency`, `srate`, `master_clk`, `deci`, `csel`, and `rsel` updated during tuning. Hardware state persists only in device registers until reset/power cycling. `init()` and `sleep()` are no-ops, so any board-level power management is outside this file. The module parameter `verbose` controls kernel logging detail.

## Dependencies And Integration Points
The file depends on the Linux I2C core, DVB frontend core, `mb86a16.h` for board config/attach contract, and `mb86a16_priv.h` for register names. It integrates with board drivers through `mb86a16_attach()`, optional frontend `set_voltage`, and tuner/LNB control through DVB SEC callbacks. Timing is implemented with `udelay()`, `msleep()`, and `msleep_interruptible()` in the tuning path.

## Risks
The tuning logic is highly register- and timing-sensitive; small arithmetic or delay changes can break lock acquisition for marginal symbol rates. Several helper failures return `-1` instead of kernel errno values, which makes error classification coarse. `mb86a16_read_ber()` uses `2 ^ timer`, which is C bitwise XOR rather than exponentiation and is a likely BER scaling bug. The sweep arrays assume offsets remain within the `V[60]` range after biasing by 30; the computed sweep bounds are intended to enforce that but are worth guarding in future changes. Signal strength and SNR callbacks rescale values in non-obvious ways after logging a different percentage/dB interpretation.

## Test Signals
Useful signals are successful attach with id `0xfe`, lock acquisition across low/high symbol rates, DVB-S transponder scans at edge frequencies 950 and 2150 MHz, DiSEqC message/burst/tone tests, LNB voltage passthrough from board config, status transitions from no signal to lock, BER/SNR/strength monotonicity checks, and I2C fault injection through every multi-register tuning sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16.h

## Purpose
`mb86a16.h` is the public integration header for the Fujitsu MB86A16 DVB-S frontend. It gives board drivers the configuration structure and the conditional `mb86a16_attach()` entry point.

## Important APIs, Types, And Functions
`struct mb86a16_config` contains the demodulator I2C address and an optional `set_voltage()` callback used to wire board-specific LNB voltage handling into the frontend ops. When `CONFIG_DVB_MB86A16` is reachable, the header declares `mb86a16_attach(const struct mb86a16_config *, struct i2c_adapter *)`; otherwise it provides a stub that logs that the driver is disabled and returns `NULL`.

## Control Flow
The header has no executable driver control flow beyond the Kconfig-disabled inline stub. Runtime behavior is implemented in `mb86a16.c`, which copies the frontend ops and assigns `ops.set_voltage` from this config.

## State And Persistence
The config is supplied by the caller and retained by pointer in `mb86a16_state`; it must outlive the attached frontend. No persistent state is defined here.

## Dependencies And Integration Points
The header includes DVB frontend types from `linux/dvb/frontend.h` and `media/dvb_frontend.h`, and is consumed by board adapter drivers and `mb86a16.c`.

## Risks
The lifetime of `struct mb86a16_config` is external to the driver. A missing or invalid `demod_address` prevents attach, and a board-supplied `set_voltage` implementation becomes part of frontend behavior without additional validation in this header.

## Test Signals
Build coverage with `CONFIG_DVB_MB86A16=y/m/n`, successful attach from a board driver, and voltage callback exercise through DVB SEC ioctls cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16_priv.h

## Purpose
`mb86a16_priv.h` defines the private MB86A16 register addresses and bit masks used by the demodulator implementation.

## Important APIs, Types, And Functions
The file is a macro-only register map. It names transport output, FEC, AGC, symbol-rate, Viterbi, frame-sync, carrier/filter, reset/status, BER, DiSEqC, tone, frequency, AFC, signal, VIMAG/VISET, and monitor registers. Bit masks such as `MB86A16_TSOUT_*`, `MB86A16_FEC_*`, `MB86A16_DCC1_*`, and `MB86A16_DCCOUT_DISEN` document individual fields used by `mb86a16.c`.

## Control Flow
There is no control flow. The C file uses these constants in ordered I2C write/read sequences for initialization, tuning, status reporting, BER/SNR/strength reads, DiSEqC control, and tone generation.

## State And Persistence
The header defines the address space but no state. Values written to these registers are transient hardware state owned by the demodulator.

## Dependencies And Integration Points
The header is private to the MB86A16 driver and is included after `mb86a16.h`. It is part of the source-level contract between the tuning algorithm and the chip data sheet.

## Risks
Wrong register numbers or bit masks directly produce wrong hardware programming. A few macro names have inconsistent capitalization (`Mb86A16_*`), which is harmless only because users reference the exact macro names. Register aliases for literal addresses used in `mb86a16.c` are incomplete, so future maintenance can accidentally duplicate or mislabel magic values.

## Test Signals
Coverage is indirect: module build, attach, acquisition, SEC control, and statistics reads all validate subsets of the register map. Hardware regression tests are the meaningful signal because compile tests cannot detect incorrect numeric constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a16_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a20s.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a20s.c

## Purpose
`mb86a20s.c` implements the Fujitsu MB86A20S ISDB-T/ISDB-Tsb frontend. It initializes a register-heavy demodulator, coordinates tuner programming through the DVB frontend I2C gate, handles 13-segment/partial/1-segment modes, reports TMCC-derived frontend parameters, and accumulates DVBv5 signal statistics for the global channel and ISDB-T layers A/B/C.

## Important APIs, Types, And Functions
`struct mb86a20s_state` stores the I2C adapter, board config, frontend, IF frequency, bandwidth mode, inversion, subchannel, per-layer estimated BER sampling rates, cached strength timestamp, and reinit state. Low-level access goes through `mb86a20s_i2c_writereg()`, `mb86a20s_i2c_writeregdata()`, and `mb86a20s_i2c_readreg()`. Initialization is `mb86a20s_initfe()`, tuning is `mb86a20s_set_frontend()` and `mb86a20s_tune()`, and lock/stat reporting is `mb86a20s_read_status_and_stats()`. TMCC decoders include `mb86a20s_get_modulation()`, `mb86a20s_get_fec()`, `mb86a20s_get_interleaving()`, `mb86a20s_get_segment_count()`, and `mb86a20s_get_frontend()`. Statistics helpers include pre/post BER, PER/block error, main CNR, per-layer MER-to-CNR, and signal strength.

## Control Flow
Attach allocates state, copies `mb86a20s_ops`, reads revision register `0`, and accepts only revision `0x13`. `initfe()` closes the tuner gate, runs two fixed initialization tables, applies inversion, bandwidth and subchannel settings, calculates IF/NCO values from board clock and tuner IF, configures serial/parallel TS output, then reopens the I2C gate. Failures leave `need_init` true for later retry.

`set_frontend()` chooses 1seg, 13seg partial, or 13seg mode from cached DVB properties, maps ISDB-Tsb subchannels, opens the gate for tuner `set_params`, always reruns demod initialization for reliability, resets reception and counters, then marks stats unavailable. `read_status_and_stats()` closes the gate, reads demod acquisition state from register `0x0a`, caches signal strength through a binary-search comparator algorithm, and when state is at least 7 reads TMCC parameters. Full BER/PER collection is gated on state 9. Per-layer counters are read only when ready bits are set; the driver then resets or updates hardware counters based on the estimated bit rates derived from modulation, FEC, guard interval, and segment count.

## State And Persistence
State is in-memory and in hardware registers only. `last_frequency` decides when DVBv5 counters are cleared. `estimated_rate[]` persists across status reads to tune future hardware BER/PER collection windows. `get_strength_time` caches signal strength for one second. The driver accumulates DVBv5 counter stats in `dtv_property_cache`; channel changes reset those counters.

## Dependencies And Integration Points
The file depends on Linux I2C, DVB frontend core, `asm/div64.h`, and `mb86a20s.h`. It calls tuner `set_params()` and `get_if_frequency()` and uses optional `i2c_gate_ctrl()` around demod/tuner access. It implements the DVBv5 stats API using `dtv_frontend_properties` counter and decibel scales.

## Risks
The initialization tables are magic values from USB snooping and are difficult to reason about without hardware documentation. Register gate direction is subtle; wrong gate state can break tuner access or demod access. Several error paths intentionally return success to userspace after failed optional stats reads, so regressions can hide behind a locked status. The main CNR read appears to read register `0x46` twice after setting the high byte, which may be intentional latch behavior or a typo; it is a point to verify on hardware. Counter scaling depends on TMCC parsing, so incorrect layer enable/segment values skew BER/PER windows.

## Test Signals
Useful tests include attach revision detection, init with default and non-default `fclk`, serial and parallel TS modes, tuner IF changes, 1seg/partial/13seg scans, ISDB-Tsb subchannel selection, lock-state progression, DVBv5 stats availability before/after lock, long-running BER/PER counter accumulation, I2C gate sequencing with tuner drivers, and fault injection for register-table writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a20s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a20s.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a20s.h

## Purpose
`mb86a20s.h` is the public board-driver contract for the Fujitsu MB86A20S ISDB-T demodulator.

## Important APIs, Types, And Functions
`struct mb86a20s_config` provides the input clock frequency, demodulator I2C address, and TS output mode (`is_serial`). `mb86a20s_attach()` is declared when the driver is reachable and replaced with a warning stub otherwise.

## Control Flow
The header has no active control flow beyond the disabled-driver stub. `mb86a20s.c` reads `fclk`, `demod_address`, and `is_serial` during attach/init and uses them to compute IF registers and TS output configuration.

## State And Persistence
Configuration is caller-owned and retained by pointer in the demodulator state. There is no persistent state in the header.

## Dependencies And Integration Points
The header depends on DVB frontend declarations and is included by adapter/bridge drivers that instantiate the demodulator.

## Risks
Wrong `fclk` or TS mode values cause valid I2C attach with broken demodulation or transport output. Because the config is referenced rather than copied, its lifetime must exceed the frontend lifetime.

## Test Signals
Builds across Kconfig states, attach from board code, initialization with serial and parallel TS output, and tuner IF programming validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mb86a20s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88443x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88443x.c

## Purpose
`mn88443x.c` implements the Socionext MN88443x ISDB-S/ISDB-T demodulator family as an I2C driver. It supports primary and secondary chip variants, manages clock/reset resources, creates separate regmaps for satellite and terrestrial register banks, switches the active delivery system, programs IF/clock parameters, and reports lock, strength, CNR, and post-BER statistics.

## Important APIs, Types, And Functions
`struct mn88443x_priv` stores the frontend, clock, reset GPIO, clock/IF configuration, variant spec, and two I2C clients/regmaps. `mn88443x_probe()` is the resource acquisition and frontend creation path, while `mn88443x_remove()` powers off and unregisters the dummy terrestrial client. Common power helpers are `mn88443x_cmn_power_on()` and `mn88443x_cmn_power_off()`. ISDB-S helpers include `mn88443x_s_sleep()`, `mn88443x_s_wake()`, `mn88443x_s_tune()`, and `mn88443x_s_read_status()`. ISDB-T helpers include `mn88443x_t_sleep()`, `mn88443x_t_wake()`, `mn88443x_t_is_valid_clk()`, `mn88443x_t_set_freq()`, `mn88443x_t_tune()`, and `mn88443x_t_read_status()`. DVB callbacks are collected in `mn88443x_ops`.

## Control Flow
Probe chooses variant data from device tree match data or I2C id data, obtains `mclk`, reads `if-frequency` unless platform data is used, gets optional reset GPIO, initializes an ISDB-S regmap on the probed client and an ISDB-T regmap on a dummy client at address `client->addr + 4`, copies frontend ops, powers on the chip, and sleeps both demods. Power-on enables the master clock, pulses reset, then configures output/HIZ registers differently for primary versus secondary variants.

`set_frontend()` switches by `delivery_system`. ISDB-S wakes the satellite block, sleeps terrestrial, selects ISDB-S TS/interrupt routing, writes stream id registers, and sets satellite output. ISDB-T sleeps satellite, wakes terrestrial, validates and programs clock/NCO/FAD/ADC/AGC settings in `mn88443x_t_set_freq()`, selects ISDB-T TS/interrupt routing, and starts auto mode. Tuner `set_params()` is called with the I2C gate opened and then closed. `read_status()` dispatches to the active delivery system. Satellite status reads CPMON lock bits, AGC, CNR using integer log math, and post-Viterbi BER. Terrestrial status reads sequence state, AGC, CNR, and post-BER length/error counters.

## State And Persistence
Persistent configuration is from firmware/device tree/platform data: variant, clock, reset GPIO, and IF frequency. Runtime state is the `mn88443x_priv` allocation and hardware registers. There is no firmware download or on-disk state. DVB stats are written into `dtv_property_cache` on each status read and marked unavailable when preconditions are not met.

## Dependencies And Integration Points
The driver uses the kernel I2C-driver model, regmap, common clock framework, GPIO descriptors, OF match data, integer log helpers, and DVB frontend callbacks. Board/platform integration can use `struct mn88443x_config` via platform data to receive the created frontend pointer.

## Risks
Clock and IF validation is central: invalid combinations return `-EINVAL`, while wrong but accepted values can silently prevent lock. The clock-buffer branch marks `use_clkbuf` but comments that it is not supported and leaves `adckt` zero, so only valid clock regimes should be supplied. `set_frontend()` ignores return values from some regmap operations and from `mn88443x_t_set_freq()`, which can hide programming failures. Dummy-client lifetime must stay paired on every probe error and remove path. CNR math uses integer-log approximations and can underflow/overflow if register values are unexpected.

## Test Signals
Validate OF and platform-data probe, primary/secondary variants, reset polarity, clock enable/disable, dummy client registration, ISDB-S and ISDB-T tuning, IF frequency boundary cases, tuner I2C gate sequencing, status/stat reads under no signal and lock, and remove/unbind cleanup with fault injection at each resource allocation stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88443x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88443x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88443x.h

## Purpose
`mn88443x.h` defines the public platform-data interface and IF-frequency constants for the Socionext MN88443x ISDB-S/ISDB-T demodulator driver.

## Important APIs, Types, And Functions
The constants `DIRECT_IF_57MHZ`, `DIRECT_IF_44MHZ`, and `LOW_IF_4MHZ` describe supported IF regimes. `struct mn88443x_config` carries the master clock, IF frequency, reset GPIO, and an output `struct dvb_frontend **fe` for non-DT platform integration.

## Control Flow
The header has no executable flow. `mn88443x_probe()` consumes the structure when `client->dev.platform_data` is present and writes back the frontend pointer.

## State And Persistence
The config is platform-provided setup state; the driver copies scalar values and resource pointers into `mn88443x_priv`. No persistent hardware state is defined here.

## Dependencies And Integration Points
It includes DVB frontend types and forward-uses kernel `clk` and GPIO descriptor types supplied by including code. It bridges legacy platform data users with the modern I2C driver implementation.

## Risks
Supplying an unsupported IF frequency or mismatched master clock causes tuning failure. The frontend pointer field must be valid for platform-data users; otherwise the caller has no handle to the created frontend.

## Test Signals
Compile with platform-data users, probe with each IF constant, and verify that `*fe` is populated and usable for tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88443x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472.c

## Purpose
`mn88472.c` implements the Panasonic MN88472 DVB-T/DVB-T2/DVB-C Annex A demodulator as an I2C driver with firmware download support. It manages three register-bank I2C clients, initializes firmware and TS output, tunes terrestrial/cable delivery systems, and reports lock, strength, CNR, and block-error counters.

## Important APIs, Types, And Functions
The driver state is `struct mn88472_dev` from the private header. `mn88472_probe()` allocates state, builds regmaps for the base client plus dummy clients at `0x1a` and `0x1c`, checks chip id `0x02`, installs `mn88472_ops`, initializes stats lengths, and returns the frontend through platform data. `mn88472_init()` powers up, conditionally downloads `dvb-demod-mn88472-02.fw`, configures TS mode and TS clock, and marks the device active. Tuning is `mn88472_set_frontend()`. Status/statistics are in `mn88472_read_status()`. `mn88472_sleep()` powers down selected blocks, and `mn88472_remove()` releases regmaps, dummy clients, and memory.

## Control Flow
Initialization first clears power-down bits in bank 2, checks firmware-running bit `regmap[0] 0xf5`, and skips download on warm firmware. Cold firmware download writes `0x03` to `0xf5`, streams firmware chunks to `0xf6` bounded by `i2c_write_max - 1`, checks parity/status register `0xf8`, then starts firmware with `0xf5 = 0`. The warm path configures serial/parallel TS and fixed/variable TS clock based on platform data.

`set_frontend()` rejects inactive devices, maps the requested delivery system to demod mode and bank-specific tuning constants, validates DVB-T/T2 bandwidth, calls tuner `set_params()` and `get_if_frequency()`, writes demod mode, bandwidth and IF registers, applies bandwidth filter coefficients, programs delivery-system-specific bank registers, writes DVB-T2 PLP/stream id when requested, and resets the FSM. `read_status()` uses different lock-state registers for DVB-T, DVB-T2, and DVB-C, then reads common strength, delivery-system-specific CNR formulas, and PER/block counters when synchronized.

## State And Persistence
The active flag gates tuning/status after firmware init. Clock, TS mode, TS clock, and I2C write limit come from platform data and remain in `mn88472_dev`. Firmware is external persistent data under the kernel firmware search path; once running, the chip can take the warm path. DVBv5 block counters accumulate in the frontend property cache across reads until userspace/core resets them.

## Dependencies And Integration Points
The driver depends on I2C dummy clients, regmap, firmware loader, DVB frontend core, and `linux/int_log.h` for CNR calculations. It integrates with a separate tuner via frontend tuner ops and exposes `get_dvb_frontend` through platform data for bridge drivers.

## Risks
Firmware availability and chunk size handling are critical; `i2c_write_max` defaults to `~0`, so adapters with real transfer limits should set it correctly. Register bank 2 is documented as not supporting sequential I/O, and the driver mostly uses single-register operations for that bank; future bulk writes there would be risky. The probe path assumes valid platform data and frontend pointer. CNR formulas and status thresholds are delivery-system-specific and easy to regress. `sleep()` powers down hardware but does not clear `active`, so callers may attempt operations after sleep depending on DVB core sequencing.

## Test Signals
Test cold and warm firmware init, missing/bad firmware, I2C write-limit chunking, chip-id rejection, all cleanup error paths for three clients/regmaps, DVB-T 5/6/7/8 MHz tuning, DVB-T2 PLP selection, DVB-C tuning, tuner IF handoff, status under no signal/partial lock/full lock, CNR sanity, and block counter accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472.h

## Purpose
`mn88472.h` defines platform data for the Panasonic MN88472 demodulator and preserves older macro names for TS clock/mode values.

## Important APIs, Types, And Functions
Compatibility macros map `VARIABLE_TS_CLOCK`, `FIXED_TS_CLOCK`, `SERIAL_TS_MODE`, and `PARALLEL_TS_MODE` to the `MN88472_*` enum-like defines. `struct mn88472_config` supplies crystal frequency, TS mode, TS clock selection, maximum I2C write size, an output frontend pointer, and a `get_dvb_frontend()` callback slot filled by the driver.

## Control Flow
No executable control flow is defined. `mn88472_probe()` reads this platform data and writes back `*fe` and `get_dvb_frontend`.

## State And Persistence
The config initializes runtime state but is not persistent. Firmware persistence is declared in the C/private files, not here.

## Dependencies And Integration Points
It includes DVB frontend declarations and is used by bridge drivers that instantiate the MN88472 I2C client.

## Risks
Missing or invalid platform data can crash or fail probe because the C file expects fields such as `fe` and timing values. Wrong TS mode/clock settings produce transport-stream failures even if RF lock works.

## Test Signals
Build coverage for legacy macro users, probe with serial/parallel and fixed/variable TS settings, frontend pointer population, and bridge callback use cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472_priv.h

## Purpose
`mn88472_priv.h` contains private includes, firmware name, and the internal runtime state for the MN88472 driver.

## Important APIs, Types, And Functions
`MN88472_FIRMWARE` names `dvb-demod-mn88472-02.fw`. `struct mn88472_dev` stores three I2C clients, three regmaps, the embedded `dvb_frontend`, maximum I2C write size, crystal clock, active flag, TS mode, and TS clock.

## Control Flow
There is no control flow. `mn88472.c` uses the structure for probe/init/tune/status/sleep/remove and the firmware macro in `request_firmware()` and `MODULE_FIRMWARE()`.

## State And Persistence
The structure is in-memory per-device state. Firmware is loaded from the kernel firmware filesystem and then resident on the demodulator until reset/power loss.

## Dependencies And Integration Points
It includes DVB frontend, integer log, public config, firmware loader, and regmap headers. It is private to `mn88472.c`.

## Risks
The bitfield active/TS fields are compact but rely on values from the public header staying within one bit. Client/regmap arrays require consistent bank indexing throughout the driver.

## Test Signals
Compile, probe/remove leak checks, firmware request path, and all three-bank tuning/status paths cover this private contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473.c

## Purpose
`mn88473.c` implements the Panasonic MN88473 DVB-T/DVB-T2/DVB-C Annex A demodulator. It is a close successor to MN88472 with a different chip id, firmware image, register constants, and statistics layout, using three I2C register banks and exposing a DVB frontend through platform data.

## Important APIs, Types, And Functions
`mn88473_probe()` allocates `struct mn88473_dev`, configures `i2c_wr_max` and clock defaults, initializes three regmaps/clients, checks chip id `0x03`, sleeps the active-by-default chip, copies `mn88473_ops`, and returns the frontend pointer. `mn88473_init()` downloads `dvb-demod-mn88473-01.fw` when needed, validates parity, configures TS output, marks the frontend active, and initializes DVBv5 stat capabilities. `mn88473_set_frontend()` programs delivery-system, bandwidth/cable coefficients, IF registers, PLP, and reset. `mn88473_read_status()` maps lock and quality registers into frontend status and stats. `mn88473_sleep()` clears active and powers down, and `mn88473_remove()` tears down regmaps and dummy clients.

## Control Flow
Probe requires `config->fe`, creates dummy clients at `0x1a` and `0x1c`, and rejects non-MN88473 ids. Init checks firmware-running bit in bank 0 register `0xf5`; cold init requests firmware, writes download mode, streams chunks to `0xf6`, releases firmware, checks parity in `0xf8`, then starts firmware. The warm path writes TS output registers and sets supported stat lengths/scales.

Tuning rejects inactive devices and unsupported delivery systems/bandwidths, calls tuner `set_params()` and `get_if_frequency()`, calculates three IF register bytes as `if_frequency * 0x1000000 / clk`, writes common bank-2 setup, writes DVB-T/T2 bandwidth or DVB-C config coefficients, applies a large common tuning register script, sets DVB-T2 PLP from `stream_id`, and resets the FSM. Status reads system-specific lock/error bits, strength from AGC registers, CNR using integer-log formulas for DVB-T, DVB-T2 SISO/MISO, or DVB-C, post-BER for DVB-T/DVB-C only, and PER/block counters for all locked modes.

## State And Persistence
Runtime state includes active flag, clock, write limit, frontend, clients, and regmaps. `active` is false after sleep and true after successful init, unlike MN88472's sleep path. Firmware is external persistent input and hardware-resident runtime state. DVB statistics accumulate in `dtv_property_cache` counters.

## Dependencies And Integration Points
The driver depends on I2C/regmap, firmware loader, DVB frontend core, `linux/int_log.h`, `linux/math64.h`, and a tuner connected through frontend tuner ops. It is instantiated by bridge code using `struct mn88473_config`.

## Risks
The C file assumes non-null platform data before dereferencing `config->fe`; invalid board data is fatal. Firmware load and parity check are mandatory for cold devices. Bank 2 single-register limitations must be preserved. Status must initialize `*status` on every path; current branches set it to zero only in several failure conditions, so stale caller values are a possible hazard if a branch does not assign before returning success. Delivery-system register scripts are opaque and sensitive to ordering.

## Test Signals
Test chip-id rejection, missing/bad firmware, warm firmware skip, TS output after init, sleep/init active gating, DVB-T 6/7/8 MHz tuning, DVB-T2 PLP, DVB-C coefficients, tuner IF handoff, status no-signal and full-lock cases, CNR formulas for SISO/MISO/cable, post-BER/PER counters, and error cleanup for every regmap/dummy-client allocation step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473.h

## Purpose
`mn88473.h` defines the platform-data structure for board drivers that instantiate the Panasonic MN88473 demodulator.

## Important APIs, Types, And Functions
`struct mn88473_config` contains an optional maximum I2C write size, optional crystal frequency defaulting to 25 MHz, and an output `struct dvb_frontend **fe` that the driver fills on successful probe.

## Control Flow
The header has no executable flow. `mn88473_probe()` consumes the structure and requires `fe` to be non-null.

## State And Persistence
The fields initialize runtime state in `mn88473_dev`; no persistent state is stored here.

## Dependencies And Integration Points
It includes `linux/dvb/frontend.h` and is used by bridge/platform code.

## Risks
If `i2c_wr_max` is too large for the adapter, firmware download can fail. If `xtal` is wrong, IF register calculations are wrong. If `fe` is absent, probe fails.

## Test Signals
Build with board users, probe with default and explicit clock/write-limit values, verify frontend pointer population, and cold firmware download on adapters with constrained I2C writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473_priv.h

## Purpose
`mn88473_priv.h` provides the private firmware name and runtime device structure for `mn88473.c`.

## Important APIs, Types, And Functions
`MN88473_FIRMWARE` is `dvb-demod-mn88473-01.fw`. `struct mn88473_dev` stores the three I2C clients, three regmaps, embedded frontend, I2C write limit, active flag, and demodulator clock.

## Control Flow
There is no executable flow. The C file uses these definitions for firmware loading, frontend callbacks, and register-bank access.

## State And Persistence
The structure is per-device in-memory state. The firmware file is an external runtime dependency and is not embedded in the driver.

## Dependencies And Integration Points
It includes DVB frontend, integer log, math64, firmware, regmap, and the public MN88473 config header.

## Risks
Bank index misuse is the main risk because the same numeric register can mean different things on each regmap. Firmware filename changes must be coordinated with packaging and `MODULE_FIRMWARE()`.

## Test Signals
Compile, firmware request, three-bank probe/remove, active gating, and tune/status tests cover this private header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312.c

## Purpose
`mt312.c` implements the Zarlink VP310/MT312/ZL10313 DVB-S satellite demodulator family. It is an attach-style I2C frontend driver that initializes chip-specific clock/ADC/MPEG settings, programs symbol rate/FEC/inversion, exposes tuner I2C gate control, reports status/statistics, and controls LNB voltage, tone, and DiSEqC messages.

## Important APIs, Types, And Functions
`struct mt312_state` stores the I2C adapter, board config, frontend, detected chip id, crystal frequency, and clock multiplier. Low-level access is `mt312_read()`, `mt312_write()`, `mt312_readreg()`, and `mt312_writereg()`. `mt312_attach()` probes the ID register, chooses model name, xtal, and `freq_mult`, and returns the frontend. Main callbacks include `mt312_initfe()`, `mt312_sleep()`, `mt312_set_frontend()`, `mt312_get_frontend()`, `mt312_i2c_gate_ctrl()`, `mt312_read_status()`, statistics readers, DiSEqC callbacks, tone, and voltage control.

## Control Flow
Initialization wakes the chip via `CONFIG`, waits, performs a full reset, writes Viterbi setup defaults, performs ZL10313-specific ADC/MPEG setup, programs system clock and DiSEqC ratio from xtal/frequency multiplier, sets SNR threshold, output control, sweep limits, and carrier sweep limit. VP310 tuning dynamically switches between 60 MHz and 90 MHz internal clock based on whether symbol rate is above 30 MS/s.

`set_frontend()` validates frequency, inversion, symbol rate, and FEC, calls tuner `set_params()` and closes the I2C gate, calculates the symbol rate register, maps inversion and FEC into `VIT_MODE`, sets QPSK control with I/Q swap and AFC for low symbol rates, writes the register sequence from `SYM_RATE_H`, then issues a soft reset/go. `get_frontend()` reads back inversion, symbol rate monitor values, and FEC status, although the symbol-rate helper currently logs derived rates rather than assigning `*sr`. Status/statistics read raw demodulator registers. SEC callbacks write DiSEqC FIFO/mode fields, mini-burst/tone bits, or voltage bit in `DISEQC_MODE`.

## State And Persistence
Runtime state is only `mt312_state` and hardware registers. The detected `id`, `xtal`, and `freq_mult` persist for the frontend lifetime and determine register calculations. There is no firmware or persistent storage. `debug` is a module parameter.

## Dependencies And Integration Points
The file depends on Linux I2C, DVB frontend, `mt312.h` for config/attach, and `mt312_priv.h` for register definitions and chip ids. Board drivers integrate through `mt312_attach()`, tuner ops, and the optional I2C gate. Satellite equipment control is exposed directly through DVB frontend ops.

## Risks
The maximum write size is fixed at 64 bytes; larger register scripts fail. The ZL10313 `GPP_CTRL` path must preserve the ADC-enable bit while toggling the tuner gate. Voltage control overwrites `DISEQC_MODE`, so interactions with current tone/burst state are delicate. `mt312_get_symbol_rate()` does not store the computed symbol rate into the caller-provided pointer, which can leave `get_frontend()` with stale data. Model-specific clock switching on VP310 is timing-sensitive and reinitializes the frontend mid-tune.

## Test Signals
Exercise attach for all three chip ids and unsupported ids, init/sleep, tuner gate open/close, VP310 symbol-rate clock switching, valid/invalid FEC and inversion inputs, DVB-S lock acquisition, BER/SNR/strength/ucblocks reads, LNB voltage inversion, tone on/off, DiSEqC master messages and bursts, and I2C error injection on read/write sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312.h

## Purpose
`mt312.h` is the public attach/config header for Zarlink VP310/MT312/ZL10313 DVB-S demodulators.

## Important APIs, Types, And Functions
`struct mt312_config` supplies the demodulator I2C address and a one-bit `voltage_inverted` setting for LNB voltage control. `mt312_attach()` is declared when `CONFIG_DVB_MT312` is reachable and replaced with a disabled-driver warning stub otherwise.

## Control Flow
No driver flow exists here beyond the Kconfig stub. `mt312.c` consumes the config in low-level I2C and voltage-control paths.

## State And Persistence
The config is retained by pointer in `mt312_state`; it must remain valid for the frontend lifetime. No persistent data is defined.

## Dependencies And Integration Points
It includes DVB frontend types and is consumed by board adapter drivers.

## Risks
Wrong `demod_address` prevents attach. Wrong `voltage_inverted` can drive incorrect LNB voltage state. Config lifetime is external to the driver.

## Test Signals
Build with enabled/disabled Kconfig, attach from board code, and SEC voltage tests with both polarity settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312_priv.h

## Purpose
`mt312_priv.h` defines the private register-address enum and model-id enum for the MT312 family driver.

## Important APIs, Types, And Functions
`enum mt312_reg_addr` maps demodulator registers from status, FEC, LNB, SNR, AGC, reset, DiSEqC, symbol-rate, Viterbi, sweep, monitor, test, and config areas. It also includes ZL10313-only aliases `HW_CTRL` and `MPEG_CTRL`. `enum mt312_model_id` names `ID_VP310`, `ID_MT312`, and `ID_ZL10313`.

## Control Flow
No executable flow. The C file uses these enum values for all I2C register access and model-specific branching.

## State And Persistence
The header defines register constants and model ids only. Hardware register values are transient demodulator state.

## Dependencies And Integration Points
It is private to `mt312.c` and intentionally not part of the board-driver API.

## Risks
Some enum values overlap for model-specific registers (`HW_CTRL` with `VIT_ERRPER_M`, `MPEG_CTRL` with `VIT_ERRPER_L`), so callers must use them only for the proper chip. Numeric changes break hardware programming.

## Test Signals
Attach/init/status/tune tests on VP310, MT312, and ZL10313 validate the register map indirectly; compile-only coverage is insufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352.c

## Purpose
`mt352.c` implements the Zarlink MT352 DVB-T demodulator. It is an attach-style frontend driver that delegates board-specific demod/tuner initialization through config callbacks, programs TPS/bandwidth/IF/tuner registers, reads back received TPS parameters, and exposes DVB-T lock and quality counters.

## Important APIs, Types, And Functions
`struct mt352_state` stores the I2C adapter, embedded frontend, and copied `mt352_config`. Low-level register access is `mt352_single_write()`, `_mt352_write()`, and `mt352_read_register()`. Tuning helpers are `mt352_calc_nominal_rate()`, `mt352_calc_input_freq()`, and `mt352_set_parameters()`. Readback/stat callbacks include `mt352_get_parameters()`, `mt352_read_status()`, `mt352_read_ber()`, `mt352_read_signal_strength()`, `mt352_read_snr()`, and `mt352_read_ucblocks()`. `mt352_init()` performs reset and board-supplied `demod_init()`, while `mt352_attach()` probes `CHIP_ID`.

## Control Flow
Attach copies config by value, checks chip id `0x13`, installs ops, and returns the frontend. Init checks clock/config bits and, if needed, writes reset `0xc0` and calls the mandatory board `demod_init()` callback. Sleep writes a small clock soft-down sequence.

`set_parameters()` converts DVB-T properties into a TPS bitfield: HP/LP FEC, modulation, transmission mode, guard interval, and hierarchy are validated and encoded. It calculates nominal rate from bandwidth and ADC clock, calculates input frequency from IF and ADC clock, then either calls tuner `set_params()` for `no_tuner` designs and starts the FSM directly, or asks tuner `calc_regs()` for five PLL bytes, writes a combined demod/tuner register sequence, and triggers `TUNER_GO`. `get_parameters()` requires lock status, reads received TPS, channel start, nominal rate and inversion registers, and maps them back into DVB frontend properties. Status combines several status registers and clears `FE_HAS_LOCK` unless carrier, Viterbi, and sync are all present.

## State And Persistence
Runtime state is small and in-memory; board config is copied at attach, so caller config lifetime is not a concern after attach. Hardware registers hold current TPS/IF/tuner programming. No firmware or persistent storage is used. The `debug` module parameter controls trace output.

## Dependencies And Integration Points
The driver depends on I2C, DVB frontend, `mt352.h`, `mt352_priv.h`, board-supplied `demod_init()`, and tuner ops `calc_regs()` or `set_params()`. It exposes `fe->ops.write` through `_mt352_write()` for board initialization helpers.

## Risks
The C file relies on the board `demod_init()` callback being non-null but does not validate it before calling. Old-style tuner integration through `calc_regs()` is fragile and writes tuner bytes via demodulator registers. Several register reads return raw negative/non-`-EREMOTEIO` values but many statistic functions do not check each read, so I2C errors can be folded into counters. IF and ADC calculations use kHz defaults and integer arithmetic; wrong config silently shifts channels. `no_tuner` changes the control flow and must be tested separately.

## Test Signals
Test attach chip-id detection, hard reset and board `demod_init()`, sleep, 6/7/8 MHz tuning, all valid and invalid TPS combinations, tuner `calc_regs()` path, `no_tuner` path with tuner `set_params()`, lock/status bit combinations, get-frontend readback, BER/strength/SNR/ucblocks reads, and I2C failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352.h

## Purpose
`mt352.h` is the public integration header for the Zarlink MT352 DVB-T demodulator.

## Important APIs, Types, And Functions
`struct mt352_config` provides demodulator I2C address, optional ADC clock and IF frequency in kHz, `no_tuner` mode, and mandatory `demod_init()` callback. `mt352_attach()` is declared when reachable and stubbed otherwise. `mt352_write()` is a public inline helper that calls `fe->ops.write` for board initialization sequences.

## Control Flow
The header itself only contains the disabled-driver attach stub and the `mt352_write()` wrapper. `mt352.c` copies the config at attach and calls `demod_init()` from init.

## State And Persistence
The config values become copied runtime state in `mt352_state`. No persistent state is declared.

## Dependencies And Integration Points
It includes DVB frontend types and is used by board drivers and initialization code that need to write demodulator register sequences through the frontend.

## Risks
`demod_init` cannot be null in practice. Misconfigured `adc_clock`, `if2`, or `no_tuner` selects wrong tuning arithmetic or control flow. The `mt352_write()` helper silently returns 0 if `fe->ops.write` is absent, which could hide misuse.

## Test Signals
Build with Kconfig enabled/disabled, board init using `mt352_write()`, attach with valid config, and tuning with custom ADC/IF and `no_tuner` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352_priv.h

## Purpose
`mt352_priv.h` defines the private MT352 register map, chip id, byte helpers, and IF-frequency scaling constant used by `mt352.c`.

## Important APIs, Types, And Functions
`ID_MT352` is the expected chip id `0x13`. `msb()` and `lsb()` extract bytes for register programming. `enum mt352_reg_addr` names status, interrupt, SNR, error counter, AGC, TPS, reset, acquisition, tuner, clock, GPIO, ADC, and chip-id registers. `IF_FREQUENCYx6` encodes the default 36.166 MHz IF in 1/6 MHz units for readback frequency calculation.

## Control Flow
There is no control flow. The C file uses these constants for all register access and calculations.

## State And Persistence
The header contains constants only. Register values live in the demodulator hardware.

## Dependencies And Integration Points
It is private to the MT352 driver and pairs with the public `mt352.h` integration header.

## Risks
Incorrect register constants or byte extraction break tuning and status. The IF scaling constant is an approximation embedded in readback logic, so changing it affects reported frequency.

## Test Signals
Hardware attach, init register writes, tuning, get-frontend readback, and stats reads validate this map indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352_priv.h -->
