# subset-b-004201 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.c

Purpose: DVB-USB v2 bridge driver for Leaguerme LME2510/LME2510C DM04/QQBOX DVB-S USB receivers, including several frontend/tuner pairings: TDA10086/TDA8263, STV0288/IX2505V, STV0299/Opera PLL, and M88RS2000/TS2020. It handles firmware selection/download, vendor USB control messages, I2C tunneling, LNB voltage/power, PID filtering, interrupt-based remote/status updates, frontend operation wrapping, and USB stream configuration.

Important APIs/types/functions: `struct lme2510_state` stores firmware/tuner identity, I2C gate parameters, PID state, cached signal/lock data, interrupt URB, USB scratch buffer, and saved frontend callbacks. `lme2510_usb_talk()` serializes generic USB bulk control exchanges. `lme2510_i2c_xfer()` maps Linux I2C messages into device gate commands. `dm04_lme2510_frontend_attach()`, `dm04_lme2510_tuner()`, `lme2510_identify_state()`, `lme2510_download_firmware()`, `lme2510_streaming_ctrl()`, `lme2510_pid_filter_ctrl()`, and `lme2510_pid_filter()` are the main dvb-usbv2 hooks. `lme2510_int_response()` decodes NEC32 remote packets and tuner status interrupt records.

Control flow: probe is delegated to `dvb_usbv2_probe()` using `lme2510_props`. `identify_state()` resets USB configuration/interface, reads firmware status, and returns COLD/WARM; cold firmware is selected by product ID and optional module state, with `lme_firmware_switch()` falling through among available firmware files and cold-reseting when the detected frontend requires another image. Firmware download sends two chunks of checksummed packets, then returns `RECONNECTS_USB`. On warm attach, frontend probing tries supported demods in order, adjusts I2C gate fields and firmware identity, then wraps frontend read/stat/voltage callbacks. Tuner attach loads the matching tuner, starts the interrupt URB, and streaming begins only after `dm04_read_status()` sees FE_HAS_LOCK and restarts the stream with the current PID mode.

State and persistence: all state is per device in `lme2510_state`; there is no disk persistence. Hardware-visible state includes selected firmware image, LNB power/voltage, PID filter table length, stream-on flag, I2C gate mode, frontend register state, and interrupt URB submission. During streaming `i2c_talk_onoff` is used as a software gate: frontend status reads can temporarily resume I2C and restart streaming after lock, while signal/SNR values come from interrupt messages.

Dependencies and integration: depends on dvb-usbv2, Linux USB and RC core, I2C, several DVB frontend/tuner modules, and firmware files declared with `MODULE_FIRMWARE()`. It exposes three USB IDs via `DVB_USB_DEVICE`, bulk MPEG streaming, NEC32 RC config, PID filter callbacks, and LNB voltage control through frontend ops.

Risks: the I2C transfer path uses static `obuf`/`ibuf` and assumes serialization by `d->i2c_mutex`; any future caller bypassing that lock would corrupt transfers. `lme2510_enable_pid()` uses static command buffers and mutates command bytes per PID. Firmware fallback is partly driven by locally present firmware files, so wrong or missing files can change cold-reset behavior. The wrapped stat path suppresses direct frontend reads while streaming, so interrupt loss can produce stale signal/lock state; the RS2000 path only clears lock after a 200 ms interrupt deadline. Several USB commands OR return values and collapse errors to generic device failures.

Test signals: build with `CONFIG_DVB_USB_LME2510`; verify cold firmware request and reconnect for each product ID; warm attach against each frontend/tuner variant; I2C demod/tuner probing with gate values 4/5; LNB 13/18/off voltage commands; PID filter on/off and max 15 feeds; stream start after lock and stream stop path; interrupt URB remote NEC32 events and signal stat updates; disconnect cleanup killing/freeing the interrupt URB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.h

Purpose: private command/data header for the LME2510 DM04/QQBOX driver. It documents vendor command formats for streaming/PID filtering and LNB voltage/power, and provides the STV0288 initialization table used by the SHARP BS2F7HZ7395 frontend path.

Important APIs/types/functions: this file exports macros rather than callable APIs. `LME_ST_ON_W`, `LME_CLEAR_PID`, `LME_ZERO_PID`, and `LME_ALL_PIDS` define byte sequences consumed by `lmedm04.c` stream and PID paths. `LME_VOLTAGE_L`, `LME_VOLTAGE_H`, `LNB_ON`, and `LNB_OFF` define LNB command payloads. `s7395_inittab[]` is a static register/value terminator table wired into `struct stv0288_config lme_config`.

Control flow: `dm04_lme2510_frontend_attach()` selects the STV0288 path for SHARP 7395 hardware and passes `s7395_inittab` to the frontend attach routine. Runtime stream, PID, power, and voltage callbacks instantiate these macros as local command arrays, then send them through `lme2510_usb_talk()`.

State and persistence: no mutable state is held here, although `s7395_inittab` is defined as a non-const static array in the header, so every translation unit including it would get a private writable copy. In practice this header is consumed by the LME driver source.

Dependencies and integration: integrates with `lmedm04.c`, STV0288 frontend configuration, and the LME2510 vendor firmware command ABI. The command comments are part of the local contract for offset and checksum-like command bytes.

Risks: defining `s7395_inittab` in a header as `static u8` rather than `static const` is easy to duplicate accidentally and permits unintended modification. The raw command arrays encode protocol semantics without type checking; any later change to payload length or byte meaning must be synchronized with PID length logic in `lmedm04.c`.

Test signals: compile the LME driver with this header; attach the 7395 frontend and observe STV0288 initialization success; exercise PID filter clear/all/zero commands; confirm LNB high/low/off command effects on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/lmedm04.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.c

Purpose: DVB-T demodulator frontend implementation for the MaxLinear MxL111SF integrated demod. It exposes `dvb_frontend_ops` for tuning, TPS reporting, lock/status, signal strength, BER/SNR stubs, and uncorrected block counts while delegating register access to callbacks supplied by the USB bridge driver.

