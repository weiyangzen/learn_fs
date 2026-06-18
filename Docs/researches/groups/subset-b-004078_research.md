# subset-b-004078 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.c

## Purpose
`stv090x.c` is the implementation of the Linux DVB frontend driver for the STV0900 dual-demodulator and STV0903 single-demodulator satellite broadcast demodulators. It exposes a `dvb_frontend_ops` implementation for DVB-S, DVB-S2, and DSS, initializes the hardware over I2C, controls the demodulator search state machines, coordinates tuner access through the demodulator I2C repeater, configures transport-stream outputs, handles DiSEqC/tone signaling, reports lock and signal metrics, and manages shared state for chips that expose two demodulator paths.

## Important APIs, Types, And Data
The file defines an internal global device list through `struct stv090x_dev`, `stv090x_first_dev`, `find_dev()`, `append_internal()`, and `remove_dev()` so two frontends attached to one STV0900 chip can share one `struct stv090x_internal`. Public integration is through `stv090x_attach()`, the I2C driver `stv090x_probe()`/`stv090x_remove()`, and the `stv090x_ops` frontend table. The driver also sets `config->get_dvb_frontend` for I2C-client users and `config->set_gpio` after probe/attach.

Large constant tables encode hardware tuning knowledge: register init tables for STV0900/STV0903 and cut-2.0 overrides; C/N lookup tables for DVB-S/DSS and DVB-S2; RF-level lookup data; and carrier-loop tables split by chip cut, frame length, MODCOD, pilot state, and symbol-rate range. These tables drive `stv090x_setup()`, `stv090x_read_cnr()`, `stv090x_read_signal_strength()`, `stv090x_optimize_carloop()`, and `stv090x_optimize_track()`.

Low-level I2C helpers are `stv090x_read_reg()`, `stv090x_write_regs()`, and `stv090x_write_reg()`. Register access is normally indirected through the demod-aware `STV090x_READ_DEMOD()` and `STV090x_WRITE_DEMOD()` macros from the private header. `MAX_XFER_SIZE` caps register writes at 64 bytes including address bytes.

## Control Flow
Attach/probe allocates `struct stv090x_state`, fills frontend ops and defaults, and calls `stv090x_setup_compound()`. That function either reuses an existing shared `internal` for a dual-demod chip or allocates a new one, initializes mutexes, and runs `stv090x_setup()` once for the physical chip. Setup stops demods, disables tuner mode, configures the I2C repeater, enables the PLL, writes the device-specific init table, reads the chip cut from `STV090x_MID`, applies cut-2.0 values, configures ADC ranges, and resets FEC.

Runtime initialization is in `stv090x_init()`: it may initialize the tuner first so the tuner clock is available, sets a 135 MHz demod master clock with `stv090x_set_mclk()`, wakes the selected path, selects LDPC single/dual mode with `stv090x_ldpc_mode()`, applies inversion and rolloff defaults, wakes/initializes the tuner through the I2C gate, and configures TS output via `stv0900_set_tspath()` or `stv0903_set_tspath()`.

Tuning starts from DVB core `search()` via `stv090x_search()`. It validates properties, maps `SYS_DSS`/`SYS_DVBS`/`SYS_DVBS2`, copies frequency and symbol rate, chooses an automatic cold search with a 5 or 10 MHz range, sets DVB-S2 PLS and MIS filtering, then calls `stv090x_algo()`. The algorithm stops the TS merger and demod, sets acquisition parameters, programs known or blind symbol-rate windows, opens the I2C gate to program tuner frequency/bandwidth/gain, verifies tuner lock, checks AGC/power, configures delivery-system search, and dispatches to blind, cold, or warm lock logic. If demod lock succeeds, it reads actual signal parameters, optimizes tracking, releases and resets the TS merger, waits for FEC/TS lock, and resets error counters.

