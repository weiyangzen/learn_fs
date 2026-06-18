# subset-b-004072 research

This grouped report covers MaxLinear, Nextwave, Oren, and Realtek DVB frontend drivers under the Ceph client source snapshot. Each source section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.c

## Purpose
`mxl5xx.c` implements the DVB frontend driver for MaxLinear Hydra/MxL5xx satellite tuner-demodulator devices. It exposes one `dvb_frontend` per demodulator while sharing one physical chip state across frontends on the same I2C adapter/address. The driver handles firmware download, SKU validation, crystal and TS-output setup, tuner activation, DVB-S/DVB-S2/DSS tune commands, lock/statistic polling, and teardown.

## Important APIs, Types, And Functions
The exported entry point is `mxl5xx_attach()`, which returns a configured frontend and passes back `set_input()` for tuner input selection. `struct mxl_base` is the shared chip object: I2C address/adapter, SKU/chip/FW metadata, demod/tuner counts, TS map, shared command buffers, frontend list, and three mutexes. `struct mxl` is per frontend and stores demod/tuner ids, selected tuner, `dvb_frontend`, and xbar data. Low-level access is split between `i2c_write()`, `i2c_read()`, `read_register()`, `write_register()`, block accessors, and `send_command()`. Major setup helpers are `probe()`, `validate_sku()`, `load_fw()`, `firmware_download()`, `do_firmware_download()`, `config_mux()`, `config_ts()`, `cfg_ts_pad_mux()`, `cfg_dev_xtal()`, and `set_drive_strength()`. Frontend callbacks are collected in `mxl_ops`: `init`, `release`, `get_frontend_algo`, `tune`, `read_status`, `sleep`, `get_frontend`, and `diseqc_send_master_cmd`.

## Control Flow
Attach either reuses an existing `mxl_base` from the global `mxllist` or allocates/probes a new chip. Probe derives capabilities from `cfg->type`, validates hardware SKU registers, configures crystal parameters, loads firmware if heartbeat is not running, reads firmware/chip info, resets/configures transport muxing, programs serial MPEG/TS output for each demod, and sets output drive strength. Firmware download verifies MBIN headers/checksum, resets CPUs and transport/baseband/xbar blocks, writes aligned firmware segments, handles special MxL568 XCPU sequencing, starts firmware, waits for heartbeat movement, and sends the firmware SKU command.

Tuning validates satellite frequency and symbol-rate ranges, maps DVB delivery systems to Hydra standards, sets rolloff/modulation/pilot/FEC policy, optionally programs DVB-S2 scrambling root from the gold sequence, throttles commands through `tune_lock`, records tuner ownership, builds `MXL_HYDRA_DEMOD_SET_PARAM_CMD`, and sends it through `send_command()`. Sleep aborts the demod tune, releases tuner ownership, and disables the tuner only when no other frontend uses it. Status reads lock firmware status snapshots with `HYDRA_DEMOD_STATUS_LOCK/UNLOCK`, maps a lock register to full DVB lock bits, and refreshes strength, CNR, and BER counters.

## State And Persistence
All driver state is in memory. Firmware is supplied either directly in `mxl5xx_cfg` or by a board callback into a temporary `vmalloc()` buffer; it is not cached after download. `mxl_base` persists as long as at least one frontend for the physical chip exists and is reference-counted by `count`. `fwversion`, `chipversion`, `sku_type`, TS map, demod/tuner limits, and `next_tune` shape later operations. Per frontend state records selected demod/tuner and `tuner_in_use`; this prevents one frontend from disabling a shared tuner still used by another. The hardware persists firmware, register, TS mux, tuner-enable, and demod tune state until reset or power loss.

## Dependencies And Integration Points
The file depends on Linux I2C, firmware, mutex, vmalloc, endian helpers, jiffies timing, and DVB frontend APIs. It consumes protocol constants and payload structs from `mxl5xx_defs.h` and hardware addresses from `mxl5xx_regs.h`. Board integration is through `struct mxl5xx_cfg`: I2C address, Hydra device type, crystal capacitance/frequency, TS clock, optional firmware blob, and optional firmware reader. It integrates with tuner routing through the returned `set_input()` callback and with userspace through DVB-S/S2/DSS frontend operations and statistics.

## Risks
The most sensitive areas are firmware segment parsing/alignment, endian conversion, and shared-chip locking. `send_command()` polls a DMA interrupt bit for newer firmware and can return `-EBUSY`; callers must propagate failures. `config_ts()` contains unusual register-field tables, including entries whose `num_of_bits` values look like encoded per-demod offsets for newer chip versions, making register math fragile. SKU validation is strict and may reject otherwise compatible variants. The global list and reference count depend on balanced frontend release; incorrect board attach/release ordering can leak or prematurely free shared state. Statistics often ignore intermediate read errors and some DiSEqC support is stubbed.

## Test Signals
Useful tests include attach/release of multiple frontends on one physical device, SKU variants 541/542/544/561/568/581/582/584/585, firmware-present and firmware-callback paths, DVB-S/DVB-S2/DSS tuning across frequency and symbol-rate limits, DVB-S2 scrambling sequence changes, concurrent frontend tuning with shared tuner ownership, sleep while another demod uses the tuner, TS clock/pad output validation, I2C fault injection, and lock/statistic reads before and after firmware download.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.h

## Purpose
`mxl5xx.h` is the public board-facing header for the MaxLinear MxL5xx satellite tuner-demodulator driver. It defines the attach configuration that board drivers pass to the demodulator and provides a Kconfig-gated attach stub.

