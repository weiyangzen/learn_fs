# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h lines 7748-11615

## Scope

This chunk is a generated register-map slice from `drxj_map.h`, covering line 7748 through line 11615. It is not executable logic; it defines preprocessor constants that encode hardware/firmware register addresses, widths, masks, reset/default values, bit positions, and enumerated values for the Trident/Hauppauge DRX-J frontend driver.

The chunk begins in the SCU RAM out-of-band receiver (`SCU_RAM_ORX_*`) region at address `0x831F06`, continues through ATV, QAM, VSB, SCU command mailbox/version registers up to `0x831FFF`, then enters SIO host/serial/pad register regions from `0x400000`, `0x410000`, `0x420000`, `0x430000`, `0x440000`, `0x450000`, `0x460000`, and `0x7F0000`. The next merge lane should treat this as a partial register-map report for the larger generated header.

## Purpose

The purpose of this chunk is to expose symbolic names for memory-mapped register contracts used by `drxj.c` and related driver code when programming the DRX-J demodulator firmware through DAP/FASI access helpers. The definitions let the C code use names such as `SCU_RAM_COMMAND__A`, `SCU_RAM_PARAM_0__A`, `SCU_RAM_QAM_FSM_RTH__A`, or `SIO_PDR_GPIO_CFG__A` instead of raw register addresses and bit masks.

Every top-level register follows the generated naming pattern:

- `*_A`: absolute register address.
- `*_W`: field/register width in bits.
- `*_M`: mask for valid bits.
- `*_PRE`: generated reset/default/preload value.
- Nested `*_B`, `*_W`, `*_M`, `*_PRE`: bitfield offset, width, mask, and preload within a register.
- Leaf constants without suffixes: legal enum values already shifted into their target bit positions when the associated mask is not zero-based.

## Important Register Groups

### SCU RAM ORX and ATV window, lines 7748-8453

The chunk starts with OOB receiver RAM status and control registers around `0x831F06` to `0x831F47`. These include MER minimum, RF/IF gain actual/min/max, analog and digital gain loop parameters, frequency/phase/timing/equalizer lock thresholds, lock windows, lock masks, frequency gain correction presets for 1544/2048/3088 kbps, and reset controls for carrier phase/timing/kernel loops. The reset fields use boolean-style enum values such as `DISABLE` and `ENABLE`.

The ATV section begins at `SCU_RAM_ATV_STANDARD__A` (`0x831F48`) and includes standard selection values for MN, B, G, DK, L, LP, I, and FM; detection enable and threshold; lock/sync status bits; AGC mode fields; AMS max reference defaults by TV standard; active AM extrema; video gain high/low; SIF gain; rate/LO/IIR control; and AGC integrator limits/thresholds. Many `SCU_RAM_ATV_RSV_*` entries are reserved address holders that preserve the generated memory layout.

### SCU RAM QAM configuration, lines 8454-9336

The QAM write/configuration region starts at `SCU_RAM_QAM_PARAM_ANNEX__A` (`0x831F74`) and defines:

- Annex selection: A, B, C, D.
- Constellation selection: unknown, QAM16, QAM32, QAM64, QAM128, QAM256.
- Interleave selection, including many `I*_J*` combinations, `UNKNOWN`, and `AUTO`.
- Symbol recovery rate high/low words and alternate rate high/low words.
- Equalizer center tap and reserved write slots.
- QAM FSM tuning registers for hum timeout, median/radius averaging, LC average offsets, target/override state, amplitude/rate/frequency/phase/median/cluster thresholds, and rate/frequency/count limits.
- Loop-control coefficient banks for CA, CP, CI, EP, EI, CF, and CF1 coarse/medium/fine tuning.
- Signal power and CMA equalizer radii `SCU_RAM_QAM_EQ_CMA_RAD0..5`.
- `SCU_RAM_QAM_CTL_ENA__A`, a 16-bit enable bitmap for QAM blocks such as AMP, ACQ, EQU, SLC, LC, AGC, FEC, AXIS, FMHUM, EQTIME, and EXTLCK.

This is one of the most actively used parts of the chunk. `drxj.c` writes QAM set-point tables by calling `drxdap_fasi_write_block()` at `SCU_RAM_QAM_EQ_CMA_RAD0__A` and many `drxj_dap_write_reg16()` calls against `SCU_RAM_QAM_FSM_*`, `SCU_RAM_QAM_LC_*`, and `SCU_RAM_QAM_SL_SIG_POWER__A`.

### SCU RAM QAM read/status and events, lines 9285-9836

The read/status QAM block defines active constellation/interleave, QAM lock, event occurrence masks, event schedule masks, tasklet schedule/run masks, active symbol rate words, AGC target-power offset, FSM state/current and new state, FSM lock flags, rate/frequency variation, error state, error lock flags, equalizer lock, equalizer state, and reserved read locations.