The search helpers cover several paths. `stv090x_blind_search()` first scans AGC2 level, then uses coarse and fine symbol-rate searches. `stv090x_get_coldlock()` starts with a demod timeout and, for low symbol rates, zigzags the tuner around the requested frequency. `stv090x_sw_algo()` performs software carrier-loop stepping through `stv090x_search_car_loop()` when hardware acquisition misses a cold lock. `stv090x_get_dmdlock()`, `stv090x_get_feclock()`, and `stv090x_get_lock()` layer demod, FEC, and TS FIFO lock checks.

Status and metrics are read through `stv090x_read_status()`, `stv090x_read_per()` wired as `.read_ber`, `stv090x_read_signal_strength()`, and `stv090x_read_cnr()`. DiSEqC is handled by `stv090x_set_tone()`, `stv090x_send_diseqc_msg()`, `stv090x_send_diseqc_burst()`, and `stv090x_recv_slave_reply()`, using per-path FIFO/status registers and optional envelope mode. Power management uses `stv090x_sleep()` and `stv090x_wakeup()` to stop/start ADC, DiSEqC, packet delineator, sampling, Viterbi, FEC, TS, and global standby clocks while respecting shared clocks on dual chips.

## State And Persistence Behavior
Persistent runtime state is in `struct stv090x_state` and `struct stv090x_internal`; there is no filesystem persistence. `internal->mclk`, `internal->dev_ver`, I2C identity, and `num_used` survive across the two frontend objects for a shared STV0900. The global linked list is process/module-global and is cleaned when the last frontend releases. Search mutates cached state fields such as `delsys`, `fec`, `modulation`, `modcod`, `frame_len`, `pilots`, `rolloff`, `inversion`, `frequency`, `srate`, `tuner_bw`, `search_range`, and timeouts so later status/metric calls reflect the last acquisition.

The hardware itself is the main persistent target: setup and tuning write many demodulator registers, and error counters are reset after lock and after PER reads. `sleep()` may place one path or the whole chip in standby depending on the other path’s ADC state. Shared register changes are protected with `internal->demod_lock`; tuner I2C access is serialized by either the board-supplied `tuner_i2c_lock` callback or `internal->tuner_lock`.

## Dependencies And Integration Points
The implementation depends on Linux kernel I2C, mutex, module, allocation, and DVB frontend APIs. It includes `stv6110x.h` for tuner modes and uses callback hooks from `struct stv090x_config` for tuner initialization, sleep, mode, frequency, bandwidth, baseband gain, reference clock, status, and I2C locking. The register and field names come from `stv090x_reg.h`; public board configuration comes from `stv090x.h`; private state and macros come from `stv090x_priv.h`.

Integration with the media stack is through `module_i2c_driver(stv090x_driver)`, the exported legacy `stv090x_attach()`, and `dvb_frontend_ops`. Capabilities advertise QPSK, DVB-S2 modulation, FEC/inversion auto, and multistream when cut >= 3.0. The frontend frequency range is 950-2150 MHz and the symbol-rate range is 1-45 Msps.

## Risks And Edge Cases
This driver is timing and register-sequence sensitive. Many error paths return `-1` instead of standard negative errno and some register writes in search/setup paths are not checked, making failure diagnosis uneven. Search loops and DiSEqC FIFO waits are polling based; some FIFO wait loops lack explicit timeout and can spin if hardware status never changes. The shared global device list has no list-level mutex, so attach/release concurrency depends on higher-level probe serialization assumptions. Register formulas involve integer scaling and shifts; bad or zero board-provided clocks, symbol rates, or TS clocks can produce invalid divisions or saturated values.

Dual-demod behavior is especially sensitive: power management stops shared FEC/TS clocks only when both paths appear asleep, while LDPC mode and MODCOD masks affect shared FEC resources. Tuner callbacks are optional, but missing callbacks reduce observability and can leave the driver assuming success. The code supports cut >= 2.0 and logs incomplete support for cuts above 3.0, so hardware revisions outside known tables need careful validation.

