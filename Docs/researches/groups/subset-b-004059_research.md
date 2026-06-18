# subset-b-004059 research

This grouped report covers DiBcom and Micronas/Trident DVB frontend sources under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib8000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib8000.h

## Purpose
`dib8000.h` is the public attachment and board-configuration contract for the DiBcom DiB8000 demodulator driver. It does not implement hardware behavior itself; instead it defines the configuration data, optional operations table, and Kconfig-gated attach stub used by USB/PCI bridge drivers and board files.

## Important APIs, Types, and Functions
`struct dib8000_config` carries MPEG output format, hostbus diversity, tuner baseband mode, AGC/PLL tables, GPIO defaults, PWM divider, output drive settings, diversity delay, output mode, reference clock selection, and optional board callbacks such as `update_lna()` and `agc_control()`. `struct dib8000_ops` is a function table filled by `dib8000_attach()` and exposes demod services including PLL updates, GPIO, tuner sleep, ADC/DC power reads, TIMF control, tune-state accessors, slave frontend management, I2C enumeration, I2C master access, PID filtering, and frontend initialization. `DEFAULT_DIB8000_I2C_ADDRESS` is 18.

## Control Flow
Callers allocate/fill `struct dib8000_config`, call `dib8000_attach(struct dib8000_ops *ops)`, then use the returned ops table to initialize and drive one or more frontends. When `CONFIG_DVB_DIB8000` is not reachable, the inline `dib8000_attach()` warns and returns `NULL`, which preserves linkability for optional users.

## State and Persistence
The header describes runtime hardware state only indirectly through GPIO, PWM, PLL, AGC, output, and diversity fields. Persistent storage is absent. Lifetime ownership of tables and callbacks is external to the header and must match the demod driver's expectations.

## Dependencies and Integration Points
The file depends on `dibx000_common.h`, DVB frontend types, Linux I2C adapters, and the common `frontend_tune_state`/DiB output constants. It integrates board-specific drivers with the DiB8000 implementation and tuner subdrivers through callback hooks.

## Risks and Edge Cases
The config contains raw pointers to AGC/PLL tables and callbacks; invalid lifetime or mismatched table counts can fail at runtime. GPIO defaults are broad bitmasks, so board-specific polarity mistakes can hold external components in reset or power them incorrectly. The disabled-driver stub returns `NULL`, so callers must handle optional support.

## Test Signals
Useful signals are successful `dib8000_attach()` discovery, expected GPIO defaults on hardware reset, correct MPEG or diversity output mode, PLL/AGC table selection per band, PID filter behavior, slave frontend enumeration, and clean fallback when `CONFIG_DVB_DIB8000` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib8000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib9000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib9000.c

## Purpose
`dib9000.c` implements the Linux DVB frontend driver for DiBcom DiB9000 COFDM demodulators. The device is firmware driven: the host performs I2C register access for reset and bootstrap, downloads RISC microcode, then controls tuning, component access, monitoring, GPIO, PID filtering, and diversity through firmware mailboxes and shared memory windows.

## Important APIs, Types, and Functions
`struct dib9000_state` is the main runtime object. It owns the physical I2C device, common DiB I2C master, firmware tuner and component-bus adapters, revision/offset data, tune state, channel status, GPIO state, mailbox and memory locks, firmware memory map, slave frontend list, component bus speed, transfer buffers, demod lock, and postponed PID commands. Public exports are `dib9000_attach()`, `dib9000_i2c_enumeration()`, `dib9000_get_tuner_interface()`, `dib9000_get_component_bus_interface()`, `dib9000_get_i2c_master()`, `dib9000_set_i2c_adapter()`, `dib9000_set_gpio()`, `dib9000_fw_pid_filter_ctrl()`, `dib9000_fw_pid_filter()`, `dib9000_firmware_post_pll_init()`, `dib9000_set_slave_frontend()`, `dib9000_get_slave_frontend()`, and `dib9000_fw_set_component_bus_speed()`.

