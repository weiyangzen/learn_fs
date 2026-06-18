# Research: subset-b-004074

Grouped research for DVB frontend, CI, demodulator, and tuner sources under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.c

## Purpose
`si21xx.c` implements a Linux DVB frontend driver for Silicon Laboratories SI2109/SI2110 DVB-S demodulators. It exposes a `struct dvb_frontend` with DVB-S tuning, status, signal metrics, LNB voltage, 22 kHz tone, and DiSEqC master/burst operations. It is intended to be attached by a board driver via `si21xx_attach()`.

## Important APIs, Types, And Functions
The private `struct si21xx_state` stores the I2C adapter, immutable board config, embedded frontend, initialization flag, error counter mode, and selected ADC sampling rate `fs`. Low-level access is through `si21_writereg()`, `si21_writeregs()`, `si21_readreg()`, and `si21_readregs()`, with `si21_write()` exported through `frontend.ops.write` for header helper use. `si21xx_attach()` allocates state, wakes the demodulator, reads revision register `0x00`, accepts only SI2110/SI2109 IDs `0x04` and `0x14`, copies `si21xx_ops`, and returns the embedded frontend. `si21xx_init()` writes `serit_sp1511lhb_inittab`, selects DVB QPSK mode, and configures a parallel, LSB-first, gapped transport stream. `si21xx_set_frontend()` validates `SYS_DVBS`, calculates ADC sampling/coarse/fine tune values, writes PLL/tune registers, stores `state->fs`, and calls `si21xx_setacquire()`. The frontend status and metrics callbacks read lock, AGC, BER/SNR, and uncorrected block registers.

## Control Flow
Attach performs a minimal hardware presence check, then DVB core calls `.init` before tuning. Tuning flows from DVB properties to sample-rate selection, PLL programming, symbol-rate register conversion, code-rate mask setup, blind-scan/QuickLock register setup, and acquisition start. Status polling maps demod lock bits into `FE_HAS_SIGNAL`, `FE_HAS_CARRIER`, `FE_HAS_VITERBI`, `FE_HAS_SYNC`, and `FE_HAS_LOCK`. DiSEqC commands write the LNB FIFO and set the LNB control start bit; mini-burst, tone, and voltage operations modify control bits after waiting for idle where needed.

## State And Persistence
State is in memory only. `state->fs` is recalculated per tune and is required by symbol-rate conversion. `state->errmode` decides whether register pair `0x1d/0x1e` is interpreted as BER or uncorrected blocks; it is initialized to BER and not otherwise switched in this file. `state->initialised` is cleared on sleep but otherwise has little effect because `.init` always writes the register table. Hardware state persists in demodulator registers across calls until reinitialized or powered down.

## Dependencies And Integration Points
The driver depends on the DVB frontend core, Linux I2C transfers, jiffies/time helpers, and `si21xx.h` for board configuration and attach declaration. Board drivers provide the I2C address and optional minimum retune delay. Integration is through `dvb_frontend_ops` and satellite equipment control callbacks. It does not own a tuner; board code must coordinate external RF hardware as needed.

## Risks And Test Signals
Important risks are register-programming fragility, integer scaling errors in sample-rate/symbol-rate math, unsupported delivery systems returning `-EOPNOTSUPP`, and weak I2C read error propagation because `si21_readreg()` returns the last byte even on failed transfer. The `coderates[crate]` indexing assumes DVB core gives a valid `fe_code_rate`; unexpected enums could index out of bounds. DiSEqC waits use short 100-jiffy timeouts and should be validated against real hardware. Test signals are successful attach ID logs, tuning lock on known DVB-S transponders over the 950-2150 MHz range, correct 13/18 V and tone behavior, DiSEqC command execution, sane SNR/strength trends, and clean I2C error handling under cable/device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.h

## Purpose
`si21xx.h` is the public board-driver interface for the SI21XX DVB-S demodulator driver. It defines the minimal configuration object, declares `si21xx_attach()`, and provides a small register-write helper for users that already hold a `struct dvb_frontend`.