## Test Signals
Useful validation signals include successful `stv090x_probe()` or `stv090x_attach()` followed by a readable chip cut, no I2C errors during init/setup, tuner lock after gate-controlled tuning, demod/FEC/TS lock bits through `read_status()`, sane C/N and strength values from the lookup paths, PER counter reset behavior after `read_ber`, DiSEqC master/burst completion with TX idle, sleep/wakeup restoration on both demods, and TS output operation for each configured serial/parallel/DVB-CI mode. Regression tests should exercise DVB-S, DVB-S2, DSS, MIS filtering, non-default PLS, low symbol-rate cold search, blind-search paths, and both STV0900 dual and STV0903 single configurations on real hardware or a register-level emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.h

## Purpose
`stv090x.h` is the public board-driver contract for the STV0900/STV0903 DVB frontend driver. It defines the device, demodulator, clock, transport-stream, I2C repeater, ADC-range, and configuration types consumed by `stv090x.c`, plus the exported `stv090x_attach()` entry point when the driver is enabled.

## Important APIs And Types
The public enums identify demodulator path (`STV090x_DEMODULATOR_0` and `_1`), chip variant (`STV0903`, `STV0900`), LDPC/demod mode (`STV090x_DUAL`, `STV090x_SINGLE`), TS mode (`SERIAL_PUNCTURED`, `SERIAL_CONTINUOUS`, `PARALLEL_PUNCTURED`, `DVBCI`), input clock mode (`CLK_INT`, `CLK_EXT`), I2C repeater level from 256 down to 2, and ADC range (`2Vpp` or `1Vpp`).

`struct stv090x_config` is the key integration object. Board code supplies chip identity, demod mode/path, crystal frequency and I2C address, TS output modes and optional TS clocks, TEI-update bits, repeater level, tuner baseband gain, ADC ranges, DiSEqC envelope selection, and tuner callback functions. It also includes callback slots populated by the demod driver: `set_gpio` and `get_dvb_frontend`.

`stv090x_attach()` returns a `struct dvb_frontend *` for legacy attach users when `CONFIG_DVB_STV090x` is reachable. The disabled inline fallback logs a Kconfig warning and returns `NULL`.

## Control Flow And Integration
Board or bridge drivers construct `struct stv090x_config`, set tuner callbacks, and either instantiate the I2C driver with platform data or call `stv090x_attach(config, i2c, demod)`. The implementation copies the config pointer into each `struct stv090x_state` and uses it throughout setup, tuning, TS-path configuration, tuner gate operations, and power management. The demod driver mutates the config only to publish `set_gpio` and `get_dvb_frontend` helper callbacks.

## State And Persistence Behavior
This header defines configuration memory owned by the caller; the driver stores the pointer, not a deep copy. Callback pointers and scalar fields therefore must remain valid for the frontend lifetime. The default comments document expected defaults for `xtal`, `address`, `tuner_bbgain`, and ADC ranges, but the header does not enforce them; enforcement is partial and happens in the implementation.

## Dependencies
The file refers to `struct dvb_frontend`, `struct i2c_adapter`, `struct i2c_client`, `u8`, `u32`, `bool`, and `enum tuner_mode`, which are supplied by the surrounding Linux media/kernel include context and by the implementation’s tuner header. It is included by board drivers and by `stv090x.c`.

## Risks And Edge Cases
Because the config is pointer-retained, stack-allocated or short-lived config objects are unsafe. The `address` and `xtal` comments state defaults, but attach/probe expects useful values for reliable I2C and clock programming. Optional tuner callbacks are checked in the implementation, but a missing callback can remove important hardware setup or status validation. The public enum values are programmed directly into register fields, so board code should use only the declared constants.

## Test Signals
Compile coverage should verify both enabled and disabled Kconfig branches. Runtime validation should confirm a board config can attach through both legacy attach and I2C probe paths, callback pointers are invoked in the expected order, TS mode and TS clock fields produce valid transport output, ADC range settings map to the expected tuner input mode, and `get_dvb_frontend`/`set_gpio` are populated after successful setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_priv.h