Low-level access is handled by `dib9000_read16_attr()`, `dib9000_write16_attr()`, and word helpers. Once firmware is running and the target register is below 1024, those helpers route APB reads/writes through `dib9000_risc_apb_access_read()` and `dib9000_risc_apb_access_write()` instead of direct host I2C. Firmware support includes `dib9000_firmware_download()`, `dib9000_mbx_host_init()`, `dib9000_mbx_send_attr()`, `dib9000_mbx_read()`, `dib9000_mbx_process()`, `dib9000_mbx_get_message_attr()`, `dib9000_risc_check_version()`, `dib9000_fw_boot()`, `dib9000_fw_init()`, and RISC memory helpers. DVB operations are provided through `dib9000_ops`: release, init, sleep, set/get frontend, tune settings, status, BER, signal strength, SNR, and uncorrected block reads.

## Control Flow
`dib9000_attach()` allocates state and a `dvb_frontend`, copies `struct dib9000_config`, initializes locks and buffers, validates the chip with `dib9000_identify()`, initializes the shared DiB I2C master, registers a firmware tuner I2C adapter and component-bus adapter, resets the chip, and returns the frontend. Firmware is brought up later via `dib9000_firmware_post_pll_init()`, which calls `dib9000_fw_init()`: boot RISC B, check allowed firmware major/minor versions, send GPIO/subband/init-demod messages, request frontend firmware download, and store firmware memory map entries.

Tuning starts in `dib9000_set_frontend()`. The driver validates frequency and bandwidth, marks PID filter commands as postponed, copies the master DVB property cache to all slave frontends, enables diversity input, drives outputs high-Z, chooses search versus tune mode from AUTO parameters, and runs a polling state machine around `dib9000_fw_tune()`. If one frontend finds a usable channel, `dib9000_get_frontend()` syncs the discovered parameters to all frontends and the remaining frontends retune with fixed parameters. Final output routing puts the master in the configured MPEG/FIFO/serial mode, slaves in diversity output, and disables diversity input on the last frontend.

## State and Persistence
All state is volatile kernel and device state. Software persistence includes the frontend/slave list, cached config, current tune state/status, `dvb_frontend_parametersContext`, GPIO cache, component bus speed, firmware-running flag, firmware memory map, mailbox cache, and postponed PID command array. Hardware state spans reset registers, power gating registers, GPIO registers, MPEG output registers, mailbox registers, and firmware memory windows. Mutexes split synchronization across demod-wide operations, mailbox interface, mailbox cache processing, raw memory access, and memory-mailbox transactions. There is no filesystem persistence.

## Dependencies and Integration Points
The driver depends on Linux I2C, mutexes, `intlog10()`, DVB frontend core, `dib9000.h`, and `dibx000_common.h`. It integrates with board/tuner drivers through exported I2C adapters, slave frontend APIs for diversity chains, the DVB frontend property cache, Kconfig/module loading, and external microcode buffers supplied through `struct dib9000_config`.

## Risks and Edge Cases
Firmware version support is narrow: major version 7 with selected minor values only. Mailbox waits are bounded but can sleep for long periods on full mailboxes or reset timeouts. Several register-level transfers truncate tuner messages to 16 bytes and component parameters to byte-sized lengths, so large transactions require caller awareness. `dib9000_attach()` frees only `st` on the common error label after `fe` allocation, which is a leak path if chip identification or adapter registration fails before returning. Postponed PID filtering stores at most ten commands and logs overflow rather than failing. Shared `i2c_read_buffer` use makes locking discipline important for metrics and frontend cache reads. Hardware register constants are largely magic numbers, increasing regression risk during porting.

## Test Signals
Key signals are successful chip identification for device IDs `0x4003` through `0x4005`, RISC firmware boot and accepted version message, valid firmware memory-map sizes, stable mailbox send/receive under debug output, successful DVB-T search and fixed retune paths, diversity chains with multiple slave frontends, MPEG output mode selection, tuner and component-bus I2C transactions, PID filter replay after tuning, status/BER/strength/SNR/unc reads, `dib9000_i2c_enumeration()` address reassignment, and clean detach removing all registered adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib9000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib9000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib9000.h

