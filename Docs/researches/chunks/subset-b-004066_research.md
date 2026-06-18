# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h lines 11616-15055

## Scope And Purpose

This chunk covers the final part of the generated DRX-J register map header. The file is generated from Trident's `reg_map` input and is included by `drxj.c`; it does not implement executable logic. Instead, it publishes preprocessor constants that the DRX39xyJ DVB frontend driver uses to address demodulator hardware registers through the DAP/FASI access helpers.

The assigned line range starts in the middle of the SIO pad-driver register definitions, continues through SIO GPIO function-selection registers, defines the VSB demodulator communication and top-level control/status map, defines two VSB sysctrl RAM windows used for equalizer/feed-forward/leak/gain tuning tables, and ends with three VSB RAM aperture base addresses for TCMEQ, FCPRE, and EQTAP data.

The constants follow a consistent generated convention:

- `*_A` is the hardware address used by `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxdap_fasi_write_block()`, and similar accessors.
- `*_W` is the bit width of the full register or subfield.
- `*_M` is the unshifted or shifted mask for the register/subfield.
- `*_PRE` is the power-on/reset or preferred default value emitted by the generator.
- Nested field constants add `_*FIELD*__B`, `__W`, `__M`, and `__PRE` for bit position, width, mask, and reset/default.

This chunk is not Ceph-specific despite the mirrored source tree path. It is media frontend hardware-description data for the DRX39xyJ demodulator.

## Important Register Blocks And Macros

SIO pad-driver and GPIO function map:

- `SIO_PDR_MD4_CFG__A` through `SIO_PDR_MD7_CFG__A` define remaining MPEG transport data pad configuration registers at `0x7F002F` through `0x7F0032`. The chunk begins just after `SIO_PDR_MD3_CFG__A`, so the final report should merge this with the preceding chunk for the complete MPEG data-pad set.
- Each MPEG data pad configuration register has `MODE`, `DRIVE`, `KEEP`, and `UIO` fields. In this chunk the full pad register width is 9 bits, mask `0x1FF`, and default/preferred value is typically `0x50`.
- `SIO_PDR_I2C_SCL1_CFG__A`, `SIO_PDR_I2C_SDA1_CFG__A`, `SIO_PDR_I2C_SDA2_CFG__A`, and `SIO_PDR_I2C_SCL2_CFG__A` describe I2C pad configuration registers. Their defaults use `MODE__PRE 0x1` and full-register `__PRE 0x11`, distinguishing them from MPEG data pads.
- `SIO_PDR_VSYNC_CFG__A`, `SIO_PDR_SMA_RX_CFG__A`, `SIO_PDR_SMA_TX_CFG__A`, `SIO_PDR_I2S_CL_CFG__A`, and `SIO_PDR_I2S_DA_CFG__A` define video sync, smart-antenna, and I2S pad registers with the same `MODE`/`DRIVE`/`KEEP`/`UIO` shape.
- `SIO_PDR_GPIO_GPIO_FNC__A`, `SIO_PDR_IRQN_GPIO_FNC__A`, `SIO_PDR_MSTRT_GPIO_FNC__A`, `SIO_PDR_MERR_GPIO_FNC__A`, `SIO_PDR_MCLK_GPIO_FNC__A`, `SIO_PDR_MVAL_GPIO_FNC__A`, `SIO_PDR_MD0_GPIO_FNC__A` through `SIO_PDR_MD7_GPIO_FNC__A`, `SIO_PDR_SMA_RX_GPIO_FNC__A`, and `SIO_PDR_SMA_TX_GPIO_FNC__A` define 2-bit GPIO function selectors at `0x7F0050` through `0x7F005F`.

VSB communication registers:

- `VSB_COMM_EXEC__A` at `0x1C00000` exposes the VSB firmware/subsystem execution control state. It provides symbolic values `VSB_COMM_EXEC_STOP`, `VSB_COMM_EXEC_ACTIVE`, and `VSB_COMM_EXEC_HOLD`.
- `VSB_COMM_MB__A` defines a 16-bit VSB mailbox register.
- `VSB_COMM_INT_REQ__A`, `VSB_COMM_INT_STA__A`, `VSB_COMM_INT_MSK__A`, and `VSB_COMM_INT_STM__A` define the VSB interrupt request/status/mask/sticky-mask style registers. The request and status registers expose single-bit subfields for `COMM_INT_REQ` and `COMM_INT_STA`.

VSB top-level control and status registers:

- `VSB_TOP_COMM_EXEC__A`, `VSB_TOP_COMM_MB__A`, `VSB_TOP_COMM_INT_REQ__A`, `VSB_TOP_COMM_INT_STA__A`, `VSB_TOP_COMM_INT_MSK__A`, and `VSB_TOP_COMM_INT_STM__A` repeat the communication pattern for the VSB top block at base `0x1C10000`.
- Clock and carrier tracking gain registers include `VSB_TOP_CKGN1ACQ__A`, `VSB_TOP_CKGN1TRK__A`, `VSB_TOP_CKGN2ACQ__A`, `VSB_TOP_CKGN2TRK__A`, `VSB_TOP_CKGN3__A`, `VSB_TOP_CYGN1ACQ__A`, `VSB_TOP_CYGN1TRK__A`, `VSB_TOP_CYGN2ACQ__A`, `VSB_TOP_CYGN2TRK__A`, and `VSB_TOP_CYGN3__A`.
- State-machine and mux/control registers include `VSB_TOP_SYNCCTRLWORD__A`, `VSB_TOP_MAINSMUP__A`, `VSB_TOP_EQSMUP__A`, `VSB_TOP_SYSMUXCTRL__A`, `VSB_TOP_CYSMSTATES__A`, `VSB_TOP_EQSMRSTCTRL__A`, `VSB_TOP_EQSMTRNCTRL__A`, `VSB_TOP_EQSMRCA1CTRL__A`, `VSB_TOP_EQSMRCA2CTRL__A`, `VSB_TOP_EQSMDDM1CTRL__A`, `VSB_TOP_EQSMDDM2CTRL__A`, `VSB_TOP_SYSSMRSTCTRL__A`, `VSB_TOP_SYSSMCYCTRL__A`, `VSB_TOP_SYSSMTRNCTRL__A`, `VSB_TOP_SYSSMEQCTRL__A`, `VSB_TOP_SYSSMAGCCTRL__A`, and `VSB_TOP_SYSSMCTCTRL__A`.
- Signal-quality and lock-status registers include `VSB_TOP_SNRTH_RCA1__A`, `VSB_TOP_SNRTH_RCA2__A`, `VSB_TOP_SNRTH_DDM1__A`, `VSB_TOP_SNRTH_DDM2__A`, `VSB_TOP_SNRTH_PT__A`, `VSB_TOP_SNR__A`, `VSB_TOP_LOCKSTATUS__A`, `VSB_TOP_MEASUREMENT_PERIOD__A`, `VSB_TOP_NR_SYM_ERRS__A`, `VSB_TOP_ERR_ENERGY_L__A`, and `VSB_TOP_ERR_ENERGY_H__A`.
- Equalizer/AGC/tap-control registers include `VSB_TOP_EQCTRL__A`, `VSB_TOP_PREEQAGCCTRL__A`, `VSB_TOP_PREEQAGCPWRREFLVLHI__A`, `VSB_TOP_PREEQAGCPWRREFLVLLO__A`, `VSB_TOP_CORINGSEL__A`, `VSB_TOP_BEDETCTRL__A`, `VSB_TOP_LBAGCREFLVL__A`, `VSB_TOP_UBAGCREFLVL__A`, `VSB_TOP_AGC_TRUNCCTRL__A`, `VSB_TOP_BEAGC_*`, `VSB_TOP_CFAGC_*`, `VSB_TOP_FIRSTLARGFFETAP*`, `VSB_TOP_SECONDLARGFFETAP*`, `VSB_TOP_FIRSTLARGDFETAP*`, and `VSB_TOP_SECONDLARGDFETAP*`.
- Notch and burst-noise related registers include `VSB_TOP_SMALL_NOTCH_CONTROL__A`, `VSB_TOP_NOTCH1_BIN_NUM__A`, `VSB_TOP_NOTCH2_BIN_NUM__A`, `VSB_TOP_NOTCH_START_BIN_NUM__A`, `VSB_TOP_NOTCH_STOP_BIN_NUM__A`, `VSB_TOP_NOTCH_TEST_DURATION__A`, `VSB_TOP_RESULT_LARGE_PEAK_BIN__A`, `VSB_TOP_RESULT_LARGE_PEAK_VALUE__A`, `VSB_TOP_RESULT_SMALL_PEAK_BIN__A`, `VSB_TOP_RESULT_SMALL_PEAK_VALUE__A`, `VSB_TOP_NOTCH_SWEEP_RUNNING__A`, `VSB_TOP_NOTCH_SCALE_1__A`, `VSB_TOP_NOTCH_SCALE_2__A`, `VSB_TOP_BNFIELD__A`, `VSB_TOP_CLPLASTNUM__A`, `VSB_TOP_BNSQERR__A`, `VSB_TOP_BNTHRESH__A`, and `VSB_TOP_BNCLPNUM__A`.
- Phase/lock accumulation registers include `VSB_TOP_PHASELOCKCTRL__A`, `VSB_TOP_DLOCKACCUM__A`, `VSB_TOP_PLOCKACCUM__A`, `VSB_TOP_CLOCKACCUM__A`, `VSB_TOP_DCRMVACUMI__A`, and `VSB_TOP_DCRMVACUMQ__A`.
- `VSB_TOP_PHASELOCKCTRL__A` is one of the more important multi-field controls in this range. Its subfields include force-polarity and force-PLL bits for D, P, and C paths plus `IQSWITCH`.