## Important APIs, Types, And Functions
`struct mxl5xx_cfg` carries the chip I2C address, device type, crystal capacitance, crystal clock, TS clock, optional firmware pointer/length, and optional `fw_read()` callback with private data. `mxl5xx_attach()` accepts an I2C adapter, config, demod id, tuner id, and an out-parameter for the driver's `set_input()` callback, returning a `struct dvb_frontend *` when `CONFIG_DVB_MXL5XX` is reachable. The disabled inline implementation logs a warning and returns `NULL`.

## Control Flow
The header has no runtime flow beyond the disabled-driver stub. At runtime `mxl5xx.c` consumes every field in `mxl5xx_cfg`: address/type for shared-chip matching and SKU setup, clock/cap for crystal programming, TS clock for MPEG output rate, firmware fields for loading, and `fw_read()` when firmware is not embedded.

## State And Persistence
The header defines no storage. It describes board-supplied immutable setup data and firmware access. Any returned frontend state is allocated and owned by `mxl5xx.c`.

## Dependencies And Integration Points
It includes Linux types, I2C declarations, and DVB frontend declarations. Board drivers integrate with the demod by including this header and holding the returned frontend and `fn_set_input` callback.

## Risks
The `type`, `clk`, `cap`, and `ts_clk` values are hardware-contract inputs; wrong values can make probe fail or produce invalid clock/TS output. Firmware pointer lifetime must cover attach-time download. The fallback stub uses `pr_warn()`, so users can detect builds where the driver was not enabled.

## Test Signals
Compile tests with `CONFIG_DVB_MXL5XX=y/m/n`, board attach tests with embedded and callback firmware, and validation that the returned `set_input` callback is non-NULL only on successful attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_defs.h

## Purpose
`mxl5xx_defs.h` defines the MaxLinear Hydra firmware command protocol, command payload structs, device/SKU enums, demod/tuner/TS configuration enums, MBIN firmware image headers, and helper macros used by `mxl5xx.c`.

## Important APIs, Types, And Functions
The header provides `enum MXL_HYDRA_HOST_CMD_ID_E` for firmware command ids, PLID constants for register and command reads/writes, max command and block sizes, MBIN file/segment structures, `BUILD_HYDRA_CMD()`, register-field helpers, SKU/device enums, demod/tuner IDs, broadcast standard/FEC/modulation/spectrum/rolloff/pilot enums, channel parameter offsets, TS PID/mux/MPEG output enums and structs, firmware download structures, tuner activation command payloads, and demod tune/scramble/abort payloads. `MXL_HYDRA_DEMOD_PARAM_T` is the main tuning payload, and `MXL_HYDRA_MPEGOUT_PARAM_T` is the main TS output configuration payload.

## Control Flow
The header contains no executable functions except the `BUILD_HYDRA_CMD()` macro. That macro builds the Hydra I2C command frame with PLID, length, payload size, command id, endian conversion, and payload copy. `mxl5xx.c` uses these constants and structs in firmware download, SKU configuration, tuner activation, demod tune, scramble-code programming, and TS output configuration.

## State And Persistence
The structures describe wire-format firmware messages and firmware image layout rather than kernel-owned persistent state. Their field order and sizes form an ABI with MaxLinear firmware. MBIN headers also define the persistent firmware file format expected by the loader.

## Dependencies And Integration Points
The header assumes Linux integer types and that `convert_endian()` is visible before `BUILD_HYDRA_CMD()` is expanded in `mxl5xx.c`. It integrates tightly with `mxl5xx_regs.h` address constants and with MaxLinear firmware semantics for command IDs, SKU values, and TS mux behavior.

## Risks
Changing enum values, struct field order, command IDs, or max lengths can break the firmware protocol. `BUILD_HYDRA_CMD()` mutates the source payload when endian conversion is enabled, so callers must not assume untouched input data in a big-endian configuration. Several protocol names encode vendor assumptions and some comments indicate incomplete or device-specific support; adding features should be checked against firmware documentation.

## Test Signals
Compile coverage on little- and big-endian targets, firmware download with valid/invalid MBIN headers and checksums, command construction tests against known byte sequences, and tuning/TS-output tests for every supported Hydra SKU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_regs.h

## Purpose
`mxl5xx_regs.h` is the register-address map for MaxLinear Hydra/MxL5xx devices. It gives `mxl5xx.c` symbolic names for PRCM, firmware, demod status, tuner status, transport stream, PID, BERT, AGC, AFE, watchdog, FSK, and miscellaneous hardware registers.

## Important APIs, Types, And Functions
The header defines CPU/clock/reset registers, crystal and firmware-version addresses, heartbeat/signature registers, demod and tuner status base/offset macros, status register offsets for lock/SNR/errors/frequency/input power, `HYDRA_DEMOD_STATUS_LOCK()` and `HYDRA_DEMOD_STATUS_UNLOCK()` write macros, TS control base addresses, PID table addresses, XPT/BERT registers, FPGA addresses, AGC/AFE addresses, and XPT DMD xbar base address. It has no types or functions.

## Control Flow
No standalone flow exists. Runtime code in `mxl5xx.c` reads/writes these addresses for firmware reset/download/startup, heartbeat checks, status snapshots, TS muxing, tuner-enable polling, and MPEG output programming.

## State And Persistence
The header defines hardware state locations. Register writes persist in the chip until overwritten, reset, or power cycle. The kernel does not persist these values independently.

## Dependencies And Integration Points
It is consumed by `mxl5xx.c` together with the Hydra protocol definitions. The lock/unlock macros rely on a `write_register()` helper and `MXL_YES/MXL_NO` from `mxl5xx_defs.h`, so include ordering matters.