## Important APIs, Types, And Functions
`struct si21xx_config` carries the demodulator I2C address and a `min_delay_ms` retune delay hint. When `CONFIG_DVB_SI21XX` is reachable, `si21xx_attach(const struct si21xx_config *config, struct i2c_adapter *i2c)` is available. Otherwise, the inline fallback logs that the driver is disabled and returns `NULL`, allowing board drivers to compile without the module. `si21xx_writeregister()` sends a two-byte register/value buffer through `fe->ops.write` if the attached frontend exposes it.

## Control Flow
Board code constructs a static config, calls `si21xx_attach()`, and then registers the returned frontend with the DVB adapter. Later code can call `si21xx_writeregister()`; it delegates to the frontend write op implemented in `si21xx.c` as `si21_write()`.

## State And Persistence
The header owns no state. It defines the externally supplied config that `si21xx.c` stores by pointer, so the config lifetime must outlive the frontend. Register writes persist only in hardware state.

## Dependencies And Integration Points
The header depends on `linux/dvb/frontend.h` and `media/dvb_frontend.h`. Its main integration point is board-level DVB adapter setup and optional direct frontend register access.

## Risks And Test Signals
The helper silently does nothing when `fe->ops.write` is absent, returning `0`, which can hide misuse. Config lifetime and address correctness are critical because the driver keeps a pointer rather than copying the config. Test signals are successful compilation in both enabled and disabled Kconfig states, attach success on valid hardware, and helper writes that produce visible register-side behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.c

## Purpose
`sp2.c` implements an I2C driver for CIMaX SP2/SP2HF Common Interface hardware, registering a single-slot EN50221 CAM interface with the DVB CA core. The driver handles SP2 control-register setup, CAM slot reset, transport-stream enable, slot status polling, and delegates actual CAM attribute/IO memory access to board-specific callback code.

## Important APIs, Types, And Functions
The private state is `struct sp2` from `sp2_priv.h`. `sp2_read_i2c()` and `sp2_write_i2c()` perform bounded register transfers, with a 35-byte write buffer and normal Linux device logging. `sp2_ci_op_cam()` is the shared read/write path for attribute memory and CAM control IO: it validates slot `0`, switches the SP2 module access bits when necessary, then calls the platform callback `ci_control(priv, read, addr, data, &mem)`. The exported CA callbacks are `sp2_ci_read_attribute_mem()`, `sp2_ci_write_attribute_mem()`, `sp2_ci_read_cam_control()`, `sp2_ci_write_cam_control()`, `sp2_ci_slot_reset()`, `sp2_ci_slot_shutdown()`, `sp2_ci_slot_ts_enable()`, and `sp2_ci_poll_slot_status()`. `sp2_init()` initializes all CIMaX registers, locks registers, powers the slot, fills `dvb_ca_en50221` ops, and calls `dvb_ca_en50221_init()`.

## Control Flow
I2C core calls `sp2_probe()`, which reads platform data, allocates state, stores client data, and runs `sp2_init()`. CA core then calls the installed callbacks for module access. Reset asserts `SP2_MOD_CTL_RST`, deasserts it after a short sleep, then waits one second for CAM startup. TS enable sets `SP2_MOD_CTL_TSOEN` and `SP2_MOD_CTL_TSIEN`. Status polling throttles I2C reads to one per second and reports present/ready if `SP2_MOD_CTL_DET` is set. Removal releases the CA interface and frees state.

## State And Persistence
Runtime state includes cached CAM status, the current module access type, the next allowed status check jiffy, and the board callback/private pointer. The hardware register image is initialized at probe and persists until device removal or reset. `module_access_type` prevents unnecessary access-mode register writes.

## Dependencies And Integration Points
The file depends on the I2C driver model, `dvb_ca_en50221`, and platform data shaped as `struct sp2_config`. It does not itself know how to address CAM memory; that is delegated to the device-specific `ci_control` callback, making it a bridge between SP2 register control and a host board's memory/IO access method.

## Risks And Test Signals
Risks include missing or malformed platform data, a NULL `ci_control`, callback ABI mismatches, single-slot assumptions, and stale cached status during the one-second poll throttle. `sp2_ci_slot_ts_enable()` ignores the return value from its read before writing the modified byte. Test signals are successful I2C probe, `CIMaX SP2 successfully attached`, EN50221 CAM insertion/removal detection, CAM reset and attribute reads, descrambling path with TS enabled, clean module removal, and failure injection for I2C read/write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.h