VSB sysctrl RAM and RAM windows:

- `VSB_SYSCTRL_RAM0_*` begins at `0x1C20000` and runs through `VSB_SYSCTRL_RAM0_FIRRCA1GAIN8__A` at `0x1C2007F`.
- `VSB_SYSCTRL_RAM1_*` begins at `0x1C30000` and runs through `VSB_SYSCTRL_RAM1_DFEDDM2GAIN__A` at `0x1C30035`.
- RAM0 contains 12-entry sequences for FFE train leak ratios, FFE RCA1/RCA2 train/data leak ratios, FFE DDM1/DDM2 train/data leak ratios, FIR train gains, and the first eight FIR RCA1 gain words.
- RAM1 continues FIR RCA1 gains 9-12, defines FIR RCA2 gain words 1-12, FIR DDM1/DDM2 gain words 1-12, and then defines aggregate DFE leak-ratio and gain controls for RCA1/RCA2/DDM1/DDM2 train/data paths.
- Most RAM0 leak-ratio definitions are 12-bit fields (`__W 12`, `__M 0xFFF`). FIR gain words are 15-bit composite words with separate 7-bit train and data gain subfields at bit 0 and bit 8. This is reflected in subfield pairs such as `*_FIRRCA1TRAINGAIN*` and `*_FIRRCA1DATAGAIN*`.
- `VSB_TCMEQ_RAM__A` at `0x1C40000`, `VSB_FCPRE_RAM__A` at `0x1C50000`, and `VSB_EQTAP_RAM__A` at `0x1C60000` define larger RAM apertures with one generated subfield each (`TCMEQ_RAM`, `FCPRE_RAM`, and `EQTAP_RAM` respectively).

## Runtime Control Flow And Usage

The header contributes constants to runtime flows in `drxj.c`.