## Risks
Incorrect addresses or offsets can corrupt unrelated hardware blocks. Some macros duplicate names (`HYDRA_HEAR_BEAT`) and many constants are raw vendor addresses; maintainability depends on preserving the original datasheet mapping. The status offset macros assume a fixed stride per demod/tuner.

## Test Signals
Hardware probe, firmware heartbeat/version reads, demod lock/statistics reads for multiple demod IDs, TS output validation, and register tracing during init/tune are the practical tests for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692.c

## Purpose
`mxl692.c` implements the MaxLinear MxL692 combo tuner-demodulator I2C driver. It handles firmware download, device reset/regulator/XTAL setup, active/sleep power modes, ATSC and QAM tuning commands, DVB frontend status/statistics, PID-independent transport output setup, and I2C driver registration.

## Important APIs, Types, And Functions
The central state is `struct mxl692_dev`, containing the frontend, I2C client, command mutex, current demod type, power mode, current frequency, device type, host-message sequence number, and init flag. I2C primitives are `mxl692_i2c_write()`/`mxl692_i2c_read()`, memory accessors are `mxl692_memwrite()`/`mxl692_memread()`, and host-message access is `mxl692_i2c_writeread()` with `mxl692_opwrite()`/`mxl692_opread()`. Firmware helpers include `mxl692_validate_fw_header()`, `mxl692_write_fw_block()`, `mxl692_fwdownload()`, and `mxl692_get_versions()`. Hardware setup uses `mxl692_reset()`, `mxl692_config_regulators()`, `mxl692_config_xtal()`, and `mxl692_powermode()`. Frontend callbacks are `mxl692_init()`, `mxl692_sleep()`, `mxl692_set_frontend()`, `mxl692_get_frontend()`, `mxl692_read_status()`, `mxl692_read_snr()`, and `mxl692_read_ber_ucb()`.

## Control Flow
I2C probe allocates state, copies frontend ops, stores the I2C client, initializes `i2c_lock`, and publishes the frontend through platform data. First frontend init resets legacy I2C mode, verifies SKU, configures regulators and crystal, requests `dvb-demod-mxl692.fw`, downloads DRAM/IRAM segments, releases CPU reset, waits for firmware, reads version, and marks the device initialized. Later init calls only ensure active power and reset supported stats.

Host commands are packetized with opcode, sequence number, payload size, status, and checksum. `mxl692_i2c_writeread()` endian-swaps opcode-specific payload fields, writes the command, polls for a nonzero response, validates status, sequence, opcode, payload length, and checksum, then swaps/copies the response. Tuning selects ATSC for `VSB_8` and QAM for QAM modulation values, avoids redundant retunes for unchanged frequency/type, sets demodulator type, programs MPEG output, programs QAM params for cable modes, sends tuner channel tune, and starts ATSC init or QAM restart.

## State And Persistence
The driver keeps in-memory `init_done`, `seqnum`, `power_mode`, `current_frequency`, and `demod_type`. Statistics accumulate in DVB property counters, especially ATSC post-bit and block error counts. Firmware and hardware configuration are resident in the chip after download; the firmware blob itself is released. Sleep only changes firmware power mode and marks state.

## Dependencies And Integration Points
It depends on Linux I2C client/driver infrastructure, firmware loading, mutexes, DVB frontend APIs, endian helpers, and protocol declarations in `mxl692_defs.h`. Board integration is through `struct mxl692_config` as I2C platform data, mainly to receive the allocated frontend pointer. Module firmware metadata names `dvb-demod-mxl692.fw`.

## Risks
The command protocol is sensitive to endian conversion, payload packing, checksum computation, sequence wrap, and the 40-iteration response timeout. `mxl692_reset()` compares a register against `dev->device_type`, but probe does not initialize `device_type` in this file, which makes platform setup or default assumptions important. QAM support is partially exposed through tuning logic while `delsys` and caps advertise only ATSC/8VSB. Error counters are ATSC-only and QAM statistics are less complete. Firmware download assumes two segments at fixed positions after a 16-byte header.

## Test Signals
Tests should cover probe/remove, missing and invalid firmware, successful firmware download/version read, sleep/wake cycles, repeated tune suppression, ATSC 8VSB lock/statistics, QAM tune attempts where board/userspace exposes them, I2C command timeout/checksum fault injection, and big-endian build/runtime validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692.h

## Purpose
`mxl692.h` is the public board-facing header for the MxL692 driver. It names the firmware file and defines the small platform-data structure used to hand the created DVB frontend back to the parent device.

## Important APIs, Types, And Functions
`MXL692_FIRMWARE` is `dvb-demod-mxl692.fw`. `struct mxl692_config` contains an `id`, an I2C address field, and `struct dvb_frontend **fe`, which the probe routine fills with the allocated frontend.

## Control Flow
The header has no executable flow and declares no attach function. The driver is an `i2c_driver`; board code instantiates an I2C client with this platform data, then `mxl692_probe()` fills `*fe`.

## State And Persistence
No state is stored here. The `fe` pointer is an out-parameter owned by the parent/board integration after probe, while runtime state is private to `mxl692.c`.

## Dependencies And Integration Points
It includes DVB frontend declarations and is consumed by board drivers and `mxl692.c`. The firmware macro is used both for `request_firmware()` and `MODULE_FIRMWARE()`.

## Risks
The `i2c_addr` and `id` fields are not actively used by the shown probe path, so parent drivers must rely on normal I2C client address setup and not expect the header fields to configure the bus. A NULL `fe` out pointer would crash probe.

## Test Signals
Compile and module-load tests, I2C client instantiation with valid platform data, and missing firmware diagnostics through the named firmware file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692_defs.h