## Purpose
`dib9000.h` is the public API and configuration header for the DiBcom DiB9000 DVB-T demodulator driver. It defines board-supplied configuration data, optional exported helper APIs, and disabled-driver stubs for users that can build without DiB9000 support.

## Important APIs, Types, and Functions
`struct dib9000_config` carries DVB-T mode, MPEG packet sizing, diversity mode, bandwidth/PLL information, IF drive strength, timing/clock values, VCXO timer, demod clock, RISC B firmware buffer and size, two GPIO function descriptors, subband selection table, and output mode. Public declarations cover attach, I2C enumeration, tuner/component-bus interfaces, common DiB I2C master access, GPIO, firmware PID filtering, post-PLL firmware init, slave frontend management, I2C adapter replacement, and component-bus speed control.

## Control Flow
Users call `dib9000_attach(i2c_adap, i2c_addr, cfg)` to obtain a DVB frontend, optionally enumerate multiple chips with `dib9000_i2c_enumeration()`, then retrieve helper I2C adapters or control GPIO/PID filtering as needed. When `CONFIG_DVB_DIB9000` is not reachable, inline stubs warn and return `NULL` or `-ENODEV`.

## State and Persistence
The header itself has no storage. It defines ownership-sensitive pointers to bandwidth config and firmware buffers whose lifetime must outlive driver initialization. State is persisted only in the attached driver's runtime object and hardware.

## Dependencies and Integration Points
It depends on `dibx000_common.h`, DVB frontend structures, Linux I2C, and common DiB GPIO/subband abstractions. The header is the integration point for bridge drivers that package DiB9000 firmware and wire the demod to tuners or component buses.

## Risks and Edge Cases
The enabled prototype for `dib9000_attach()` uses `const struct dib9000_config *`, while the disabled inline stub uses a non-const pointer; this is source-compatible for most callers but not identical. Missing firmware buffer data or invalid clock/timing fields will fail later in the implementation, not at compile time. Callers must handle optional support through `NULL` and `-ENODEV`.

## Test Signals
Build coverage should exercise both enabled and disabled Kconfig paths. Runtime signals include successful attach, firmware post-PLL init, tuner/component I2C adapter retrieval, GPIO configuration, PID filter calls, multi-demod enumeration, and slave frontend get/set behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib9000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.c

## Purpose
`dibx000_common.c` implements shared I2C-master support for the DiBcom demodulator family. It turns demodulator-hosted GPIO/tuner I2C interfaces into Linux `i2c_adapter` instances and provides common speed, reset, init, and cleanup helpers for DiB3000/7000/8000/9000-family drivers.

## Important APIs, Types, and Functions
Exported functions are `dibx000_i2c_set_speed()`, `dibx000_get_i2c_adapter()`, `dibx000_reset_i2c_master()`, `dibx000_init_i2c_master()`, and `dibx000_exit_i2c_master()`. Internal helpers include `dibx000_write_word()`, `dibx000_read_word()`, `dibx000_is_i2c_done()`, `dibx000_master_i2c_write()`, `dibx000_master_i2c_read()`, `dibx000_i2c_select_interface()`, direct GPIO12/GPIO34 transfer functions, gated tuner/GPIO67 transfer functions, `dibx000_i2c_gate_ctrl()`, and `i2c_adapter_init()`.

## Control Flow
Initialization sets the demod revision, parent adapter, shifted I2C address, base register (`1024` for DiB7000P/DiB8000, otherwise `768`), registers four child adapters, closes the gate, and selects the tuner interface. Direct master transfers select GPIO12 or GPIO34 and then chunk reads or writes through demod FIFO/control registers in up to eight-byte pieces. Gated transfers select the target interface, build a combined parent I2C transaction that opens the gate, forwards the caller messages, then closes the gate.

## State and Persistence
Runtime state lives in `struct dibx000_i2c_master`: selected interface, registered child adapters, parent adapter/address, base register, transfer buffers, message array, and `i2c_buffer_lock`. There is no persistent storage; hardware gate/interface registers and speed divisors are volatile.