`SCU_RAM_QAM_LOCKED__A` splits into an internal lock progression level (`NOT_LOCKED`, `AMP_OK`, `RATE_OK`, `FREQ_OK`, `UPRIGHT_OK`, `PHNOISE_OK`, `TRACK_OK`, `IMPNOISE_OK`) and a coarser locked result (`NOT_LOCKED`, `DEMOD_LOCKED`, `LOCKED`, `NEVER_LOCK`). The event registers expose pre/post BER, packet fail, PRBS, lock in/out, FIFO full/empty, grab/change, FSM change, timer, clip, sense, power, median, MER, loop, frequency wrap, SER, Viterbi/symbol lock in/out, syncword, equalizer lock in/out, MPEG lock in/out, and reserved bits.

### SCU RAM VSB, command mailbox, and version, lines 9843-10157

The VSB block starts at `SCU_RAM_VSB_CTL_MODE__A` (`0x831FD7`) with AGC and monitor mode bits, notch threshold, reserved slots, AGC power target, outer-loop cycle, field number, and segment number. `drxj.c` writes `SCU_RAM_VSB_AGC_POW_TGT__A` during VSB/AGC setup, so width and mask correctness matter for tuner behavior.

The generic SCU mailbox appears at `SCU_RAM_PARAM_15__A` through `SCU_RAM_PARAM_0__A`, followed by `SCU_RAM_COMMAND__A`, `SCU_RAM_VERSION_HI__A`, and `SCU_RAM_VERSION_LO__A`. `SCU_RAM_PARAM_0__A` enumerates ATV/QAM `SET_ENV` parameters and result codes (`RESULT_OK`, `RESULT_UNKCMD`, `RESULT_UNKSTD`, `RESULT_INVPAR`, `RESULT_SIZE`). `SCU_RAM_PARAM_1__A` enumerates `GET_LOCK` results. `SCU_RAM_COMMAND__A` enumerates standard demod commands (`RESET`, `SET_ENV`, `SET_PARAM`, `START`, `GET_LOCK`, `GET_PARAM`, `HOLD`, `RESUME`, `STOP`), QAM IRQ/debug/admin commands, auxiliary atomic access, and high-byte standard selectors for ATV, QAM, VSB, OFDM, OOB, and TOP.

`drxj.c` uses these mailbox definitions in `scu_command()`: it polls `SCU_RAM_COMMAND__A` for ready state, writes `SCU_RAM_PARAM_0..4__A` according to parameter length, writes the combined command word, waits for readiness again, reads `SCU_RAM_PARAM_0..3__A` for results, and maps fixed result codes from `SCU_RAM_PARAM_0_*` to `-EINVAL` or `-EIO`. Because this command path is a firmware ABI, any address, mask, or enum change can break standard selection, lock polling, and error handling.

### SIO communication, host register access, debug, serial, and pad regions, lines 10158-11615

After the SCU RAM window, the chunk defines SIO-side blocks:

- `SIO_COMM_*` at `0x400000`: command execution, state, mailbox, and interrupt request/status/mask/sticky registers.
- `SIO_TOP_*` at `0x410000`: top-level execution, unlock/update key, and JTAG ID words.
- `SIO_HI_RA_RAM_*` at `0x420010`: host-interface register-access slave slots S0/S1, CRC/access flags, bank/block/address buffers, command/result/parameter mailbox registers, I2C control, and virtual-bank mapping entries/offsets.
- `SIO_HI_IF_*` at `0x430000` and `0x440000`: trap breakpoints/stack registers and high-interface execution/debug stack/breakpoint controls.
- `SIO_CC_*` at `0x450000`: clock/control PLL mode, lock, clock delay/invert, powerdown level, soft reset, and update key.
- `SIO_SA_*` at `0x460000`: serial-access execution, interrupts, prescaler, TX/RX data/length/command/status.
- `SIO_PDR_*` at `0x7F0000`: pad-ring/pin-drive register controls for monitoring, feedback, SMA RX/TX, UIO inputs/outputs, PWM outputs, OOB pins, GPIO/IRQ, and MPEG transport stream pins through `SIO_PDR_MD3_CFG__A`.

These SIO definitions are primarily low-level hardware interface constants. They connect to DAP/FASI, serial access, pad configuration, and hardware bring-up paths elsewhere in the driver or adjacent chunks of the generated map.

## APIs, Types, and Functions

This chunk defines no C functions, structs, or callable APIs. Its effective API is the set of macros consumed by driver routines. Important consumers visible outside the chunk include:

- `scu_command()` in `drxj.c`, which depends on `SCU_RAM_PARAM_*__A`, `SCU_RAM_COMMAND__A`, command enums, result-code enums, and standard selector bit values.
- QAM setup functions in `drxj.c`, which use `SCU_RAM_QAM_EQ_CMA_RAD0__A`, `SCU_RAM_QAM_FSM_*__A`, `SCU_RAM_QAM_LC_*__A`, and `SCU_RAM_QAM_SL_SIG_POWER__A` for constellation-specific tuning.
- VSB/AGC setup in `drxj.c`, which uses `SCU_RAM_VSB_AGC_POW_TGT__A`.
- OOB setup in `drxj.c`, which uses adjacent ORX/SCU command constants; this chunk includes the later ORX loop and reset fields plus OOB-capable `SCU_RAM_COMMAND_STANDARD_OOB`.