## Purpose
`mxl692_defs.h` defines the MaxLinear Eagle/MxL69x firmware protocol used by `mxl692.c`: packet sizes, firmware format limits, opcodes and debug names, device/demod/power/tuner enums, MPEG/QAM/OOB/ATSC/SMA structs, and packed host-message payloads.

## Important APIs, Types, And Functions
Key constants include host-message header size, firmware header/segment sizes, max I2C packet size, firmware load time, and firmware max size. `enum MXL_EAGLE_OPCODE_E` and `MXL_EAGLE_OPCODE_STRING[]` define all host-command IDs used for device, tuner, ATSC, QAM, OOB, SMA, and internal commands. Important structs include `MXL_EAGLE_HOST_MSG_HEADER_T`, `MXL_EAGLE_DEV_VER_T`, `MXL_EAGLE_DEV_XTAL_T`, `MXL_EAGLE_DEV_STATUS_T`, `MXL_EAGLE_MPEGOUT_PARAMS_T`, `MXL_EAGLE_QAM_DEMOD_PARAMS_T`, `MXL_EAGLE_QAM_DEMOD_STATUS_T`, `MXL_EAGLE_ATSC_DEMOD_STATUS_T`, `MXL_EAGLE_ATSC_DEMOD_ERROR_COUNTERS_T`, and `MXL_EAGLE_TUNER_CHANNEL_PARAMS_T`.

## Control Flow
The header is declarative. `mxl692.c` uses the opcode enum to select endian-swap logic, command names for diagnostics, payload structs for command construction/parsing, and firmware constants during validation/download.

## State And Persistence
These definitions describe firmware wire formats and hardware command semantics. Packed structs are part of the host/firmware ABI. Persistent runtime state lives in firmware and device registers, not in this header.

## Dependencies And Integration Points
The file depends on Linux integer types and `__packed` support through included kernel headers in the C file. It integrates with the MxL692 firmware and with DVB frontend logic that maps Linux modulation/frequency requests into Eagle demod/tuner payloads.

## Risks
Struct packing and endian conversions must match firmware exactly. Changing opcode ordering breaks `MXL_EAGLE_OPCODE_STRING[]` indexing and command IDs. Some constants are duplicated, and many protocol areas are defined even if the current driver only uses a subset, so future feature additions need careful swap/checksum coverage.

## Test Signals
Build tests with structure packing warnings enabled, known-command byte-vector checks, firmware validation/download tests, ATSC and QAM status payload parsing, and endian coverage on big- and little-endian kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl692_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.c

## Purpose
`nxt200x.c` supports Nextwave NXT2002 and NXT2004 ATSC 8VSB / ITU J.83 Annex B QAM demodulators. It detects the chip variant, loads external firmware, controls the demod microcontroller, configures tuner and demod registers for VSB/QAM, exposes DVB frontend status/statistics, and provides the `nxt200x_attach()` API for board drivers.

## Important APIs, Types, And Functions
`struct nxt200x_state` holds the I2C adapter, board config, frontend, detected chip type, and initialization flag. I2C helpers are `i2c_writebytes()`, `i2c_readbytes()`, `nxt200x_writebytes()`, and `nxt200x_readbytes()`. Multi-register helpers `nxt200x_writereg_multibyte()` and `nxt200x_readreg_multibyte()` abstract variant-specific indirect register access. Firmware helpers are `nxt200x_crc()`, `nxt2002_load_firmware()`, `nxt2004_load_firmware()`, `nxt2002_init()`, and `nxt2004_init()`. Tuning uses `nxt200x_setup_frontend_parameters()`, `nxt200x_writetuner()`, `nxt200x_agc_reset()`, and microcontroller start/stop helpers. Public export is `nxt200x_attach()`.

## Control Flow
Attach allocates state, reads five ID bytes from the demod, selects NXT2002 or NXT2004, verifies known IDs, copies `nxt200x_ops`, and returns the frontend. First `init` requests the matching firmware file, downloads it with the chip-specific loader, then runs a long register initialization sequence. NXT2002 firmware is chunked with CRCs and RAM-base selection; NXT2004 firmware uses a fixed RAM base, whole-image CRC, and 255-byte writes.

Tuning stops the microcontroller, performs NXT2004 digital-mode setup, asks board code to set punctured TS clock for QAM or non-punctured for VSB, obtains tuner register bytes through `tuner_ops.calc_regs`, writes them either directly or through the demod depending on chip type, resets AGC, programs target power, SDM, accumulators, AGC controls, modulation-specific values, and restarts the microcontroller. Status reads register `0x31` and maps bit `0x20` to full DVB lock. BER, signal strength, SNR, and uncorrected block reads come from indirect registers around `0xA6` and `0xE6`.

## State And Persistence
`initialised` prevents repeated firmware loads. `demod_chip` selects firmware, register sequences, multireg protocol, and tuner write path. Hardware retains firmware and register configuration until reset. No persistent kernel metadata is stored.

## Dependencies And Integration Points
The driver depends on Linux firmware loading, I2C, DVB frontend APIs, tuner operations (`calc_regs`), and the board callback `set_ts_params()` from `nxt200x_config`. Firmware files are `dvb-fe-nxt2002.fw` and `dvb-fe-nxt2004.fw`.

## Risks
The code is built around undocumented register sequences with many comments marked unknown. Several helper calls ignore return values, so I2C failures can be masked. `nxt200x_writereg_multibyte()` logs an error but still returns 0 after failed completion polling. Firmware download and CRC handling are variant-specific and can silently misconfigure if the wrong firmware is supplied. Statistics scaling is approximate and old DVBv3 style.