For MPEG/output pad handling, `ctrl_set_cfg_mpeg_output()` and related output-control logic write SIO PDR registers to switch MPEG transport stream pads between input, serial output, and parallel output. The code uses address macros such as `SIO_PDR_MD4_CFG__A` through `SIO_PDR_MD7_CFG__A` and field-position macros such as `SIO_PDR_MD0_CFG_DRIVE__B` and `SIO_PDR_MD0_CFG_MODE__B` to compose the pad values. When the transport output is disabled or serial-only, the driver writes zero to unused MD pad configuration registers, effectively tri-stating those pins.

For smart-antenna and UIO-related pin control, the driver writes pad config and GPIO function selector registers such as `SIO_PDR_SMA_TX_CFG__A`, `SIO_PDR_SMA_RX_CFG__A`, `SIO_PDR_GPIO_CFG__A`, `SIO_PDR_IRQN_CFG__A`, and the function selectors in this chunk. This lets higher-level smart-antenna or GPIO configuration code decide whether a pin is controlled as a hardware function or general-purpose I/O.

For 8VSB setup, `set_vsb()` first stops the VSB communication executor through `VSB_COMM_EXEC__A` along with FEC and IQM executors, resets/configures the demodulator through SCU commands, writes VSB top-level parameters such as CF/BE AGC gain shifts, carrier tracking gains, burst/noise thresholds, SNR thresholds, equalizer control, and measurement period, then restarts the VSB executor with `VSB_COMM_EXEC_ACTIVE`.

For VSB equalizer and leak/gain initialization, `set_vsb_leak_n_gain()` writes two packed byte tables with `drxdap_fasi_write_block()`. The first block starts at `VSB_SYSCTRL_RAM0_FFETRAINLKRATIO1__A`; the second starts at `VSB_SYSCTRL_RAM1_FIRRCA1GAIN9__A`. Those start addresses depend on the contiguous generated ordering in this chunk. The comments in the initializer arrays line up one-for-one with the RAM0/RAM1 symbols defined here.

For link-quality reporting, the VSB measurement helpers read:

- `VSB_TOP_NR_SYM_ERRS__A` to report pre-Viterbi BER-related symbol error counts.
- `VSB_TOP_ERR_ENERGY_H__A` to calculate VSB MER.
- `VSB_TOP_MEASUREMENT_PERIOD__A` is written during VSB setup so later count calculations use the same measurement window.

There are no C functions, call graphs, locking paths, or allocation paths inside this header itself. Its control-flow role is indirect: it determines which physical register or RAM location each `drxj.c` access reaches.

## State And Persistence Behavior

The constants in this chunk model persistent hardware state rather than software-owned memory state.

SIO pad configuration state persists in the demodulator registers until changed by the driver, hardware reset, or power-state transition. The generated `__PRE` values document expected reset/default states, but runtime code often overwrites them depending on transport-output mode, smart-antenna mode, or low-power/safe pad handling.

VSB `COMM_EXEC` state persists in hardware and gates whether the VSB processing subsystem is stopped, active, or held. The runtime sequence deliberately stops VSB while mode setup and RAM table writes occur, then restarts it after IQM/FEC/VSB configuration is complete. A stale or incorrect `COMM_EXEC` value can leave the VSB datapath inactive even though frontend software state says a standard has been selected.

VSB top-level register state stores live acquisition/tracking, equalizer, AGC, burst-noise, notch, phase-lock, and measurement configuration. Some registers are write-only or tuning-oriented from the driver's perspective; others are status/measurement registers sampled after the demodulator is running.

VSB sysctrl RAM0/RAM1 state stores table-driven equalizer leak and gain parameters loaded by the driver. The tables are not mirrored as a C struct after the block write; the durable copy for the running demodulator is in hardware RAM. Because `drxdap_fasi_write_block()` writes raw bytes to the generated base address, table length, byte order (`DRXJ_16TO8()` packing), and address continuity are the persistence contract.

The generated `__M`, `__B`, and `__W` values are also a form of static state contract. They encode the hardware layout expected by hand-written bit composition in `drxj.c`. If these constants drift from the silicon/firmware register map, the driver can silently set the wrong bits while still compiling cleanly.