Important APIs/types/functions: `struct mxl111sf_demod_state` ties `struct dvb_frontend` to the shared `mxl111sf_state` and `mxl111sf_demod_config`. Callback wrappers are `mxl111sf_demod_read_reg()`, `mxl111sf_demod_write_reg()`, and `mxl111sf_demod_program_regs()`. TPS helpers read code rate, modulation, FFT mode, guard interval, and hierarchy from V6 registers. `mxl111sf_demod_set_frontend()` invokes tuner `set_params()`, applies a PHY PLL patch register sequence, and clears IRQ state. `mxl111sf_demod_attach()` allocates the frontend and is exported.

Control flow: the main USB driver calls `mxl111sf_demod_attach()` for DVB-T profiles, then later attaches the MxL111SF tuner. When users tune, DVB core calls `set_frontend()`, which first tunes RF through tuner ops, waits, programs the PLL patch through bridge callbacks, resets IRQ status, and waits again. Status reads sample RS, TPS, sync, and FEC bits and translate them into DVB frontend status flags; `get_frontend()` reads TPS fields and asks tuner ops for current bandwidth/frequency.

State and persistence: state is allocated per frontend and released by `mxl111sf_demod_release()`. The demod driver caches no lock counters other than frontend private state; hardware registers hold tune, TPS, error, SNR, and status values. BER/SNR calculations are disabled by default to avoid floating point in kernel code, so those metrics return zero-derived values.

Dependencies and integration: depends on `mxl111sf.h` for shared state/debug, `mxl111sf-reg.h` for register constants, and DVB frontend APIs. It is a bridge-attached module selected with `CONFIG_DVB_USB_MXL111SF` and relies on the USB driver for register transport and register programming.

Risks: many switch statements do not set defaults for invalid hardware encodings, so output fields may retain caller-provided values when register contents are unexpected. `read_signal_strength()` derives strength from a disabled SNR calculation unless the optional macro is enabled. `get_frontend()` ignores return codes from TPS helper calls. The PLL patch is hard-coded and globally applied for every tune.

Test signals: build/export symbol resolution; DVB-T attach and release; tune to 6/7/8 MHz channels through tuner ops; frontend status transitions for RS/TPS/sync/FEC lock bits; TPS field reads matching known broadcasts; `read_ucblocks()` scale behavior; no floating-point build warnings on all architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.h

Purpose: public attach/config header for the MxL111SF DVB-T demodulator module. It defines the bridge callback contract needed by `mxl111sf-demod.c` and provides a Kconfig-aware attach stub.

Important APIs/types/functions: `struct mxl111sf_demod_config` carries `read_reg`, `write_reg`, and `program_regs` callbacks accepting `struct mxl111sf_state`. `mxl111sf_demod_attach()` returns a configured `struct dvb_frontend *` when `CONFIG_DVB_USB_MXL111SF` is enabled; otherwise the inline stub warns and returns NULL.

Control flow: `mxl111sf.c` builds a static config pointing to its USB register helpers and calls `dvb_attach(mxl111sf_demod_attach, state, &mxl_demod_config)`. The demod module stores the callback table in private state and uses it for all runtime frontend operations.

State and persistence: this header has no runtime state. It defines which external state object owns the register transport (`mxl111sf_state`) and makes demod instances dependent on that object outliving the frontend.

Dependencies and integration: includes DVB frontend definitions and the MxL111SF shared header. Its Kconfig guard ties the demod attach helper to the USB driver symbol, so bridge builds without the symbol receive a visible warning rather than an unresolved function.

Risks: no callback is mandatory at compile time; missing callbacks fail at runtime with `-EINVAL`. The guard key is the bridge config symbol, so reuse outside the MxL111SF USB driver would need matching Kconfig wiring.

Test signals: build with `CONFIG_DVB_USB_MXL111SF=y/m/n`; verify `dvb_attach()` succeeds when enabled and returns NULL from the stub when disabled; probe a DVB-T MxL111SF profile and ensure demod operations call through the USB register callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.c

Purpose: GPIO, port-expander, and pin-mux helper implementation for MxL111SF-based Hauppauge devices. It abstracts internal MxL111SF GPIO registers and optional PCA9534-like I2C expanders, then uses them to switch between DVB-T, ATSC, and mobile-DTV board modes.

Important APIs/types/functions: internal helpers `mxl111sf_set_gpo_state()`, `mxl111sf_get_gpi_state()`, and `mxl111sf_config_gpio_pins()` operate on hardware pins. `mxl111sf_config_pin_mux_modes()` rewrites mux/control registers for TS output, GPIO, serial/parallel TS input, SPI input, and BT656/I2S modes. `mxl111sf_set_gpio()`, `mxl111sf_init_port_expander()`, and `mxl111sf_gpio_mode_switch()` are the exported driver helpers. PCA9534 paths use `i2c_transfer()` on the device adapter.

Control flow: board attach and frontend init call `mxl111sf_init_port_expander()` to detect and initialize external GPIO hardware or fall back to internal GPIO. For ATSC/MH profiles, `mxl111sf_gpio_mode_switch()` powers/reset-lines the LG demodulators in a timed sequence and selects transport mode with GPIO3. Pin mux programming is selected by profile and streaming path, especially SPI versus transport-stream input on v8 silicon.

State and persistence: persistent state lives in `mxl111sf_state`: `gpio_port_expander`, `port_expander_addr`, and current `gpio_mode`. Hardware-visible persistence is in MxL111SF mux/GPO registers and the port-expander output/config registers. There is no cleanup path restoring default GPIO levels beyond mode switches.

Dependencies and integration: depends on MxL111SF register helpers, I2C adapter access, and the main board driver's frontend mode decisions. The helper is tightly integrated with Hauppauge board wiring: GPIO3-7 are interpreted as ATSC/MH reset, enable, and transport selectors.

Risks: `pca9534_set_gpio()` and `pca9534_init_port_expander()` ignore `i2c_transfer()` return values and always report success. `pca9534_set_gpio()` uses fixed `PCA9534_I2C_ADDR`, not `state->port_expander_addr`, despite probing two possible addresses. Large mux updates are written register by register without rollback, so partial failures can leave mixed pin modes. Several helper calls in mode switching ignore errors.