## Test Signals
Hardware attach for NXT2002 and NXT2004 cards, missing/wrong firmware tests, VSB/QAM tuning with tuner `calc_regs`, TS puncture callback verification, lock acquisition and statistic reads, I2C failure injection during firmware and multireg access, and repeated init/tune/sleep cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.h

## Purpose
`nxt200x.h` is the public attach/configuration header for NXT2002/NXT2004 VSB/QAM demodulators.

## Important APIs, Types, And Functions
`nxt_chip_type` enumerates `NXTUNDEFINED`, `NXT2002`, and `NXT2004`. `struct nxt200x_config` supplies the demodulator I2C address and optional `set_ts_params()` callback used to switch board DMA/TS parameters for punctured versus non-punctured clocks. `nxt200x_attach()` is exported when `CONFIG_DVB_NXT200X` is reachable, with a warning stub otherwise.

## Control Flow
The header contains only declarations and the disabled-driver stub. Runtime attach and detection are implemented in `nxt200x.c`.

## State And Persistence
It defines no persistent state. The config object is board-owned and referenced by the driver.

## Dependencies And Integration Points
It includes DVB frontend and firmware declarations. Board drivers integrate by creating a config, calling `nxt200x_attach()`, and wiring tuner operations into the returned frontend.

## Risks
An incorrect demod I2C address prevents chip detection. Missing `set_ts_params()` is tolerated but may break TS output on boards that require clock-mode changes for QAM/VSB.

## Test Signals
Build coverage for enabled/disabled Kconfig, attach with valid and invalid I2C addresses, and VSB/QAM board callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000.c

## Purpose
`nxt6000.c` implements the NxtWave NXT6000 DVB-T demodulator frontend. It programs OFDM/Viterbi/RS/AGC/TS registers, tunes bandwidth/guard/mode/inversion settings, gates tuner I2C access, reads lock and signal statistics, and exports `nxt6000_attach()`.

## Important APIs, Types, And Functions
`struct nxt6000_state` stores the I2C adapter, board config, and frontend. Low-level register helpers are `nxt6000_writereg()` and `nxt6000_readreg()`. Setup/control helpers include `nxt6000_reset()`, `nxt6000_setup()`, `nxt6000_set_bandwidth()`, `nxt6000_set_guard_interval()`, `nxt6000_set_inversion()`, `nxt6000_set_transmission_mode()`, and `nxt6000_i2c_gate_ctrl()`. Frontend callbacks include init, set_frontend, get_tune_settings, read_status, read_ber, read_signal_strength, read_snr, release, and i2c gate control.

## Control Flow
Attach allocates state, verifies `OFDM_MSC_REV` equals `NXT6000ASICDEVICE`, copies ops, and returns the frontend. Init toggles core reset and writes a default setup table for RS sync, BER timing, Viterbi interrupts/control, OFDM core/mode/AGC, ITB frequency, carrier acquisition, TPS/symbol tracking, PPM, nominal rate, analog control, acquisition, diagnostics, clock inversion, and TS format. Tune first lets the tuner set parameters and closes the I2C gate, then programs bandwidth nominal rate, guard interval, transmission mode, and inversion before a 500 ms settle delay. Status reads AGC, symbol recovery, Viterbi, RS, and TPS bits to build the DVB lock mask.

## State And Persistence
Runtime state is minimal and in memory. Hardware register settings persist on the chip until reset/power loss. The driver does not cache current tune parameters or persistent counters.

## Dependencies And Integration Points
The file depends on the register/bit map in `nxt6000_priv.h`, public config in `nxt6000.h`, Linux I2C, and DVB frontend/tuner operations. The I2C gate exposes tuner access by writing `ENABLE_TUNER_IIC`.

## Risks
Many setup values are magic constants from old hardware support. Most register writes are not retried, and reads return a byte even after transfer failure, so fault handling is limited. Only a subset of DVB-T parameters is actively programmed; code rate, hierarchy, and constellation are effectively auto-detected rather than explicitly set. Debug status dumping reads many registers and can add I2C overhead.

## Test Signals
Attach ID-read tests, init register trace comparison, DVB-T tune across 6/7/8 MHz bandwidths, guard intervals, 2K/8K modes, inversion on/off, tuner I2C gate behavior, BER/SNR/strength reads, lock acquisition timing, and I2C fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000.h

## Purpose
`nxt6000.h` is the board-facing header for the NXT6000 DVB-T demodulator driver.

## Important APIs, Types, And Functions
`struct nxt6000_config` provides the demodulator I2C address and a one-bit `clock_inversion` option. `nxt6000_attach()` is exported when `CONFIG_DVB_NXT6000` is reachable and otherwise replaced by a warning stub.

## Control Flow
No executable flow is defined beyond the Kconfig-disabled stub. `nxt6000.c` uses the config during attach, register I/O, setup, and clock inversion programming.

## State And Persistence
The header defines board configuration only. State allocated by attach is private to `nxt6000.c`.

## Dependencies And Integration Points
It includes DVB frontend declarations and is used by board drivers that instantiate NXT6000 demods and attach tuners to the returned frontend.

## Risks
Wrong I2C address prevents probe; wrong clock inversion setting can break transport stream timing. The config is referenced by the driver and should remain valid for the frontend lifetime.

## Test Signals
Kconfig build coverage, attach with valid/invalid demod address, and TS validation with both clock inversion settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000_priv.h

## Purpose
`nxt6000_priv.h` is the private register and bit-mask map for the NXT6000 DVB-T demodulator. It gives `nxt6000.c` names for RS, BER, Viterbi, OFDM, AGC, tuner I2C, diagnostics, TS format, and chip revision registers.