## Purpose
`sp2.h` is the public interface for boards integrating the CIMaX SP2/SP2HF Common Interface driver. It defines platform configuration and declares the EN50221 callback functions implemented by `sp2.c`.

## Important APIs, Types, And Functions
`struct sp2_config` supplies the `dvb_adapter`, a device-specific `ci_control` callback pointer, and a private callback context. The header declares the CA memory/control callbacks and slot operations that are also installed into `struct dvb_ca_en50221`: attribute memory read/write, CAM control read/write, reset, shutdown, transport-stream enable, and poll status.

## Control Flow
Board code passes `struct sp2_config` as I2C client platform data. During probe, `sp2.c` copies these fields into `struct sp2` and binds the declared functions into DVB CA core operations. External users generally do not call the functions directly except through the CA framework.

## State And Persistence
No state is stored in the header. The callback pointers and private context must remain valid for the lifetime of the I2C client and CA device.

## Dependencies And Integration Points
The header depends on `media/dvb_ca_en50221.h`. It is the contract between board-specific CI access code and the generic SP2 I2C driver.

## Risks And Test Signals
The untyped `void *ci_control` field hides the actual callback signature, so a board can compile with an incompatible pointer and fail at runtime. The API is single-slot oriented even though the hardware naming references module A/B. Test signals are successful platform-data handoff, CA callback invocation with the expected private pointer, and CAM transactions that match the board's low-level memory mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2_priv.h

## Purpose
`sp2_priv.h` contains private state and register-bit definitions for the SP2 Common Interface driver. It is included by `sp2.c`, not intended as the board-facing API.

## Important APIs, Types, And Functions
`struct sp2` holds cached status, the bound I2C client, DVB adapter, embedded `dvb_ca_en50221` instance, current access mode, next status poll time, and the board callback/private context. Constants define module access spaces (`SP2_CI_ATTR_ACS`, `SP2_CI_IO_ACS`), read/write direction values, and module control bits including detection, access selects, TS input/output enable, and reset.

## Control Flow
The control-bit definitions drive `sp2_ci_op_cam()` access switching, `sp2_ci_slot_reset()` reset toggling, `sp2_ci_slot_ts_enable()` stream enabling, and `sp2_ci_poll_slot_status()` detect-bit interpretation.

## State And Persistence
The state object is allocated at I2C probe, attached to client data, used by CA callbacks through `en50221->data`, and freed at remove. Hardware state is represented by the module control register bits, while cached status and access type reduce polling and redundant register writes.

## Dependencies And Integration Points
It includes `sp2.h` and `media/dvb_frontend.h`, tying private state to both public SP2 config and DVB core types.

## Risks And Test Signals
Bit definitions are hardware contracts; wrong values can hold CAM reset, disable TS, or select the wrong CAM memory space. Test signals are correct transitions in register `0x00` during reset, access-space switching, detect status, and TS enable on a logic analyzer or via successful CAM operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp887x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp887x.c

## Purpose
`sp887x.c` implements a firmware-backed DVB-T frontend driver for Spase SP887x demodulators. It uploads firmware, programs OFDM parameters, controls an I2C gate for an external tuner, and exposes DVB-T status and metrics through `dvb_frontend_ops`.

## Important APIs, Types, And Functions
`struct sp887x_state` stores the I2C adapter, board config, embedded frontend, and an `initialised` flag guarding one-time firmware load. Register access uses 16-bit register addresses with 12-bit values via `sp887x_writereg()` and `sp887x_readreg()`, plus `i2c_writebytes()` for firmware blocks. `sp887x_initial_setup()` validates firmware size, soft-resets the device, stops the microcontroller, writes the 0x4000-byte firmware payload in 30-byte chunks after skipping a 10-byte header, configures MPEG TS output and AGC, and enables data-valid signaling. `configure_reg0xc05()` maps DVB-T modulation, hierarchy, and HP code rate into a control word, using autoprobing when values are AUTO. `sp887x_setup_frontend_parameters()` validates bandwidth, programs the external tuner, corrects sample-rate/carrier offsets, writes bandwidth/scan/order/control registers, and starts the microcontroller.