Test signals: attach boards with and without a port expander; verify probe at 0x70/0x40 and hardware GPIO fallback; switch DVB-T, ATSC, and MH modes repeatedly; check GPIO line levels with hardware instrumentation; test SPI/isoc/bulk profiles on v6 and v8 chips; confirm errors propagate from internal GPIO register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.h

Purpose: public GPIO and pin-mux helper header for MxL111SF board support. It gives the main USB driver a compact API for GPIO writes, port-expander initialization, ATSC/MH/DVB-T mode switching, and transport pin mux selection.

Important APIs/types/functions: exported prototypes are `mxl111sf_set_gpio()`, `mxl111sf_init_port_expander()`, `mxl111sf_gpio_mode_switch()`, and `mxl111sf_config_pin_mux_modes()`. Mode constants are `MXL111SF_GPIO_MOD_DVBT`, `MXL111SF_GPIO_MOD_MH`, and `MXL111SF_GPIO_MOD_ATSC`. `enum mxl111sf_mux_config` names pin-mux targets including TS output serial/parallel, GPIO, serial/SPI/parallel input, BT656/I2S, and default mode.

Control flow: `mxl111sf.c` includes this header and calls these helpers during device init, frontend attach/init, and streaming setup depending on product profile, chip revision, endpoint, and `spi`/`isoc` module options.

State and persistence: no direct state is defined here; all operations mutate `struct mxl111sf_state` fields and hardware registers in the implementation. The enum values are persistent ABI within this driver directory because board profiles depend on their names and meanings.

Dependencies and integration: includes `mxl111sf.h`, so it inherits the shared state/debug contract. It bridges board-profile logic with low-level GPIO/pin-mux programming.

Risks: the enum is unscoped C state with a broad default case in implementation; adding values requires updating the large switch in `mxl111sf-gpio.c`. The mode constants are plain integers rather than enum members, so invalid mode values compile and fall into default behavior.

Test signals: compile all MxL111SF profiles; exercise each enum mode from board attach and streaming paths; validate DVB-T, ATSC, and MH mode switching on hardware variants with internal and external GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.c

Purpose: I2C adapter implementation for MxL111SF devices. It supports a software bit-banged bus for v6 silicon and a USB-command-driven hardware I2C engine for newer revisions, exposing a single `master_xfer` used by demods, tuners, EEPROM, and GPIO expanders.

Important APIs/types/functions: `mxl111sf_i2c_xfer()` is the exported adapter entry point. Software helpers implement start/stop, ACK/NACK, byte send/receive, and `mxl111sf_i2c_sw_xfer_msg()`. Hardware helpers build 26-byte USB I2C command buffers using `USB_WRITE_I2C_CMD`, `USB_READ_I2C_CMD`, `I2C_*` register constants, `mxl111sf_i2c_send_data()`, `mxl111sf_i2c_get_data()`, status/fifo polling, and `mxl111sf_i2c_hw_xfer_msg()`.

Control flow: the main driver's I2C algorithm calls `mxl111sf_i2c_xfer()`, which locks `d->i2c_mutex`, chooses hardware I2C when `state->chip_rev > MXL111SF_V6`, loops each `i2c_msg`, and returns `num` or `-EREMOTEIO`. Software mode emits start, address byte, payload bytes or reads, ACKs all but the last byte, NACKs at the end, and stops. Hardware mode enables the I2C mux, writes control/slave/address/timeout commands, transfers data in 8-byte blocks plus leftover bytes, retries FIFO-empty read tails through `mxl111sf_i2c_readagain()`, then disables the mux and stops.

State and persistence: no private allocation exists here; it uses `mxl111sf_state`, the bridge USB control buffers, chip revision, and the shared I2C mutex. Hardware engine configuration is transient per message, but the function attempts to deinitialize the mux at exit.

Dependencies and integration: depends on the shared MxL111SF register/control message APIs in `mxl111sf.c`, Linux I2C core, and chip revision discovery. All board EEPROM reads, tuner/demod register access, and PCA9534 GPIO operations pass through this adapter.

Risks: hardware mode is complex and frequently ignores return values from cleanup/status helper calls, so a failed STOP/deinit can be hidden. `mxl111sf_i2c_check_status()` and FIFO polling return only a boolean and do not propagate USB errors. Software mode has a FIXME that it stops after every write transaction, which can break combined transactions that require repeated-start semantics. Hardware write lengths are not explicitly capped against the 8-byte block protocol beyond the 26-byte command buffer shape.

Test signals: v6 bitbang transfers for EEPROM, tuner, and demod; v8 hardware transfers for simple reads/writes and combined write-read register reads; NACK behavior against absent I2C addresses; long transfer block and leftover paths; FIFO-empty readagain path; no deadlocks under concurrent frontend/tuner access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.h

Purpose: minimal public header for the MxL111SF I2C adapter implementation.

Important APIs/types/functions: it declares `mxl111sf_i2c_xfer(struct i2c_adapter *adap, struct i2c_msg msg[], int num)`, the only function consumed by the main driver's `struct i2c_algorithm`.

Control flow: `mxl111sf.c` assigns this function to `.master_xfer`; Linux I2C core calls it for all child device transactions after dvb-usbv2 registers the adapter.

State and persistence: no state is defined here. The function contract implies that caller-provided adapter data resolves to a `dvb_usb_device` whose private data is `struct mxl111sf_state`.

Dependencies and integration: includes `mxl111sf.h`, and through it the dvb-usbv2 and shared state definitions. It links `mxl111sf-i2c.c` to the main bridge file without exposing the many software/hardware helper internals.

Risks: the header does not declare functionality flags or helper types; maintainers must keep the `.functionality` implementation in `mxl111sf.c` synchronized manually. The broad include of `mxl111sf.h` may pull more dependencies than the one prototype needs.

Test signals: compile the MxL111SF driver; verify `mxl111sf_i2c_algo.master_xfer` resolves; run I2C attach/probe paths for EEPROM, demods, tuners, and GPIO expander.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.c

Purpose: physical-layer and port-configuration helpers for MxL111SF chips. It programs reset, device mode, tuner/demod default patches, USB output, MPEG TS input, I2S input, SPI mode, and IDAC antenna switching current settings.