## Important APIs, Types, And Functions
The header defines register addresses such as `RS_COR_STAT`, `BER_CTRL`, `VIT_SYNC_STATUS`, `OFDM_COR_CTL`, `OFDM_COR_STAT`, `OFDM_COR_MODEGUARD`, `OFDM_AGC_CTL`, `OFDM_ITB_CTL`, `OFDM_SYR_STAT`, `OFDM_TRL_NOMINALRATE_*`, `OFDM_CHC_SNR`, `OFDM_MSC_REV`, `ENABLE_TUNER_IIC`, `EN_DMD_RACQ`, `DIAG_CONFIG`, `SUB_DIAG_MODE_SEL`, and `TS_FORMAT`. Bit masks include lock/status indicators, reset bits, BER control flags, AGC/mode flags, clock inversion, TS signal polarity flags, and `NXT6000ASICDEVICE`.

## Control Flow
There is no executable flow. The C file uses these constants to write the initialization sequence, tune DVB-T parameters, read lock/statistics, and gate the tuner bus.

## State And Persistence
The definitions represent hardware register state. Writes persist in the chip until reset/power loss; this header stores no kernel state.

## Dependencies And Integration Points
It is private to the NXT6000 driver and expects the C file to provide I2C read/write helpers. The register names encode the interface between frontend callbacks and demod hardware.

## Risks
Changing constants changes hardware behavior directly. Some aliases are duplicated and comments indicate old names, so cleanup can accidentally break compatibility with code that uses either alias. A few masks include semicolons or formatting oddities inherited from vendor-era code.

## Test Signals
Compile coverage, attach chip-revision verification, init/tune register traces, and status/statistic reads are the effective validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt6000_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51132.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51132.c

## Purpose
`or51132.c` supports the Oren OR51132 demodulator used by pcHDTV HD-3000 class hardware for ATSC 8VSB and J.83 Annex B QAM64/QAM256. It loads modulation-specific firmware, switches receiver modes, delegates tuner setup, reads lock and modulation state, calculates SNR/strength, and exports `or51132_attach()`.

## Important APIs, Types, And Functions
`struct or51132_state` stores I2C adapter, board config, frontend, current modulation, last fixed-point SNR, and current frequency. I/O helpers are `or51132_writebuf()`, `or51132_readbuf()`, `or51132_readreg()`, and the constant-byte macro `or51132_writebytes()`. Firmware and mode helpers are `or51132_load_firmware()`, `modulation_fw_class()`, `or51132_setmode()`, and `or51132_set_parameters()`. Frontend reads are `or51132_get_parameters()`, `or51132_read_status()`, `or51132_read_snr()`, `or51132_read_signal_strength()`, plus placeholder BER/UCB functions.

## Control Flow
Attach initializes state with current frequency/modulation set to invalid sentinel values and returns a frontend. Setting parameters compares the new modulation's firmware class with the current one; switching between VSB and QAM requests either `dvb-fe-or51132-vsb.fw` or `dvb-fe-or51132-qam.fw`, uploads the two firmware chunks described by little-endian lengths at the start of the file, sends run commands, reads/logs microcode version, and calls board `set_ts_params()` with non-punctured VSB or punctured QAM clock mode. It then writes receiver mode registers, calls tuner `set_params`, closes any I2C gate, writes mode again, and records frequency.

Status and get_frontend read receiver status register 0. Low byte values identify VSB/QAM64/QAM256; bit `0x0100` indicates lock. SNR reads equalizer noise register 2, chooses a modulation-specific fixed-point logarithm constant, adjusts VSB for NTSC rejection, computes `10*(c - 2*log10(MSE))`, and scales to DVBv3 SNR/strength.

## State And Persistence
The driver caches only the current modulation class, exact modulation, frequency, and last SNR. Hardware firmware and receiver mode persist until overwritten or reset. No BER/UCB counters are maintained.

## Dependencies And Integration Points
It depends on Linux firmware, I2C, `intlog10()`, DVB frontend/tuner APIs, and board `or51132_config` with demod I2C address and `set_ts_params()`. It integrates with external tuner operations through the returned frontend.

## Risks
Firmware format and mode commands are strict and lightly validated. Modulation switching is firmware-class based, so wrong cache state can skip required reloads. Some errors return `-1` rather than canonical errno. BER/UCB are stubbed as zero. The SNR equation depends on datasheet constants and unsigned clipping; bad status reads can produce retries or remote I/O errors.

## Test Signals
Firmware missing/corrupt tests for both VSB and QAM files, VSB/QAM64/QAM256 tuning transitions, TS clock callback validation, tuner handoff, receiver status decoding, SNR/strength sanity across signal levels, and I2C fault injection during firmware upload and register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51132.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51132.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51132.h

## Purpose
`or51132.h` is the public configuration/attach header for the OR51132 VSB/QAM demodulator.

## Important APIs, Types, And Functions
`struct or51132_config` supplies the demodulator I2C address and a `set_ts_params()` callback used to switch the board's transport/DMA mode between non-punctured VSB and punctured QAM clocks. `or51132_attach()` returns a `dvb_frontend *` when `CONFIG_DVB_OR51132` is reachable, with a warning stub otherwise.

## Control Flow
Only the disabled-driver stub has inline behavior. Runtime attach, firmware loading, and tuning are in `or51132.c`.

## State And Persistence
The header stores no state. The config is board-owned and referenced by the demod driver.

## Dependencies And Integration Points
It includes firmware and DVB frontend headers. Board drivers call the attach function and provide tuner operations through the returned frontend.

## Risks
Incorrect demod address or missing TS callback can prevent operation or produce bad TS timing when switching VSB/QAM. The config must remain valid for the frontend lifetime.

