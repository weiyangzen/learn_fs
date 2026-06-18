# subset-b-001080 TPM driver research

Grouped research for Linux TPM core, event log, ST33ZP24, Atmel, and CRB driver files under the Ceph client source tree. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/Kconfig

## Purpose
Defines the TPM driver configuration surface: the common TCG TPM core, TPM2 HMAC bus protection, hwrng exposure, TIS/FIFO transports, legacy vendor drivers, CRB, vTPM proxy, TEE fTPM, SVSM vTPM, and the ST33ZP24 subdirectory.

## Important APIs, Types, And Functions
Important symbols are `TCG_TPM`, `TCG_TPM2_HMAC`, `HW_RANDOM_TPM`, `TCG_TIS_CORE`, `TCG_TIS`, `TCG_TIS_SPI`, `TCG_TIS_I2C`, vendor I2C/PNP/platform options, `TCG_CRB`, `TCG_ARM_CRB_FFA`, `TCG_VTPM_PROXY`, `TCG_FTPM_TEE`, `TCG_SVSM`, and `TCG_LOONGSON`. The file uses Kconfig `depends on`, `select`, `imply`, and `source` to connect build options.

## Control Flow
Configuration starts at `menuconfig TCG_TPM`; all child choices are available only when TPM support is enabled. Transport-specific options select common core modules where needed, and optional interfaces gate source compilation through the Makefile.

## State And Persistence
The selected symbols persist in the kernel `.config` and determine compiled-in or module TPM support. They also control runtime availability of securityfs event logs, hwrng integration, encrypted TPM2 transactions, and bus-specific probe code.

## Dependencies And Integration Points
Integrates with ACPI, EFI, OF, I2C, SPI, PNP, XEN, TEE/OP-TEE, AMD memory encryption, MFD Loongson, Arm FF-A, crypto primitives, and securityfs. It sources `drivers/char/tpm/st33zp24/Kconfig` for STMicroelectronics support.

## Risks And Edge Cases
Wrong dependency relationships can expose unbuildable drivers or hide necessary transports. `TCG_TPM2_HMAC` pulls crypto dependencies and changes TPM2 transaction behavior. `HW_RANDOM_TPM` has a built-in/module compatibility constraint against impossible link combinations.

## Test Signals
Useful signals are `allyesconfig`/`allmodconfig` builds across ACPI, OF, I2C, SPI, X86, ARM64, Xen, TEE, and COMPILE_TEST targets, plus boot probes confirming expected `/dev/tpm*`, `/dev/tpmrm*`, securityfs logs, and hwrng behavior for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/Makefile

## Purpose
Builds the TPM core object and maps Kconfig symbols to TPM transport, vendor, virtual, and firmware-backed driver modules.

## Important APIs, Types, And Functions
The aggregate `tpm.o` includes `tpm-chip.o`, `tpm-dev-common.o`, `tpm-dev.o`, `tpm-interface.o`, `tpm1-cmd.o`, `tpm2-cmd.o`, `tpmrm-dev.o`, `tpm2-space.o`, `tpm-sysfs.o`, eventlog code, `tpm-buf.o`, and `tpm2-sessions.o`. Conditional additions include `tpm_ppi.o`, eventlog ACPI/EFI/OF readers, TIS, I2C/SPI variants, ST33ZP24, CRB/FF-A, vTPM, fTPM TEE, SVSM, and Loongson modules.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` lines to compile selected modules. The common `tpm.o` core is built when `CONFIG_TCG_TPM` is enabled; transport drivers then register `struct tpm_chip` instances through exported TPM core APIs.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is the object composition and module names exposed to kernel packaging and modprobe.

## Dependencies And Integration Points
It is tightly coupled to `Kconfig` symbols and the source layout in `drivers/char/tpm/`, including the `st33zp24/` subdirectory. The eventlog objects are conditionally folded into the common core depending on firmware interface support.

## Risks And Edge Cases
Missing object references can compile a feature without required helpers, while stale object names break module builds. Conditional eventlog inclusion must match the inline stubs in `eventlog/common.h`.

## Test Signals
Build TPM as built-in and as modules across ACPI, EFI, OF, I2C, SPI, CRB, and ST33ZP24 configs. Module load tests should confirm expected names such as `tpm`, `tpm_crb`, `tpm_st33zp24_i2c`, and `tpm_st33zp24_spi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/acpi.c

## Purpose
Reads the firmware TPM event log from ACPI TCPA or TPM2 tables and stores it in `chip->log` for securityfs export.

## Important APIs, Types, And Functions
Defines `struct acpi_tcpa`, `tpm_is_tpm2_log()`, `tpm_bios_log_free()`, and exported reader `tpm_read_log_acpi()`. It consumes `struct acpi_table_tpm2`, `struct acpi_tpm2_phy`, `struct tpm_bios_log`, `TCG_SPECID_SIG`, `EFI_TCG2_EVENT_LOG_FORMAT_TCG_1_2`, and `EFI_TCG2_EVENT_LOG_FORMAT_TCG_2`.

## Control Flow
The reader rejects chips without an ACPI device handle. TPM2 chips read the ACPI `TPM2` table and its physical log area fields; TPM1 chips read the `TCPA` table and select client/server length/address layout by platform class. It maps firmware memory, copies the log into kernel memory, verifies TPM2 logs have an EFI Spec ID event signature, registers a devm cleanup action, and returns the detected log format.

## State And Persistence
The copied log persists in `chip->log.bios_event_log` until device-managed cleanup or explicit failure cleanup. The ACPI table references are temporary and are released with `acpi_put_table()`.

## Dependencies And Integration Points
Called from `eventlog/common.c` before EFI and OF fallbacks. It depends on ACPI table discovery, ACPI I/O memory mapping, TPM chip flags, and TCG event-log structures from `linux/tpm_eventlog.h`.

## Risks And Edge Cases
ACPI does not bind event logs to a specific TPM, so multiple ACPI TPMs can expose the same log. Bad firmware lengths, zero addresses, unmappable memory, or TPM2 logs without the expected Spec ID event return errors so EFI can be tried. Pointer arithmetic over firmware-provided lengths is boundary-sensitive.

## Test Signals
Boot TPM1 and TPM2 ACPI systems with valid and missing TCPA/TPM2 tables, malformed zero-length log areas, invalid TPM2 Spec ID signatures, and securityfs reads of `binary_bios_measurements`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.c

## Purpose
Coordinates firmware event-log discovery and exposes TPM measurement logs through securityfs seq_files.

## Important APIs, Types, And Functions
Key functions are `tpm_bios_measurements_open()`, `tpm_bios_measurements_release()`, `tpm_read_log()`, `tpm_bios_log_setup()`, and `tpm_bios_log_teardown()`. It uses `struct tpm_chip_seqops`, `struct tpm_chip`, `securityfs_create_dir()`, `securityfs_create_file()`, and TPM1/TPM2 seq operation tables.