Important APIs/types/functions: exported helpers include `mxl111sf_init_tuner_demod()`, `mxl1x1sf_soft_reset()`, `mxl1x1sf_set_device_mode()`, `mxl1x1sf_top_master_ctrl()`, `mxl111sf_disable_656_port()`, `mxl111sf_enable_usb_output()`, `mxl111sf_config_mpeg_in()`, `mxl111sf_init_i2s_port()`, `mxl111sf_disable_i2s_port()`, `mxl111sf_config_i2s()`, `mxl111sf_config_spi()`, and `mxl111sf_idac_config()`.

Control flow: frontend attach and per-frontend init in `mxl111sf.c` use this file to reset the chip, apply initialization register sequences, choose tuner versus SoC mode, power the top master, enable USB output, and configure endpoint-specific data paths. EP6 ATSC paths configure MPEG input, EP5 mobile paths configure I2S and optional SPI, and antenna hunting calls IDAC configuration to switch internal/external RF paths.

State and persistence: the helper mutates `state->device_mode` after a successful mode write. All other persistence is in chip registers, including page register 0x00, reset, top master, MPEG/I2S/SPI port state, and IDAC values. Some routines temporarily switch register pages and must return to page 0.

Dependencies and integration: depends on shared MxL111SF register helpers and the register constants in `mxl111sf-reg.h`. It is not an independent subsystem; it is a hardware-programming layer for the main bridge and tuner modules.

Risks: many routines call `mxl_fail(ret)` but continue after intermediate failures, which can cause later writes to run against partially configured hardware. `mxl111sf_config_mpeg_in()` does not stop after the first pin-mux write failure. `mxl111sf_config_spi()` must restore page 0; a failure before the final page write can strand subsequent accesses on page 2. Magic register sequences depend on silicon revisions and board wiring.

Test signals: reset and chip-info probe after attach; DVB-T, ATSC, and MH frontend init sequencing; EP4/EP5/EP6 stream start/stop; SPI toggle on v8 Mercury paths; antenna path switching through IDAC; register trace confirming page returns to 0 after SPI and init patch programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.h

Purpose: public prototype header for MxL111SF physical-layer and transport-port helpers.

Important APIs/types/functions: it declares reset, device-mode, top-master, USB output, 656 disable, tuner/demod init, MPEG input configuration, I2S init/config/disable, SPI mode, and IDAC configuration helpers. The prototypes expose transport parameters such as serial/parallel TS, bit order, clock phase, MPEG valid/sync polarity, I2S bit positions, and IDAC control/current/hysteresis fields.

Control flow: `mxl111sf.c` and `mxl111sf-tuner.c` call these helpers during frontend attach/init, stream control, tuner IF setup, antenna hunting, and product profile setup. The header is the compile-time contract between the board driver and lower-level register programming.

State and persistence: no state is defined here; all helpers accept `struct mxl111sf_state *` and modify its `device_mode` or chip registers. Parameter choices persist until reset or later reconfiguration.

Dependencies and integration: includes `mxl111sf.h` for shared state and debug conventions. It is paired with `mxl111sf-reg.h` constants in the implementation.

Risks: parameters are plain integers rather than enums, so invalid serial/parallel, clock phase, and polarity values compile and may produce unintended register values. Adding new transport modes requires changes in both the board driver and implementation.

Test signals: compile all MxL111SF users; exercise frontend init and stream control for EP4/EP5/EP6; verify IDAC antenna switching and SPI mode changes on v8 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-reg.h

Purpose: register constant map for the MxL111SF USB bridge/tuner/demod helper stack. It names chip ID/revision registers, DVB-T demod status/TPS/error/SNR registers, MPEG/I2S/SPI transport controls, tuner IF/RF tuning registers, GPIO/GPO bits, ATSC config, mode/start-tune registers, IDAC registers, and digital RF power registers.

Important APIs/types/functions: this header exports macros only. Important groups include `CHIP_ID_REG`, `TOP_CHIP_REV_ID_REG`, `V6_*` demod/TPS/status fields, `TSIF_INPUT_*`, `V6_MPEG_*`, `V6_I2S_*`, `TUNER_*`, `V6_TUNER_*`, `V6_GPO_*`, `MXL_111SF_GPO_*`, `MXL_MODE_REG`, `START_TUNE_REG`, and IDAC bit masks.

Control flow: all MxL111SF modules include these constants to interpret register reads and compose masked writes. Demod status/TPS reads, tuner tune calculations, PHY transport setup, GPIO helpers, chip-info detection, and antenna RF strength all depend on these names.

State and persistence: no software state exists here. The file documents persistent on-chip register state that survives until reset, page change, or explicit overwrite by the driver.

Dependencies and integration: used by `mxl111sf.c`, `mxl111sf-demod.c`, `mxl111sf-tuner.c`, `mxl111sf-phy.c`, and `mxl111sf-gpio.c`. It is the shared ABI between high-level DVB operations and chip register programming.

Risks: register constants are not type checked, and several names encode revision-specific assumptions (`V6_*`) while being used by v8 paths too. Typo-like names such as `V6_TPS_HIERACHY_REG` can propagate into callers. Any mismatch with the vendor register map can cause silent tuning, GPIO, or transport failures.

Test signals: build all MxL111SF modules; chip ID/revision reads match expected values; frontend status/TPS reporting maps correctly; transport pin and SPI/I2S setup registers match hardware traces; RF strength and antenna switching work after page changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.c

Purpose: DVB tuner implementation for the MxL111SF CMOS tuner block. It provides tuner ops for RF tuning across DVB-T, ATSC, ATSC-MH, and US cable modes, tracks tuned frequency/bandwidth, reports lock/RF power, and exposes IF frequency selection.

Important APIs/types/functions: `struct mxl111sf_tuner_state` stores shared chip state, config callbacks, IF enum, cached frequency, and bandwidth. `mxl111sf_calc_phy_tune_regs()` computes bandwidth and RF channel register values. `mxl1x1sf_tune_rf()` stops tuning, checks device mode, programs RF registers, optionally toggles top master and IF output, starts tuning, and runs `ant_hunt`. `mxl111sf_tuner_set_params()`, `mxl111sf_tuner_get_status()`, `mxl111sf_get_rf_strength()`, and getter/release functions populate `dvb_tuner_ops`. `mxl111sf_tuner_attach()` is exported.