## Test Signals
Kconfig enabled/disabled builds, successful attach with a valid I2C address, VSB/QAM mode changes that invoke `set_ts_params()`, and board-level stream validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51132.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51211.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51211.c

## Purpose
`or51211.c` supports the Oren OR51211 demodulator used by pcHDTV HD-2000 class ATSC 8VSB hardware. It loads external firmware with board-specific EEPROM/reset help, configures VSB receiver mode, delegates tuner setup, reads lock status, estimates SNR/strength, and exports `or51211_attach()`.

## Important APIs, Types, And Functions
`struct or51211_state` stores the I2C adapter, board config, frontend, optional `bt878` pointer, initialization flag, last SNR, and current frequency. I2C helpers are `i2c_writebytes()` and `i2c_readbytes()`, where the first argument is used as the I2C address. Firmware/mode helpers are `or51211_load_firmware()`, `or51211_init()`, `or51211_setmode()`, and `or51211_set_parameters()`. Frontend statistic callbacks are `or51211_read_status()`, `or51211_read_snr()`, `or51211_read_signal_strength()`, `or51211_read_ber()`, and `or51211_read_ucblocks()`.

## Control Flow
Attach allocates state, stores config/I2C, clears initialization, copies frontend ops, and returns the frontend. First init asks board config to request `dvb-fe-or51211.fw`, builds a firmware buffer by combining two regions of the firmware file with 192 bytes of EEPROM data read from address `0x50`, calls board reset, writes the staged firmware blocks to the demod, sends run commands, sets receiver register 1 for automatic ATSC/VSB operation, and reads/logs microcode version/status. Tuning only retunes when frequency changes: it calls tuner `set_params`, closes any I2C gate, invokes `or51211_setmode(fe, 0)`, and caches the frequency.

Status sends a receiver-status command and maps bit 0 of the two-byte response to full DVB lock. SNR sends an equalizer-noise command, reads one noise byte, computes fixed-point VSB SNR with `intlog10()`, and strength scales the cached 8.24 SNR to 0..65535. BER/UCB callbacks return `-ENOSYS` through unsigned output variables while reporting success.

## State And Persistence
`initialized` prevents repeated firmware upload. `current_frequency` suppresses duplicate tune work. Firmware and receiver mode persist in hardware until reset. Board callbacks own reset, sleep, request_firmware, and mode side effects.

## Dependencies And Integration Points
The driver depends on Linux I2C, firmware, `intlog10()`, DVB frontend/tuner APIs, and `struct or51211_config` callbacks. It is tightly coupled to the board EEPROM layout and demod firmware file format.

## Risks
Firmware staging assumes fixed firmware offsets and EEPROM size. Many failures return `-1` instead of errno. `or51211_read_ber()` and `_read_ucblocks()` assign negative values to unsigned counters, which can surprise callers. The public ops list includes `SYS_DVBC_ANNEX_B` even though caps and implementation are VSB-only. Board callbacks are mandatory and unchecked before use.

## Test Signals
Firmware request/load with valid and missing files, EEPROM read failure injection, board reset/mode/sleep callback coverage, ATSC tune/lock/SNR reads, repeated init suppression, and verification that BER/UCB behavior is acceptable for userspace consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51211.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51211.h

## Purpose
`or51211.h` is the public configuration/attach header for the OR51211 VSB demodulator.

## Important APIs, Types, And Functions
`struct or51211_config` supplies demodulator I2C address plus board callbacks: `request_firmware()`, `setmode()`, `reset()`, and `sleep()`. `or51211_attach()` returns a frontend when `CONFIG_DVB_OR51211` is reachable, with a warning stub otherwise.

## Control Flow
The header only declares the attach path and disabled-driver stub. Runtime behavior is in `or51211.c`, which calls every config callback during init, tune, release, or firmware load.

## State And Persistence
No state is stored here. The config object is board-owned and must remain valid while the frontend exists.

## Dependencies And Integration Points
It includes DVB frontend and firmware declarations. Board drivers use it to provide demod reset, firmware retrieval, mode switching, sleep, and the I2C address.

## Risks
The callbacks are not optional in practice; NULL callbacks will crash. `request_firmware()` takes a mutable `char *name` rather than `const char *`, matching old driver conventions but constraining callers.

## Test Signals
Kconfig enabled/disabled builds, attach/release with all callbacks, missing-callback negative tests in board integration, and firmware load through the board-provided request path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/or51211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830.c

## Purpose
`rtl2830.c` implements the Realtek RTL2830 DVB-T demodulator as an I2C client driver. It creates a DVB frontend, owns a regmap over paged demod registers, exposes a one-transfer I2C repeater for the tuner, programs demod init/tune tables, reports DVB-T TPS/status/statistics, and provides PID filter callbacks through platform data.

## Important APIs, Types, And Functions
The private state is `struct rtl2830_dev` from `rtl2830_priv.h`. Regmap wrappers `rtl2830_bulk_write()`, `rtl2830_bulk_read()`, and `rtl2830_update_bits()` take the I2C segment lock around regmap operations. Frontend callbacks are `rtl2830_init()`, `rtl2830_sleep()`, `rtl2830_get_tune_settings()`, `rtl2830_set_frontend()`, `rtl2830_get_frontend()`, `rtl2830_read_status()`, `rtl2830_read_snr()`, `rtl2830_read_ber()`, `rtl2830_read_ucblocks()`, and `rtl2830_read_signal_strength()`. PID support is in `rtl2830_pid_filter_ctrl()` and `rtl2830_pid_filter()`. I2C repeater and regmap integration use `rtl2830_select()`, `rtl2830_regmap_read()`, `rtl2830_regmap_write()`, `rtl2830_regmap_gather_write()`, and probe/remove.

