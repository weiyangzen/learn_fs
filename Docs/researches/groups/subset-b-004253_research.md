# subset-b-004253 research

Grouped research report for the requested misc driver files under `sources/distributed-fs/ceph-client/drivers/misc`. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.c

Purpose: implements the shared Analog Devices AD525x/AD52xx digital potentiometer core used by bus-specific I2C and SPI frontends. It translates device capability encodings from `ad525x_dpot.h` into per-RDAC sysfs files, handles RDAC/EEPROM/OTP/tolerance access, and exports `ad_dpot_probe` and `ad_dpot_remove`.

Important APIs and functions: `struct dpot_data` stores copied bus ops, feature bits, wiper mask, RDAC mask, OTP enable bits, and write-only RDAC cache. Bus wrappers call `struct ad_dpot_bus_ops`. `dpot_read_spi`, `dpot_read_i2c`, `dpot_write_spi`, and `dpot_write_i2c` contain device-family protocol differences. Sysfs helpers are `sysfs_show_reg`, `sysfs_set_reg`, and `sysfs_do_cmd`; generated attributes cover `rdacN`, `eepromN`, `toleranceN`, `otpN`, `otpNen`, and increment/decrement commands.

Control flow: bus drivers call `ad_dpot_probe` with a device id encoding. Probe allocates state, derives max position and masks, creates sysfs files for each enabled wiper, initializes write-only caches to midscale, and optionally creates command attributes. Sysfs writes parse decimal values, clamp to the RDAC range, require explicit `otpNen` before OTP writes, serialize on `update_lock`, and sleep after EEPROM or OTP programming. Remove deletes per-wiper files and frees state.

State and persistence: software state is per device and held in drvdata. Hardware RDAC state is volatile unless written to EEPROM or OTP through exposed sysfs paths. OTP enable state is a software guard only and is not persistent. Write-only SPI parts rely on `rdac_cache` for reads.

Dependencies and integration points: depends on kernel device/sysfs APIs, mutexes, sleep delays, and bus ops supplied by sibling I2C/SPI drivers. The ABI is the misc-device sysfs interface documented externally by the driver family.

Risks: the file contains malformed-looking source in this snapshot around the SPI appdata path, including a dangling `else`/`BUG()` structure, which is a build risk if not caused by snapshot corruption. `ad_dpot_remove` does not remove the command attribute group created for `F_CMD_INC`. Sysfs writes ignore `dpot_write` return values and still return `count`, so programming failures can be hidden. OTP writes are destructive and exposed through sysfs after a simple enable flag. The wiper attribute table starts with duplicate `rdac0`, which is intentional for index alignment but brittle.

Test signals: build with AD525x I2C/SPI frontends, probe every encoded family class, verify sysfs file creation for one through six wipers, exercise read/write paths on EEPROM, OTP, tolerance, and write-only parts, and use bus-error injection to confirm user-visible failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.h

Purpose: defines the shared AD525x digital potentiometer device-id encoding, feature flags, register command constants, bus-operation contract, and shared probe/remove declarations.

Important APIs and types: `DPOT_CONF` packs feature flags, active wiper bits, maximum-position exponent, and a unique id into an `enum dpot_devid` value. `DPOT_UID`, `DPOT_MAX_POS`, `DPOT_WIPERS`, and `DPOT_FEAT` unpack that encoding. `enum dpot_devid` lists supported AD5258/AD5259, AD516x, AD52xx, ADN28xx, and OTP-capable parts. `struct ad_dpot_bus_ops` abstracts byte, register-byte, and register-word reads/writes. `struct ad_dpot_bus_data` passes a bus client plus ops into `ad_dpot_probe`.

Control flow: bus-specific drivers select an enum value from their device-id tables, fill bus ops, and call the shared core. The core uses feature bits such as `F_CMD_EEP`, `F_CMD_OTP`, `F_RDACS_WONLY`, `F_AD_APPDATA`, and `F_SPI_*` to choose register protocols and sysfs exposure.

State and persistence: this header owns no runtime state, but its encodings directly determine persistent hardware affordances such as EEPROM and one-time programmable support. Incorrect encodings change both ABI shape and hardware commands.

Dependencies and integration points: depends on Linux integer types and an including translation unit with `struct device`. It is included by the shared core and by I2C/SPI frontend drivers.

Risks: many constants encode hardware protocol details in compact bitfields, so table mistakes are hard to see in review. `DPOT_MAX_POS` is an exponent, not a literal maximum, which can be misused. Function declarations rely on transitive visibility for `struct device` rather than declaring it locally.

Test signals: compile all frontends, verify each device id creates the expected number of sysfs attributes and RDAC range, and cross-check encoded features against datasheets for EEPROM, OTP, tolerance, SPI width, and write-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Kconfig

Purpose: declares the `ALTERA_STAPL` kernel configuration option for the Altera FPGA firmware download module.