Control flow: the main bridge attaches this tuner to each created frontend after demod attachment. Tune requests select a bandwidth code by delivery system, call RF tune, and cache the selected frequency/bandwidth. In tuner mode, IF output frequency is configured before `START_TUNE_REG` is asserted. RF strength temporarily switches to register page 2, reads digital RF power LSB/MSB, and restores page 0.

State and persistence: per-frontend tuner state is allocated and freed by tuner ops release. Hardware tune state persists in RF tune registers, IF selection/bypass registers, start-tune bit, page register, and top-master state. Cached frequency/bandwidth are software-only and are returned by getter ops.

Dependencies and integration: depends on shared MxL111SF register callbacks, PHY `top_master_ctrl`, and optional antenna hunt callback supplied by `mxl111sf.c`. It integrates with DVB frontend tuning via `fe->ops.tuner_ops`.

Risks: `mxl_phy_tune_rf` is a static mutable register array shared across all tuner instances, so concurrent tunes could race if multiple frontends tune simultaneously. Unsupported bandwidth or delivery system returns `-EINVAL`. RF strength page restoration happens even after errors, but the final restore result overwrites the earlier error. IF frequency calculations are mostly disabled and use hard-coded bypass values.

Test signals: attach tuner to all frontends; tune ATSC, ATSC-MH, DVB-C Annex B, and DVB-T 6/7/8 MHz paths; validate RF lock bits; confirm RF strength reads restore page 0; exercise antenna hunting; concurrent multi-frontend tune testing on multi-profile devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.h

Purpose: public attach/config header for the MxL111SF tuner module. It defines IF selection values, bridge callback requirements, optional antenna hunting hook, and a Kconfig-aware attach API.

Important APIs/types/functions: `enum mxl_if_freq` names supported IF outputs from 4.0 MHz through 44 MHz. `struct mxl111sf_tuner_config` carries IF frequency, invert-spectrum bit, register read/write/program callbacks, top-master callback, and `ant_hunt` callback. `mxl111sf_tuner_attach()` installs tuner ops into an existing DVB frontend when enabled; otherwise an inline stub warns and returns NULL.

Control flow: `mxl111sf.c` supplies a static config using IF 6 MHz and bridge register helpers, then calls `dvb_attach(mxl111sf_tuner_attach, fe, state, &mxl_tuner_config)` for each frontend. Runtime tuner ops call back into the bridge for register access and antenna path control.

State and persistence: no mutable state is stored in the header. The IF enum and config fields define how the tuner instance will persist its IF selection in runtime private state and chip registers.

Dependencies and integration: includes DVB frontend APIs and `mxl111sf.h`. The Kconfig guard matches the MxL111SF USB symbol and prevents unresolved symbols when the tuner module is unavailable.

Risks: config callbacks are optional only at runtime; missing callbacks cause `-EINVAL`. IF enum values are raw register encodings, so changing them would alter hardware programming. The attach stub warns but can still permit higher-level attach code to fail later if not checked.

Test signals: build enabled/disabled configs; attach tuner after demod for all product profiles; verify IF frequency getter values for each enum; exercise antenna hunt callback presence and absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.c

Purpose: top-level dvb-usbv2 bridge driver for MaxLinear MxL111SF Hauppauge USB devices. It owns USB control message transport, register helpers, I2C algorithm, chip/revision detection, EEPROM parsing, frontend/tuner attach matrices for DVB-T/ATSC/MH/Mercury profiles, stream endpoint selection, GPIO/PHY setup, media tuner entity registration, and USB device ID binding.

Important APIs/types/functions: `mxl111sf_ctrl_msg()`, `mxl111sf_read_reg()`, `mxl111sf_write_reg()`, `mxl111sf_write_reg_mask()`, and `mxl111sf_ctrl_program_regs()` form the shared register transport used by all MxL111SF modules. `mxl1x1sf_get_chip_info()` caches chip ID/revision. `mxl111sf_adap_fe_init()`/`sleep()` wrap frontend init/sleep with shared hardware setup and `fe_lock`. Attach functions select LGDT3305, LG2160/LG2161, and integrated MxL demod frontends. Stream config/ctrl functions map frontend IDs to EP4/EP5/EP6 bulk or isoc paths.

Control flow: `dvb_usbv2_probe()` selects a `dvb_usb_device_properties` profile from the USB ID table. `mxl111sf_probe()` initializes message locking; `mxl111sf_init()` reads chip info, configures v8 pin mux, and parses Hauppauge EEPROM. Frontend attach functions set alt mode, reset/program the chip, choose tuner or SoC mode, initialize GPIO/port expander, power the relevant demod, and wrap frontend init/sleep. Tuner attach loops over `state->num_frontends` and installs the integrated tuner. Streaming config uses `isoc` and `spi` module options plus frontend ID to choose endpoint, TS type, frame count/size, and streaming control function.

State and persistence: `struct mxl111sf_state` persists USB device pointer, chip identity, GPIO/port expander state, alt/gpio/device modes, frontend lock, per-frontend adapter state, shared message buffers, EEPROM data, and optional media-controller tuner entity. Per-frontend `mxl111sf_adap_state` persists alt mode, GPIO mode, device mode, EP6 clock phase, and saved frontend callbacks. Hardware registers persist reset/mode/pin/GPIO/transport/tune state until reinitialized.

Dependencies and integration: depends on dvb-usbv2, Linux USB/I2C, Hauppauge TV EEPROM parsing, media-controller optional support, MxL111SF helper modules, LGDT3305/LG2160 demods, and the integrated tuner/demod modules. It registers many Hauppauge USB IDs and supports suspend/resume/reset-resume through dvb-usbv2.

Risks: `fe_lock` is locked in frontend init and unlocked in sleep, which relies on strictly paired frontend lifecycle calls; failure after locking in init can leave it locked. Static command buffers in helpers are protected by `msg_lock`, but higher-level mutable state is shared across frontends. Several attach paths duplicate long initialization sequences and may diverge. Some errors are logged with `mxl_fail()` but not immediately returned. Module options materially change endpoint and GPIO/SPI behavior and need coverage across product variants.