## Control Flow
Open locks the inode, rejects removed dentries, grabs the chip device reference, opens the configured seq iterator, and stores the chip in `seq->private`. Setup skips virtual chips, tries ACPI then EFI then OF readers, creates a securityfs directory named after the TPM device, selects TPM2 binary or TPM1 binary/ascii seqops, and creates the exported measurement files. Any creation failure tears down the directory.

## State And Persistence
Securityfs dentries persist while the chip is registered. Per-open device references keep the chip alive during seq_file reads. `chip->bin_log_seqops`, `chip->ascii_log_seqops`, and `chip->bios_dir` hold the runtime export state.

## Dependencies And Integration Points
Called by `tpm_chip_register()` and `tpm_chip_unregister()`. It integrates firmware log readers from `common.h`, securityfs, seq_file, and TPM event parser files `tpm1.c` and `tpm2.c`.

## Risks And Edge Cases
The inode link check avoids opening removed files, but lifetime correctness still depends on paired `get_device()`/`put_device()`. Securityfs may be disabled and return `-ENODEV`; setup intentionally treats missing logs as nonfatal. TPM2 gets no ascii export here.

## Test Signals
Register/unregister chips while reading securityfs files, boot with securityfs disabled, exercise ACPI/EFI/OF fallback ordering, verify TPM1 exposes both binary and ascii files, and verify TPM2 exposes only binary output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.h

## Purpose
Declares event-log seq operation exports and firmware reader entry points, with configuration-dependent stubs for disabled firmware interfaces.

## Important APIs, Types, And Functions
Exports `tpm1_ascii_b_measurements_seqops`, `tpm1_binary_b_measurements_seqops`, `tpm2_binary_b_measurements_seqops`, and reader functions `tpm_read_log_acpi()`, `tpm_read_log_of()`, and `tpm_read_log_efi()`.

## Control Flow
When `CONFIG_ACPI`, `CONFIG_OF`, or `CONFIG_EFI` is disabled, inline stubs return `-ENODEV`, allowing `common.c` to continue fallback probing without conditional call-site logic.

## State And Persistence
The header has no runtime state. It defines the compile-time contract between the common event-log setup and backend readers/parsers.

## Dependencies And Integration Points
Includes `../tpm.h`, is included by ACPI/EFI/OF readers and TPM1/TPM2 seq parser implementations, and mirrors Makefile conditional object inclusion.

## Risks And Edge Cases
Stub return values are part of fallback semantics; changing them would alter probing. Prototype drift between enabled readers and stubs would cause build or link failures across config combinations.

## Test Signals
Compile TPM event-log support with ACPI, EFI, and OF independently enabled or disabled. Runtime fallback should skip missing backends cleanly and still expose logs when another backend succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/efi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/efi.c

## Purpose
Reads TPM2 event logs from EFI configuration tables, including optional final-events log append data.

## Important APIs, Types, And Functions
The exported function is `tpm_read_log_efi()`. It uses global EFI table addresses `efi.tpm_log` and `efi.tpm_final_log`, `efi_tpm_final_log_size`, `struct linux_efi_tpm_eventlog`, `struct efi_tcg2_final_events_table`, `devm_kmemdup()`, and `devm_krealloc()`.

## Control Flow
The reader only handles TPM2 chips and rejects invalid EFI TPM log table addresses. It maps the fixed log header to obtain size, remaps the full payload, copies the main log into devm memory, and records its version. If a valid TPM2 final-events table exists, it maps that table, subtracts the portion already present in the preboot log, grows the log buffer, appends the remaining final events, and updates the end pointer.

## State And Persistence
The combined log persists as device-managed memory in `chip->log`. EFI table mappings are temporary and are unmapped before return. On allocation failure, copied log memory is freed and the reader returns an error.

## Dependencies And Integration Points
Used as the second backend in `tpm_read_log()` after ACPI fallback. It depends on EFI boot services handoff tables populated by architecture EFI code and on TPM2 event-log format constants.

## Risks And Edge Cases
Final-events size arithmetic is sensitive because the global final size excludes the preboot prefix after adjustment. Empty logs are errors. Partial allocation failure must avoid leaving stale `chip->log` pointers. The backend intentionally rejects TPM1.

## Test Signals
Boot EFI TPM2 systems with only the main log, with final-events data, with invalid table addresses, and with zero-sized logs. Compare securityfs binary output length against main plus final-events expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/of.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/of.c

## Purpose
Reads TPM firmware event logs described by Open Firmware/device-tree properties or reserved memory regions.

## Important APIs, Types, And Functions
Key functions are `tpm_read_log_memory_region()` and `tpm_read_log_of()`. It uses `of_reserved_mem_region_to_resource()`, `devm_memremap()`, `of_get_property()`, `of_property_match_string()`, `of_property_read_bool()`, `devm_kmemdup()`, and `__va()`.

## Control Flow
The reader obtains the parent OF node, records `powered-while-suspended` as `TPM_CHIP_FLAG_ALWAYS_POWERED`, and then looks for `linux,sml-size` and `linux,sml-base`. If both are absent, it maps the first reserved-memory region. If exactly one is present, it fails. Physical TPM properties are converted from big endian, while IBM virtual TPM compatibles are treated as already little endian. Nonzero logs are copied or remapped and the format is returned from the TPM version flag.

## State And Persistence
The log pointer and end pointer persist in `chip->log` as devm allocations or mappings. `TPM_CHIP_FLAG_ALWAYS_POWERED` persists on the chip after OF probing and affects suspend logic.

## Dependencies And Integration Points
Used as the final event-log backend. It integrates with PowerPC and OF firmware conventions, reserved memory, TPM virtual-device bindings, and the core TPM suspend path.

## Risks And Edge Cases
Endian handling differs for IBM vTPM versus physical TPM nodes. `__va(base)` assumes the firmware-described log is directly mapped. Mixed presence of size/base is treated as firmware error. Reserved-memory mapping exposes firmware memory directly rather than copying it.

## Test Signals
Exercise IBM physical and virtual TPM device trees, reserved-memory-only descriptions, missing or partial `linux,sml-*` properties, zero-size logs, and suspend behavior when `powered-while-suspended` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm1.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm1.c

## Purpose
Parses TPM 1.1/1.2 BIOS event logs and exposes both binary and human-readable securityfs seq_file views.

## Important APIs, Types, And Functions
Defines TPM1 seq callbacks `tpm1_bios_measurements_start()`, `tpm1_bios_measurements_next()`, `tpm1_bios_measurements_stop()`, `tpm1_binary_bios_measurements_show()`, `tpm1_ascii_bios_measurements_show()`, and helper `get_event_name()`. Exports `tpm1_ascii_b_measurements_seqops` and `tpm1_binary_b_measurements_seqops`.

## Control Flow
The iterator walks variable-sized `struct tcpa_event` records by repeatedly validating header fit, endian-converted event size/type, terminator records, and end-of-log bounds. Binary output emits a temporary header with endian-normalized numeric fields, followed by original event payload bytes. ASCII output prints PCR index, SHA1 digest, event type, and a decoded event-name string for known TCPA/PC event IDs.

## State And Persistence
No parser state persists beyond the seq_file position. The parser reads immutable `chip->log` memory and allocates a temporary event-name buffer per ascii record.