## Control Flow
Attach allocates state and verifies that register `0x0200` is readable. On first `.init`, the driver requests `dvb-fe-sp887x.fw` through the board-supplied firmware callback, uploads it, and enables TS pins. Tuning stops the microcontroller, calls tuner `set_params()` and `get_frequency()` through the I2C gate, clears pending status, writes offset/filter/acquisition registers, and restarts the microcontroller. Status polling reads SNR and sync registers; lock is reported when `0xf17` has the expected OFDM/SAW lock code.

## State And Persistence
The only software persistence is `initialised`, which prevents repeated firmware uploads. Signal counters and microcontroller state live in hardware. BER reads clear the BER registers after reporting. Sleep tristates TS output but does not clear `initialised`.

## Dependencies And Integration Points
The driver depends on Linux firmware loading, I2C, DVB frontend core, and `sp887x.h` for board config. It integrates with a separate tuner through `fe->ops.tuner_ops` and gates tuner I2C through `.i2c_gate_ctrl`. The board must provide a firmware request callback.

## Risks And Test Signals
Risks include missing firmware, wrong firmware size/header, I2C failures during block upload, unsupported bandwidth/property enums, and the unimplemented tuner adjustment request path logged from status register `0x200`. Read errors return `-1` as register data, so callers must be robust. Test signals are firmware upload completion, DVB-T locks across 6/7/8 MHz channels, valid auto and fixed modulation/FEC tuning, BER counters that clear after read, external tuner access through the gate, and clean behavior when firmware is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp887x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp887x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp887x.h

## Purpose
`sp887x.h` is the public board-driver interface for the SP887x DVB-T demodulator driver. It defines the board configuration and attach function, including the firmware retrieval hook required by `sp887x.c`.

## Important APIs, Types, And Functions
`struct sp887x_config` contains the demodulator I2C address and `request_firmware(struct dvb_frontend *fe, const struct firmware **fw, char *name)`. When `CONFIG_DVB_SP887X` is reachable, `sp887x_attach()` is declared; otherwise, an inline stub logs that the driver is disabled and returns `NULL`.

## Control Flow
Board code supplies the config and I2C adapter to `sp887x_attach()`. The attached frontend later calls the configured firmware callback during `.init` to retrieve `dvb-fe-sp887x.fw`.

## State And Persistence
No state is stored in the header. The config pointer is retained by the driver, so the object and firmware callback must stay valid for the frontend lifetime.

## Dependencies And Integration Points
The header depends on DVB frontend and Linux firmware types. It integrates board-specific firmware loading policy with the generic demodulator implementation.

## Risks And Test Signals
The firmware callback is mandatory for real initialization; a NULL or incompatible callback will fail when `.init` runs. Test signals include successful builds with the driver enabled/disabled, attach success with readable hardware, and firmware callback invocation with the expected firmware name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp887x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_algo.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_algo.c

## Purpose
`stb0899_algo.c` contains the acquisition algorithms for the STB0899 multistandard satellite demodulator. It implements separate DVB-S/DSS and DVB-S2 lock procedures used by `stb0899_drv.c` custom frontend search.

## Important APIs, Types, And Functions
The exported functions are `stb0899_dvbs_algo()`, `stb0899_dvbs2_algo()`, and `stb0899_carr_width()`. DVB-S support includes symbol-rate programming (`stb0899_set_srate()`), first/subsequent search range calculation, timing lock checks/search (`stb0899_check_tmg()`, `stb0899_search_tmg()`), carrier detection/search, data lock search, and range validation. DVB-S2 support configures UWP/CSM thresholds, BTR symbol-rate and loop bandwidth, CRL carrier nominal frequency, acquisition step geometry, timing-loop reset, reacquire triggers, demod lock polling, FEC lock polling, manual CSM tuning for specific modcod/pilot cases, and measured parameter storage.

## Control Flow
For DVB-S/DSS, the driver sets the SFR registers, optimizes loop constants by symbol rate, resets the stream merger, computes a tuner subrange, tunes the external tuner through the I2C gate, waits for AGC/timing, then searches timing, carrier, data, and final range in a zigzag pattern. On success it switches loops from acquisition to tracking and applies puncture-rate-specific Viterbi/carrier loop settings. For DVB-S2, it tunes the external tuner, sets acquisition AGC, initializes UWP/CSM/BTR/CRL, sets IQ inversion, triggers acquisition, waits for UWP+CSM demod lock, waits for packet/FEC lock, retries false locks using measured carrier offset, flips IQ inversion if needed, optionally reconfigures manual CSM for low master-clock/symbol-rate ratios, then stores final offset, symbol rate, modcod, pilots, frame length, and AGC tracking settings.