## Purpose
`stv090x_priv.h` is the private implementation contract for `stv090x.c`. It defines logging levels, demod-path register access macros, bitfield manipulation helpers, acquisition thresholds, internal enums for signal/search/delivery/modulation state, lookup-table row types, and the two core runtime state structures.

## Important APIs, Types, And Macros
`dprintk()` gates kernel logging through the module-global `verbose` value. The register access macros `STV090x_READ_DEMOD()` and `STV090x_WRITE_DEMOD()` select P1 or P2 register symbols based on `state->demod`, while `STV090x_ADDR_OFFST()` computes the opposite path address family used by a few shared-register scenarios. `STV090x_SETFIELD()`, `STV090x_GETFIELD()`, `STV090x_SETFIELD_Px()`, and `STV090x_GETFIELD_Px()` encode/decode bitfields using the offset/width macros from `stv090x_reg.h`.

The header defines internal state enums: `stv090x_signal_state` for acquisition results, `stv090x_fec`, `stv090x_modulation`, `stv090x_frame`, `stv090x_pilot`, `stv090x_rolloff`, `stv090x_inversion`, `stv090x_modcod`, `stv090x_search`, `stv090x_algo`, and `stv090x_delsys`. These values are cached in `struct stv090x_state` and many of them mirror hardware register encodings.

Small data types support the implementation’s tables: `struct stv090x_long_frame_crloop`, `struct stv090x_short_frame_crloop`, `struct stv090x_reg`, and `struct stv090x_tab`.

`struct stv090x_internal` represents physical-chip shared state: I2C adapter/address, demod and tuner mutexes, master clock, device cut/version, and reference count. `struct stv090x_state` represents one DVB frontend path and stores device/demod mode, config, frontend, cached delivery/search parameters, signal metadata, tuner bandwidth, search range, and lock timeouts.

## Control Flow And Integration
The implementation relies on this header at every layer. Setup fills `struct stv090x_internal`, attach/probe fill `struct stv090x_state`, register helpers use the path macros, search and tracking functions update the internal enums, and metric/status paths read the cached delivery system and modulation state. The thresholds `STV090x_IQPOWER_THRESHOLD` and `STV090x_SEARCH_AGC2_TH()` guide no-signal and blind-search decisions.

## State And Persistence Behavior
The header itself stores no state, but it defines the persistent in-memory layout used for the lifetime of the frontend. `struct stv090x_internal` can be shared by two `struct stv090x_state` objects; the mutexes in that object serialize shared demod registers and tuner I2C access. `struct stv090x_state` is mutable across tuning operations, so cached fields are both inputs to later operations and outputs from the most recent acquisition.

## Dependencies
It includes `<media/dvb_frontend.h>` and depends on public enums from `stv090x.h` plus register symbols from `stv090x_reg.h` being available in the including C file. The field macros assume every referenced bitfield has matching `STV090x_OFFST_*` and `STV090x_WIDTH_*` definitions.

## Risks And Edge Cases
The bitfield macros do not mask `val` before shifting, so callers must pass values that fit the field width. They also use `1 << width`, so unexpected widths at or above the native int width would be unsafe, though this register file uses small fields. `STV090x_READ_DEMOD()` and `STV090x_WRITE_DEMOD()` choose paths by comparing only with `STV090x_DEMODULATOR_1`; invalid demod values silently map to P1. Logging macro behavior is nonstandard because it compares `verbose > level`, which can make exact level expectations surprising.

## Test Signals
Compile-time coverage is the primary signal: every field macro reference should resolve against `stv090x_reg.h`. Runtime signals include correct P1/P2 register selection for both demodulators, shared mutex behavior on dual-demod hardware, accurate cached state after tuning, correct threshold behavior for no-signal and blind-search cases, and logging controlled by the `verbose` module parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_reg.h