## Dependencies and Integration Points
The file depends on Linux I2C, mutexes, modules, and `dibx000_common.h`. It is integrated by demod drivers that embed `struct dibx000_i2c_master` and expose child I2C buses to tuner drivers. The exported speed function expects `i2c_get_adapdata()` to return the master object.

## Risks and Edge Cases
The transfer code returns `0` rather than a negative error from some child adapter paths when a chunk read/write fails, which I2C callers may interpret as no messages transferred. Gated paths reject more than 32 messages because the master has 34 `i2c_msg` slots. Speed calculation divides `60000 / speed`; invalid zero speed would fault. `dibx000_init_i2c_master()` logs adapter-registration failures but still continues and returns only the final gate-close transfer result, so partially registered adapter sets are possible. Lock interruption maps to `-EINVAL` in some helpers.

## Test Signals
Test child adapter registration/removal, direct GPIO12/GPIO34 reads and writes over multiple eight-byte chunks, gated tuner and GPIO67 transactions with open/close gate sequencing, interface switching, speed programming with old and new device revisions, reset closing the gate, error handling for NACK/timeouts, and cleanup after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.h

## Purpose
`dibx000_common.h` defines shared data structures, constants, and prototypes used by DiBcom demodulator drivers. It covers demod-hosted I2C master state, tuner band classification, AGC/PLL configuration tables, ADC power states, output/input modes, tuning state machine IDs, frontend channel-status context, GPIO/subband board functions, and TIMF commands.

## Important APIs, Types, and Functions
`enum dibx000_i2c_interface` names tuner and GPIO-based I2C interfaces. `struct dibx000_i2c_master` stores child adapters, parent I2C information, base register, buffers, messages, and a mutex. Prototypes expose `dibx000_init_i2c_master()`, `dibx000_get_i2c_adapter()`, `dibx000_exit_i2c_master()`, `dibx000_reset_i2c_master()`, and `dibx000_i2c_set_speed()`. `struct dibx000_agc_config` and `struct dibx000_bandwidth_config` describe board-specific RF gain and clock/PLL/timing parameters. `enum frontend_tune_state` defines multi-phase tuner, AGC, and demod states. `struct dvb_frontend_parametersContext`, `struct dibGPIOFunction`, and `struct dibSubbandSelection` define shared firmware/board abstractions.

## Control Flow
The header is included by concrete demod drivers and board code. Config tables are selected by frequency band using `BAND_OF_FREQUENCY()`, I2C adapters are requested by interface/gating mode, and tune-state constants coordinate staged demod control loops in implementation files.

## State and Persistence
This file declares runtime state layouts but does not allocate storage. State is held by embedding drivers and by hardware registers programmed through the common implementation. There is no durable persistence.

## Dependencies and Integration Points
It requires Linux I2C and DVB frontend definitions through includers. It integrates DiB8000/DiB9000 and related demods with tuner drivers, board GPIO policy, PLL/AGC tables, and DVB frontend property/tune state handling.

## Risks and Edge Cases
`BAND_OF_FREQUENCY()` is an inline macro with a nonmonotonic first two comparisons: frequencies less than or equal to 170000 kHz classify as CBAND before the FM threshold check, so callers must understand the intended legacy mapping. Many structures contain raw pointers to config tables that need stable lifetime. Output mode constants are shared across chips but not every chip implements every mode. Numeric tune/status values are negative sentinel codes and should not be mixed with Linux errno without care.

## Test Signals
Compile coverage across DiB demod drivers, I2C adapter selection for all interfaces, AGC/PLL table selection by band, GPIO/subband application, tune-state transitions, bandwidth conversion macros, and status-code handling are the important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Kconfig

## Purpose
This Kconfig fragment declares the `DVB_DRX39XYJ` frontend option for Micronas DRX-J demodulators, specifically the DRX39xx family such as `drx3933j`.

## Important APIs, Types, and Functions
The single symbol is `config DVB_DRX39XYJ`, a tristate named "Micronas DRX-J demodulator". It depends on `DVB_CORE` and `I2C`, defaults to module when `MEDIA_SUBDRV_AUTOSELECT` is disabled, and documents support for ATSC 8VSB plus QAM64/256 tuner modules.