## State And Persistence
The algorithms mutate `state->internal`: current frequency, symbol rate, search range, tuner bandwidth, derotator frequency, inversion, FEC/modcod, lock status, timing constants, and DVB-S2 measured parameters. The code also writes many demodulator, S2 demod, and S2 FEC registers; those register settings persist until the next tune, sleep, or init. No data is persisted outside the frontend instance.

## Dependencies And Integration Points
This file depends on `stb0899_priv.h` state definitions, `stb0899_drv.h` config callbacks, and `stb0899_reg.h` register/bitfield definitions. It calls the low-level read/write helpers and `stb0899_i2c_gate_ctrl()` from `stb0899_drv.c`, and it relies on board-provided tuner callbacks in `struct stb0899_config`.

## Risks And Test Signals
The highest risks are integer scaling/overflow in loop and NCO calculations, divide-by-zero if symbol rate or master clock are invalid, fragile timing sleeps, false locks, and bad state carryover between DVB-S and DVB-S2. The comment in DVB-S warns that status reads during acquisition can break lock, so instrumentation must be careful. Test signals are successful locks for DVB-S, DSS, and DVB-S2 across low/high symbol rates, IQ inversion recovery, false-lock retries that converge, correct reported final frequency/symbol rate, stable reacquisition after failed searches, and no I2C gate leaks around tuner calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_algo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_cfg.h

## Purpose
`stb0899_cfg.h` provides reusable static initialization tables and DVB-S2 tuning constants for the STB0899 driver. It is data, not executable logic, but it directly shapes hardware initialization and acquisition behavior.

## Important APIs, Types, And Functions
The file defines `stb0899_s2_init_2[]` for S2 demodulator initialization, `stb0899_s2_init_4[]` for S2 FEC initialization, and `stb0899_s1_init_5[]` for S1/test register initialization. Each table ends with a sentinel (`0xffff`, `0xffffffff`) consumed by loops in `stb0899_init()`. It also defines default DVB-S2 parameters such as Es/N0 averaging/quantization, coarse/fine acquisition frame counts, miss thresholds, UWP thresholds, SOF search timeout, BTR/CRL NCO widths, gain-shift offset, and LDPC max iterations.

## Control Flow
Board-specific `struct stb0899_config` instances can point at these tables. During frontend `.init`, `stb0899_drv.c` iterates each configured table and writes S1 registers or S2 base/offset/data triples. Later, `stb0899_algo.c` reads the constants through config fields to program UWP, BTR, CRL, and LDPC behavior.

## State And Persistence
The tables are immutable static data compiled into the module. Once written, their values persist in hardware registers until reprogrammed. The constants are usually copied into board config fields, then used repeatedly during searches.

## Dependencies And Integration Points
The file relies on `stb0899_drv.h` table types and `stb0899_reg.h` register macros being visible to includers. It integrates initialization data with the driver proper and board configuration.

## Risks And Test Signals
Risks are table drift against silicon revisions, wrong sentinel placement, and parameter values that work for one board clock/tuner path but not another. Because this header defines static objects, including it in multiple C files would create duplicate private copies; it should be included only where intended by board code. Test signals are clean init-table completion, readable S2 demod/FEC core IDs after wake, DVB-S2 lock stability across modcods, and no writes past sentinel values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.c

## Purpose
`stb0899_drv.c` is the main Linux DVB frontend driver for the STB0899 multistandard satellite demodulator. It owns attach/probe, low-level register I/O, init, custom search dispatch, status/metric callbacks, DiSEqC and LNB controls, I2C repeater control, postprocess GPIO events, and module metadata.