## Dependencies And Integration Points
Used by `eventlog/common.c` for TPM1 securityfs files. It depends on TCPA event definitions, `do_endian_conversion()`, `MAX_TEXT_EVENT`, seq_file, and TPM event type constants.

## Risks And Edge Cases
Firmware logs are untrusted; every record length must be bounded before dereference. The ascii decoder only recognizes selected event IDs and truncates free-form separator/action strings to `MAX_TEXT_EVENT`. Binary output intentionally normalizes header endianness, which differs from a raw memory dump.

## Test Signals
Read logs with valid records, terminators, truncated headers, oversized event payloads, unknown event types, `EVENT_TAG` records with hash payloads, and long text events. Compare ascii and binary seq iteration counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm2.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm2.c

## Purpose
Parses TPM 2.0 crypto-agile event logs for binary securityfs export.

## Important APIs, Types, And Functions
Key functions are `calc_tpm2_event_size()`, `tpm2_bios_measurements_start()`, `tpm2_bios_measurements_next()`, `tpm2_bios_measurements_stop()`, and `tpm2_binary_bios_measurements_show()`. It exports `tpm2_binary_b_measurements_seqops` and delegates record sizing to `__calc_tpm2_event_size()`.

## Control Flow
Position zero returns `SEQ_START_TOKEN` for the initial Spec ID event when it fits and is not an empty terminator. Later positions skip the first event header and walk agile `struct tcg_pcr_event2_head` entries by computing each event size against the first header. Show writes either the initial event header block or the current agile event block directly to the seq_file.

## State And Persistence
Parser state is derived from `*pos` and `chip->log` on each seq callback. No data is modified or persisted by this file.

## Dependencies And Integration Points
Used by `eventlog/common.c` when the reader reports `EFI_TCG2_EVENT_LOG_FORMAT_TCG_2`. It depends on TPM2 event-log helpers from `linux/tpm_eventlog.h` and on firmware logs beginning with a valid Spec ID event.

## Risks And Edge Cases
The iterator uses strict boundary checks and treats zero-size or past-end events as end of sequence. Off-by-one choices around `>= limit` can suppress exactly-ending entries, so event-size helper behavior matters. No ascii TPM2 view is provided.

## Test Signals
Use TPM2 logs with multiple digest banks, final-events appended records, truncated agile records, invalid digest counts, empty terminators, and exact-end boundary cases. Validate securityfs binary output can be parsed by userspace event-log tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/tpm2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Kconfig

## Purpose
Defines configuration symbols for the STMicroelectronics ST33ZP24 TPM 1.2 core and its I2C and SPI physical bus drivers.

## Important APIs, Types, And Functions
Symbols are `TCG_TIS_ST33ZP24`, `TCG_TIS_ST33ZP24_I2C`, and `TCG_TIS_ST33ZP24_SPI`. The bus options depend on `I2C` or `SPI` and select the common core symbol.

## Control Flow
Selecting either bus transport pulls in the shared ST33ZP24 core. Kbuild then builds the common `tpm_st33zp24` object and the chosen physical transport module.

## State And Persistence
The selected Kconfig symbols persist in `.config` and decide whether the ST33ZP24 platform can probe via I2C, SPI, or both.

## Dependencies And Integration Points
This sub-Kconfig is sourced from the main TPM Kconfig and integrates with the ST33ZP24 Makefile, Linux I2C/SPI device matching, ACPI IDs, and OF compatibles.

## Risks And Edge Cases
The core is hidden and only selected by transports, so direct user selection is avoided. Dependency mistakes could build a bus driver without its bus framework or omit the shared core.

## Test Signals
Build configurations for I2C-only, SPI-only, both transports, and module versus built-in variants. Runtime probe tests should bind `st33zp24-i2c` and `st33zp24-spi` devices and register TPM chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Makefile

## Purpose
Maps ST33ZP24 Kconfig symbols to the common TPM 1.2 core and I2C/SPI transport module objects.

## Important APIs, Types, And Functions
Build variables are `tpm_st33zp24-objs = st33zp24.o`, `tpm_st33zp24_i2c-objs = i2c.o`, and `tpm_st33zp24_spi-objs = spi.o`, with `obj-$(CONFIG_TCG_TIS_ST33ZP24*)` selecting each module.

## Control Flow
Kbuild compiles the shared core when the hidden core symbol is selected and compiles each physical-layer wrapper when the corresponding transport option is enabled.

## State And Persistence
There is no runtime state. The persistent build effect is module composition and module naming.

## Dependencies And Integration Points
Coupled to `st33zp24/Kconfig` and to exported symbols from `st33zp24.c` consumed by `i2c.c` and `spi.c`.

## Risks And Edge Cases
If the common core module is not selected with a bus wrapper, bus probe code will fail to link. Module names must stay consistent with Kconfig help text and udev/modprobe expectations.

## Test Signals
Build module and built-in variants for `TCG_TIS_ST33ZP24_I2C` and `TCG_TIS_ST33ZP24_SPI`, and verify symbol exports resolve between core and transport objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/i2c.c

## Purpose
Implements the I2C physical transport for ST33ZP24 TPM 1.2 devices and delegates TPM protocol handling to the shared ST33ZP24 core.

## Important APIs, Types, And Functions
Defines `struct st33zp24_i2c_phy`, low-level helpers `write8_reg()` and `read8_reg()`, transport callbacks `st33zp24_i2c_send()` and `st33zp24_i2c_recv()`, and driver callbacks `st33zp24_i2c_probe()` and `st33zp24_i2c_remove()`. It registers I2C IDs, OF compatible `st,st33zp24-i2c`, ACPI ID `SMO3324`, and PM ops using `st33zp24_pm_suspend()`/`resume()`.

## Control Flow
Probe verifies adapter I2C capability, allocates a per-device physical context, stores the `i2c_client`, and calls `st33zp24_probe()` with the I2C send/receive callbacks and IRQ. Writes prepend the TPM register byte; reads first write a dummy byte to select the register and then receive the requested payload.

## State And Persistence
The per-device I2C context persists as devm memory and includes a scratch buffer sized for the ST33ZP24 FIFO plus address byte. The actual TPM chip state is owned by the shared core.

## Dependencies And Integration Points
Integrates Linux I2C, OF, ACPI, TPM core, and `st33zp24.h`. `i2c_set_clientdata()` is indirectly handled through `tpmm_chip_alloc()` setting driver data on the parent device.

## Risks And Edge Cases
The read path expects `write8_reg()` to return exactly two bytes for the register-select transaction before receiving data. Buffer sizing assumes `tpm_size <= ST33ZP24_BUFSIZE`. Transport errors propagate to the core timing and locality logic.

## Test Signals
Probe with capable and incapable I2C adapters, read/write TPM registers under fault injection, interrupt and polling modes through the shared core, ACPI/OF matching, suspend/resume, and oversized transaction rejection by upper layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/spi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/spi.c

## Purpose
Implements the SPI physical transport for ST33ZP24 TPM 1.2 devices, including ST-specific status-byte handling and latency detection.