## Control Flow
Kernel configuration selects this symbol directly or through media subdriver autoselection. The symbol controls compilation of the `drx39xyj` object from the local Makefile and enables the reachable attach declaration in `drx39xxj.h`.

## State and Persistence
Kconfig contributes build-time state only. There is no runtime state or persistence.

## Dependencies and Integration Points
The option integrates with the media DVB frontend menu, DVB core, I2C subsystem, the local Makefile, and callers that use `IS_REACHABLE(CONFIG_DVB_DRX39XYJ)`.

## Risks and Edge Cases
If the symbol is disabled, attach callers receive a `NULL` inline stub. The help text mentions a tuner module even though this directory builds a demodulator frontend, which may confuse configuration review. Missing `I2C` or `DVB_CORE` correctly prevents selection.

## Test Signals
Build test `y`, `m`, and disabled configurations; verify `drx39xyj.o` is produced when enabled and callers handle the disabled attach stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Makefile

## Purpose
This Makefile wires the DRX39xyj frontend into the kernel media build.

## Important APIs, Types, and Functions
`drx39xyj-objs := drxj.o` declares the module object list. `obj-$(CONFIG_DVB_DRX39XYJ) += drx39xyj.o` connects the object to the Kconfig symbol. `ccflags-y += -I$(srctree)/drivers/media/tuners/` adds the tuner include directory for local compilation.

## Control Flow
When `CONFIG_DVB_DRX39XYJ` is built in or modular, kbuild compiles `drxj.o` and links it into `drx39xyj.o`. The additional include path is active for files in this directory.

## State and Persistence
This file affects build graph state only and has no runtime storage.

## Dependencies and Integration Points
It depends on the local `Kconfig` symbol and on a `drxj.c` implementation file in the same directory. It integrates with tuner headers through the extra include path.

## Risks and Edge Cases
The module object is a wrapper around `drxj.o`; if future source files are added but not listed, they will not be linked. The explicit tuner include path can hide missing local includes if a file accidentally relies on tuner-private headers.

## Test Signals
Run kernel/module builds with `CONFIG_DVB_DRX39XYJ=m` and `=y`, confirm `drx39xyj.o` links, and verify no include path regressions when tuner headers move.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx39xxj.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx39xxj.h

## Purpose
`drx39xxj.h` is the Linux-facing public header for the Micronas DRX39xxJ frontend driver. It defines the per-device wrapper state used by the frontend implementation and exposes the attach entry point.

## Important APIs, Types, and Functions
`struct drx39xxj_state` stores the parent `i2c_adapter`, a generic `struct drx_demod_instance`, embedded `struct dvb_frontend`, an `i2c_gate_open` bit, and a firmware handle. `drx39xxj_attach(struct i2c_adapter *i2c)` returns a DVB frontend when `CONFIG_DVB_DRX39XYJ` is reachable; otherwise the inline stub returns `NULL`.

## Control Flow
Bridge drivers include this header and call `drx39xxj_attach()` with an I2C adapter. The implementation allocates and initializes the state, then exposes the embedded `frontend`. Disabled builds compile to a no-op attach path.

## State and Persistence
The state structure tracks runtime I2C, demod core, frontend, gate state, and firmware object lifetime. No durable storage is represented.

## Dependencies and Integration Points
It includes Linux DVB frontend headers and `drx_driver.h`, binding the Linux media layer to the generic DRX driver abstraction. It is controlled by `CONFIG_DVB_DRX39XYJ`.

## Risks and Edge Cases
The header exposes the state layout, so implementation and any users must stay synchronized. The trailing comment says `DVB_DUMMY_FE_H`, which is stale and can mislead include-guard audits. Callers must check for `NULL` when the driver is disabled or attach fails.

## Test Signals
Compile enabled/disabled configurations, attach on hardware or emulated I2C, firmware request/release paths, and I2C gate open/close behavior through tuner interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx39xxj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_dap_fasi.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_dap_fasi.h