## Important APIs, Types, And Functions
The exported attach point is `stb0899_attach()`, which allocates `struct stb0899_state`, stores config/I2C, wakes clocks, reads device/core IDs, and returns an embedded frontend. Low-level I/O includes `stb0899_read_reg()`, `_stb0899_read_s2reg()`, `stb0899_write_s2reg()`, `stb0899_read_regs()`, `stb0899_write_regs()`, and `stb0899_write_reg()`, including the documented 0xf2xx/0xf6xx follow-up read workaround. `stb0899_init()` writes all configured init tables, calculates clocks/rolloff, and initializes DiSEqC. `stb0899_search()` reads DVB properties, selects delivery, configures tuner bandwidth/gain and master clock, then calls `stb0899_dvbs_algo()` or `stb0899_dvbs2_algo()`. Status and metric callbacks translate hardware status into DVB frontend flags, C/N, RF strength, and BER/PER. DiSEqC routines handle FIFO writes, RX replies, mini-bursts, and 22 kHz tone.

## Control Flow
Attach wakes the device, enables clocks, checks IDs, and leaves full initialization to DVB core `.init`. Init iterates config tables for device, S2 demod, S1 demod, S2 FEC, and test registers, then calculates master clock and AGC defaults. Search validates symbol rate, switches delivery-mode clocks/FEC/stream settings, opens the I2C repeater for tuner callbacks, sets tuner bandwidth, adjusts AGC and LDPC iteration settings, runs the selected acquisition algorithm, and sets `internal->lock`. Read callbacks use `state->delsys` and `internal->lock` to choose S1 or S2 status paths.

## State And Persistence
`struct stb0899_state` persists frontend config, current delivery system, cached requested params, `rx_freq`, a mutex field, and extensive `internal` demod state. Hardware register state includes init table values, clock gates, stream merger reset state, DiSEqC config, GPIO postproc state, and acquisition settings. The driver keeps board config by pointer, so config and callback lifetimes must outlive the frontend.

## Dependencies And Integration Points
The driver depends on DVB frontend core, Linux I2C, `stb0899_priv.h`, `stb0899_drv.h`, and `stb0899_reg.h`. It integrates board-specific tuner operations through function pointers in `struct stb0899_config` and exposes an I2C repeater for tuner drivers such as STB6000. Postproc GPIO entries allow board-specific power/lock signaling.

## Risks And Test Signals
Risks include S2 indirect register protocol errors, master-clock misconfiguration, stale `internal->srate` when choosing RF gain before assignment, inconsistent symbol-rate limits (`info` minimum is 5 Msps while search accepts 1 Msps), commented-out wakeup op despite attach using wake, and division by hardware-derived values. GPIO voltage control is board-specific and can be unsafe on mismatched designs. Test signals are attach ID/core logs, init table writes, locks for DVB-S/DSS/DVB-S2, correct I2C repeater toggling around tuner access, DiSEqC TX/RX and burst behavior, voltage/tone verification, plausible C/N/RF strength metrics, and regression tests across low and high symbol rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.h

## Purpose
`stb0899_drv.h` is the public configuration and attach interface for the STB0899 multistandard frontend. Board drivers use it to provide init tables, clock/transport settings, postprocess GPIO behavior, DVB-S2 algorithm constants, and tuner callbacks.

## Important APIs, Types, And Functions
It defines table element types `struct stb0899_s1_reg` and `struct stb0899_s2_reg`, IQ inversion enum values, GPIO address constants, postprocess event definitions, `struct stb0899_postproc`, and the large `struct stb0899_config`. The config includes init-table pointers, postproc pointer, inversion default, crystal frequency, demod address, TS output/control options, low/high master-clock settings, DVB-S2 acquisition constants, and tuner callback hooks for frequency, bandwidth, and RF signal gain. `stb0899_attach()` is declared or stubbed depending on Kconfig.

## Control Flow
Board code fills `struct stb0899_config` and calls `stb0899_attach()`. The main driver later walks the table pointers in `.init`, reads clock fields in search, and invokes tuner callbacks through the I2C repeater.

## State And Persistence
The header owns no runtime state, but config objects are retained by pointer inside `struct stb0899_state`. Init tables and callbacks must remain valid for the frontend lifetime.

## Dependencies And Integration Points
It depends on Linux module/kernel headers and `media/dvb_frontend.h`. It is the main integration contract among board files, `stb0899_drv.c`, `stb0899_algo.c`, and external tuner drivers.