## Important APIs, Types, And Functions
Defines `struct st33zp24_spi_phy`, `st33zp24_status_to_errno()`, `st33zp24_spi_send()`, `st33zp24_spi_read8_reg()`, `st33zp24_spi_recv()`, `st33zp24_spi_evaluate_latency()`, `st33zp24_spi_probe()`, and `st33zp24_spi_remove()`. Registers SPI IDs, OF compatible `st,st33zp24-spi`, ACPI ID `SMO3324`, and PM ops from the common core.

## Control Flow
Probe allocates the SPI physical context, measures required latency by reading `TPM_INTF_CAPABILITY` with increasing dummy-byte counts, then calls `st33zp24_probe()`. Send constructs a pre-header with write direction and locality, optionally inserts FIFO length, appends payload, clocks latency bytes, and decodes the final status byte. Receive constructs a read pre-header, clocks latency plus payload bytes, checks the pre-payload status, and returns the requested byte count on success.

## State And Persistence
The SPI context persists in devm memory and holds large transmit/receive scratch buffers plus the detected latency. The latency value affects every later transaction.

## Dependencies And Integration Points
Integrates with the Linux SPI core, ACPI/OF matching, and shared ST33ZP24 TPM core through `struct st33zp24_phy_ops`.

## Risks And Edge Cases
Latency detection failure prevents probe. ST status codes map to protocol, size, unsupported, or raw errors; an unmapped status is returned directly. FIFO length insertion happens only for `TPM_DATA_FIFO`, so register framing must match hardware expectations.