The concrete access APIs are in `drxj.c` and related support code, not in this header slice: `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, and `drxdap_fasi_write_block()` use the `_A` constants as hardware addresses and the surrounding enum values as payloads.

## Control Flow and State Behavior

There is no runtime control flow inside the header. The state model encoded by the constants is hardware/firmware state:

- SCU RAM `PARAM_*` and `COMMAND` registers form a persistent command mailbox while the demodulator firmware processes commands. Driver code writes parameter registers, writes a command word, then waits until firmware clears/returns the command register to ready.
- QAM tuning registers persist programmed thresholds, loop gains, equalizer radii, and enable bits in demodulator RAM. Status registers expose active constellation/interleave, lock phase, FSM state, event occurrence flags, and equalizer state.
- ORX/ATV/VSB registers persist standard-specific gain, lock, frequency, timing, equalizer, and AGC state.
- SIO registers persist host-interface routing, serial access, clock/reset/power, pad drive, UIO, PWM, and transport pin configuration.

Because this is generated hardware ABI data, persistence is in the device/firmware register file, not in kernel memory. The macros themselves are compile-time constants.

## Dependencies and Integration Points

The file is guarded by `__DRXJ_MAP__H__` and optionally exposes `drxj_map[]` and `drxj_map_info[]` under `_REGISTERTABLE_` with `<registertable.h>`. Normal driver compilation mostly consumes the macro definitions.

Integration depends on:

- The DRX-J firmware register layout matching these generated addresses and bit encodings.
- Kernel I2C/DAP/FASI helpers issuing correctly sized 16-bit register accesses and block writes.
- Higher-level DVB frontend control paths translating standards, constellations, symbol rates, interleave modes, OOB modes, and lock polling into the command/register values defined here.
- Adjacent chunks of `drxj_map.h` defining earlier SCU RAM, QAM, AGC, ORX, and DAP symbols referenced by the same functions.

The map was generated from `reg_map` by `IDF:x 1.3.0` in 2010; manual edits are explicitly discouraged in the file header.

## Risks

- Address or enum drift is high impact: driver writes would target the wrong firmware registers, especially for the SCU mailbox and QAM tuning tables.
- Some enum constants are pre-shifted to their bit positions, for example command standard selectors and QAM lock result values. Treating them as unshifted field values would produce invalid command words or status comparisons.
- Reserved registers are part of the address layout. Removing or renumbering them can break block writes and generated-table alignment even when the names look unused.
- Many widths are narrower than 16 bits despite 16-bit access helpers. Callers must respect masks when composing values; invalid high bits may be ignored, latched, or interpreted as reserved hardware controls.
- `SCU_RAM_COMMAND__A` command codes reuse low-byte values across QAM IRQ, debug, admin, and auxiliary command spaces. Correct high-byte standard/context bits are required to disambiguate.
- Status/event bits are hardware-driven and may be clear-on-read or sticky depending on firmware behavior not visible in this chunk. Tests should avoid assuming ordinary RAM semantics unless confirmed elsewhere.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware/firmware tests:

- Build coverage: compile the `drx39xyj` driver with this header and ensure all referenced macros resolve.
- SCU command smoke tests: exercise reset, set environment, start, get lock, and stop paths; verify `scu_command()` sees `SCU_RAM_COMMAND__A` return ready and maps `SCU_RAM_PARAM_0_*` errors correctly.
- QAM tune tests: tune QAM16/32/64/128/256 paths and verify the driver writes the expected FSM, LC, CMA radius, and signal power values without DAP write errors.
- Lock/status tests: read `SCU_RAM_QAM_LOCKED__A`, FSM state, lock flags, event occurrence registers, and equalizer lock/state while tuning to known-good and no-signal inputs.
- VSB setup tests: verify `SCU_RAM_VSB_AGC_POW_TGT__A` programming in VSB mode and check field/segment counters progress.
- SIO/bring-up tests: check JTAG ID, PLL lock, soft reset/update key, serial access, UIO/PWM, and pad-drive configuration where the board design exposes those paths.

## Open Questions for Merge Lane

- The source chunk starts after earlier ORX definitions, so merge should combine this with prior chunks before making whole-file statements about ORX command parameters.
- Many SIO definitions in this slice may be consumed outside the visible `SCU_RAM_*` search set. A final per-file report should include a full-symbol usage pass for `SIO_*` across the directory.
- Hardware side effects such as clear-on-read, write-one-to-clear, or sticky event semantics are not documented by the generated names alone and should be inferred only if adjacent driver code or vendor docs confirm them.