## Risks And Test Signals
Because most fields are raw hardware values, misconfiguration can prevent attach, lock, TS output, or safe LNB/GPIO behavior. Callback NULL checks are partial and semantics are board-specific. Test signals are successful build with Kconfig enabled/disabled, attach with stable config storage, init-table sentinel correctness, and tuner callback calls with expected frequency/bandwidth values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_priv.h

## Purpose
`stb0899_priv.h` defines the internal state model, algorithm status enums, bitfield helpers, debug macro, and cross-file prototypes for the STB0899 driver. It connects the main driver, algorithm file, and register map.

## Important APIs, Types, And Functions
The file defines debug levels and `dprintk()`, scalar helpers (`GETBYTE`, `MAKEWORD32`, `STB0899_GETFIELD`, `STB0899_SETFIELD_VAL`), `enum stb0899_status`, DVB-S2 `enum stb0899_modcod`, frame and rolloff enums, interpolation table type `struct stb0899_tab`, S1 FEC enum values, requested-parameter cache `struct stb0899_params`, dynamic demod state `struct stb0899_internal`, and top-level `struct stb0899_state`. It declares register accessors, S2 indirect I/O, I2C gate control, DVB-S/DVB-S2 algorithms, and carrier-width calculation.

## Control Flow
`stb0899_drv.c` allocates and owns `struct stb0899_state`, then both the driver and algorithm routines mutate `state->internal` while using the declared helpers. The macro `STB0899_READ_S2REG()` assumes a local variable named `state`, so it is tightly coupled to call-site naming.

## State And Persistence
`struct stb0899_internal` is the core persistent software state for search and readback: clocks, frequencies, symbol rate, FEC/modcod, search geometry, tuner offsets/bandwidth, rolloff, derotator settings, AGC timings, lock/status, DVB-S2 UWP/CSM/FEC attributes, and cached error/status registers. `struct stb0899_state` also stores config, frontend, current delivery system, requested params, DiSEqC receiver frequency, and a search mutex.

## Dependencies And Integration Points
The header depends on DVB frontend types and `stb0899_drv.h`. It is private to the STB0899 implementation but exports prototypes across the split C files.

## Risks And Test Signals
Bitfield macros assume valid widths and may overflow if used with 32-bit-wide fields in inappropriate expressions. `STB0899_READ_S2REG()`'s hidden `state` dependency is error-prone. The search mutex exists but is not visibly used by search in the read code, so concurrent access should be audited. Test signals are clean compilation across C files, correct field extraction/set behavior for representative registers, and stable state transitions after repeated tune/fail/retune cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_reg.h

## Purpose
`stb0899_reg.h` is the STB0899 register and bitfield map used by the main driver and acquisition algorithms. It names S1 demod/FEC registers, S2 demod/FEC indirect base/offset pairs, GPIO/I2C/clock registers, and bit masks with matching offset/width macros.

## Important APIs, Types, And Functions
There are no functions. The important API is macro naming consistency: each field used with `STB0899_GETFIELD()` or `STB0899_SETFIELD_VAL()` must provide `STB0899_OFFST_<field>` and `STB0899_WIDTH_<field>`. The map includes device ID, timing/carrier/data status (`DSTATUS`, `TLIR`, `RTF`, `VSTATUS`, `PLPARM`), symbol-rate and derotator registers (`SFR*`, `CFR*`), S1 FEC controls, DiSEqC registers, GPIO/clock/I2C repeater registers, S2 demod UWP/CSM/BTR/CRL/equalizer/acquisition registers, and S2 FEC/LDPC/BCH registers. `STB0899_S2DEMOD` and `STB0899_S2FEC` define the indirect I2C device selectors.

## Control Flow
The header drives almost every register access in `stb0899_drv.c` and `stb0899_algo.c`. Init tables in `stb0899_cfg.h` are built from its offset/base macros. Search algorithms read lock/status fields and write loop/acquisition fields through this map. Delivery switching uses clock-stop and FEC fields; I2C gate control uses `STB0899_I2CRPT`/`STB0899_I2CTON`.

## State And Persistence
The file is compile-time hardware metadata. It does not store runtime state, but incorrect definitions directly corrupt persistent demodulator register state during operation.