## Test Signals
SPI transfer tests with varying latency, status-code fault injection, FIFO command/response paths, ACPI/OF matching, suspend/resume, and boundary tests around `ST33ZP24_SPI_BUFFER_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/st33zp24.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/st33zp24.c

## Purpose
Provides the shared ST33ZP24 TPM 1.2 core used by both I2C and SPI transports, implementing TIS-like locality, FIFO send/receive, IRQ/poll waiting, power management, and TPM chip registration.

## Important APIs, Types, And Functions
Important functions include `clear_interruption()`, `st33zp24_cancel()`, `st33zp24_status()`, `check_locality()`, `request_locality()`, `release_locality()`, `get_burstcount()`, `wait_for_stat()`, `recv_data()`, `tpm_ioserirq_handler()`, `st33zp24_send()`, `st33zp24_recv()`, `st33zp24_probe()`, `st33zp24_remove()`, `st33zp24_pm_suspend()`, and `st33zp24_pm_resume()`. The core registers `struct tpm_class_ops st33zp24_tpm`.

## Control Flow
Probe allocates a TPM chip and private device, sets default TIS timeouts, maps optional ACPI GPIOs, obtains optional `lpcpd` power GPIO, configures IRQs if present, enables selected interrupt sources, and registers the chip. Send requests locality 0, forces command-ready if needed, writes all but the final command byte in burst-sized chunks, verifies `DATA_EXPECT`, writes the final byte, clears `DATA_EXPECT`, writes `GO`, and optionally waits for data availability by ordinal duration. Receive reads the response header, validates the expected length, reads the remaining bytes, then cancels and releases locality.

## State And Persistence
`struct st33zp24_dev` persists as chip driver data and holds the physical callback pointer, locality, IRQ number, interrupt counter, optional GPIO, and wait queue. Locality and interrupt enablement persist while the chip is registered. Suspend may drive `lpcpd` low instead of sending TPM suspend commands.

## Dependencies And Integration Points
Bus-specific transports provide `send` and `recv` register callbacks. The file integrates TPM core registration, TPM1 self-test/resume, generic TPM suspend/resume, ACPI GPIO mapping, Linux IRQs, wait queues, and GPIO descriptor APIs.

## Risks And Edge Cases
The send path must release locality on all error exits. IRQ waits rely on interrupt counter changes and disabled/enabled IRQ ordering; polling fallback uses status reads. Burstcount and response-size parsing are protocol-critical. PM behavior differs depending on optional `lpcpd` GPIO presence.

## Test Signals
Exercise command send/receive over I2C and SPI, locality acquisition timeout, burstcount zero timeout, IRQ and polling modes, command cancellation, malformed response lengths, suspend/resume with and without `lpcpd`, and TPM1 self-test after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/st33zp24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/st33zp24.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/st33zp24.h

## Purpose
Defines the shared ST33ZP24 bus/core interface, device-private state, constants, and exported core entry points used by I2C and SPI physical drivers.

## Important APIs, Types, And Functions
Defines names `TPM_ST33_I2C`, `TPM_ST33_SPI`, `TPM_WRITE_DIRECTION`, `ST33ZP24_BUFSIZE`, `struct st33zp24_dev`, `struct st33zp24_phy_ops`, PM prototypes, `st33zp24_probe()`, and `st33zp24_remove()`.

## Control Flow
Physical drivers allocate a bus-specific context and pass it with callback operations to `st33zp24_probe()`. The shared core calls `ops->send()` and `ops->recv()` for register-level access.

## State And Persistence
`struct st33zp24_dev` persists per chip and stores the TPM chip pointer, physical context pointer, callback table, locality, IRQ state, optional GPIO, and wait queue.

## Dependencies And Integration Points
Used by `i2c.c`, `spi.c`, and `st33zp24.c`. It depends on TPM core types, wait queues, and GPIO descriptor definitions included through source files.

## Risks And Edge Cases
Callback semantics must remain consistent across transports: return values are interpreted by the core as byte counts or negative errors. `ST33ZP24_BUFSIZE` bounds physical buffers and TPM command sizing assumptions.

## Test Signals
Compile each physical transport against the header, verify symbol exports, and run register callback fault tests to ensure the shared core handles transport return values consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/st33zp24.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-buf.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-buf.c

## Purpose
Provides helper routines for constructing and parsing page-sized TPM command buffers and TPM2B sized buffers.

## Important APIs, Types, And Functions
Exports `tpm_buf_init()`, `tpm_buf_reset()`, `tpm_buf_init_sized()`, `tpm_buf_reset_sized()`, `tpm_buf_destroy()`, `tpm_buf_length()`, `tpm_buf_append()`, scalar append helpers, `tpm_buf_append_handle()`, and scalar read helpers `tpm_buf_read_u8/u16/u32()`.

## Control Flow
Initialization allocates one page and writes the TPM header or a TPM2B size prefix. Append checks for prior overflow, bounds writes to `PAGE_SIZE`, copies data, advances the length, and updates either the command header length or TPM2B length. Read helpers advance a caller-supplied offset and set a boundary-error flag if the requested range exceeds the buffer length.

## State And Persistence
Each `struct tpm_buf` owns a page until `tpm_buf_destroy()`. Buffer flags record overflow or boundary errors, length tracks valid bytes, and `handles` counts command handles for TPM2 session construction.

## Dependencies And Integration Points
Used throughout TPM1, TPM2, TPM2 sessions, and TPM2 resource-manager code. It depends on big-endian TPM wire formats and exported Linux TPM command structures.

## Risks And Edge Cases
Append overflow is sticky and silent after the first warning, so callers must avoid continuing with malformed commands. Read boundary failures return zero values and set a flag, which can hide parsing errors if callers do not validate final status. `tpm_buf_append_handle()` rejects TPM2B buffers only by logging.

## Test Signals
Unit-style tests for append length updates, overflow behavior at `PAGE_SIZE`, TPM2B size updates, endian scalar writes/reads, handle counting, and parser behavior when offsets cross buffer boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-chip.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-chip.c

## Purpose
Owns TPM chip allocation, lifecycle, device numbers, class devices, locality/ops locking, bootstrap, hwrng registration, event-log setup, and char-device registration.

## Important APIs, Types, And Functions
Exports `tpm_chip_start()`, `tpm_chip_stop()`, `tpm_try_get_ops()`, `tpm_put_ops()`, `tpm_default_chip()`, `tpm_chip_alloc()`, `tpmm_chip_alloc()`, `tpm_chip_bootstrap()`, `tpm_chip_register()`, and `tpm_chip_unregister()`. It defines `tpm_class`, `tpmrm_class`, `tpm_devt`, `dev_nums_idr`, and helper flows for hwrng and legacy sysfs links.

## Control Flow
Allocation assigns an IDR device number, initializes the class device and cdev, allocates TPM2 workspace buffers, and sets locality invalid. `tpm_try_get_ops()` takes a device reference, read-locks `ops_sem`, locks `tpm_mutex`, refuses suspended/disabled chips, starts locality/clock/cmd-ready, and returns with the chip ready for I/O. Registration bootstraps the chip, attaches sysfs groups, firmware logs, PPI, hwrng, primary and resource-manager char devices, then publishes the chip in the IDR.

## State And Persistence
Persistent chip state includes device number, class devices, ops pointer, flags, locality, TPM2 work space, hwrng registration, event-log dentries, sysfs groups, and IDR publication. Shutdown/unregister set `chip->ops = NULL` under write lock to block future operations.

## Dependencies And Integration Points
Central integration point for all transport drivers. It calls TPM1/TPM2 startup, PCR allocation, TPM2 shutdown, TPM2 auth-session teardown, eventlog, PPI, sysfs, hwrng, char devices, and resource-manager helpers.

## Risks And Edge Cases
Ops locking and device references are lifetime-critical during unregister. Shutdown may be called twice and guards against null ops. Hwrng must stay disabled for firmware-upgrade chips and AMD CRB quirked devices. Legacy sysfs symlink cleanup must match additions.

## Test Signals
Probe/remove stress, open file descriptors during unregister, suspend/resume races, TPM2 shutdown on reboot, default chip lookup, hwrng registration failures, firmware-upgrade mode, and resource-manager device creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev-common.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev-common.c

## Purpose
Implements the shared file operations behind `/dev/tpm*` and `/dev/tpmrm*`: command write, response read, polling, asynchronous nonblocking execution, timeouts, and TPM2 space preparation/commit.

## Important APIs, Types, And Functions
Key functions are `tpm_dev_transmit()`, `tpm_dev_async_work()`, `user_reader_timeout()`, `tpm_timeout_work()`, `tpm_common_open()`, `tpm_common_read()`, `tpm_common_write()`, `tpm_common_poll()`, `tpm_common_release()`, `tpm_dev_common_init()`, and `tpm_dev_common_exit()`. It uses `struct file_priv`, `tpm_dev_wq`, timers, workqueues, wait queues, and TPM2 space helpers.

## Control Flow
Write validates command size and embedded TPM length, ensures previous response was consumed or timed out, copies user data, and either queues async work for nonblocking files or synchronously takes chip ops and transmits. `tpm_dev_transmit()` ends any active TPM2 auth session, prepares the resource-manager space, transmits, commits or flushes the space, and synthesizes a TPM2 command-code response for unsupported commands. Read returns pending response bytes, zeroes consumed data, updates offsets, and clears the user-read timer when done.

## State And Persistence
Per-open `file_priv` persists the chip, optional TPM2 space, buffer, response length, read state, command-enqueued flag, timer, work items, and wait queue. Async results persist until userspace reads them or the 120-second timer clears the buffer.

## Dependencies And Integration Points
Used by `tpm-dev.c` and TPM resource-manager fops. It integrates `tpm_try_get_ops()`, `tpm_transmit()`, TPM2 space virtualization, Linux usercopy, poll, timers, and workqueues.

## Risks And Edge Cases
The write/read state machine must prevent overlapping commands and stale responses. Nonblocking errors are reported on the subsequent read. The timeout path is deprecated but still mutates response state. TPM2 space errors must flush loaded handles to avoid leaks.

## Test Signals
Blocking and nonblocking command tests, partial reads, write while response pending, user-read timeout, invalid embedded lengths, oversize writes, unsupported TPM2 command synthesis, resource-manager handle virtualization, and unregister while file descriptors are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.c

## Purpose
Provides the exclusive raw TPM character-device file operations for `/dev/tpmN`.

## Important APIs, Types, And Functions
Defines `tpm_open()`, `tpm_release()`, and exported `tpm_fops`. It uses `struct file_priv`, `container_of(inode->i_cdev, struct tpm_chip, cdev)`, `test_and_set_bit()` on `chip->is_open`, and shared common file helpers.

## Control Flow
Open resolves the chip from the inode cdev and atomically enforces a single opener for the raw TPM device. It allocates per-file state and calls `tpm_common_open()` with no TPM2 resource-manager space. Release calls `tpm_common_release()`, clears `chip->is_open`, and frees the per-file state.

## State And Persistence
The raw-device open bit persists while one file descriptor owns the device. Per-open command/response state is stored in `struct file_priv` until release.

## Dependencies And Integration Points
Registered by `tpm-chip.c` through `cdev_init()`. It delegates read, write, poll, and release mechanics to `tpm-dev-common.c`.

## Risks And Edge Cases
Exclusive open is raw-device-specific; `/dev/tpmrm*` can support isolated spaces separately. Allocation failure must clear the open bit. Release assumes `file->private_data` was initialized by open.

## Test Signals
Open contention should return `-EBUSY`, allocation-failure injection should leave the device reopenable, and raw command traffic should bypass TPM2 space virtualization while still using common transmit logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.h

## Purpose
Declares shared TPM character-device per-file state and common file operation helpers.

## Important APIs, Types, And Functions
Defines `struct file_priv` with chip pointer, optional `struct tpm_space`, buffer mutex, user-read timer, timeout and async work, wait queue, response length, response flags, command-enqueued flag, and `data_buffer[TPM_BUFSIZE]`. Declares `tpm_common_open/read/write/poll/release()`.

## Control Flow
The structure supports both raw and resource-manager devices: open initializes it, write fills `data_buffer`, async or sync transmit updates response state, read drains response bytes, and release flushes outstanding work/timers.

## State And Persistence
State persists per file descriptor and is guarded by `buffer_mutex`. The optional `space` pointer selects whether TPM2 commands are virtualized.

## Dependencies And Integration Points
Included by `tpm-dev.c`, `tpm-dev-common.c`, and the TPM resource-manager device implementation. It depends on TPM core types, poll types, mutexes, timers, workqueues, and wait queues through included headers.

## Risks And Edge Cases
All fields participate in concurrency behavior; missing mutex coverage can race reads, writes, async completion, and timeout cleanup. The fixed `TPM_BUFSIZE` buffer bounds user command and response sizes.

## Test Signals
Compile raw and resource-manager file operations, run concurrent poll/read/write tests, and validate buffer-state transitions under async completion and timeout cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-interface.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-interface.c

## Purpose
Implements the generic TPM command transport wrapper and public in-kernel TPM APIs for command transmit, PCR operations, RNG, startup, suspend/resume, and module initialization.

## Important APIs, Types, And Functions
Exports `tpm_calc_ordinal_duration()`, `tpm_transmit()`, `tpm_transmit_cmd()`, `tpm_get_timeouts()`, `tpm_is_tpm2()`, `tpm_pcr_read()`, `tpm_pcr_extend()`, `tpm_pm_suspend()`, `tpm_pm_resume()`, and `tpm_get_random()`. Internal helpers include `tpm_try_transmit()`, `tpm_chip_cancel()`, `tpm_chip_status()`, and module init/exit for classes, char-device region, and common dev workqueue.

## Control Flow
`tpm_try_transmit()` validates the command header length, sends through chip ops, handles synchronous devices or waits for IRQ/poll completion, receives the response, and validates response length. `tpm_transmit()` wraps this with TPM2 retry/testing backoff and restores the original header/handles before retries. Public APIs acquire ops, dispatch to TPM1 or TPM2 implementations, and release ops. Suspend sends TPM2 shutdown-state or TPM1 savestate unless the chip is always powered or firmware-managed.

## State And Persistence
Module initialization registers TPM classes and char-device numbers. Runtime state changes include suspended flags, TPM2 auth-session teardown, retry buffers, PCR/RNG command buffers, and module parameter `suspend_pcr`.

## Dependencies And Integration Points
Central path for transport `struct tpm_class_ops`, TPM1/TPM2 command files, chip lifecycle locking, PM core, hwrng, userspace char devices, and in-kernel consumers of PCR/RNG APIs.

## Risks And Edge Cases
Command length validation protects against malformed buffers. Retry loops must preserve transformed handles for TPM2 spaces. Poll completion must detect cancellation and timeout. Suspend intentionally ignores errors after logging to avoid blocking system sleep.

## Test Signals
Malformed command headers, synchronous and asynchronous transport paths, IRQ and polling completion, TPM2 `RC_RETRY` and `RC_TESTING`, PCR read/extend across banks, RNG size validation, suspend/resume on TPM1 and TPM2, and module init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-sysfs.c

## Purpose
Builds TPM sysfs attributes for legacy TPM1 state, TPM version reporting, optional TPM2 HMAC null-key name exposure, and PCR bank value directories.

## Important APIs, Types, And Functions
Defines show/store handlers for `pubek`, `pcrs`, `enabled`, `active`, `owned`, `temp_deactivated`, `caps`, `cancel`, `durations`, `timeouts`, `tpm_version_major`, and optional `null_name`. It builds PCR attribute groups with macros `PCR_ATTR_BUILD()` for SHA1, SHA256, SHA384, SHA512, and SM3, and exports `tpm_sysfs_add_device()`.

## Control Flow
TPM1 attributes issue TPM1 commands under `tpm_try_get_ops()` to read PUBEK, PCRs, capability flags, version, and state. PCR bank files call generic `tpm_pcr_read()` using the bank algorithm and PCR number encoded in the attribute. `tpm_sysfs_add_device()` attaches either TPM1 or TPM2 base group and then one PCR group per allocated bank.

## State And Persistence
Attribute groups persist on the class device while the chip is registered. PCR values are read live on each file read. The optional `null_name` exposes the TPM2 NULL primary name saved during HMAC session initialization.

## Dependencies And Integration Points
Called during `tpm_chip_register()` after PCR allocation. Integrates TPM1 command helpers, generic PCR APIs, TPM2 HMAC initialization state, sysfs attribute groups, and legacy sysfs symlinks created by `tpm-chip.c`.

## Risks And Edge Cases
TPM1 sysfs handlers return zero-length output on command failure, preserving older behavior but hiding errors. PCR group macros assume 24 platform PCRs and fixed supported hash algorithms. Adding a new TPM hash requires a macro group and switch case.

## Test Signals
Read each TPM1 sysfs file on enabled, disabled, and deactivated TPMs; read TPM2 PCR bank directories for every allocated bank; validate unsupported bank logging; check `cancel` store behavior; and verify `null_name` appears only with TPM2 HMAC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm.h

## Purpose
Defines the internal TPM driver contract: shared constants, TPM1 capability layouts, TPM2 property constants, global class/device exports, and prototypes linking chip lifecycle, command, eventlog, sysfs, TPM1, TPM2, sessions, and resource-manager code.

## Important APIs, Types, And Functions
Important definitions include `TPM_MINOR`, `TPM_BUFSIZE`, `TPM_NUM_DEVICES`, timeout enums, TPM1 error/warning codes, `TPM2_SPACE_BUFFER_SIZE`, TPM1 capability structures/unions, TPM capability enums, TPM2 property enums, `TPM_MAX_RNG_DATA`, class/device globals, and prototypes for `tpm_transmit()`, `tpm_chip_alloc/register/unregister()`, TPM1/TPM2 command helpers, TPM2 space helpers, event-log setup, and dev common init/exit.

## Control Flow
The header does not execute code except for `tpm_msleep()` and config stubs. It establishes which implementation files can call each other and which symbols are exported to transport drivers and other kernel code.

## State And Persistence
The structures describe persistent chip state consumed elsewhere, especially TPM1 capability data, TPM2 resource-manager buffer size, and global TPM class/device number state declared here and defined in implementation files.

## Dependencies And Integration Points
Included by nearly every TPM source file in this subset and by bus drivers. It pulls in Linux device, module, TPM, eventlog, synchronization, delay, and architecture CPU matching headers.

## Risks And Edge Cases
Wire-format structures are packed and endian-qualified; layout drift would break TPM command parsing. Constants such as buffer sizes and RNG limits are baked into multiple callers. Prototype changes can break modules outside this immediate directory.

## Test Signals
Compile all TPM configurations, run sparse/endian checks on packed structures, validate TPM1/TPM2 command parsers against wire-format fixtures, and exercise APIs from transport drivers and in-kernel TPM consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm1-cmd.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm1-cmd.c

## Purpose
Implements TPM 1.x command helpers used by the kernel for startup, timeout discovery, PCR operations, capabilities, RNG, self-test, suspend savestate, and PCR allocation.

## Important APIs, Types, And Functions
Exports `tpm1_calc_ordinal_duration()`, `tpm1_get_timeouts()`, `tpm1_pcr_extend()`, `tpm1_getcap()`, `tpm1_get_random()`, `tpm1_pcr_read()`, `tpm1_do_selftest()`, `tpm1_auto_startup()`, `tpm1_pm_suspend()`, and `tpm1_get_pcr_allocation()`. Internal helpers include `tpm1_startup()` and `tpm1_continue_selftest()`.

## Control Flow
Timeout discovery reads TIS timeout and duration capabilities, performs manual startup on `TPM_ERR_INVALID_POSTINIT`, applies vendor override hooks, repairs zero or millisecond-reported values, and stores jiffies in the chip. Self-test sends `ContinueSelfTest` and polls PCR0 reads until tests finish, disabled/deactivated states are accepted, or the duration expires. RNG loops `GetRandom` up to five retries. Suspend optionally extends a dummy PCR then retries `SaveState` on `TPM_WARN_RETRY`.

## State And Persistence
The file initializes `chip->timeout_*`, `chip->duration[]`, `timeout_adjusted`, `duration_adjusted`, `TPM_CHIP_FLAG_HAVE_TIMEOUTS`, `TPM_CHIP_FLAG_ALWAYS_POWERED`, `TPM_CHIP_FLAG_FIRMWARE_UPGRADE`, and the single SHA1 allocated PCR bank.

## Dependencies And Integration Points
Called by generic TPM APIs and chip bootstrap. It depends on `tpm_buf` construction, `tpm_transmit_cmd()`, TPM1 capability structures from `tpm.h`, hash digest sizes, and optional transport timeout/duration update hooks.

## Risks And Edge Cases
Firmware-reported timeouts and durations are often wrong and require heuristics. Positive TPM errors are converted to probe failures in startup paths. RNG and PCR read length checks must prevent short response use. Suspend SaveState after prior firmware use may need repeated retries.

## Test Signals
TPM1 startup on already-started and postinit-required chips, bogus timeout/duration reports, disabled/deactivated self-test behavior, failed self-test firmware-upgrade mode, PCR read/extend, random short reads and retries, and suspend SaveState retry loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm1-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-cmd.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-cmd.c

## Purpose
Implements TPM 2.0 command helpers used by the kernel for timeouts, PCR read/extend, RNG, context flush, property/capability reads, shutdown, self-test, protocol probe, PCR bank discovery, command-attribute discovery, startup, and session initialization.

## Important APIs, Types, And Functions
Exports `tpm2_find_hash_alg()`, `tpm2_get_timeouts()`, `tpm2_calc_ordinal_duration()`, `tpm2_pcr_read()`, `tpm2_pcr_extend()`, `tpm2_get_random()`, `tpm2_flush_context()`, `tpm2_get_tpm_pt()`, `tpm2_probe()`, `tpm2_get_pcr_allocation()`, `tpm2_get_cc_attrs_tbl()`, `tpm2_auto_startup()`, and `tpm2_find_cc()`. It includes module parameter `disable_pcr_integrity`.

## Control Flow
PCR read builds a bank-selecting `PCR_Read` command and validates digest size. PCR extend starts an HMAC session unless disabled, appends protected handle/name and auth, fills HMAC, transmits, and validates the response HMAC. RNG starts a session, optionally requests response encryption, loops until enough random bytes are returned or retries are exhausted, and ends the session on errors. Auto-startup sets timeouts, handles initialize/startup, self-tests, reads command attributes, handles field-upgrade/failure modes, and initializes TPM2 sessions.

## State And Persistence
The file populates `chip->allocated_banks`, `nr_allocated_banks`, `cc_attrs_tbl`, `nr_commands`, timeout flags, firmware-upgrade flag, and optionally TPM2 HMAC session/null-key state through `tpm2_sessions_init()`.

## Dependencies And Integration Points
Used by generic TPM core, sysfs PCR access, resource-manager command validation, TPM2 sessions, and chip bootstrap. It depends on `tpm_buf`, crypto hash metadata, TPM2 command attributes, and session/HMAC helpers.

## Risks And Edge Cases
PCR integrity can be disabled by module parameter. Capability responses must be length-checked and bounded by `TPM2_MAX_PCR_BANKS` and command-count sanity limits. Field-upgrade TPMs can return success with empty property lists. HMAC sessions must be ended on allocation or transmit failures.

## Test Signals
TPM2 probe across TPM1/TPM2 hardware, PCR bank discovery for supported and unknown hashes, PCR extend with and without HMAC integrity, RNG with encrypted responses, command-attribute table parsing, startup from `RC_INITIALIZE`, field-upgrade modes, and shutdown on suspend/reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-sessions.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-sessions.c

## Purpose
Implements optional TPM2 HMAC authorization sessions and first-parameter encryption/decryption for kernel-originated TPM2 transactions, based on a salted session derived from a TPM NULL primary key.

## Important APIs, Types, And Functions
Important exported helpers are `tpm_buf_append_name()`, `tpm_buf_append_auth()`, `tpm_buf_append_hmac_session()`, `tpm_buf_fill_hmac_session()`, `tpm_buf_check_hmac_response()`, `tpm2_end_auth_session()`, `tpm2_start_auth_session()`, and `tpm2_sessions_init()`. Core internal pieces include `struct tpm2_auth`, `name_size()`, `tpm2_read_public()`, `tpm2_KDFa()`, `tpm2_KDFe()`, `tpm_buf_append_salt()`, `tpm2_parse_start_auth_session()`, `tpm2_load_null()`, `tpm2_parse_create_primary()`, and `tpm2_create_primary()`.

## Control Flow
Initialization creates a fixed ECC P-256 NULL primary, validates its template/name, saves its context, and stores the public key coordinates. Starting a session loads or recreates the NULL key, generates caller nonce and ECDH salt, sends `StartAuthSession`, derives the session key, and stores `chip->auth`. Command construction records names for handles, appends the HMAC session placeholder, optionally encrypts the first parameter, computes `cpHash`, and fills the HMAC. Response checking parses the session area, computes `rpHash`, verifies the TPM HMAC, optionally decrypts the first response parameter, and either resets or frees the auth session.

## State And Persistence
`chip->auth` holds active session handle, nonces, salt/scratch, session key, passphrase, AES key schedule, attributes, ordinal, and up to three handle names. `chip->null_key_context`, `null_key_name`, and public EC coordinates persist after initialization to bootstrap later sessions.

## Dependencies And Integration Points
Compiled only when `CONFIG_TCG_TPM2_HMAC` enables the heavy implementation; otherwise `tpm.h` provides a no-op init. It integrates TPM2 command helpers, TPM2 context load/save, Linux random, SHA256/HMAC, ECDH P-256, AES-CFB, and TPM2 command-attribute metadata.

## Risks And Edge Cases
The initial NULL primary creation cannot itself be session protected, so the file exposes `null_name` for userspace verification. Handle names must be appended with `tpm_buf_append_name()` or HMACs are wrong. Session offsets and parameter sizes are fragile, and failures must flush sessions and sensitive memory. Unsupported name algorithms or changed NULL primary names disable the chip.

## Test Signals
PCR extend and RNG with HMAC enabled, HMAC mismatch fault injection, encrypted request and response parameter tests, NULL primary context reload and recreation, tampered NULL key name, too many handles, unsupported name algorithms, command failure cleanup, and sysfs `null_name` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-sessions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-space.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-space.c

## Purpose
Implements TPM2 resource-manager spaces for `/dev/tpmrm*`, virtualizing transient object handles and sessions by loading contexts before each command and saving/flushing them afterward.

## Important APIs, Types, And Functions
Exports `tpm2_init_space()`, `tpm2_del_space()`, `tpm2_load_context()`, `tpm2_save_context()`, `tpm2_flush_space()`, `tpm2_prepare_space()`, `tpm2_commit_space()`, `tpm_devs_add()`, and `tpm_devs_remove()`. Internal helpers include `tpm2_load_space()`, `tpm2_map_command()`, `tpm_find_and_validate_cc()`, `tpm2_map_response_header()`, `tpm2_map_response_body()`, and `tpm2_save_space()`.

## Control Flow
Before a user command, `tpm2_prepare_space()` validates the command code against `chip->cc_attrs_tbl`, copies the file space into `chip->work_space`, loads saved transient and session contexts, maps virtual transient handles in the command to physical handles, and records `last_cc`. After transmit, `tpm2_commit_space()` maps returned physical handles to virtual handles, filters `GetCapability` handle lists to handles owned by the space, saves and flushes active contexts, copies updated state back to the file space, and adjusts the response length.

## State And Persistence
Each `struct tpm_space` owns context/session backing buffers plus tables of virtual-to-physical transient handles and session handles. Saved contexts persist across commands for a file descriptor, while physical TPM handles are flushed after saving.

## Dependencies And Integration Points
Used by common TPM char-device transmit for resource-manager files and by chip allocation for the internal work space. It depends on TPM2 context load/save/flush commands, command attribute tables from `tpm2_get_cc_attrs_tbl()`, cdev device registration, and TPM class state.

## Risks And Edge Cases
Handle-table slots are finite; when full, newly returned handles are flushed and `-ENOMEM` is reported. Context integrity, stale sessions, or external flushes can make loads return `-ENOENT` or `-EINVAL`. Command-length validation must match command attributes or user buffers could be remapped incorrectly.

## Test Signals
Create/load/flush transient objects through `/dev/tpmrm*`, session persistence across commands, concurrent spaces with isolated virtual handles, handle table exhaustion, `GetCapability` handle filtering, invalid command codes/lengths, context integrity errors, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_atmel.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_atmel.c

## Purpose
Implements the legacy Atmel TPM 1.1 I/O-port/platform driver and registers it with the generic TPM core.

## Important APIs, Types, And Functions
Defines `struct tpm_atmel_priv`, register helpers `tpm_read_index()`, `atmel_verify_tpm11()`, `atmel_get_base_addr()`, TPM ops `tpm_atml_recv()`, `tpm_atml_send()`, `tpm_atml_cancel()`, `tpm_atml_status()`, `tpm_atml_req_canceled()`, lifecycle helpers `init_atmel()`, `cleanup_atmel()`, and `atml_plat_remove()`.

## Control Flow
Module init registers a platform driver, verifies Atmel vendor/version bytes through indexed I/O ports, reads the base address, maps two I/O ports, optionally reserves the region, creates a platform device, allocates private state and a TPM chip, and registers it. Send writes command bytes to the data port. Receive reads the six-byte header and payload while checking `DATA_AVAIL`, validates response size, and ensures data availability clears. Cancel writes the abort bit.

## State And Persistence
The global `pdev` persists the created platform device. Per-chip private state stores region ownership, base port, region size, and mapped I/O base. The TPM core owns device registration, sysfs, and char-device state.

## Dependencies And Integration Points
Depends on legacy x86-style I/O port access, `ioport_map()`, platform device/driver APIs, TPM core registration, and generic TPM PM helpers.

## Risks And Edge Cases
The driver reserves the region only opportunistically and records whether it succeeded. Probe is legacy and global rather than firmware-enumerated. Receive must drain or detect leftover data on size errors. Cleanup order depends on `pdev` existing after init success.

## Test Signals
Legacy Atmel hardware probe, vendor/version rejection, region reservation failure/success, command send/receive, malformed response sizes, cancel behavior, suspend/resume, and module unload after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_atmel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb.c

## Purpose
Implements the ACPI TPM 2.0 Command Response Buffer driver, including memory mapping, locality control, command ready/idle sequencing, command start/cancel methods, Pluton support, ARM SMC, and Arm FF-A start integration.

## Important APIs, Types, And Functions
Important types include `struct crb_regs_head`, `struct crb_regs_tail`, `struct crb_priv`, `struct tpm2_crb_smc`, `struct tpm2_crb_ffa`, and `struct tpm2_crb_pluton`. Key functions are `tpm_crb_has_idle()`, `crb_wait_for_reg_32()`, `crb_try_pluton_doorbell()`, `__crb_go_idle()`, `__crb_cmd_ready()`, locality request/relinquish helpers, `crb_status()`, `crb_recv()`, `crb_send()`, `crb_cancel()`, `crb_map_io()`, `crb_map_pluton()`, `crb_acpi_probe()`, and `crb_acpi_remove()`.

## Control Flow
ACPI probe reads the `TPM2` table, rejects FIFO-handled memory-mapped start method, parses start-method-specific parameter blocks, initializes FF-A if needed, maps Pluton doorbells when present, maps CRB control/command/response regions from ACPI resources, requests locality, wakes the device, reads command/response buffer addresses and sizes, maps buffers, releases locality, allocates a TPM2 chip, bootstraps it, applies AMD hwrng disable quirk, and registers it. Send clears cancel, copies the command to the mapped buffer, issues the appropriate CRB/ACPI/SMC/FF-A/Pluton start method, and returns for generic polling. Receive validates error status and response length before copying from the response buffer.

## State And Persistence
`struct crb_priv` persists mapped register pointers, command/response buffers, command size, start method, ACPI HID, SMC function ID, Pluton doorbells, and FF-A metadata. TPM chip flags mark TPM2 and may disable hwrng for selected AMD systems.

## Dependencies And Integration Points
Integrates ACPI TPM2 tables/resources, platform driver matching `MSFT0101`, TPM core class ops, PM suspend/resume, memory-mapped I/O, optional ARM SMCCC, optional CRB FF-A helper, x86 CPU vendor quirk data, and TPM2 bootstrap.

## Risks And Edge Cases
Firmware ACPI resource descriptions are frequently inconsistent; `crb_fixup_cmd_size()` trusts the ACPI region over register size. Start-method handling differs for ACPI start, memory-mapped CRB, ARM SMC, FF-A, Pluton, and Intel PTT quirked MSFT0101 devices. Locality and idle transitions can time out. Response length and overlapping command/response buffer sizes must be validated.

## Test Signals
Boot CRB TPM2 systems using each start method, malformed ACPI table/resource tests, command/response buffer overlap and truncation cases, Pluton doorbell completion, ARM SMC/FF-A start paths, cancellation, suspend/resume, AMD hwrng quirk, and securityfs/char-device command traffic after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb.c -->