## Purpose
`drx_dap_fasi.h` defines compile-time configuration and address flag macros for the DRX Data Access Protocol Fast Access Sequential Interface. FASI is an I2C-oriented protocol using short or long register-address formats and single-master or multi-master transaction behavior.

## Important APIs, Types, and Functions
The header sets defaults for `DRXDAPFASI_LONG_ADDR_ALLOWED`, `DRXDAPFASI_SHORT_ADDR_ALLOWED`, `DRXDAP_SINGLE_MASTER`, `DRXDAP_MAX_WCHUNKSIZE`, and `DRXDAP_MAX_RCHUNKSIZE`, then validates combinations with preprocessor errors. Public protocol flags include `DRXDAP_FASI_RMW`, `DRXDAP_FASI_BROADCAST`, `DRXDAP_FASI_CLEARCRC`, `DRXDAP_FASI_SINGLE_MASTER`, `DRXDAP_FASI_MULTI_MASTER`, `DRXDAP_FASI_SMM_SWITCH`, `DRXDAP_FASI_MODEFLAGS`, and `DRXDAP_FASI_FLAGS`. Address macros extract block, bank, and offset and classify short/long format eligibility.

## Control Flow
The header is included by DRX access-protocol code after `drx_driver.h`. Compile-time conditionals choose minimum write chunk size based on address format and master mode, reject impossible configurations, and enforce even read chunk sizes. Runtime code then uses the address and flag macros to encode FASI operations.

## State and Persistence
There is no runtime state. The only state is compile-time feature selection and constants that shape buffer sizing and transaction encoding.

## Dependencies and Integration Points
It depends on `drx_driver.h`, which supplies default DAP chunk sizes and master-mode policy. It integrates generic DRX register access code with FASI-capable demod firmware/hardware.

## Risks and Edge Cases
Misconfigured chunk sizes fail compilation, which is good for safety but can surprise downstream ports with smaller I2C limits. The default allows both short and long addressing; platforms requiring only one mode must override the macros before inclusion. Address classification relies on bit masks such as `0xFC30FF80`, so new address maps need careful validation.

## Test Signals
Compile coverage should include short-only, long-only, both-format, single-master, and multi-master builds. Runtime validation should exercise read, write, read-modify-write, broadcast, CRC-clear, short-format boundary, long-format address, and offset-too-large paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_dap_fasi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver.h

## Purpose
`drx_driver.h` is the generic DRX demodulator driver contract shared by the DRX39xyj implementation. It defines board-support I2C/tuner hooks, tuning and modulation enums, control structures, audio/video/OOB configuration payloads, data-access function tables, demod common attributes, stringification helpers, and access macros.

## Important APIs, Types, and Functions
The BSP layer starts with `struct i2c_device_addr`, `IS_I2C_10BIT()`, `drxbsp_i2c_init()`, `drxbsp_i2c_term()`, `drxbsp_i2c_write_read()`, `drxbsp_i2c_error_text()`, and `drx_i2c_error_g`. Tuner integration is modeled by `struct tuner_common`, `struct tuner_ops`, `struct tuner_instance`, and helper prototypes for set/get frequency and default I2C forwarding. DAP configuration defaults include `DRXDAP_SINGLE_MASTER`, `DRXDAP_MAX_WCHUNKSIZE`, and `DRXDAP_MAX_RCHUNKSIZE`.

The header defines the core RF/channel vocabulary: `enum drx_standard`, `drx_substandard`, `drx_bandwidth`, `drx_mirror`, `drx_modulation`, `drx_hierarchy`, `drx_priority`, `drx_coderate`, `drx_guard`, `drx_fft_mode`, `drx_classification`, `drx_interleave_mode`, `drx_carrier_mode`, `drx_frame_mode`, `drx_tps_frame`, `drx_ldpc`, `drx_pilot_mode`, `drxu_code_action`, `drx_lock_status`, `drx_uio`, and OOB/audio enums. Main payload structures include `drxu_code_info`, `drx_mc_version_rec`, `drx_filter_info`, `drx_channel`, `drx_frequency_plan`, `drx_scan_param`, `drxtps_info`, `drx_version`, `drx_cfg_mpeg_output`, `drxi2c_data`, audio status/config structures, `drx_access_func`, `drx_reg_dump`, `drx_common_attr`, and `drx_demod_instance`.