Test signals: build with all dependent demod/tuner modules; probe every USB ID profile; EEPROM parsing for 117xxx/126xxx/138xxx; chip revision v6/v8 paths; DVB-T, ATSC, MH, ATSC+MH, Mercury, Mercury-MH attach; bulk/isoc and SPI/TP stream paths; FE init/sleep lock pairing; media-controller tuner entity registration; suspend/resume and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.h

Purpose: shared private header for the MxL111SF bridge, helper, tuner, and demod files. It centralizes endpoint constants, chip/mode enums, private state layout, register control structures, exported bridge register APIs, and debug macros.

Important APIs/types/functions: `struct mxl111sf_state` is the device-wide state carrier. `struct mxl111sf_adap_state` stores per-frontend alt mode, GPIO mode, device mode, EP6 clock phase, and saved frontend callbacks. `enum mxl111sf_gpio_port_expander`, `enum mxl111sf_pads`, chip revision constants, device mode constants, endpoint constants, `MXL_MAX_XFER_SIZE`, and `struct mxl111sf_reg_ctrl_info` define the local ABI. Prototypes expose `mxl111sf_read_reg()`, `mxl111sf_write_reg()`, `mxl111sf_write_reg_mask()`, `mxl111sf_ctrl_program_regs()`, and `mxl111sf_ctrl_msg()`.

Control flow: all MxL111SF sources include this header. The main driver fills and owns `mxl111sf_state`; helper modules receive it through config callbacks or direct calls and operate on shared USB buffers, chip revision, GPIO state, and debug flags.

State and persistence: the header describes all long-lived bridge state: USB pointer, GPIO expander type/address, chip ID/version/revision, current modes, EEPROM info, frontend lock, per-frontend state array, control message buffers, message mutex, and optional media-controller tuner entity/pads. No on-disk persistence exists.

Dependencies and integration: includes dvb-usbv2, TV EEPROM, and media entity definitions. Debug macros are shared across in-tree and separately built tuner/demod modules, with `mxl_fail()` conditionally using the external debug variable.

Risks: this header exposes internals broadly and couples helper modules tightly to the bridge state layout. `adap_state[3]` assumes at most three frontends. Debug macros are statement-like and not wrapped in `do { } while (0)`, which can be awkward in conditionals. Some historic conditional enum code is disabled, leaving parallel integer mode fields.

Test signals: compile all MxL111SF objects under module and built-in configs; check `MXL_MAX_XFER_SIZE` against all USB command callers; exercise three-frontend profiles; media-controller builds with tuner pads; debug flag paths in external tuner/demod modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.c

Purpose: dvb-usbv2 bridge driver for Realtek RTL2831U/RTL2832U/RTL2832P USB receivers. It implements vendor control transfers, a multi-method I2C adapter, chip/tuner/slave-demod detection, dynamic I2C/platform child device attachment, tuner attachment, SDR side-device registration, power/endpoint control, frontend control, PID filter delegation, RC handling, and a large USB ID table.

Important APIs/types/functions: `rtl28xxu_ctrl_msg()` is the locked USB control transport. Register helpers choose USB/SYS/IR command spaces. `rtl28xxu_i2c_xfer()` supports integrated demod page access, old I2C access, and newer direct-address access. `rtl2831u_read_config()` and `rtl2832u_read_config()` probe tuner/slave-demod hardware. Attach/detach functions create `rtl2830`/`rtl2832`, slave demod, tuner, and SDR child devices. Power and RC paths are split by chip generation.

Control flow: `identify_state()` distinguishes RTL2831U from RTL2832U using a zero-length direct-address I2C read, marks the device warm, and tunes adapter retries/timeouts. `read_config()` configures GPIOs and probes tuner IDs, with RTL2832U also resetting/probing slave demods for R828D/Si2157 designs. Frontend attach creates the demod I2C client and receives a DVB frontend and demod I2C adapter; optional slave demods populate `adap->fe[1]`. Tuner attach binds legacy `dvb_attach()` tuners or I2C-client tuners and may register `rtl2832_sdr`. Stream data comes through bulk endpoint 0x81.

State and persistence: `struct rtl28xxu_dev` persists the USB control buffer, chip ID, tuner ID/name, cached demod register page, demod I2C adapter, RC active flag, direct-I2C-write preference, child I2C clients, SDR platform device, slave-demod enum, and demod platform data. Hardware state includes GPIO power/reset, demod/tuner I2C gates, USB endpoint DMA/FIFO, RC registers, and PID filters delegated to demod platform data.

Dependencies and integration: depends on dvb-usbv2, USB control APIs, I2C core, RC core when enabled, RTL2830/RTL2832 demod drivers, many tuner drivers, optional slave demods, and `rtl2832_sdr`. It integrates V4L2 subdev pointers for some tuners and platform-device SDR registration.

Risks: tuner detection is heuristic and order-dependent; identical ID values such as R820T/R828D are disambiguated only by probe request/address ordering. Some `i2c_new_client_device()` failure paths call `i2c_client_has_driver(client)` without an explicit `IS_ERR_OR_NULL()` check. Reduced-mode fallback hides slave-demod attach failures. RC raw decoding can consume USB bandwidth; `disable_rc` exists partly to avoid SDR sample loss. The I2C adapter has strict message shape/length limits and maps `-EPIPE` to retry.

Test signals: probe RTL2831U, RTL2832U, and RTL2832P devices; exercise each tuner path and slave-demod fallback; stream DVB-T and DVB-T2/C when slave demod exists; attach/detach child I2C clients and SDR platform device; PID filter delegation; power off/on and endpoint halt clearing; RC NEC/raw events with and without `disable_rc`; suspend/resume/reset-resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.h

Purpose: private header for the Realtek RTL28xxU DVB USB bridge driver. It declares the private device state, chip/tuner/slave-demod identifiers, USB command encodings, request/register helper structs, and register maps for USB, SYS/GPIO/I2C, and IR blocks.