## Dependencies And Integration Points

Direct code dependency:

- `drxj.c` includes `drxj_map.h` and consumes the generated constants throughout mode setup, pad configuration, VSB setup, quality measurement, firmware control, and low-power transitions.

Hardware access dependency:

- Address macros feed the DRX DAP/FASI access helpers, primarily `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxdap_fasi_write_reg32()`, and `drxdap_fasi_write_block()`.
- Block writes to `VSB_SYSCTRL_RAM0_*` and `VSB_SYSCTRL_RAM1_*` assume the target addresses are word-addressed and contiguous in the order emitted by this header.

Frontend integration:

- The VSB register block is used when the selected standard is `DRX_STANDARD_8VSB`.
- VSB setup is coordinated with IQM and FEC register blocks outside this chunk. `set_vsb()` stops VSB/FEC/IQM executors, applies IQM filter and ADC/AGC setup, configures FEC output behavior, writes VSB thresholds/gains, and then restarts IQM, VSB, and FEC.
- Signal-quality APIs exposed through the DVB frontend ultimately depend on VSB measurement registers from this chunk when the frontend is operating in 8VSB mode.

Generated map integration:

- The optional `_REGISTERTABLE_` path at the top of the header declares generated register-table metadata, though this chunk only contains the generated `#define` output. The line range relies on the header guard and include established at the top of the file.
- The chunk starts mid-register for `SIO_PDR_MD3_CFG`; the final per-file report should merge this chunk with the preceding chunk to avoid treating the MD3 field list as orphaned.

## Risks And Edge Cases

- This is generated hardware metadata. Manual edits are risky because a single bad address, mask, width, or bit position can redirect a hardware write without producing a compiler error.
- The assigned range starts mid-definition, after the `SIO_PDR_MD3_CFG__A` full-register lines and before the final MD3 field lines. Any standalone reading of this chunk should not infer that MD3 is incomplete in the real header; it is only incomplete in this line slice.
- SIO PDR writes often require a hardware unlock sequence outside this chunk. `drxj.c` writes `SIO_TOP_COMM_KEY__A` before changing PDR registers. Code that uses these SIO address macros without the correct key sequence may see writes ignored or partially applied.
- Several pad registers share the same shape but not the same reset defaults. Copying values between MPEG data, I2C, smart-antenna, I2S, and GPIO pads can break electrical behavior, bus ownership, or board-level pin muxing.
- MPEG serial/parallel output code writes MD pad groups in loops expanded by hand. Missing one of `SIO_PDR_MD4_CFG__A` through `SIO_PDR_MD7_CFG__A`, or using an MD0 field shift for a register whose layout later changes, would cause only some transport bits to drive correctly.
- VSB sysctrl RAM writes rely on table-size and register-map alignment. If a table in `set_vsb_leak_n_gain()` is extended, shortened, or reordered without matching this generated RAM map, all later leak/gain fields in the block can be shifted into the wrong hardware locations.
- The `DRXJ_16TO8()` packed constants written to the RAM windows must match the access layer's byte order. The register map exposes 12-bit/15-bit logical fields, but the runtime writes byte arrays.
- Measurement registers such as `VSB_TOP_NR_SYM_ERRS__A` and `VSB_TOP_ERR_ENERGY_H__A` are meaningful only after VSB measurement-period setup and demodulator startup. Reads while stopped, reset, or on another standard can report stale or meaningless values.
- Some `__PRE` values are not the values used by runtime tuning. For example, `set_vsb()` writes tuned thresholds and gains after reset. Tests should not assume generated `__PRE` is the post-configuration state.
- `VSB_COMM_EXEC__A` and `VSB_TOP_COMM_EXEC__A` have similar names and execution-state values but different addresses. Confusing top-level and subsystem communication registers can stop/start the wrong hardware block.
- The large RAM aperture macros `VSB_TCMEQ_RAM__A`, `VSB_FCPRE_RAM__A`, and `VSB_EQTAP_RAM__A` expose wide memory regions through a single generated base. Access code must know the valid length and element width from surrounding driver/firmware contracts, not from this header alone.