## Control Flow
The header establishes a layered control model. Platform I2C and tuner callbacks feed a generic demod instance. Higher-level code issues configuration through `drx_ctrl()` style access macros such as `DRX_ACCESSMACRO_SET()` and `DRX_ACCESSMACRO_GET()`, passing `struct drx_cfg` payloads for device-specific settings. Scan state in `drx_common_attr` tracks frequency-plan progress, inner scan function, lock requirements, and current channel. Data access is abstracted through function pointers for block and 8/16/32-bit register reads, writes, and read-modify-write operations.

## State and Persistence
The file defines the central persistent-in-memory state shape but does not allocate it. `struct drx_common_attr` tracks microcode file/version policy, clocks, IF/mirror settings, MPEG defaults, open state, scan progress, power mode, tuner ranges/polarities, current/previous/cache standards, bootloader use, capabilities, and product ID. `struct drx_demod_instance` connects I2C address, common attributes, device-specific attributes, and the Linux I2C adapter. This state is runtime only; persistence across module reload or power loss is not provided by the header.

## Dependencies and Integration Points
It depends on Linux kernel types, errno, and I2C. It is included by DRX39xyj public and implementation headers and by the FASI DAP header. The string macros support debug/log reporting, while standard-class macros such as `DRX_ISATVSTD()`, `DRX_ISQAMSTD()`, `DRX_ISVSBSTD()`, and `DRX_ISDVBTSTD()` support mode-specific control flow.

## Risks and Edge Cases
This is a very broad ABI-like header with many raw pointers and callback tables, so initialization order and object lifetime are critical. Several macros assume an external `drx_ctrl()` symbol and can hide failures by writing fallback values. `DRX_ATTR_MICROCODE(d)` references `my_common_attr->microcode`, while the visible common attribute field is `microcode_file`; that mismatch should be checked against the implementation before using the macro. Some comments and spellings are legacy, and generated or vendor-style layouts may not follow normal kernel style. Auto/unknown sentinel values share fixed numeric values across many enums, so casts between unrelated enums can mask invalid state.

## Test Signals
Important coverage includes BSP I2C write/read error mapping, tuner callback operation, microcode upload/verify metadata, channel set/get for DVB-T, ATSC 8VSB, QAM, and analog modes, scan plan progress, power-mode transitions, MPEG/I2S/audio/OOB config payloads, DAP function-table calls for all register widths, string macro output for invalid values, and build coverage for all users of DRX access macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver_version.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver_version.h

## Purpose
`drx_driver_version.h` is a generated version header for the DRX-J driver package. It records the generated source metadata and exposes the driver version constants used by the DRX implementation and optional register-table tooling.

## Important APIs, Types, and Functions
When `_REGISTERTABLE_` is defined, it declares external `drx_driver_version[]` and `drx_driver_version_info[]` register-table symbols. The active version macros are `VERSION_MAJOR 1`, `VERSION_MINOR 0`, and `VERSION_PATCH 56`. `VERSION__A` is defined as `0x0`.

## Control Flow
Normal builds include the header for compile-time constants only. Register-table builds additionally use the external arrays. The file is generated and explicitly warns against manual editing.

## State and Persistence
There is no runtime state. The header provides build-time version identity that may be reported or compared by driver code.

## Dependencies and Integration Points
It can depend on `<registertable.h>` under `_REGISTERTABLE_`. Otherwise it is self-contained and integrates with the DRX driver version/reporting path.

## Risks and Edge Cases
Because it is generated, manual edits would be overwritten or create inconsistency with the original IDF source. The `_REGISTERTABLE_` path requires external symbols not defined in this header. Version constants are old vendor metadata and should not be assumed to match Linux module versioning.

## Test Signals
Compile with and without `_REGISTERTABLE_`, verify reported version `1.0.56`, and ensure generated-source updates refresh this header consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver_version.h -->