Important APIs/types/functions: `struct rtl28xxu_dev` stores control buffer, chip/tuner state, cached demod page, demod adapter, RC flag, child devices, SDR platform device, slave-demod enum, and a union of RTL2830/RTL2832 platform data. `enum rtl28xxu_chip_id`, `enum rtl28xxu_tuner`, `struct rtl28xxu_req`, `struct rtl28xxu_reg_val`, and `struct rtl28xxu_reg_val_mask` define driver-local contracts. Command macros encode vendor-control `index` values.

Control flow: `rtl28xxu.c` uses these definitions for every USB request, register read/write, tuner switch, frontend/platform data setup, and RC register program sequence. Child demod/tuner headers included here provide platform data and attach types used by the implementation.

State and persistence: the header captures all runtime bridge state but allocates none by itself. Register macros describe hardware state that persists until reset or explicit writes: endpoint setup, USB DMA/FIFO, GPIO, demod control, system I2C master, and IR receive buffers.

Dependencies and integration: includes dvb-usbv2, platform device support, RTL demod headers, slave demod headers, and tuner headers. The `enum rtl28xxu_tuner` explicitly says it must stay synchronized with the RTL2832 demod driver.

Risks: coupling this header to many frontend/tuner headers increases rebuild and config fragility. The tuner enum synchronization comment is a real maintenance hazard: mismatched values could program wrong demod/tuner settings. Register-space command routing is encoded by numeric ranges in implementation and must stay aligned with this map.

Test signals: compile with all supported tuner/demod configs; verify enum values against RTL2832 demod expectations; run register read/write paths across USB, SYS, and IR spaces; validate child-device lifecycle fields are initialized and cleaned on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/usb_urb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/usb_urb.c

Purpose: generic dvb-usbv2 streaming URB helper for bulk and isochronous USB data paths. It allocates stream buffers, allocates/fills URBs, submits/kills/reconfigures them, dispatches completed payloads to the stream callback, and frees resources.

Important APIs/types/functions: public functions are `usb_urb_initv2()`, `usb_urb_submitv2()`, `usb_urb_killv2()`, `usb_urb_reconfig()`, and `usb_urb_exitv2()`. Internal helpers allocate/free URBs and buffers for bulk/isoc configurations. `usb_urb_complete()` is the shared completion handler that handles status codes, iterates isoc frame descriptors, invokes `stream->complete()`, clears isoc frame metadata, and resubmits the URB.

Control flow: dvb-usbv2 stream setup calls `usb_urb_initv2()` with static or runtime stream properties. Starting a stream calls submit, optionally reconfiguring the URBs if a frontend-specific stream config is provided. Completion callbacks pass valid data chunks upstream and immediately resubmit unless the URB was killed or shut down. Stop kills all submitted URBs, and exit frees URBs and buffers.

State and persistence: mutable state lives in `struct usb_data_stream`: copied `props`, `urb_list`, `buf_list`, `buf_num`, `buf_size`, `urbs_initialized`, `urbs_submitted`, state flags, device pointer, and completion callback. Buffers persist for the life of the stream and can be reused by reconfigured URBs when large enough.

Dependencies and integration: depends on Linux USB URB APIs and `dvb_usb_common.h` stream structures. It is shared by dvb-usbv2 bridge drivers that request bulk or isoc streams and by runtime stream configuration hooks such as MxL111SF and LME2510.

Risks: allocation uses `GFP_ATOMIC` in initialization paths where sleeping allocation might be more resilient. `usb_urb_reconfig()` checks bulk buffer size using `stream->props.u.bulk.buffersize` rather than the new `props->u.bulk.buffersize`, so growing a bulk buffer request can be incorrectly accepted if old props are smaller or stale. Completion always resubmits and ignores submit errors. Isoc frame errors are logged but do not affect stream health. No DMA mapping is used despite debug printing `dma_addr`.

Test signals: bulk and isoc stream init/submit/kill/exit under dvb-usbv2; runtime reconfiguration between endpoints/frame sizes; forced URB error statuses; disconnect while URBs are active; kmemleak/resource checks for buffers and URBs; data callback count and byte accounting for bulk and isoc frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/usb_urb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/zd1301.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/zd1301.c

Purpose: dvb-usbv2 USB bridge driver for the ZyDAS ZD1301 reference design. It transports demod register reads/writes over vendor bulk messages, registers a platform demod device, attaches an MT2060 tuner over the demod-provided I2C adapter, controls streaming, and binds the USB ID.

Important APIs/types/functions: `struct zd1301_dev` stores an 8-byte control buffer, demod platform data, MT2060 platform data, platform demod device, and tuner I2C client. `zd1301_ctrl_msg()` performs locked bulk OUT to endpoint 0x04 and optional bulk IN from endpoint 0x83, including a repeat-read quirk when reply length is short. `zd1301_demod_wreg()`/`rreg()` implement demod register callbacks. `zd1301_frontend_attach()` and `zd1301_frontend_detach()` manage child devices. `zd1301_streaming_ctrl()` sends start/stop commands.

Control flow: dvb-usbv2 probe allocates private state and later calls frontend attach. Attach registers `zd1301_demod` as a platform device with register callbacks, takes a module reference, retrieves the demod I2C adapter/frontend, then creates an MT2060 I2C client using platform data pointing at that frontend. On success it stores child handles and assigns `adap->fe[0]`. Streaming sends command `{0x03, 0x00, 0x07}` for on and `{0x03, 0x00, 0x08}` for off.

State and persistence: software state persists in `zd1301_dev` until detach/disconnect. Hardware state includes demod registers, tuner state behind the demod I2C adapter, and bridge stream enable. There is no firmware handling or persistent storage.

Dependencies and integration: depends on dvb-usbv2, USB bulk messaging, `zd1301_demod` platform driver, MT2060 tuner driver, and I2C core. It exposes one bulk stream on endpoint 0x81 with 6 buffers sized to 21 TS packets.

Risks: `zd1301_ctrl_msg()` copies `wlen` bytes into an 8-byte buffer without an explicit length check; current callers use 3 or 7 bytes, but future callers could overflow. `memcpy(&dev->buf, ...)` relies on array address equivalence. Attach paths must handle platform/I2C child device failures carefully to avoid module reference leaks; current labels mostly unwind but depend on handles being valid. Short reply retry still copies `rlen` bytes even if the second actual length is short.