## Test Signals

Build and static checks:

- Compile the DRX39xyJ frontend with `drxj.c` including this generated header; undefined-symbol or duplicate-macro failures catch broken generated output or include ordering.
- Use warnings/static analysis to catch shifts that exceed the destination width when composing values from `__B` and `__M` constants.
- Verify no local patch modifies `drxj_map.h` manually unless it regenerates the map from the authoritative source.

SIO pad and output tests:

- Enable MPEG transport output in serial mode and verify only MD0 is driven while MD1-MD7 are tri-stated through the SIO PDR addresses in this chunk.
- Enable MPEG transport output in parallel mode and verify MD0-MD7, MCLK, MVAL, MSTRT, and MERR all drive with the expected pad mode and drive strength.
- Disable MPEG output and verify the PDR registers return to input/tri-state values.
- Exercise smart-antenna/GPIO direction changes and confirm `SIO_PDR_SMA_RX_CFG__A`, `SIO_PDR_SMA_TX_CFG__A`, and corresponding GPIO function selectors produce the expected pin behavior.
- Probe I2C pad-related defaults carefully on hardware variants that use secondary I2C pins, since their `__PRE` values differ from the MPEG and generic GPIO pad defaults.

VSB setup and operation tests:

- Tune an 8VSB channel and trace register writes to confirm `VSB_COMM_EXEC__A` is stopped before VSB setup/RAM writes and set active after setup.
- Confirm the VSB sysctrl RAM block writes begin at `VSB_SYSCTRL_RAM0_FFETRAINLKRATIO1__A` and `VSB_SYSCTRL_RAM1_FIRRCA1GAIN9__A` with byte counts matching the initializer arrays.
- Validate that VSB lock acquisition still succeeds after writing tuned values to `VSB_TOP_CFAGC_GAINSHIFT__A`, `VSB_TOP_CYGN*`, `VSB_TOP_BNTHRESH__A`, `VSB_TOP_CLPLASTNUM__A`, `VSB_TOP_SNRTH_*`, `VSB_TOP_EQCTRL__A`, `VSB_TOP_BEDETCTRL__A`, and `VSB_TOP_LBAGCREFLVL__A`.
- Read `VSB_TOP_NR_SYM_ERRS__A`, `VSB_TOP_ERR_ENERGY_H__A`, and related measurement registers after a stable VSB lock and compare reported BER/MER against known signal conditions.
- Force weak-signal, burst-noise, and notch-heavy RF scenarios to exercise the threshold and notch-control registers defined in this range.

Regression signals:

- A failure to start VSB demodulation after otherwise successful SCU/IQM/FEC setup points to `VSB_COMM_EXEC__A` sequencing or VSB top-level register writes.
- Incorrect transport stream pin behavior with a working demodulator points to SIO PDR mode/drive/function selector constants.
- Good lock but bad BER/MER reporting points to measurement-period, symbol-error, or error-energy register definitions.
- Hardware that locks only before `set_vsb_leak_n_gain()` changes may indicate a RAM block-write length, address, or byte-order mismatch against the `VSB_SYSCTRL_RAM0/1` map.

## Cross-Chunk Notes

The preceding chunk contains the beginning of the SIO PDR register family, including the full definitions for some MPEG and GPIO pad registers referenced by `drxj.c`. This chunk should be merged with that context for a complete description of transport-output pad handling.

Earlier `drxj_map.h` chunks define ATV, QAM, IQM, FEC, SCU, and other SIO registers that are configured in the same `drxj.c` mode-transition paths. The VSB setup flow depends on those other blocks: IQM and FEC are stopped/configured alongside VSB, then all relevant executors are restarted.

Later per-file reconciliation should preserve that `drxj_map.h` is a generated register-address contract, not a normal implementation unit. The most important behavioral findings come from how `drxj.c` consumes these constants.