## Control Flow
Probe validates platform data, allocates state, initializes a paged regmap whose selector register is `0x00`, reads register 0 to check I2C access, creates one muxed tuner adapter, copies frontend ops, stores the I2C client in `demodulator_priv`, and fills platform callback pointers for frontend, tuner adapter, and PID filtering. Init writes a table of masked demod registers using platform AGC/inversion values, writes IF/AGC helper tables, toggles soft reset, initializes supported stats, and clears `sleeping`.

Tuning calls tuner `set_params`, maps bandwidth 6/7/8 MHz to register table indices, asks tuner for IF frequency, computes a 22-bit negative IF control word from IF frequency and platform clock, preserves high bits from register `0x119`, writes bandwidth filter coefficients in split I2C writes, and writes additional bandwidth parameters. `get_frontend()` decodes TPS bytes into modulation, transmission mode, guard interval, hierarchy, and HP/LP code rates. `read_status()` maps state 11 to full lock and 10 to partial signal/carrier/Viterbi, then updates relative strength from signed IF AGC, CNR from constellation/hierarchy-specific constants plus `intlog10()`, and cumulative BER counters when locked.

## State And Persistence
The driver tracks `sleeping`, last `fe_status`, enabled PID filter bits, cumulative post-bit errors/count, and previous error count for DVBv3 `read_ber()`. Hardware register setup and PID tables persist in the demod until reset or reprogrammed. The I2C mux opens the repeater for a single tuner transfer and hardware closes it automatically.

## Dependencies And Integration Points
It depends on Linux I2C client/driver APIs, I2C mux, regmap, `intlog10()`, math64, bitops, and DVB frontend APIs. Platform data supplies clock, AGC and inversion parameters and receives callbacks. Tuner integration needs `set_params()` and `get_if_frequency()`.

## Risks
Regmap uses unlocked `__i2c_transfer()` for mux compatibility, so the wrapper locking contract is important; direct regmap calls are only used where the adapter is already locked or intentionally unlocked for mux select. `rtl2830_regmap_gather_write()` uses a fixed 256-byte stack buffer and assumes writes fit. IF control math depends on valid platform clock and tuner IF reporting. PID index/bitmap is limited to 32 entries and invalid PID/index requests are silently ignored. `delsys` advertises DVB-T only; no DVB-T2 support.

## Test Signals
Probe/remove with valid/invalid platform data, regmap page reads/writes, tuner adapter access through the mux, init register table verification, 6/7/8 MHz DVB-T tuning with different IF frequencies/clocks, TPS decode tests, lock/statistics reads, PID filter programming for indices 0..31, sleep behavior, and I2C fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830.h

## Purpose
`rtl2830.h` is the public platform-data header for the RTL2830 DVB-T demodulator I2C driver.

## Important APIs, Types, And Functions
`struct rtl2830_platform_data` supplies board parameters: demod clock, spectrum inversion, AGC take-over point, AGC ratio, and AGC target. Probe fills callback fields `get_dvb_frontend`, `get_i2c_adapter`, `pid_filter`, and `pid_filter_ctrl` so parent drivers can retrieve the frontend/tuner adapter and control the demod PID filter.

## Control Flow
The header contains no executable code. Platform data is consumed and augmented by `rtl2830_probe()`.

## State And Persistence
No state is stored in the header. The platform data object must remain valid after probe because the driver keeps `dev->pdata` and writes callbacks back into it.

## Dependencies And Integration Points
It includes DVB frontend declarations and references `struct i2c_client`/`struct i2c_adapter` through callback signatures. Parent USB/bridge drivers instantiate the I2C client with this platform data and then use the callbacks.

## Risks
Invalid clock or AGC values directly affect demod programming. The driver writes callback pointers into platform data, so read-only or short-lived platform data is unsafe. Callback users must wait until successful probe.

## Test Signals
Probe with valid platform data, callback population checks, frontend/tuner adapter retrieval, PID filter callbacks from the bridge driver, and tuning with every supported clock configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830_priv.h

## Purpose
`rtl2830_priv.h` defines the private runtime state and register-table tuple used by the RTL2830 demodulator driver.

## Important APIs, Types, And Functions
`struct rtl2830_dev` holds platform data, I2C client, regmap, I2C mux core, DVB frontend, sleeping flag, PID filter bitmap, cached frontend status, cumulative post-bit error/count counters, and previous error count for old `read_ber()`. `struct rtl2830_reg_val_mask` represents one masked register update with 16-bit logical register address, value, and mask.

## Control Flow
The header has no executable flow. `rtl2830.c` allocates `rtl2830_dev` in probe, fills all fields, uses it from frontend callbacks through `i2c_get_clientdata()`, and frees it in remove.

## State And Persistence
All fields are in-memory and per I2C client. Hardware register and PID state persists separately in the demod after writes, while these fields cache frontend status and aggregate counters for userspace reads.

## Dependencies And Integration Points
It includes DVB frontend, integer-log, public RTL2830 platform data, I2C mux, math64, regmap, and bitops headers. It is private to `rtl2830.c` and should not be consumed by board drivers.

## Risks
The `filters` bitmap is an `unsigned long` but the driver treats it as 32 PID filter bits; this is fine on 32/64-bit kernels but should not be extended without revisiting serialization and register layout. Counter fields are updated in status reads without explicit locking, relying on frontend call serialization expectations. Lifetime is tied to I2C clientdata and remove.

## Test Signals
Build coverage, probe/remove memory lifetime checks, PID filter bitmap updates, cumulative BER accounting across repeated status/read_ber calls, and sleep/status state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2830_priv.h -->