## Dependencies And Integration Points
It is included by STB0899 driver and algorithm files and indirectly supports board init tables. Its macro names must remain aligned with the private bitfield helpers in `stb0899_priv.h`.

## Risks And Test Signals
Risks include typoed field names, wrong widths/offsets, duplicate or conflicting addresses, and fields with suspicious zero widths that can make generic bitfield helpers behave unexpectedly if used. Because S2 registers are accessed through an indirect protocol, base/offset mistakes are hard to diagnose. Test signals are successful compile of all referenced macros, attach core-ID reads, init table writes to intended S2 demod/FEC regions, lock-bit interpretation matching hardware traces, and regression coverage for I2C repeater, DiSEqC, GPIO, and clock gating fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6000.c

## Purpose
`stb6000.c` implements a DVB-S silicon tuner driver for the ST STB6000. It attaches tuner operations to an existing DVB frontend, programs RF frequency and bandwidth over I2C, supports sleep, and reports the cached tuned frequency.

## Important APIs, Types, And Functions
`struct stb6000_priv` stores tuner I2C address, adapter, and cached frequency. `stb6000_attach()` probes for an I2C device at the requested address through the frontend I2C gate, allocates private state, copies `stb6000_tuner_ops` into `fe->ops.tuner_ops`, and stores `fe->tuner_priv`. `stb6000_set_params()` reads `frequency` and `symbol_rate` from `dtv_property_cache`, derives MHz and approximate bandwidth, selects register values by frequency band, computes divider values `n` and `m`, writes a 12-byte programming sequence, then writes a 5-byte follow-up sequence. `stb6000_sleep()` writes register 10 to zero, and `stb6000_get_frequency()` returns the cached value.

## Control Flow
Board code first attaches a demodulator frontend, then calls `stb6000_attach()`. During tuning, the demodulator calls tuner `.set_params()` directly or through its configured tuner callback. The tuner opens the demodulator I2C repeater if available, performs I2C writes, delays briefly, closes the gate, and caches the tuned frequency.

## State And Persistence
Software state is limited to tuner private data and last programmed frequency. Hardware state is the tuner register set written during set-params and sleep. The driver does not read back lock status or bandwidth.

## Dependencies And Integration Points
It depends on Linux I2C, DVB frontend/tuner ops, and `stb6000.h`. It integrates naturally with demodulators exposing `.i2c_gate_ctrl`, including STB0899. The frontend's property cache is the source of tuning inputs.

## Risks And Test Signals
Risks include the unusual zero-length first I2C probe message, returning raw `ret` values instead of normalized errors, coarse integer bandwidth in MHz capped at 31, no explicit lower bandwidth bound, and hardcoded frequency-band tables. It returns `-1` for out-of-range frequency rather than `-EINVAL`. Test signals are successful attach probe, I2C gate open/close around transfers, correct LO programming from 950-2150 MHz, successful demod locks with the companion frontend, sleep current reduction, and `get_frequency()` matching the requested kHz value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6000.h

## Purpose
`stb6000.h` is the public attach interface for the STB6000 DVB-S tuner driver. Board drivers include it to bind an STB6000 tuner to an already-created frontend.

## Important APIs, Types, And Functions
When `CONFIG_DVB_STB6000` is reachable, `stb6000_attach(struct dvb_frontend *fe, int addr, struct i2c_adapter *i2c)` is declared and returns the same frontend pointer on success. When disabled, an inline stub logs a warning and returns `NULL`.

## Control Flow
Board setup calls the demodulator attach first, then calls `stb6000_attach()` with the demod frontend, tuner I2C address, and adapter. The implementation installs tuner ops into `fe->ops.tuner_ops` and stores private tuner state in `fe->tuner_priv`.

## State And Persistence
The header owns no state. The implementation stores all runtime state in frontend tuner private data after attach.

## Dependencies And Integration Points
The header depends on Linux I2C and DVB frontend types. It is the integration point between board files and the tuner implementation, commonly paired with satellite demodulators that expose an I2C gate.

## Risks And Test Signals
The API mutates an existing frontend, so callers must attach in the correct order and avoid overwriting another tuner's ops. Test signals are successful build with enabled/disabled Kconfig, attach returning the frontend pointer, and subsequent frontend tuning invoking the STB6000 tuner ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6000.h -->