Test signals: probe USB VID/PID 0x0ace/0x13a1; demod platform device creation and module refcounting; MT2060 I2C client attach; demod register read/write callbacks; stream start/stop commands and bulk endpoint data; detach/unplug after partial attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/zd1301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Kconfig

Purpose: Kconfig menu for the legacy `dvb-usb` framework and its USB DVB bridge drivers. It defines the common `DVB_USB` module, global debug option, and per-device options such as A800, AF9005, CXUSB, DiBcom variants, DW2102, Technisat, and others.

Important APIs/types/functions: Kconfig symbols include `DVB_USB`, `DVB_USB_DEBUG`, `DVB_USB_A800`, `DVB_USB_DIB3000MC`, `DVB_USB_CXUSB`, `DVB_USB_CXUSB_ANALOG`, and many device-specific tristates. Dependencies require DVB core, USB, I2C, and RC core for the base framework. `select` clauses pull in Cypress firmware support, demodulators, tuners, videobuf2, and analog helper drivers where automatic subdevice selection is enabled.

Control flow: enabling `DVB_USB` makes the legacy framework object available and reveals the `if DVB_USB` device submenu. Selecting a device driver causes the Makefile to build its composite object and, when `MEDIA_SUBDRV_AUTOSELECT` is enabled, selects likely frontend/tuner dependencies.

State and persistence: no runtime state; this file controls build-time availability, module composition, and dependency closure.

Dependencies and integration: integrated with the sibling Makefile and the wider media Kconfig hierarchy. It bridges user configuration with demod/tuner modules and optional analog/RC support.

Risks: `select` can force dependencies in ways that may surprise minimal configs. Some help text references external wiki information and old device names, so hardware support claims may drift. Built-in/module combinations are constrained in places such as analog support and DIB3000MC helper behavior.

Test signals: `oldconfig`, `allmodconfig`, and `randconfig` builds; each device symbol producing the expected module object; configs with and without `MEDIA_SUBDRV_AUTOSELECT`; base `DVB_USB_DEBUG`; analog CXUSB dependency combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Makefile

Purpose: Kbuild object composition for the legacy `dvb-usb` framework and its device-specific modules. It links the common framework pieces and maps Kconfig symbols to composite driver objects.

Important APIs/types/functions: `dvb-usb-objs` aggregates common framework files including firmware, init, URB, I2C, DVB, remote, and generic `usb-urb.o`. `obj-$(CONFIG_DVB_USB)` emits `dvb-usb.o`. Per-driver composite variables such as `dvb-usb-a800-objs`, `dvb-usb-cxusb-objs`, `dvb-usb-dib0700-objs`, and others map source files to modules. `ccflags-y` adds include paths for DVB frontends, tuners, and media common code.

Control flow: after Kconfig selects a symbol, Kbuild includes the corresponding `obj-*` line. Composite object lists fold one or more C files into each resulting module. CXUSB conditionally adds analog support when `CONFIG_DVB_USB_CXUSB_ANALOG=y`.

State and persistence: no runtime state; it defines build artifacts and include path visibility.

Dependencies and integration: pairs with `Kconfig` and legacy source files in this directory. Include flags allow direct inclusion of frontend/tuner/common headers used by the many bridge drivers.

Risks: missing an object from a composite list causes unresolved symbols or missing functionality. Common `ccflags-y` expose broad include paths to every object, which can mask dependency boundaries. Object naming differs from source names in some cases, so Kconfig/module naming must remain synchronized.

Test signals: `make M=drivers/media/usb/dvb-usb` under each selected symbol; module names match expected `dvb-usb-*`; CXUSB analog object inclusion when enabled; link success with frontend/tuner configs as modules and built-ins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/a800.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/a800.c

Purpose: legacy dvb-usb driver for the AVerMedia AverTV DVB-T USB 2.0 A800 receiver. It wraps the DiBcom USB helper stack with A800-specific firmware, cold/warm detection, remote-control polling, USB IDs, and device properties.

Important APIs/types/functions: `a800_power_ctrl()` is a no-op power hook. `a800_identify_state()` treats devices with `iManufacturer != 1` as cold. `a800_rc_query()` polls a vendor control message for 5 bytes and reports NEC keydown/repeat events. `a800_probe()` calls `dvb_usb_device_init()`. `a800_properties` defines Cypress FX2 control, firmware name, one adapter/frontend, PID filtering, DIB3000MC frontend/tuner attach callbacks, bulk stream endpoint 0x06, RC core settings, DiBUSB I2C algorithm, and device descriptors.

Control flow: USB probe initializes the legacy dvb-usb device using `a800_properties`. Cold devices load `dvb-usb-avertv-a800-02.fw` through the Cypress FX2 framework and reconnect as warm. Frontend/tuner attachment and streaming are delegated to DiBcom helper functions. RC polling sends vendor request 0x04 and maps response type 1 to NEC scancode and type 2 to repeat.

State and persistence: per-adapter private state is `struct dibusb_state` owned by the shared DiBUSB helpers. This file has only module parameters and transient remote-query buffers. Firmware and hardware PID filters persist in device state after initialization.

Dependencies and integration: depends on the legacy `dvb-usb` framework, Cypress firmware loader, DiBUSB helpers, DIB3000MC frontend, tuner helpers selected by Kconfig, USB core, and RC core. It registers cold/warm AVerMedia USB IDs through `DVB_USB_DEV`.

Risks: `a800_rc_query()` allocates on every poll and blocks up to 2 seconds on the control message; repeated allocation/failure can affect responsiveness. It deliberately drops NEC extended/NEC32 information and reports only NEC with selected bytes. Cold detection relies on `iManufacturer` value rather than an explicit firmware status command. Power control is a no-op, so suspend/power behavior is left to shared helpers/hardware.

Test signals: cold firmware load and warm reconnect; DIB3000MC frontend/tuner attach; bulk stream on endpoint 0x06 with seven 4096-byte buffers; PID filter enable/disable and 32 PID slots; RC keydown/repeat events using `RC_MAP_AVERMEDIA_M135A`; disconnect through `dvb_usb_device_exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/a800.c -->