## Purpose
`stv090x_reg.h` is the symbolic register map and bitfield catalog for STV0900/STV0903 demodulators. It contains no executable code; its purpose is to let `stv090x.c` express hardware access by names instead of numeric addresses and to feed the private `STV090x_GETFIELD`/`STV090x_SETFIELD` macros with consistent offsets and widths.

## Important Register Families
The file begins with global chip identification, DAC/output, interrupt, I2C repeater, GPIO, clock, PLL, standby, ADC, tuner-test, and FSK/DiSEqC support registers. It then defines per-path DiSEqC TX/RX registers under `Px_DISTX*` and `Px_DISRX*`.

The main per-demodulator block is parameterized by `STV090x_Px_*(__x)` macros, with P1 and P2 aliases generated from path number. Addressing generally uses a 0x200 separation between paths for demod/FEC/TS blocks and smaller offsets for shared low-level blocks. Important families include AGC/IQ/power, demod mode/status, carrier frequency and search bounds, timing recovery and symbol-rate registers, equalizer/FFE, noise estimators, DVB-S2 MODCOD and PLS root registers, Viterbi configuration/status, packet delineator and MIS filtering, LDPC/BCH counters, TS FIFO/output registers, and error/PER/BER counters.

The final global families define LDPC iteration and LLR gain tuning, `GENCFG` for single/dual LDPC demod mode, `RCCFGH`, `TSGENERAL`/`TSGENERAL1X`, reset controls, and test DiSEqC receive selection.

## Control Flow And Integration
The implementation includes this header before the public/private headers. Init tables in `stv090x.c` use register constants directly. Field macros from `stv090x_priv.h` combine names such as `STV090x_OFFST_Px_LOCK_DEFINITIF_FIELD` and `STV090x_WIDTH_Px_LOCK_DEFINITIF_FIELD` to read lock, status, MODCOD, rolloff, transport stream, and DiSEqC bits. Demod-specific macros such as `STV090x_Px_DSTATUS(__x)` allow a single implementation path to select P1 or P2 at compile time through `STV090x_READ_DEMOD(state, DSTATUS)`.

## State And Persistence Behavior
The header has no runtime state. It documents the hardware state that the driver persists in registers: PLL and clocks, standby, ADC power/range, demod search modes, symbol/carrier offsets, MODCOD masks, PLS/MIS filtering, packet/error counters, TS FIFO mode/speed, and DiSEqC FIFO state. Because these names map directly to hardware registers, any value written by the implementation remains in the chip until overwritten, reset, or powered down.

## Dependencies
The register map depends on the STV090x hardware data sheet conventions and on the private bitfield macros using a strict `STV090x_OFFST_*`/`STV090x_WIDTH_*` naming scheme. It is tightly coupled to `stv090x.c`; nearly every helper there references one or more constants from this header.

## Risks And Edge Cases
Register-map correctness is critical. A wrong address or bit offset can misprogram hardware without compiler errors if the symbol name still exists. Some comments mark fields as `check`, indicating areas that may have been uncertain when authored. Several macros use arithmetic on path or index arguments; callers must pass valid path numbers and index ranges. P1/P2 address formulas are not uniform across all families, so adding new register names by copying a nearby macro can be risky.

## Test Signals
The strongest signals are hardware bring-up and tuning success across both STV0900 paths and the STV0903 single path. Specific checks should cover chip ID reads, I2C repeater enable/disable, PLL/mclk programming, per-path demod lock bits, Viterbi and packet delineator lock bits, C/N and RF metric reads, MODCOD mask programming, MIS/PLS filtering, TS FIFO configuration and line lock, DiSEqC TX/RX FIFO operation, sleep/wakeup clock bits, and error-counter reset/readback behavior. Static review should also verify every `STV090x_*_FIELD` used by `stv090x.c` has matching offset and width definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_reg.h -->