Important APIs and symbols: `ALTERA_STAPL` is a tristate named "Altera FPGA firmware download module". It depends on `I2C`. A comment is shown when I2C is unavailable.

Control flow: selecting this symbol enables kbuild to compile the STAPL interpreter, decompressor, and JTAG support through the local Makefile. The resulting module provides the firmware execution helper exported by `altera.c`.

State and persistence: no runtime state is stored here. The selected tristate persists in the kernel build configuration and controls whether the module is built in, modular, or absent.

Dependencies and integration points: integrates into the misc driver Kconfig tree and requires I2C even though the optional legacy parallel-port JTAG fallback is gated separately by `CONFIG_HAS_IOPORT` in the Makefile.

Risks: the help text is minimal and does not explain that the module interprets firmware bytecode and drives board-specific JTAG callbacks. Users may enable it without the board driver that supplies `struct altera_config`.

Test signals: menuconfig visibility with and without I2C, allmodconfig build coverage, and module build confirmation for `CONFIG_ALTERA_STAPL=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Makefile

Purpose: maps `CONFIG_ALTERA_STAPL` to the objects that form the Altera STAPL firmware download module.

Important APIs and entries: `altera-stapl-y` links `altera-jtag.o`, `altera-comp.o`, and `altera.o`. `altera-stapl-$(CONFIG_HAS_IOPORT)` adds `altera-lpt.o` only when port I/O is available. `obj-$(CONFIG_ALTERA_STAPL)` emits `altera-stapl.o`.

Control flow: kbuild combines the interpreter, decompressor, and JTAG state-machine implementation into one module. The optional LPT implementation supplies the fallback `netup_jtag_io_lpt` function declared in `altera-exprt.h`.

State and persistence: no runtime state. Build composition changes depending on architecture support for I/O ports.

Dependencies and integration points: depends on the local Kconfig symbol and on the source files exporting matching symbols. It integrates with board drivers that link against `altera_init`.

Risks: builds without `CONFIG_HAS_IOPORT` still compile declarations for the LPT fallback, but `altera_init` must avoid using that fallback when port I/O is disabled. Adding new interpreter support requires updating this object list.

Test signals: build with `ALTERA_STAPL=y/m` on I/O-port and non-I/O-port architectures, and verify unresolved-symbol checks for `netup_jtag_io_lpt` do not fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-comp.c -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-comp.c

Purpose: implements the STAPL/Jam bytecode decompressor used by `altera.c` to expand compressed Boolean-array sections from firmware into executable variable buffers.

Important APIs and functions: `altera_shrink(u8 *in, u32 in_length, u8 *out, u32 out_length, s32 version)` is the exported decompression entry point. `altera_bits_req` computes the number of packed bits needed for offsets, and `altera_read_packed` consumes variable-width bitfields from the compressed stream.

Control flow: `altera_shrink` clears the output buffer, reads the uncompressed byte length from the compressed input, validates it against `out_length`, and then decodes a stream of literal blobs or back-references. A zero tag copies up to three literal bytes; a one tag reads an offset plus byte length and copies from already decompressed output. Version greater than zero reduces the match window by one.

State and persistence: all state is local to the decompression call. Output persists only in the caller-owned buffer, usually a dynamically allocated interpreter variable in `altera_execute`.

Dependencies and integration points: depends on kernel integer types and `altera-exprt.h`. It is called from `altera.c` while initializing compressed Boolean arrays in firmware data sections.

Risks: `in_length` is not used to bound packed reads, so corrupt firmware can drive reads past the compressed input if earlier validation is insufficient. Back-references assume nonzero valid offsets and can underflow `out[i - offset]` if the stream is malicious. Error signaling is limited to returning zero length.

Test signals: known-good compressed JBC fixtures, fuzzed malformed streams, boundary cases for zero-length output, out_length too small, maximum match-window offsets, and KASAN/UBSAN runs around packed reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-exprt.h -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-exprt.h

Purpose: declares cross-file helper exports for the Altera STAPL module.

Important APIs and types: declares `altera_shrink` for compressed firmware data expansion and `netup_jtag_io_lpt` for the optional ByteBlaster-style parallel-port JTAG fallback.

Control flow: `altera.c` includes this header to call the decompressor and, when no board-specific `jtag_io` callback is provided and I/O ports are enabled, to install the LPT JTAG callback. `altera-comp.c` and `altera-lpt.c` provide the definitions.

State and persistence: the header owns no state. The declared functions operate on caller-provided buffers or on external hardware through a callback-style interface.

Dependencies and integration points: relies on Linux fixed-width types being available. It is internal to the `altera-stapl` module and forms a narrow boundary between interpreter, compression, and optional LPT transport code.

Risks: `netup_jtag_io_lpt` is declared unconditionally even though the object defining it is built only with `CONFIG_HAS_IOPORT`; callers must keep the runtime guard correct. There are no comments documenting `altera_shrink` buffer ownership or bounds expectations.

Test signals: module link checks with and without `CONFIG_HAS_IOPORT`, decompressor unit-style fixture coverage through `altera_init`, and hardware tests for fallback LPT JTAG where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-exprt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.c -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.c

Purpose: implements the JTAG TAP state machine and scan primitives used by the Altera STAPL interpreter. It turns interpreter operations into `jtag_io` callback toggles for TMS/TDI/TDO.

Important APIs and functions: initialization and configuration functions are `altera_jinit`, `altera_set_drstop`, `altera_set_irstop`, `altera_set_dr_pre/post`, and `altera_set_ir_pre/post`. State movement uses `altera_goto_jstate`, `altera_wait_cycles`, and `altera_wait_msecs`. Scan operations are `altera_irscan`, `altera_swap_ir`, `altera_drscan`, and `altera_swap_dr`; `altera_free_buffers` resets and releases allocations.

Control flow: the file models TAP transitions in `altera_transitions` and selects paths using `altera_jtag_path_map`. Scan calls normalize the current state to IDLE, DRPAUSE, or IRPAUSE, allocate a reusable buffer large enough for preamble, target bits, and postamble, concatenate the bit ranges, clock them through low-level IR or DR scan helpers, update the cached TAP state to pause, move to the configured stop state, and optionally extract captured target bits from the shared scan buffer.

State and persistence: `struct altera_jtag` tracks current TAP state, stop states, pre/post bit counts, and reusable buffers. State persists across opcodes in one `altera_init` execution and is freed at interpreter completion.

Dependencies and integration points: depends on `struct altera_config->jtag_io`, firmware delays, slab allocation, and definitions from `altera-jtag.h`. `altera.c` invokes these helpers for STAPL opcodes.

Risks: this snapshot contains malformed-looking duplicate lines in `altera_set_ir_post` and a duplicated parameter in `altera_extract_target_data`, which are severe build risks if not generated by source corruption. Buffer bit operations assume pre/post data pointers are valid when counts are nonzero. TAP state tracking can diverge if the callback fails silently because `alt_jtag_io` does not carry errors.

Test signals: compile coverage, TAP path tests for every state transition, IR/DR scan loopback with known TDO data, preamble/postamble extraction tests, and real JTAG programming on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.h -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.h

Purpose: defines the Altera STAPL JTAG state structures and declares the TAP manipulation functions implemented in `altera-jtag.c`.

Important APIs and types: `enum altera_jtag_state` names the full TAP state set plus `ILLEGAL_JTAG_STATE`. `struct altera_jtag` stores current state, DR/IR stop states, pre/post counts, buffer lengths, and owned buffers. `struct altera_state` combines an `altera_config`, JTAG state, message buffer, and fixed-size interpreter stack. The header declares scan, swap, wait, pre/post, and cleanup helpers.

Control flow: `altera.c` creates `struct altera_state`, initializes it with `altera_jinit`, and then uses these functions while interpreting bytecode opcodes such as DRSCAN, IRSCAN, WAIT, DRPRE, DRPOST, IRPRE, and IRPOST.

State and persistence: state is per firmware execution. The `stack` and `msg_buff` are part of interpreter state, while the nested `struct altera_jtag` persists scan configuration across opcodes until `altera_free_buffers`.

Dependencies and integration points: requires `struct altera_config` from `<misc/altera.h>` and kernel integer types. It is the internal contract between the bytecode interpreter and the JTAG transport implementation.

Risks: `ALTERA_STACK_SIZE` is fixed at 128, so bytecode stack-depth handling depends on runtime checks. The header exposes raw buffers and counts without encapsulation, making ownership discipline important. Invalid enum values can be passed to stop-state setters without local validation.

Test signals: build coverage, interpreter tests that stress stack depth and scan padding, and assertions that cleanup releases all buffers after failed and successful firmware executions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-jtag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-lpt.c -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-lpt.c

Purpose: provides an optional legacy parallel-port ByteBlaster JTAG bit-banging backend for the Altera STAPL module.

Important APIs and functions: `netup_jtag_io_lpt(void *device, int tms, int tdi, int read_tdo)` is the exported callback-compatible entry point. Internal helpers `byteblaster_write` and `byteblaster_read` wrap `outb` and `inb` at offsets relative to base port `0x378`.

Control flow: the first callback initializes the LPT control port once by setting control bits. Each call builds a data byte from TDI and TMS, writes it, optionally reads inverted TDO from the status port, pulses TCK by setting bit 0, then drops it.

State and persistence: a single static `lpt_hardware_initialized` flag persists for the module lifetime. The hardware port state is mutated directly and is not restored on module exit in this file.

Dependencies and integration points: built only when `CONFIG_HAS_IOPORT` is available. It is selected by `altera_init` when no board-specific JTAG callback is provided and the architecture supports port I/O.

Risks: the `device` argument is unused and the base port is hard-coded to `0x378`, so it is not safe for arbitrary parallel-port configurations. There is no locking around the global initialization flag or port access. Direct I/O port use can conflict with other parallel-port users.

Test signals: compile on `CONFIG_HAS_IOPORT` platforms, oscilloscope or logic-analyzer validation of TMS/TDI/TCK/TDO timing, and negative tests confirming non-I/O-port builds do not reference this backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-lpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera.c -->
# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera.c

Purpose: implements the Altera Jam STAPL/JBC firmware bytecode interpreter and exports `altera_init` for board drivers that need to program FPGAs over JTAG.

Important APIs and functions: `altera_init(struct altera_config *config, const struct firmware *fw)` is the exported entry point. `altera_execute` parses bytecode headers, allocates interpreter variables, and dispatches opcodes. Helper functions read notes, validate CRC, enumerate file/action/procedure metadata, and export debug values. `enum altera_fpga_opcode` defines stack, arithmetic, flow-control, array, scan, wait, and export operations.

Control flow: `altera_init` allocates work buffers and state, installs a JTAG callback or optional LPT fallback, checks firmware CRC, prints metadata under debug, and calls `altera_execute`. The executor validates the JBC magic, locates tables, initializes scalar and array variables including compressed arrays through `altera_shrink`, chooses the requested action for format version 2, then runs a stack VM loop. JTAG opcodes call `altera_drscan`, `altera_irscan`, swap variants, wait helpers, and state-transition helpers. On exit it resets/free JTAG buffers and releases dynamic variable arrays.

State and persistence: all interpreter state is transient for one firmware execution: variable arrays, procedure attributes, stack, message buffer, and JTAG state. Persistent effects are external: FPGA/JTAG device programming and optional debug logs.

Dependencies and integration points: depends on firmware loader data, unaligned endian accessors, module parameters, `struct altera_config` from `<misc/altera.h>`, decompression in `altera-comp.c`, and JTAG helpers in `altera-jtag.c`.

Risks: this snapshot contains malformed-looking duplicate lines and an extra comment terminator around opcode and note handling, which are build risks if not snapshot artifacts. The VM processes firmware-controlled offsets, counts, and stack operations, so bounds validation is security-critical. CRC errors are logged but `altera_init` does not use the CRC return to abort before execution. Debug printing uses firmware-provided strings.

Test signals: compile the module, run known-good Jam/JBC firmware with expected action names, validate CRC mismatch behavior, fuzz table offsets/opcodes under sanitizers, test action selection failures, and confirm JTAG programming on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Kconfig

Purpose: declares configuration for AMD side-band RMI support over I2C/I3C and optional hwmon exposure.

Important APIs and symbols: `AMD_SBRMI_I2C` is a tristate depending on `I3C_OR_I2C` and ARM/ARM64/COMPILE_TEST. It selects `REGMAP_I2C` and conditionally `REGMAP_I3C`. `AMD_SBRMI_HWMON` is a bool depending on `AMD_SBRMI_I2C` and `HWMON`, with a guard against built-in driver plus modular hwmon.

Control flow: enabling `AMD_SBRMI_I2C` builds the transport and core as `sbrmi-i2c`. Enabling `AMD_SBRMI_HWMON` links in `rmi-hwmon.o` and causes probe to create hwmon power sensors.

State and persistence: configuration state persists only in the kernel build. Runtime state is in the corresponding driver objects.

Dependencies and integration points: integrates with BMC-side AMD APML management over I2C/I3C and with the hwmon subsystem for socket power telemetry and limit control.

Risks: the symbol name references I2C although the driver also registers an I3C driver. Users may assume it runs on the managed host, but help text correctly states it is intended for the BMC.

Test signals: Kconfig dependency checks for I2C-only, I3C-only, and hwmon combinations; module name verification; allmodconfig builds; and menu visibility on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Makefile

Purpose: defines the object composition for the AMD SB-RMI driver module.

Important APIs and entries: `sbrmi-i2c-objs` includes `rmi-i2c.o` and `rmi-core.o`. `sbrmi-i2c-$(CONFIG_AMD_SBRMI_HWMON)` adds `rmi-hwmon.o`. `obj-$(CONFIG_AMD_SBRMI_I2C)` builds the final `sbrmi-i2c.o` module or built-in object.

Control flow: kbuild always links the transport/probe layer with the ioctl/mailbox core, and optionally links hwmon callbacks when configured.

State and persistence: no runtime state. The build artifact shape determines whether `create_hwmon_sensor_device` is a real function or the inline stub from `rmi-core.h`.

Dependencies and integration points: tied to Kconfig symbols in the same directory and to exported symbols shared among the three C files.

Risks: naming remains `sbrmi-i2c` even when I3C support is active, which can obscure transport coverage in logs and module listings. Missing `rmi-hwmon.o` is expected when hwmon is off, so core callers must continue using the stub.

Test signals: build with hwmon enabled and disabled, verify no unresolved symbols, and inspect module contents for expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.c

Purpose: implements AMD SB-RMI/APML protocol operations and the userspace misc-device ioctl interface for mailbox, CPUID, MCA/MSR, and raw register transfers.

Important APIs and functions: `rmi_mailbox_xfer` is shared with hwmon. `create_misc_rmi_device` registers `/dev/sbrmi-<addr>`. Static ioctl helpers are `apml_mailbox_xfer`, `apml_cpuid_xfer`, `apml_mcamsr_xfer`, and `apml_rmi_reg_xfer`. CPUID/MSR helpers prepare protocol-specific bulk messages for revision 0x20 and extended revisions 0x21/0x31.

Control flow: ioctl dispatch copies a UAPI structure from userspace, runs the selected protocol under `data->lock`, and copies results back. Mailbox transfer writes command/data bytes to inbound registers, triggers firmware via software interrupt, polls `SBRMI_STATUS` for software alert, reads outbound data and firmware status, clears alert bits, and reports firmware errors as `-EPROTOTYPE` with `fw_ret_code`. CPUID and MCA/MSR transfers cache the RMI revision, write protocol payloads, poll hardware alert, bulk-read output, clear status, validate returned byte count/status, and update the input/output value.

State and persistence: `struct sbrmi_data` holds regmap, mutex, cached revision, max power limit, static address, and miscdevice metadata. Hardware mailbox state is transient; firmware-visible registers are cleared or overwritten per transfer.

Dependencies and integration points: depends on regmap, miscdevice, UAPI `amd-apml.h`, and transport setup from `rmi-i2c.c`. `rmi-hwmon.c` reuses mailbox commands for power telemetry.

Risks: this snapshot has missing braces after `if (ret < 0)` in CPUID error handling, causing `msg->cpu_in_out = 0` to run unconditionally. Raw register ioctl exposes arbitrary device register access to root-only misc users. Poll timeouts are fixed at two seconds and serialize all protocols through one mutex.

Test signals: ioctl ABI tests, firmware error-code propagation, timeout injection, revision 0x10/0x20/0x21/0x31 coverage, CPUID thread >127 handling, and hwmon mailbox concurrency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.h -->
# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.h

Purpose: defines shared AMD SB-RMI register constants, mailbox message ids, per-device state, and cross-file function declarations.

Important APIs and types: `enum sbrmi_reg` names revision, control, status, inbound/outbound message, software interrupt, and thread extension registers. `enum sbrmi_msg_id` defines package power read/write/max commands. `struct sbrmi_data` owns the miscdevice, regmap, mutex, cached max power limit, static address, and revision. It declares `rmi_mailbox_xfer`, `create_misc_rmi_device`, and conditional `create_hwmon_sensor_device`.

Control flow: transport probe initializes `struct sbrmi_data`, stores it as drvdata, then calls the declarations here to register hwmon and misc interfaces. Core and hwmon functions share the same mutex and regmap through this structure.

State and persistence: the header describes per-device runtime state but stores none itself. Cached revision and max power limit persist for the lifetime of the probed device.

Dependencies and integration points: depends on miscdevice, mutex, I2C/platform/regmap headers, and AMD APML UAPI structures. It is the coupling point for `rmi-core.c`, `rmi-hwmon.c`, and `rmi-i2c.c`.

Risks: register enum values rely on implicit increments matching the SB-RMI register map. The hwmon stub silently returns success when disabled, so probe behavior changes by config without logging. The include set is broader than needed for some consumers.

Test signals: compile with and without `CONFIG_AMD_SBRMI_HWMON`, static checks of enum addresses against APML documentation, and probe tests validating drvdata fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-hwmon.c

Purpose: exposes SB-RMI package power telemetry and power cap controls through the Linux hwmon subsystem.

Important APIs and functions: `create_hwmon_sensor_device` registers a hwmon device named `sbrmi`. `sbrmi_read` handles `hwmon_power_input`, `hwmon_power_cap`, and `hwmon_power_cap_max`. `sbrmi_write` handles `hwmon_power_cap`. `sbrmi_is_visible` defines read/write permissions.

Control flow: reads build an `apml_mbox_msg` for current package power or current power limit, or return cached `pwr_limit_max`. Values from firmware are in milliwatts and converted to microwatts for hwmon. Writes convert microwatts to milliwatts, clamp to `[0, pwr_limit_max]`, and send `SBRMI_WRITE_PKG_PWR_LIMIT` through `rmi_mailbox_xfer`.

State and persistence: no private state beyond the `sbrmi_data` pointer passed as drvdata. The maximum power limit is cached during transport probe. The configured cap persists in platform firmware/hardware according to SB-RMI behavior, not in this file.

Dependencies and integration points: depends on hwmon APIs, APML UAPI message structures, and the core mailbox transfer function. It is optionally linked by Kconfig.

Risks: clamping silently changes out-of-range writes rather than reporting an error. If `pwr_limit_max` cache is stale, writes can enforce an obsolete maximum. All mailbox failures propagate to hwmon callers, so sensor reads can block until the core timeout.

Test signals: hwmon sysfs reads/writes for `power1_input`, `power1_cap`, `power1_cap_max`, unit conversion checks, clamp behavior at negative and over-max values, and firmware error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-i2c.c

Purpose: provides the AMD SB-RMI transport probe/remove layer for I2C and I3C devices, creates regmaps, enables alerts, caches maximum power, and registers hwmon/misc interfaces.

Important APIs and functions: `sbrmi_common_probe` initializes shared state for both buses. `sbrmi_i2c_probe/remove` bind the I2C driver. `sbrmi_i3c_probe/remove` bind the I3C driver. `sbrmi_enable_alert` clears the control bit that masks software alerts, and `sbrmi_get_max_pwr_limit` initializes `pwr_limit_max`.

Control flow: I2C probe creates an 8-bit register regmap, reads `SBRMI_REV`, and switches to a 16-bit little-endian register-address regmap for revision 0x21 or newer to avoid bus corruption. I3C probe first filters devices by instance id, performs the same revision/regmap selection, and passes the dynamic address into common probe. Common probe allocates `sbrmi_data`, initializes the mutex, enables alerts, reads max power, stores drvdata, registers hwmon if enabled, then registers the misc device. Remove deregisters the misc device.

State and persistence: per-device state is devm-allocated and lasts until device removal. Regmap selection persists for the lifetime of the device. Firmware power-limit and alert state live in the managed AMD device.

Dependencies and integration points: depends on I2C, I3C, regmap, OF matching, the APML core in `rmi-core.c`, and optional hwmon creation.

Risks: common probe enables alerts and performs a mailbox command before misc registration, so probe fails if firmware is slow or unavailable. I2C remove nulls fields after deregistration but I3C remove does not. Address-width switching depends solely on revision read success.

Test signals: I2C and I3C probe/remove, revision 0x20 versus 0x21+ regmap behavior, I3C instance-id filtering, alert-enable register writes, max-power mailbox read, and devnode creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/apds9802als.c -->
# sources/distributed-fs/ceph-client/drivers/misc/apds9802als.c

Purpose: implements a simple I2C sysfs driver for the Avago APDS9802 ambient light sensor.

Important APIs and functions: probe/remove are `apds9802als_probe` and `apds9802als_remove`. Sysfs attributes under group `apds9802als` are `lux0_sensor_range` and `lux0_input`. Runtime/system PM uses `apds9802als_suspend` and `apds9802als_resume`. Helpers include `als_wait_for_data_ready`, `als_set_default_config`, and `als_set_power_state`.

Control flow: probe allocates `struct als_data`, stores it as I2C client data, creates the sysfs group, writes default power/range/manual-measurement configuration, initializes the mutex, and enables runtime PM. Reading `lux0_input` runtime-resumes the device, locks the mutex, clears EOC status, starts a measurement, waits up to ten 30 ms retries for data-ready, reads LSB/MSB result bytes, unlocks, and runtime-suspends. Range writes parse lux range and adjust register 0x81 bits under the same mutex.

State and persistence: software state is only a mutex. Sensor configuration persists in device registers while powered. No cached lux value is kept.

Dependencies and integration points: depends on I2C SMBus byte operations, sysfs, mutex, sleep, and runtime PM. It registers through `module_i2c_driver` with id `apds9802als`.

Risks: probe calls `als_set_default_config` before `mutex_init`, but that helper path itself does not take the mutex. `pm_runtime_get_sync` return values are ignored. I2C write failures during measurement setup are mostly unchecked. The module author string is missing a closing angle bracket.

Test signals: sysfs range/read tests, data-ready timeout path, suspend/resume and runtime PM cycles, I2C fault injection, and validation of first-measurement discard behavior after power-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/apds9802als.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/apds990x.c -->
# sources/distributed-fs/ceph-client/drivers/misc/apds990x.c

Purpose: implements an I2C driver for APDS990x combined ambient-light and proximity sensors, exposing calibration, thresholds, reporting mode, raw proximity, and power controls through sysfs.

Important APIs and functions: probe/remove are `apds990x_probe` and `apds990x_remove`; IRQ handling is `apds990x_irq`. Register helpers wrap command-bit SMBus byte/word accesses. Core algorithms include `apds990x_get_lux`, `apds990x_calc_again`, `apds990x_lux_to_threshold`, `apds990x_refresh_athres`, and `apds990x_refresh_pthres`. PM paths are system and runtime suspend/resume.

Control flow: probe requires platform data, loads optical factors or defaults, computes reverse threshold factors, initializes calibration/threshold/gain defaults, enables regulators, detects chip id/revision, configures integration/wait/persistence registers, starts ALS, creates sysfs files, and requests a threaded IRQ. The IRQ acknowledges ALS/proximity interrupts, reads clear/IR/proximity data, computes lux, adjusts gain, refreshes thresholds, wakes readers waiting for a fresh lux result, and notifies sysfs attributes. Sysfs stores adjust calibration, ALS rate, proximity enable count, reporting mode, thresholds, and runtime power state.

State and persistence: `struct apds990x_chip` caches platform data, regulators, wait queue, lux/proximity readings, gain state, calibration, thresholds, persistence, and chip identity. Hardware register configuration is rewritten after power-on/resume.

Dependencies and integration points: depends on I2C, threaded IRQs, regulators named `Vdd` and `Vled`, runtime PM, wait queues, and `linux/platform_data/apds990x.h`.

Risks: this snapshot contains duplicate/malformed-looking lines around `apds990x_force_a_refresh` and `apds990x_rate_store`, which are build risks if not source corruption. The driver requires platform data and has no OF/ACPI matching. Many register writes combine errors with bitwise OR or ignore return values. Sysfs proximity enable is a reference count without owner tracking.

Test signals: chip-id detection, IRQ-driven lux/proximity updates, sysfs polling/notify behavior, regulator and runtime PM cycles, gain adaptation under bright/dark conditions, threshold hysteresis, and fault injection for I2C and IRQ setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/apds990x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/atmel-ssc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/atmel-ssc.c

Purpose: implements the Atmel AT91 Synchronous Serial Controller platform driver and exports a small reservation API for other kernel users, especially audio.

Important APIs and functions: exported functions are `ssc_request(unsigned int ssc_num)` and `ssc_free(struct ssc_device *ssc)`. Platform lifecycle is `ssc_probe` and `ssc_remove`. Optional audio integration uses `ssc_sound_dai_probe` and `ssc_sound_dai_remove`. Device matching uses platform ids and OF compatibles for AT91RM9200, AT91SAM9RL, and AT91SAM9G45 variants.

Control flow: probe allocates `struct ssc_device`, selects platform data from OF or platform id, records optional `atmel,clk-from-rk-pin`, maps registers, gets `pclk`, disables all SSC interrupts under a prepared clock, obtains IRQ, adds the device to the global `ssc_list`, stores drvdata, and optionally registers the SSC for ASoC DAI use. `ssc_request` scans the list by OF alias or platform id, rejects missing or busy devices, increments a user count under `user_lock`, prepares the clock, and returns the device. `ssc_free` decrements the user count and unprepares the clock.

State and persistence: a global list and per-device `user` count serialize exclusive ownership. Register mappings, clock, IRQ, platform data, and audio flag persist for the platform-device lifetime.

Dependencies and integration points: depends on platform devices, OF aliases, clk, MMIO, `linux/atmel-ssc.h`, and optional Atmel ASoC SSC helpers.

Risks: only one user can reserve an SSC, so sharing must be coordinated externally. `clk_prepare` return value is ignored in `ssc_request`. Removal does not explicitly handle an active user beyond list deletion. OF alias lookup mutates `pdev->id`.

Test signals: DT and platform-id probe, request/free busy behavior, clock prepare/unprepare balancing, interrupt-disable register writes, audio DAI auto-setup, and removal while unused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/atmel-ssc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Kconfig

Purpose: declares configuration for the Broadcom VK accelerator PCI host driver and optional tty console support.

Important APIs and symbols: `BCM_VK` is a tristate depending on `PCI_MSI`. `BCM_VK_TTY` is a bool depending on `TTY` and `BCM_VK`, enabling tty ports named like `/dev/bcm-vk.x_ttyVKy`.

Control flow: selecting `BCM_VK` builds the PCI misc driver, message queue, and scatter-gather support. Selecting `BCM_VK_TTY` also builds tty support and enables IRQ allocation/structures for VK tty channels.

State and persistence: no runtime state. The selected config determines whether userspace sees only `/dev/bcm-vk.N` or also tty devices.

Dependencies and integration points: integrates with PCI MSI/MSI-X, miscdevice userspace access, optional tty core, and Broadcom VK accelerator firmware loading.

Risks: help text describes broad accelerator use cases but not firmware file requirements or auto-load behavior. `BCM_VK_TTY` is bool rather than tristate, so it follows the base driver's build mode.

Test signals: menu visibility, builds with and without tty, PCI probe on MSI-X-capable systems, and device-node creation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Makefile

Purpose: defines the object composition for the Broadcom VK accelerator driver.

Important APIs and entries: `obj-$(CONFIG_BCM_VK)` builds `bcm_vk.o`. The base object links `bcm_vk_dev.o`, `bcm_vk_msg.o`, and `bcm_vk_sg.o`. `bcm_vk-$(CONFIG_BCM_VK_TTY)` conditionally adds `bcm_vk_tty.o`.

Control flow: kbuild combines PCI lifecycle/firmware loading, message queues, scatter-gather DMA, and optional tty support into one module or built-in object.

State and persistence: no runtime state; build composition determines whether tty functions are real implementations or inline stubs from `bcm_vk.h`.

Dependencies and integration points: depends on Kconfig symbols in the same directory and on internal headers shared by device, message, scatter-gather, and tty code.

Risks: adding new driver subsystems requires updating the object list. Conditional tty linkage must stay synchronized with the stubs and IRQ count macros in `bcm_vk.h`.

Test signals: base-only and tty-enabled builds, link checks for internal symbols, and module load tests confirming expected device nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk.h -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk.h

Purpose: central internal header for the Broadcom VK PCI accelerator driver, defining register offsets, boot status bits, BAR layout, alert constants, device state, and cross-module functions.

Important APIs and types: register macros cover boot image pushing, firmware status, card telemetry, error logs, doorbells, BAR1 message-queue metadata, DMA/scratch addresses, authentication fields, and reset values. `struct bcm_vk` is the main per-device state with PCI device, BAR mappings, miscdevice, tty state, kref, message contexts, workqueues, DMA scratch area, panic notifier, heartbeat, alert state, peer log, and process monitor data. Inline helpers `vkread32`, `vkwrite32`, `vkread8`, and `vkwrite8` wrap MMIO access.

Control flow: `bcm_vk_dev.c` owns PCI lifecycle and firmware/reset ioctls; `bcm_vk_msg.c`, `bcm_vk_sg.c`, and optional `bcm_vk_tty.c` use the shared structures and prototypes to implement userspace messaging, DMA, and tty channels.

State and persistence: state is per PCI device and persists from probe until the last kref is released. Hardware state spans BAR registers, firmware boot phases, message queues, peer logs, and card telemetry.

Dependencies and integration points: depends on PCI, miscdevice, kref, poll, tty, firmware, UAPI `linux/misc/bcm_vk.h`, and internal `bcm_vk_msg.h`.

Risks: the header exposes a large shared mutable structure across modules, so locking discipline is distributed. Register offsets and masks are firmware ABI and must remain synchronized with card firmware. Optional tty stubs must match real function semantics.

Test signals: build all modules using this header, firmware ABI compatibility tests, BAR register smoke tests, message queue marker validation, and lockdep coverage for shared state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_dev.c -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_dev.c

Purpose: implements Broadcom VK PCI device lifecycle, firmware boot loading, reset handling, notification work, mmap/ioctl entry points, panic reset, and module parameters.

Important APIs and functions: PCI lifecycle is `bcm_vk_probe`, `bcm_vk_remove`, and `bcm_vk_shutdown`. Userspace file operations include `bcm_vk_ioctl` and `bcm_vk_mmap` plus message operations declared elsewhere. Firmware helpers are `bcm_vk_load_image_by_type`, `bcm_vk_auto_load_all_images`, `bcm_vk_load_image`, and `bcm_vk_next_boot_image`. Reset and access control use `bcm_vk_reset`, `bcm_vk_trigger_reset`, `bcm_vk_blk_drv_access`, and `bcm_vk_reset_successful`. Notifications use `bcm_vk_notf_irqhandler`, `bcm_vk_wq_handler`, and `bcm_vk_handle_notf`.

Control flow: probe allocates state, enables PCI, requests regions, configures 64-bit DMA, allocates scratch DMA, allocates MSI-X vectors, maps BAR0/1/2, registers IRQs, allocates a device id, registers `/dev/bcm-vk.N`, creates a workqueue, initializes message queues, syncs card info, registers panic notifier, optionally initializes tty, triggers asynchronous autoload from BROM state, and starts heartbeat. Firmware loading pushes BOOT1 through BAR1 ITCM after SRAM open and BOOT2 through DMA chunks after DDR open, then waits for firmware ready, checks interface version, syncs queues, and reads card info. Reset drains queues, sends shutdown, kills users, rings reset doorbells, and validates firmware reset status.

State and persistence: `struct bcm_vk` owns persistent PCI, BAR, IRQ, misc, workqueue, DMA, message, alert, heartbeat, and card-info state. Firmware images and reset choices change card hardware state across driver operations.

Dependencies and integration points: depends on PCI/MSI-X, DMA coherent allocation, firmware loader, miscdevice, panic notifier, Broadcom VK UAPI, internal message/SG/tty/heartbeat code, and firmware files such as `vk*-boot1.bin` and `vk*-boot2.bin`.

Risks: this snapshot contains a malformed-looking comma after `misc_device->fops = &bcm_vk_fops`, which is a build risk if not source corruption. Firmware loading and reset paths are highly stateful and rely on BAR status bits, fixed timeouts, and correct image names. `bcm_vk_blk_drv_access` sends SIGKILL to client processes. Mmap exposes BAR2 MMIO to userspace with bounds checks. Error unwind mixes devm IRQs, PCI vectors, and manual frees and needs careful regression testing.

Test signals: PCI probe/remove/unwind injection, MSI-X allocation variants, firmware autoload/manual load for BOOT1/BOOT2, reset in BROM/BOOT1/BOOT2/ramdump states, `/dev/bcm-vk.N` ioctl and mmap tests, panic notifier behavior, heartbeat/notification alerts, and concurrent userspace access during reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_dev.c -->
