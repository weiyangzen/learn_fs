# subset-b-001010 research

This grouped report covers the requested Speakup synthesizer support files and ACPI driver/configuration files. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/synth.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/synth.c

## Purpose
`synth.c` is the central Speakup speech-synthesizer manager. It owns the active global `struct spk_synth *synth`, the registered synthesizer list, the shared `speakup_info` spinlock state, synth output buffering, UTF-8-to-wide-character ingress helpers, catch-up output flow control, synth index commands, I/O port resource claims, and synth attach/release paths.

## Important APIs, Types, And Functions
The exported state and APIs include `speakup_info`, `spk_do_catch_up`, `spk_do_catch_up_unicode`, `spk_synth_flush`, `spk_synth_get_index`, `spk_synth_is_alive_nop`, `spk_synth_is_alive_restart`, `synth_printf`, `synth_putwc`, `synth_putwc_s`, `synth_putws`, `synth_putws_s`, `synth_request_region`, `synth_release_region`, `synth_add`, `synth_remove`, and `synth_current`. `synth_time_vars` provides default Speakup timing variables for delay, trigger, jiffy delta, full timeout, and flush timeout. Internal control is concentrated in `_spk_do_catch_up()`, `synth_start()`, `spk_do_flush()`, `synth_utf8_get()`, `synth_writeu()`, `do_synth_init()`, and `synth_release()`.

## Control Flow
Text enters through `synth_write()`, `synth_writeu()`, `synth_printf()`, or wide-character helpers, is appended to the synth buffer, and `synth_start()` arms `thread_timer` based on the `TRIGGER` variable. The Speakup thread wakes on `speakup_event` and calls the synth's `catch_up` callback, normally `spk_do_catch_up()` or the Unicode variant. `_spk_do_catch_up()` repeatedly locks `speakup_info.spinlock`, handles flush requests, skips non-Latin-1 when needed, peeks the next buffered character, sleeps if the synth reports full, periodically emits the synth `procspeech` marker at spaces, and consumes characters only after output succeeds. Initialization looks up a named synth from `synths`, releases any existing synth, probes the new one, copies timing defaults from the synth descriptor, emits the init string, registers variables, creates optional sysfs attributes, and wakes the Speakup thread. Removal reverses that by stopping output, deleting the timer, removing sysfs, unregistering variables, and invoking the synth release callback.

## State And Persistence
All state is in kernel memory. Persistent user-visible effects are through sysfs groups created by individual synth drivers and through registered Speakup variables. Shared mutable state includes `synth`, `synths`, `spk_pitch_buff`, `spk_quiet_boot`, `speakup_info.flushing`, `thread_timer`, `index_count`, `sentence_count`, and `synth_res`. Buffer and timing updates are protected by `speakup_info.spinlock`; synth registration and selection are serialized by `spk_mutex`.

## Dependencies And Integration Points
The file depends on Speakup private headers (`spk_priv.h`, `speakup.h`, `serialio.h`), the synth buffer helpers, kernel timers, wait queues, kthreads, sysfs, ioport resources, and per-synth `io_ops`. It integrates with `thread.c` through `speakup_event` and `speakup_task`, with variable registration in `varhandlers.c`, with serial synth drivers through `struct spk_synth`, and with console/keyboard paths that enqueue Speakup output.

## Risks
This file is concurrency-sensitive: lock handoff in `_spk_do_catch_up()`, timer wakeups, flush handling, and synth release must avoid sleeping while holding the Speakup spinlock or dereferencing a released synth. `synth_utf8_get()` accepts 2- through 6-byte forms and only stores values below `0x10000`, so malformed or supplementary-plane input is dropped rather than fully represented. `synth_release_region()` ignores its arguments and releases the single static `synth_res`, so callers must not assume independent ranges. Indexing functions assume `synth` and `synth->get_index` are valid when called.

## Test Signals
Useful signals are boot/module tests selecting and releasing synth drivers, sysfs variable registration and removal, Speakup text output under flush and full-buffer conditions, Unicode and invalid UTF-8 output, and synth index count progression. Race-oriented tests should exercise synth removal while `speakup_thread()` is active, timer-triggered catch-up, and pitch-shift restoration in `spk_do_flush()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/thread.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/thread.c

## Purpose
`thread.c` implements the Speakup progression kthread. It waits for speech-buffer work, flush requests, and pending beeps, then drives synthesizer catch-up and restarts TTY output processing.

## Important APIs, Types, And Functions
It exports `DECLARE_WAIT_QUEUE_HEAD(speakup_event)` and defines `speakup_thread(void *data)`. The loop uses `struct bleep`, `spk_unprocessed_sound`, `kd_mksound()`, `synth`, `synth->catch_up`, `synth_buffer_empty()`, `speakup_info.flushing`, and `speakup_start_ttys()`.

## Control Flow
The thread starts with `spk_mutex` held and loops until `kthread_should_stop()`. It prepares a wait entry, takes `speakup_info.spinlock`, copies and clears `spk_unprocessed_sound`, and decides whether to break out for stop, sound playback, or synth catch-up work. If no work is ready, it drops `spk_mutex`, schedules, and reacquires the mutex. After wakeup it finishes the wait, plays any pending sound via `kd_mksound()`, invokes `synth->catch_up(synth)` when the active synth is alive and has buffered or flushing work, and then calls `speakup_start_ttys()`.

## State And Persistence
The thread itself persists as a kernel task while Speakup is running. It consumes the one-shot `spk_unprocessed_sound` state by clearing `active` under the Speakup spinlock. It does not persist data outside memory.

## Dependencies And Integration Points
It depends on kernel kthreads and wait queues plus Speakup internals declared in `spk_types.h`, `speakup.h`, and `spk_priv.h`. It is woken by `synth_start()`, `spk_do_flush()`, synth timers, and other Speakup paths that signal `speakup_event`.

## Risks
The file deliberately calls `synth->catch_up()` without holding `speakup_info.spinlock`, so the callee must perform its own locking and be robust against sleeping. Correct lock ordering between `spk_mutex` and the spinlock is important. Missed wakeups or incorrect `prepare_to_wait()`/`finish_wait()` use would stall speech output or beeps.

## Test Signals
Regression coverage should include queued speech wakeups, flush wakeups, beep delivery, `kthread_stop()` shutdown, and TTY restart after catch-up. Stress tests should combine high-rate output with synth removal or state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/utils.h -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/utils.h

## Purpose
`utils.h` is a small userspace build-time utility header for Speakup keymap/table generation tools. It supplies global parser state, a simple name hash table, file opening/error helpers, and key insertion/lookup helpers.

## Important APIs, Types, And Functions
It defines `MAXKEYS`, `MAXKEYVAL`, `HASHSIZE`, sentinel values `is_shift`, `is_spk`, and `is_input`, plus `struct st_key { name, next, value, shift }`. Global state includes `key_table`, `extra_keys`, `def_name`, `def_val`, `infile`, `lc`, and `filename`. Inline helpers are `open_input()`, `oops()`, `hash_name()`, `find_key()`, and `add_key()`.

## Control Flow
Generation tools call `open_input()` to form a path and open the input file, increment `lc` while parsing, use `hash_name()` to normalize names to lowercase and select a bucket, then call `find_key()` or `add_key()` to resolve or register key names. Errors are fatal through `oops()`, which reports the current file and line and exits.

## State And Persistence
The hash table is process-local state in the generator. `hash_name()` mutates its input string by lowercasing it. `add_key()` stores duplicated key names with `strdup()` and monotonically consumes entries from `extra_keys`; entries are not freed because the generator is short-lived.

## Dependencies And Integration Points
The header uses libc I/O and string APIs (`stdio.h`, `fopen`, `snprintf`, `fprintf`, `exit`, `strdup`, `strcmp`, `tolower`, `isupper`). It is meant for Speakup host tools, not kernel object code.

## Risks
Because this header defines globals, including it in more than one translation unit would create multiple-definition problems. The fixed `MAXKEYS` table can abort on large maps, `filename` truncation is not checked, and `hash_name()` modifies caller-owned strings. Fatal `exit(1)` behavior is appropriate for generators but unsuitable for reusable libraries.

## Test Signals
Useful tests parse key names with different case, detect duplicate keys, exhaust or approach `MAXKEYS`, and verify error messages include filename and line count. Build tests should ensure the header is used only by intended userspace tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/varhandlers.c -->
# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/varhandlers.c

## Purpose
`varhandlers.c` maps Speakup variable IDs to names, storage, and setter behavior. It supports proc/sysfs-style variable registration, numeric and string updates, punctuation mask updates, character-table keyword decoding, and simple parser helpers used by Speakup configuration paths.

## Important APIs, Types, And Functions
The central tables are `var_headers[]`, `var_ptrs[MAXVARS]`, and `punc_vars[]`. Public or shared functions include `spk_chartab_get_value()`, `speakup_register_var()`, `speakup_unregister_var()`, `spk_get_var_header()`, `spk_var_header_by_name()`, `spk_get_var()`, `spk_get_punc_var()`, `spk_set_num_var()`, `spk_set_string_var()`, `spk_set_mask_bits()`, `spk_strlwr()`, and `spk_s2uchar()`.

## Control Flow
The first `speakup_register_var()` call initializes `var_ptrs` from `var_headers`, clears header data pointers, attaches the passed `struct var_t`, and applies default numeric/time/string values. Numeric updates in `spk_set_num_var()` interpret `how` as default, set, increment, decrement, or new-default operation, range-check the value, update an optional backing integer, adjust `spk_punc_mask` for punctuation level, apply multiplier/offset, optionally let the active synth consume the adjustment, and finally emit a synth command for synth-specific variables. String updates copy defaults or user data into the registered backing buffer. `spk_set_mask_bits()` validates punctuation/delimiter input against `spk_chartab` and sets or clears class bits.

## State And Persistence
State is stored in the registered `struct var_t` objects, header `data` pointers, global Speakup settings such as `spk_punc_mask`, `spk_chartab`, and synth command side effects. It is in-memory kernel state; user-visible persistence depends on the surrounding Speakup variable interfaces.

## Dependencies And Integration Points
The file depends on `spk_types.h`, `spk_priv.h`, `speakup.h`, kernel ctype helpers, timing conversion through `msecs_to_jiffies()`, active synth output via `synth_printf()`, and shared punctuation data such as `spk_punc_info`, `spk_punc_masks`, and `spk_chartab`.

## Risks
`spk_var_header_by_name()` assumes `var_ptrs` has been initialized before use; calling it too early can dereference NULL table entries. `spk_set_num_var()` formats into 32-byte buffers or `spk_pitch_buff`, so synth format strings and value strings must remain bounded. `spk_set_string_var()` uses `strcpy()` after only checking `len <= MAXVARLEN`, so backing buffers must match that contract. Mask updates rely on the correctness of global character classification data.

## Test Signals
Test signals include registration/unregistration ordering, all numeric update modes and range failures, time variable jiffy conversion, synth command emission for rate/pitch/volume-style variables, string default restore behavior, punctuation mask validation, and early lookup behavior before registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accessibility/speakup/varhandlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/acpi/Kconfig

## Purpose
This Kconfig file defines the ACPI subsystem feature matrix: global ACPI enablement, debugger and table features, power-management pieces, bus/device drivers, platform-specific helpers, and exported ACPI table/opregion options.

## Important APIs, Types, And Functions
Important symbols in this file include `ACPI`, `ACPI_DEBUGGER`, `ACPI_DEBUGGER_USER`, `ACPI_SPCR_TABLE`, `ACPI_FPDT`, `ACPI_LPIT`, `ACPI_SLEEP`, `ACPI_EC`, `ACPI_AC`, `ACPI_BATTERY`, `ACPI_BUTTON`, `ACPI_TAD`, `ACPI_PROCESSOR`, `ACPI_IPMI`, `ACPI_HOTPLUG_CPU`, `ACPI_PROCESSOR_AGGREGATOR`, `ACPI_THERMAL`, `ACPI_TABLE_UPGRADE`, `ACPI_CONFIGFS`, `ACPI_EXTLOG`, `ACPI_ADXL`, `ACPI_PCC`, `ACPI_FFH`, `ACPI_MRRM`, and `X86_PM_TIMER`. It also sources nested ACPI submenus for NFIT, NUMA, APEI, DPTF, ARM64, RISC-V, PMIC, and other architecture-specific support.

## Control Flow
Kconfig dependency and selection rules determine which source files in `drivers/acpi/Makefile` are built. `menuconfig ACPI` gates most symbols. Tristate driver symbols become modules when selected as `m`; bool helper symbols are compiled into the ACPI core or architecture-specific paths. Defaults enable common x86 ACPI support, processor, battery, AC adapter, fans, and thermal support where dependencies are met.

## State And Persistence
The file contributes persistent build configuration through `.config`. Those choices alter kernel ABI visibility such as sysfs/debugfs/configfs nodes, module availability, power management support, and architecture-specific ACPI behavior.

## Dependencies And Integration Points
It integrates with architecture capability symbols (`ARCH_SUPPORTS_ACPI`, `ACPI_SYSTEM_POWER_STATES_SUPPORT`, `ARCH_HAS_ACPI_TABLE_UPGRADE`), subsystem dependencies such as `POWER_SUPPLY`, `INPUT`, `THERMAL`, `PCC`, `MAILBOX`, `CONFIGFS_FS`, `DEBUG_FS`, `IPMI_HANDLER`, `EDAC`, and kernel documentation referenced in help text.

## Risks
Incorrect dependencies can create build failures or expose drivers without required core subsystems. Defaults matter because ACPI controls power, hotplug, and firmware interfaces; overly broad defaults can expose risky debug/configfs functionality, while missing `select` statements can remove required support. Help text must stay aligned with actual module names and behavior.

## Test Signals
Validation comes from Kconfig dependency checks across x86, ARM64, LoongArch, and RISC-V configurations, allmodconfig/allyesconfig builds, module name checks, and targeted builds toggling debugger, configfs, IPMI, FPDT, LPIT, PCC, FFH, MRRM, and processor options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/acpi/Makefile

## Purpose
The ACPI Makefile maps Kconfig selections to ACPI core objects, built-in helpers, optional modules, and nested subdirectories. It is the build contract for the files in this subset.

## Important APIs, Types, And Functions
Key object lists are `obj-$(CONFIG_ACPI)`, `acpi-y`, conditional `acpi-$(CONFIG_...)`, and module-specific lists such as `processor-y`, `fan-objs`, and `video-objs`. This subset is wired through entries for `acpi_processor.o`, `acpi_apd.o`, `acpi_platform.o`, `acpi_pnp.o`, `acpi_lpat.o`, `acpi_fpdt.o`, `acpi_lpit.o`, `acpi_pcc.o`, `acpi_ffh.o`, `acpi_mrrm.o`, `acpi_adxl.o`, `acpi_ipmi.o`, `ac.o`, `acpi_tad.o`, `processor.o`, `acpi_memhotplug.o`, `acpi_pad.o`, `acpi_extlog.o`, `acpi_configfs.o`, and `acpi_dbg.o`.

## Control Flow
Built-in ACPI core composition is collected into `acpi-y`, while standalone drivers are assigned to `obj-*`. `CONFIG_ACPI_CUSTOM_DSDT` adds an explicit dependency from `tables.o` to the configured included DSDT file. `CONFIG_TRACE_BRANCH_PROFILING` disables branch profiling for `processor_idle.o`. Nested directories are added conditionally by subsystem or architecture.

## State And Persistence
The Makefile does not manage runtime state. It persists the build topology: whether objects are linked into the ACPI core module/built-in object, emitted as independent modules, or omitted.

## Dependencies And Integration Points
It depends directly on Kbuild conventions and the Kconfig symbols defined in this and nested ACPI Kconfig files. It integrates ACPI with PMIC, DPTF, APEI, NFIT, NUMA, architecture subdirectories, processor cpufreq/idle/throttling helpers, and video/fan composite objects.

## Risks
Moving objects between `acpi-y` and `obj-*` changes module boundaries, initialization ordering, symbol visibility, and module parameters. The comment that IPMI initializes before other drivers is important because AML IPMI OpRegions may be used by unrelated ACPI drivers. Missing conditional dependencies can silently drop firmware support.

## Test Signals
Allmodconfig/allyesconfig and minimal ACPI builds should verify object inclusion. Module builds should confirm expected module names (`ac`, `acpi_ipmi`, `acpi_tad`, `processor`, `acpi_pad`, `acpi_configfs`, `acpi_dbg`, `acpi_extlog`) and built-in core linkage for helper files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ac.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/ac.c

## Purpose
`ac.c` is the ACPI AC adapter power-supply driver for `ACPI0003` devices. It evaluates `_PSR` to expose whether mains power is online, reports ACPI/netlink notifier events, and registers a Linux power supply named after the ACPI device BID.

## Important APIs, Types, And Functions
The main state is `struct acpi_ac`, holding the `power_supply`, descriptor, ACPI device, cached state, and battery notifier. Important functions are `acpi_ac_get_state()`, `get_ac_property()`, `acpi_ac_notify()`, `acpi_ac_battery_notify()`, `thinkpad_e530_quirk()`, `ac_only_quirk()`, `acpi_ac_probe()`, `acpi_ac_resume()`, `acpi_ac_remove()`, `acpi_ac_init()`, and `acpi_ac_exit()`.

## Control Flow
Module init exits if ACPI is disabled or the platform quirk says to skip ACPI AC/battery, applies DMI quirks, and registers a platform driver. Probe fetches the ACPI companion, allocates `struct acpi_ac`, reads `_PSR` unless forced online by `ac_only`, registers a `POWER_SUPPLY_TYPE_MAINS` power supply with `POWER_SUPPLY_PROP_ONLINE`, subscribes to ACPI battery events, and installs an ACPI notify handler. Notify events optionally sleep for a DMI-configured EC delay, reread state, generate netlink and ACPI notifier-chain events, and call `power_supply_changed()`. Resume rereads state and emits a power-supply change if it differs.

## State And Persistence
State is in memory as the cached AC line state, DMI quirk flags, and registered power-supply object. User-visible state is exposed through power-supply sysfs and ACPI events. No durable persistence is used.

## Dependencies And Integration Points
It depends on ACPI platform enumeration, `_PSR`, Linux `power_supply`, DMI quirks, ACPI notifier chain, battery class events, and platform-driver PM operations. It uses `acpi_quirk_skip_acpi_ac_and_battery()` to respect broader platform quirks.

## Risks
Firmware notification ordering can make `_PSR` stale, hence the ThinkPad delay quirk. `ac_only` forces online state on systems with broken firmware, trading correctness for usability. Notification and battery callbacks both update cached state without a dedicated lock; consumers rely on simple scalar semantics. Probe error paths must keep notifier and power-supply registration ordering correct.

## Test Signals
Tests should cover `_PSR` online/offline/unknown results, ACPI notify events `0x80`, bus check, device check, resume transitions, battery-triggered rereads, DMI quirk behavior, and power-supply sysfs `online` updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/ac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_adxl.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_adxl.c

## Purpose
`acpi_adxl.c` implements the ACPI ADXL address-translation interface via `_DSM` calls on `\_SB.ADXL`. It exposes memory-address component names and decodes a system physical address into platform topology component values.

## Important APIs, Types, And Functions
Important constants are `ADXL_REVISION`, `ADXL_IDX_GET_ADDR_PARAMS`, `ADXL_IDX_FORWARD_TRANSLATE`, `ACPI_ADXL_PATH`, and `ADXL_MAX_COMPONENTS`. Exported APIs are `adxl_get_component_names()` and `adxl_decode()`. Internal state includes the ACPI `handle`, retained `_DSM` `params`, `adxl_count`, `adxl_component_names`, and the ADXL GUID. `adxl_dsm()` validates the two-element DSM response package.

## Control Flow
`adxl_init()` finds `\_SB.ADXL`, verifies `_DSM`, checks both required function bits, evaluates the parameter-name DSM, validates a bounded component count, allocates a NULL-terminated string pointer array, and points entries at the retained ACPI object strings. `adxl_decode()` builds a one-element package containing the address, calls the forward-translate DSM, requires the returned package count to match `adxl_count`, copies integer values into the caller-provided array, and frees the result object.

## State And Persistence
ADXL component metadata is retained for the lifetime of the kernel after `subsys_initcall()`. There is no cleanup path because this is built-in ACPI support. The decoded values are per-call outputs only.

## Dependencies And Integration Points
It depends on ACPI DSM helpers and exports the ADXL API declared by `<linux/adxl.h>` for memory error reporting or platform topology consumers. The source references Intel's ADXL specification by URL in comments.

## Risks
`adxl_component_names` points into the retained `params` ACPI object, so freeing `params` would invalidate exported names. `adxl_decode()` assumes returned elements are integers and does not validate each element type. Firmware-provided component counts are bounded, but callers must allocate enough `u64` slots according to the name list.

## Test Signals
Validation should exercise absent ADXL, missing `_DSM`, unsupported DSM bits, excessive component counts, mismatched decode result counts, and successful decode with undefined components represented as `~0ull`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_adxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_apd.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_apd.c

## Purpose
`acpi_apd.c` creates platform devices for selected ACPI-described AMD, Hygon, and ARM64 SoC peripherals that need platform-device representation, fixed input clocks, or built-in device properties.

## Important APIs, Types, And Functions
The main descriptors are `struct apd_device_desc` and `struct apd_private_data`. Setup functions include `acpi_apd_setup()` for fixed-rate clocks and `fch_misc_setup()` for AMD FCH clock data. `acpi_apd_create_device()` is the scan-handler attach callback. The ACPI ID table maps HIDs such as `AMD0010`, `AMD0020`, `AMDI0010`, `AMDI0015`, `HYGO0010`, `APMC0D0F`, `BRCM900D`, `CAV900D`, `HISI02A*`, and `NXP0001` to descriptors.

## Control Flow
`acpi_apd_init()` registers an ACPI scan handler. When a matching ACPI node is scanned, `acpi_apd_create_device()` either directly calls `acpi_create_platform_device()` for descriptor-less devices or allocates private data, runs the descriptor setup hook, stores it in `adev->driver_data`, and creates a platform device with optional properties. Fixed-clock setup registers a clock named after the ACPI device. FCH setup parses memory resources, obtains an optional `clk-name` device property, maps the MMIO resource, and registers a `clk-fch` platform device.

## State And Persistence
State is in the created platform devices, optional fixed clocks, `clk-fch` child device data, and `adev->driver_data`. There is no explicit detach cleanup in this file, so lifetime follows ACPI scan/platform-device lifetime and devm-managed allocations where used.

## Dependencies And Integration Points
It depends on ACPI scan handlers, platform device creation in `acpi_platform.c`, Linux clock APIs, ACPI property/resource helpers, and architecture config symbols `CONFIG_X86_AMD_PLATFORM_DEVICE` and `CONFIG_ARM64`. UART descriptors provide properties consumed by serial drivers.

## Risks
Clock registration failures are not checked in `acpi_apd_setup()`, so a bad fixed clock can propagate as a later driver issue. Non-devm `pdata` allocated by `kzalloc_obj()` needs matching lifetime assumptions. FCH setup maps the first memory resource and returns errors for missing resources or allocation failures. Adding IDs must use correct fixed clock rates and properties or downstream platform drivers can misconfigure hardware.

## Test Signals
Builds should cover x86 AMD and ARM64 configurations. Runtime tests should verify platform-device creation for each HID, fixed-clock registration, UART property propagation, FCH `clk-fch` registration, and failure paths for missing `_CRS` resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_apd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_configfs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_configfs.c

## Purpose
`acpi_configfs.c` exposes a configfs interface under `/config/acpi/table` for host-directed dynamic ACPI SSDT table loading, inspection, and unloading.

## Important APIs, Types, And Functions
The central state is `struct acpi_table { config_item, header, index }`. Key functions are `acpi_table_aml_write()`, `get_header()`, `acpi_table_aml_read()`, metadata show functions for table header fields, `acpi_table_make_item()`, `acpi_table_drop_item()`, `acpi_configfs_init()`, and `acpi_configfs_exit()`. The binary attribute is `aml` with `MAX_ACPI_TABLE_SIZE` of 128 KiB.

## Control Flow
Module init registers the `acpi` configfs subsystem and creates the default `table` group. Creating an item allocates an empty `struct acpi_table`. Writing to its `aml` binary attribute checks lockdown policy, rejects duplicate loads, validates the supplied ACPI table length and `SSDT` signature, duplicates the table, and calls `acpi_load_table()` while retaining the returned index. Reads and text attributes require a loaded header. Dropping the item calls `acpi_unload_table(index)` and releases the config item.

## State And Persistence
Loaded SSDTs become live ACPI interpreter state until the configfs item is dropped or the module exits. The driver keeps an in-memory copy of the table header/body and ACPICA table index; it does not persist tables across reboot.

## Dependencies And Integration Points
It depends on configfs, ACPI table load/unload APIs, security lockdown (`LOCKDOWN_ACPI_TABLES`), and ACPICA header formats. It exposes metadata through configfs/sysfs attribute conventions.

## Risks
Dynamic table loading is privileged and potentially dangerous, so lockdown checks are central. Only SSDT signatures are accepted. `acpi_table_drop_item()` calls unload even when no table was loaded, relying on index initialization semantics. The binary read path copies `h->length` when `data` is supplied; callers rely on configfs size handling.

## Test Signals
Tests should cover lockdown denial, invalid length, non-SSDT signature, duplicate writes, successful load/read/show/unload, and cleanup during module exit with active configfs items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_dbg.c

## Purpose
`acpi_dbg.c` provides the userspace I/O bridge for the in-kernel ACPICA AML debugger. It exposes `debugfs/acpi/acpidbg`, connects user reads and writes to ACPICA debugger callbacks, and manages a debugger kthread plus circular input/output buffers.

## Important APIs, Types, And Functions
The central type is `struct acpi_aml_io`, containing wait queue, flags, user count, lock, debugger thread, aligned input/output buffers, circular-buffer cursors, callback, context, and usage count. Important flags include `ACPI_AML_OPENED`, `ACPI_AML_CLOSED`, `ACPI_AML_IN_USER`, `ACPI_AML_IN_KERN`, `ACPI_AML_OUT_USER`, and `ACPI_AML_OUT_KERN`. Important functions are buffer access predicates, `acpi_aml_lock_write()`, `acpi_aml_lock_read()`, `acpi_aml_write_kern()`, `acpi_aml_readb_kern()`, `acpi_aml_write_log()`, `acpi_aml_read_cmd()`, `acpi_aml_thread()`, `acpi_aml_create_thread()`, file operations `open/read/write/poll/release`, and the registered `struct acpi_debugger_ops`.

## Control Flow
Init creates the debugfs file and registers debugger operations with ACPICA. The first non-write-only opener becomes the active reader, initializes the ACPICA debugger, marks the interface opened, and resets circular buffers. ACPICA creates the debugger thread through `acpi_aml_create_thread()`. Kernel debugger output goes to `out_crc` via `write_log`; userspace reads it from the debugfs file. Userspace writes commands into `in_crc`; the debugger thread consumes bytes via `read_cmd()` until newline. Release of the active reader marks the interface closed, wakes blocked readers/writers, waits for busy operations to drain, terminates the ACPICA debugger, waits for the thread usage count to drop, and clears opened/closed flags when all users are gone.

## State And Persistence
All state is in memory and scoped to module lifetime. User-visible state is the debugfs file. The circular buffers hold transient debugger input/output. `acpi_aml_active_reader` enforces a single controlling reader.

## Dependencies And Integration Points
It depends on debugfs, wait queues, kthreads, circular-buffer helpers, user copy APIs, ACPICA debugger registration (`acpi_register_debugger()`), ACPICA callbacks (`acpi_os_printf`, `acpi_os_get_line`), and `acpi_debugfs_dir`.

## Risks
The code is highly stateful: open/close races, blocking reads/writes, and thread termination depend on `flags`, `users`, `usages`, and wait queues being updated in the right order. Memory barriers around circular-buffer head/tail updates are essential. Only the debugger thread may perform kernel-side buffer access; violating that assumption causes `-EFAULT`. A stuck userspace peer can block debugger command/log flow unless nonblocking I/O is used.

## Test Signals
Test debugfs open exclusivity, writer-before-reader rejection, nonblocking read/write `-EAGAIN`, poll readiness, command echo/log output, active-reader close while operations block, module unload, and ACPICA debugger init failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_extlog.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_extlog.c

## Purpose
`acpi_extlog.c` implements Extended MCA Logging support. It maps firmware-provided eMCA L1 and error-log tables, opts the OS into handling, consumes error records during machine-check decode, prints or traces CPER sections, and clears firmware record status for reuse.

## Important APIs, Types, And Functions
Important structures and state include `struct extlog_l1_head`, physical/virtual L1 and elog addresses, `elog_buf`, `l1_entry_base`, and `l1_percpu_entry`. Main functions are `extlog_elog_entry_check()`, `__print_extlog_rcd()`, `print_extlog_rcd()`, `extlog_print_pcie()`, `extlog_cxl_cper_handle_prot_err()`, `extlog_print()`, `extlog_get_l1addr()`, `extlog_init()`, and `extlog_exit()`. The notifier `extlog_mce_dec` registers at `MCE_PRIO_EXTLOG`.

## Control Flow
Init verifies CPU eMCA capability through `MSR_IA32_MCG_CAP`, obtains the L1 directory physical address via a `_DSM` on `\_SB`, validates 4 KiB alignment, reserves and maps the L1 header, reads table sizes and elog base/length, reserves/maps full L1 and elog regions, allocates a 4 KiB record buffer, registers the MCE decode notifier, and sets the OS opt-in flag. On an MCE, `extlog_print()` indexes the L1 entry by physical CPU ID and bank, checks valid bits and CPER status, skips CEC-handled records, copies the record to `elog_buf`, clears firmware `block_status`, and either prints the CPER record or emits trace/nonstandard/PCIe/CXL events. Exit unregisters the notifier, clears opt-in, unmaps memory, releases regions, and frees the buffer.

## State And Persistence
Mapped firmware memory and the L1 opt-in flag are persistent while the module is loaded. Individual records are transient: copied to `elog_buf`, then firmware status is cleared. Trace events and printk output are the durable diagnostic outputs.

## Dependencies And Integration Points
It depends on x86 MCE, ACPI DSM, CPER/APEI/GHES helpers, EDAC/RAS tracepoints, optional PCIe AER and CXL CPER handlers, MSR access, and ACPI OS iomem mapping. Kconfig ties it to `X86_MCE`, local APIC, EDAC, UEFI CPER, APEI, and GHES.

## Risks
Firmware table addresses and lengths are trusted after limited validation; bad firmware can cause mapping failures or invalid record access. Rate limiting protects logs but may hide repeated corrected events. The CXL helper currently returns early when `cxl_cper_sec_prot_err_valid(prot_err)` is true, which should be reviewed against helper semantics. Correct clearing of `block_status` is important to avoid losing or repeatedly reporting records.

## Test Signals
Validation should cover systems without eMCA capability, missing/invalid DSM address, mapping reservation conflicts, valid corrected and uncorrected records, CEC-handled records, userspace RAS consumers present/absent, PCIe and CXL CPER sections, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_extlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_ffh.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_ffh.c

## Purpose
`acpi_ffh.c` installs an ACPI Fixed Function Hardware address-space handler and delegates all architecture-specific setup and accesses to weak arch-overridable hooks.

## Important APIs, Types, And Functions
The file defines weak defaults `acpi_ffh_address_space_arch_setup()` and `acpi_ffh_address_space_arch_handler()`, both returning `-EOPNOTSUPP`. It wraps them with ACPICA-compatible `acpi_ffh_address_space_setup()` and `acpi_ffh_address_space_handler()`, and exposes `acpi_init_ffh()` to install the handler for `ACPI_ADR_SPACE_FIXED_HARDWARE`.

## Control Flow
During ACPI initialization, `acpi_init_ffh()` calls `acpi_install_address_space_handler()` on `ACPI_ROOT_OBJECT`. Region setup calls the arch setup hook with handler context and region context. AML accesses call the arch handler to populate or consume the ACPI integer value.

## State And Persistence
The only file-local state is `ffh_ctx`, passed as handler context. Any meaningful per-region state is supplied by architecture implementations through `region_context`.

## Dependencies And Integration Points
It depends on ACPICA address-space handling and architecture code that overrides the weak functions, commonly for platform-specific FFH operation regions or C-state support.

## Risks
Without arch overrides, FFH accesses return unsupported. Handler install failure is logged only as an alert; callers must tolerate missing FFH support. The generic handler ignores function, address, and bit-width parameters and relies entirely on arch code.

## Test Signals
Build tests should cover configurations with and without arch overrides. Runtime validation should verify handler installation, region setup, successful arch-backed reads/writes, and graceful unsupported behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_ffh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_fpdt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_fpdt.c

## Purpose
`acpi_fpdt.c` parses the ACPI Firmware Performance Data Table and exposes firmware boot and S3 suspend/resume timing data under `/sys/firmware/acpi/fpdt`.

## Important APIs, Types, And Functions
It defines FPDT subtable and record structures for FBPT, S3PT, boot, suspend, and resume records. Global record pointers are `record_resume`, `record_suspend`, and `record_boot`. Important functions are generated `*_show()` sysfs readers, `fpdt_address_valid()`, `fpdt_process_subtable()`, and `acpi_init_fpdt()`. Binary attributes `FBPT` and `S3PT` expose raw subtable bytes.

## Control Flow
`acpi_init_fpdt()` obtains the FPDT table, creates the `fpdt` kobject, iterates subtable entries, and processes FBPT or S3PT addresses. `fpdt_process_subtable()` validates the physical address, maps the subtable header, verifies the signature matches the type, remaps the full subtable, walks records by `record_header->length`, creates a sysfs group for the first boot/suspend/resume record of each type, and exposes raw binary attributes for the subtable. On parse errors it removes any groups and binary files it created.

## State And Persistence
Mapped FPDT subtables remain referenced through binary-attribute private pointers and record pointers for sysfs show functions. The data itself is firmware-provided memory. The code does not define an exit path because it is initialized with `fs_initcall()`.

## Dependencies And Integration Points
It depends on ACPI table APIs, ACPI OS physical memory mapping, sysfs/kobject infrastructure, `acpi_kobj`, and x86 physical address width checks when applicable.

## Risks
The record walk relies on firmware record lengths and only guards against zero length; malformed lengths can skip beyond expected layout if still below table length. Some error paths after remapping do not unmap the full subtable on failure. Duplicate records are ignored after logging, so only the first instance is exposed. Address validation is architecture-specific and minimal outside x86 physical-address-width checks.

## Test Signals
Tests should include no FPDT table, invalid high physical addresses, signature/type mismatch, zero-length records, duplicate records, boot-only and S3 records, raw `FBPT`/`S3PT` binary reads, and sysfs timing attribute values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_fpdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_ipmi.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_ipmi.c

## Purpose
`acpi_ipmi.c` implements the ACPI IPMI operation-region handler. It lets AML issue IPMI commands through a selected ACPI-described BMC system interface and returns IPMI responses in the ACPI-defined request/response buffer format.

## Important APIs, Types, And Functions
Core structures are `struct acpi_ipmi_device`, `struct ipmi_driver_data`, `struct acpi_ipmi_msg`, and `struct acpi_ipmi_buffer`. Important functions include `ipmi_dev_alloc()`, `__ipmi_dev_kill()`, `acpi_ipmi_dev_get()`, `ipmi_msg_alloc()`, `acpi_format_ipmi_request()`, `acpi_format_ipmi_response()`, `ipmi_flush_tx_msg()`, `ipmi_cancel_tx_msg()`, `ipmi_msg_handler()`, `ipmi_register_bmc()`, `ipmi_bmc_gone()`, `acpi_ipmi_space_handler()`, `acpi_wait_for_acpi_ipmi()`, `acpi_ipmi_init()`, and `acpi_ipmi_exit()`.

## Control Flow
Module init installs an `ACPI_ADR_SPACE_IPMI` handler at the root and registers an IPMI SMI watcher. When an ACPI-backed BMC appears, `ipmi_register_bmc()` creates an IPMI user, records the ACPI handle, selects the first SMI if none is selected, completes the selection wait, and adds it to the device list. AML write accesses allocate a message tied to the selected SMI, format netfn/cmd from the OpRegion address, copy request data from the ACPI buffer, assign a message ID, add the message to the pending list, send it with `ipmi_request_settime()`, wait for completion, and format the response back into the ACPI buffer. The IPMI receive handler matches response message IDs, copies bounded response data, sets ACPI completion status, completes the pending request, and releases references. Exit unregisters the watcher, kills devices, flushes pending messages, and removes the address-space handler.

## State And Persistence
State is in memory: the selected SMI, list of IPMI devices, per-device pending transmit lists, message IDs, completions, dead flags, and krefs. ACPI OpRegion transactions are synchronous from AML's perspective but backed by asynchronous IPMI receive callbacks.

## Dependencies And Integration Points
It depends on ACPI address-space handling, the IPMI core, `ipmi_smi_watcher`, completions, spinlocks, krefs, and ACPI firmware using IPMI OpRegions. `acpi_wait_for_acpi_ipmi()` is exported so other ACPI code can wait briefly for BMC selection.

## Risks
The removal path in `ipmi_bmc_gone()` appears to remove an entry when `iter->ipmi_ifnum != iface`, which is surprising because the gone callback should target the matching interface; this deserves review. The code intentionally skips parsing IPMB `SEND_MESSAGE` addressing. Response handling sets `msg->recv_type = IPMI_RESPONSE_RECV_TYPE` before checking it, making that condition tautological. Timeouts and BMC removal must correctly complete and release pending messages to avoid stuck AML execution.

## Test Signals
Tests should cover no selected SMI, ACPI-backed and non-ACPI SMI registration, multiple BMCs, BMC removal, request length overflow, response length overflow, timeout completion code, pending request flush during exit, and AML write/read behavior for the IPMI OpRegion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_ipmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpat.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpat.c

## Purpose
`acpi_lpat.c` parses ACPI `LPAT` packages and provides linear conversion between raw sensor values and temperatures for thermal-related ACPI devices.

## Important APIs, Types, And Functions
Exported APIs are `acpi_lpat_raw_to_temp()`, `acpi_lpat_temp_to_raw()`, `acpi_lpat_get_conversion_table()`, and `acpi_lpat_free_conversion_table()`. The main data contract is `struct acpi_lpat_conversion_table`, containing an array of `struct acpi_lpat` raw/temperature points and a count.

## Control Flow
`acpi_lpat_get_conversion_table()` evaluates the `LPAT` object, requires a package with an even count of at least four integers, copies values into an allocated integer array, casts it as `struct acpi_lpat` points, and returns a table wrapper. Conversion functions find the adjacent segment containing the requested raw or temperature value and linearly interpolate between endpoints. The free helper releases both the point array and wrapper.

## State And Persistence
Conversion tables are caller-owned heap allocations. The file stores no global state.

## Dependencies And Integration Points
It depends on ACPI object evaluation and the public `<acpi/acpi_lpat.h>` definitions. Thermal and sensor drivers can call it when firmware provides LPAT calibration data.

## Risks
Conversion divides by `delta_raw` or `delta_temp`; malformed tables with duplicate raw or temperature endpoints can divide by zero. `temp_to_raw()` only handles ascending temperature ranges, while `raw_to_temp()` accepts either raw direction. The parser does not sort points or validate monotonicity.

## Test Signals
Tests should cover absent LPAT, malformed package count/type, successful parse/free, ascending and descending raw interpolation, out-of-range `-ENOENT`, and duplicate endpoint handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpit.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpit.c

## Purpose
`acpi_lpit.c` parses the Low Power Idle Table and exposes low-power idle residency counters through CPU sysfs attributes.

## Important APIs, Types, And Functions
The central type is `struct lpit_residency_info`, with ACPI generic address, frequency, and optional mapped MMIO address. File state is split between `residency_info_mem` and `residency_info_ffh`. Important functions are `lpit_read_residency_counter_us()`, sysfs show functions for system and CPU residency, exported `lpit_read_residency_count_address()`, `lpit_update_residency()`, `lpit_process()`, and `acpi_init_lpit()`.

## Control Flow
`acpi_init_lpit()` obtains the LPIT table and passes its body to `lpit_process()`. The processor scans native LPIT entries with type and flags zero. The first system-memory residency counter is ioremapped and exposed as `cpuidle/low_power_idle_system_residency_us`; the first fixed-hardware counter is exposed as `cpuidle/low_power_idle_cpu_residency_us`. Sysfs reads fetch either MMIO or MSR/FFH counter values, apply bit masks/offsets for FFH, and convert ticks to microseconds using the table frequency or TSC-derived fallback.

## State And Persistence
The selected counter descriptors and MMIO mapping persist after ACPI initialization. Sysfs attributes are added under the CPU subsystem root's `cpuidle` group. No teardown is present.

## Dependencies And Integration Points
It depends on ACPI LPIT structures, CPU subsystem sysfs, `ioremap`, ACPI OS MMIO reads, x86 MSR reads, TSC frequency, and cpuidle attribute grouping. `lpit_read_residency_count_address()` exports the system-memory counter address to other kernel code.

## Risks
The LPIT entry loop increments by firmware-provided `header.length` without an explicit zero-length guard, so malformed tables could hang. The MMIO mapping length is `bit_width / 8`, which assumes byte-aligned widths. Missing cpuidle sysfs group is silently ignored. No unmap/removal path exists for the ioremapped counter.

## Test Signals
Tests should include absent LPIT, memory and FFH counters, zero frequency fallback, sysfs reads, exported address read, malformed entry lengths, unsupported address spaces, and systems without a CPU root device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_lpit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_memhotplug.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_memhotplug.c

## Purpose
`acpi_memhotplug.c` registers the ACPI memory-device scan handler for `PNP0C80` and, when hotplug is enabled, turns firmware memory resource notifications into Linux memory hot-add/remove operations.

## Important APIs, Types, And Functions
Key types are `struct acpi_memory_info` for merged memory ranges and `struct acpi_memory_device` for per-device state. Important functions are `acpi_memory_get_resource()`, `acpi_memory_free_device_resources()`, `acpi_memory_get_device_resources()`, `acpi_memory_check_device()`, `acpi_bind_memory_blocks()`, `acpi_unbind_memory_blocks()`, `acpi_memory_enable_device()`, `acpi_memory_remove_memory()`, `acpi_memory_device_free()`, `acpi_memory_device_add()`, `acpi_memory_device_remove()`, `acpi_memory_hotplug_init()`, and the `acpi_no_memhotplug` setup handler.

## Control Flow
Initialization registers an ACPI scan handler, with hotplug enabled unless the boot parameter `acpi_no_memhotplug` was set. Attach allocates per-device state, walks `_CRS` resources, converts memory address resources to `acpi_memory_info` entries, merges adjacent compatible ranges, checks `_STA`, registers a static memory group, and calls `__add_memory()` for each nonempty range with `MHP_NID_IS_MGID` and `MHP_MEMMAP_ON_MEMORY`. Successfully added or preexisting memory blocks are bound to the ACPI device. Detach unbinds enabled memory blocks, calls `__remove_memory()`, frees range entries, unregisters the memory group, and clears driver data.

## State And Persistence
Per-device memory range lists, enabled flags, and memory group IDs persist while the ACPI memory device is bound. The durable system effect is added or removed system memory and ACPI companion binding on `memory_block` devices.

## Dependencies And Integration Points
It depends on ACPI scan/hotplug infrastructure, `_CRS`, `_STA`, memory hotplug APIs, memory groups, NUMA node lookup, memory block walking, and ACPI device binding helpers in `internal.h`.

## Risks
There is no rollback for earlier successful `__add_memory()` calls if later ranges fail, as noted in comments. `memory_group_unregister()` can fail when some memory remains, but the free path does not surface that strongly. Firmware range correctness is critical. The no-hotplug boot mode still registers the handler but suppresses attach, which affects enumeration expectations.

## Test Signals
Tests should cover absent/disabled `_STA`, empty resources, adjacent resource merging, multiple ranges in one device, `-EEXIST` from preexisting memory, binding failures, hot-remove, `acpi_no_memhotplug`, NUMA node selection, and memory group cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_memhotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_mrrm.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_mrrm.c

## Purpose
`acpi_mrrm.c` parses the ACPI Memory Range and Region Mapping table and reports boot memory ranges, NUMA node association, and local/remote region IDs through sysfs.

## Important APIs, Types, And Functions
The exported helper is `acpi_mrrm_max_mem_region()`. Main state includes `max_mem_region`, `struct mrrm_mem_range_entry`, `mrrm_mem_range_entry`, and `mrrm_mem_entry_num`. Key functions are `get_node_num()`, `acpi_parse_mrrm()`, generated `RANGE_ATTR()` sysfs readers, `add_boot_memory_ranges()`, and `mrrm_init()`.

## Control Flow
`mrrm_init()` parses `ACPI_SIG_MRRM`. The parser rejects unsupported revisions and OS-assigned region mode, counts memory range entries, allocates internal entries, copies base/length, resolves the NUMA node by checking online populated zones for intersection, records valid local/remote region IDs or `-1`, and updates `max_mem_region`. Sysfs setup creates `/sys/firmware/acpi/memory_ranges/rangeN` kobjects with `base`, `length`, `node`, `local_region_id`, and `remote_region_id` attributes.

## State And Persistence
Parsed MRRM data is retained in memory and exposed through sysfs for the running boot. `max_mem_region` defaults to one region if parsing is absent or fails.

## Dependencies And Integration Points
It depends on ACPI table parsing, sysfs/kobject infrastructure, `acpi_kobj`, NUMA node/zone APIs, and potential resctrl consumers of `acpi_mrrm_max_mem_region()`.

## Risks
The parser walks entries by firmware-provided lengths without explicit per-entry length validation or a zero-length guard. `local_region_id` and `remote_region_id` are `u8` but assigned `-1`, which becomes 255 while displayed with `%d`. Cleanup in `add_boot_memory_ranges()` removes child kobjects but does not keep a parent pointer for later teardown because this is boot-time-only setup.

## Test Signals
Tests should cover no MRRM table, unsupported revision, OS-assignment flag, no ranges, malformed entry lengths, valid local/remote IDs, missing IDs, NUMA node matching, sysfs range attributes, and the exported max-region value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_mrrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_pad.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_pad.c

## Purpose
`acpi_pad.c` implements the ACPI Processor Aggregator driver for `ACPI000C`. It responds to firmware requests to idle a number of CPUs by creating high-priority kernel threads that enter deep MWAIT states and rotates those threads across CPUs.

## Important APIs, Types, And Functions
Important state includes `power_saving_mwait_eax`, TSC instability flags, `cpu_weight`, `tsk_in_cpu`, `pad_busy_cpus_bits`, `idle_pct`, `round_robin_time`, `ps_tsks`, and `ps_tsk_num`. Main functions are `power_saving_mwait_init()`, `round_robin_cpu()`, `power_saving_thread()`, `create_power_saving_task()`, `destroy_power_saving_task()`, `set_power_saving_task_num()`, sysfs `idlecpus`, `idlepct`, and `rrtime` handlers, `acpi_pad_pur()`, `acpi_pad_handle_notify()`, `acpi_pad_notify()`, `acpi_pad_probe()`, `acpi_pad_remove()`, `acpi_pad_init()`, and `acpi_pad_exit()`.

## Control Flow
Init skips Xen Dom0, determines the deepest usable MWAIT hint, and registers the platform driver. Probe installs an ACPI notify handler. On notify `0x80`, the driver evaluates `_PUR`; if firmware returns a CPU count, it creates or stops power-saving threads to match, then reports status and current idle count via `_OST` and emits a netlink event. Each power-saving thread is RT-priority, periodically chooses a CPU avoiding sibling contention where possible, enters low-power MWAIT with interrupts disabled and tick broadcast coordination, sleeps enough to respect `idle_pct`, and exits its CPU assignment on stop. Sysfs can also set requested idle CPU count, idle percentage, and rotation time.

## State And Persistence
All state is runtime kernel state. Sysfs attributes reflect and mutate global driver settings. Created kthreads persist until firmware/sysfs requests fewer idle CPUs, device removal, or module exit.

## Dependencies And Integration Points
It depends on ACPI platform devices and notifications, `_PUR`/`_OST`, CPU masks and hotplug read locking, scheduler RT policy, MWAIT CPUID and idle helpers, tick broadcast, perf low-power callbacks, TSC stability handling, and Xen detection.

## Risks
This driver deliberately consumes CPU time to force package power savings; incorrect settings can impact latency and throughput. MWAIT support and TSC behavior vary by CPU vendor. The global arrays are sized by `NR_CPUS`, and hotplug/online CPU changes must remain coordinated through CPU locks. `round_robin_cpu()` leaves `preferred_cpu` uninitialized in theory if the loop never runs, though the code checks for empty masks before the loop.

## Test Signals
Tests should cover unsupported MWAIT, Xen Dom0 skip, `_PUR` success/failure, `_OST` status, sysfs bounds for `idlepct` and `rrtime`, CPU hotplug during active threads, thread creation failure, and module removal stopping all threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_pad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_pcc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_pcc.c

## Purpose
`acpi_pcc.c` installs an ACPI Platform Communications Channel address-space handler for PCC Operation Regions. It copies AML-provided buffers into PCC shared memory, sends mailbox commands, waits for interrupt completion, and copies results back.

## Important APIs, Types, And Functions
The main per-region type is `struct pcc_data`, containing a PCC mailbox channel, completion, mailbox client, and copied `struct acpi_pcc_info` context. Important functions are `pcc_rx_callback()`, `acpi_pcc_address_space_setup()`, `acpi_pcc_address_space_handler()`, and `acpi_init_pcc()`. `PCC_CMD_WAIT_RETRIES_NUM` scales timeout beyond the nominal channel latency.

## Control Flow
`acpi_init_pcc()` installs a handler for `ACPI_ADR_SPACE_PLATFORM_COMM` with `pcc_ctx` as handler context. Region setup allocates `pcc_data`, initializes the mailbox client and completion, copies PCC context fields, requests the PCC subspace channel, and requires interrupt-based transmit completion. Each AML access reinitializes completion, copies `ctx.length` bytes from the ACPI integer buffer into PCC shared memory, sends a mailbox message, waits up to `500 * latency`, marks txdone, copies shared memory back into the ACPI buffer, and returns ACPICA status.

## State And Persistence
Per-region `pcc_data` persists as ACPICA region context. PCC shared memory is external platform state. The file has no visible teardown for freeing region contexts.

## Dependencies And Integration Points
It depends on ACPICA address-space handling, `<acpi/pcc.h>`, PCC mailbox channels, Linux mailbox APIs, completions, and ACPI contexts prepared by the PCC table parser.

## Risks
`acpi_integer *value` is treated as a pointer to a buffer of `ctx.length`, which relies on ACPICA OpRegion plumbing and context correctness. Channels without interrupt txdone are rejected. Timeout sizing is arbitrary and can be too short or too long for specific platforms. Missing region-context cleanup could leak on dynamic region removal.

## Test Signals
Tests should cover handler install, missing PCC channel, non-interrupt channel rejection, successful command/response, timeout, mailbox send failure, and buffer length/context mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_pcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_platform.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_platform.c

## Purpose
`acpi_platform.c` converts eligible ACPI namespace devices into Linux platform devices, including resource translation, parent selection, DMA mask setup, and hot-remove handling.

## Important APIs, Types, And Functions
The exported API is `acpi_create_platform_device(struct acpi_device *adev, const struct property_entry *properties)`. Supporting pieces include `forbidden_id_list`, `acpi_platform_device_find_by_companion()`, `acpi_platform_device_remove_notify()`, `acpi_platform_fill_resource()`, `acpi_platform_resource_count()`, and `acpi_platform_init()`.

## Control Flow
Initialization registers an ACPI reconfiguration notifier. Device creation first skips ACPI nodes that already have physical devices except backlight cases, rejects forbidden legacy IDs, handles the SMBus virtual-device exception, collects `_CRS` resources for ordinary ACPI device nodes, copies resources while setting PCI parent resource pointers when needed, fills `platform_device_info` with parent, ACPI fwnode, optional properties, resources, and DMA mask, then calls `platform_device_register_full()`. On ACPI reconfiguration removal, the notifier finds the companion platform device and unregisters it.

## State And Persistence
Created platform devices persist in the Linux device model until unregistered. Temporary resource arrays are freed after registration because the platform core copies them. No extra file-local runtime state is kept beyond the notifier.

## Dependencies And Integration Points
It depends on ACPI scan/reconfiguration, ACPI resources, platform bus, PCI resource parenting, DMA capability checks, fwnode/property infrastructure, and legacy-device filtering coordinated with PNP support.

## Risks
Eligibility decisions are subtle: creating a platform device for a legacy PNP, IOAPIC, PIC, timer, or already-bound ACPI node can create duplicate drivers. The SMBus virtual-device exception depends on absence of resources. Hot-remove relies on ACPI companion matching and reference handling (`put_device()` after unregister).

## Test Signals
Tests should cover forbidden IDs, allowed resource-less SMBus virtual device, resource-bearing rejection, parent PCI resource assignment, DMA mask selection, physical-node skip behavior, successful platform registration, and ACPI reconfiguration removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_pnp.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_pnp.c

## Purpose
`acpi_pnp.c` identifies ACPI devices that should be treated as legacy PNP devices and registers an ACPI scan handler for a curated list of PNP-compatible IDs.

## Important APIs, Types, And Functions
The large `acpi_pnp_device_ids[]` table lists HIDs for storage, TPMs, keyboards, mice, serial/modem, IR, parallel ports, watchdogs, sound devices, touchscreens, and wildcard-style entries such as `WACFXXX`. Important functions are `matching_id()`, `acpi_pnp_match()`, `acpi_pnp_attach()`, exported `acpi_is_pnp_device()`, and `acpi_pnp_init()`.

## Control Flow
`acpi_pnp_init()` adds the scan handler. Matching compares a candidate ID to each table entry: lengths and first three bytes must match, positions 3 through 6 must be hex digits in the candidate, and the table can use `X` as a wildcard. Attach returns true to mark the ACPI device as handled by the PNP scan handler. `acpi_is_pnp_device()` checks whether a device's handler pointer is the PNP handler.

## State And Persistence
The only persistent state is the registered scan handler and handler association on matched ACPI devices. No per-device private data is allocated.

## Dependencies And Integration Points
It depends on ACPI scan infrastructure, ACPI device IDs, ctype helpers, and PNP/legacy bus coordination. `acpi_platform.c` uses related filtering to avoid creating duplicate platform devices for these classes.

## Risks
The ID table contains duplicates and many legacy IDs; changing it can alter which subsystem binds a device. `matching_id()` requires seven-character IDs, so nonstandard length IDs will not match. Wildcard behavior is limited to the numeric suffix positions.

## Test Signals
Tests should cover exact matches, lowercase hex candidate IDs, wildcard table entries, length mismatch, non-hex suffix rejection, duplicate IDs, and `acpi_is_pnp_device()` for matched and unmatched devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_pnp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_processor.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_processor.c

## Purpose
`acpi_processor.c` handles ACPI processor enumeration and early processor control negotiation. It maps ACPI processor objects/devices to Linux CPU devices, detects duplicate processor IDs, handles CPU hot-add/remove hooks, exposes per-CPU ACPI handles, initializes cpufreq platform devices, processes old PIIX4 errata, and evaluates `_CST` idle-state packages when configured.

## Important APIs, Types, And Functions
It defines per-CPU `processors`, exported `errata`, and helpers such as `acpi_get_processor_handle()`, `acpi_duplicate_processor_id()`, `acpi_processor_init()`, `acpi_processor_claim_cst_control()`, and `acpi_processor_evaluate_cst()`. Key internal functions include `acpi_processor_errata_piix4()`, `acpi_processor_errata()`, `cpufreq_add_device()`, `acpi_pcc_cpufreq_init()`, `acpi_processor_set_per_cpu()`, `acpi_processor_hotadd_init()`, `acpi_processor_get_info()`, `acpi_processor_add()`, `acpi_processor_post_eject()`, `processor_physically_present()`, `_OSC`/`_PDC` setup helpers, duplicate-ID namespace walkers, and processor/container scan handlers.

## Control Flow
Init first walks processor namespace entries and processor device HIDs to record duplicate ACPI IDs, registers the processor scan handler with hotplug support, registers processor container handling, and creates `pcc-cpufreq` if `\_SB.PCCH` exists on x86. Attach allocates `struct acpi_processor`, allocates throttling cpumask storage, reads processor ID from a `Processor` object or device `_UID`, rejects duplicate IDs, maps ACPI/physical IDs to a logical CPU, handles CPU0 fallback for UP systems without MADT entries, creates `acpi-cpufreq` if `_PCT` is present on the first processor, hot-adds a CPU if needed, stores per-CPU mappings, renames the ACPI BID to `CPU%X`, records PBLK throttling data, applies `_SUN` package ID hints, binds the ACPI device to the CPU device, and triggers CPU device driver probe. Hot-eject detaches the CPU driver, unbinds ACPI, unregisters and unmaps the CPU, clears per-CPU state, and tries to offline the NUMA node. `_CST` evaluation parses and validates package contents, maps FFH or system-I/O C-state entry methods, and populates the caller's power-state array.

## State And Persistence
Runtime state is per-CPU ACPI processor pointers, the duplicate-ID arrays, PIIX4 errata flags, processor-device companion bindings, per-processor throttling state, and cpufreq platform devices. Firmware negotiation through `_OSC`, `_PDC`, and `_CST` influences processor idle/performance behavior for the boot.

## Dependencies And Integration Points
It depends on ACPI scan and table helpers, CPU hotplug and device model APIs, architecture CPU mapping/unmapping, PCI for PIIX4 errata, cpufreq platform drivers (`acpi-cpufreq`, `pcc-cpufreq`), processor idle/throttling/performance subdrivers, Xen Dom0 processor presence handling, and namespace-specific exports for `ACPI_PROCESSOR_IDLE`.

## Risks
Processor ID mapping is firmware-sensitive; duplicate or wrong `_UID`/ProcessorID values can reject CPUs or bind the wrong ACPI companion. Hotplug paths must coordinate CPU map locks and ACPI removal locks. `processor_device_array` is intentionally not cleared on some errors for BIOS diagnostics, which can surprise cleanup reasoning. `_CST` parsing must guard malformed packages and hardware-unsupported FFH states. Legacy PBLK and PIIX4 errata behavior is architecture- and hardware-specific.

## Test Signals
Tests should cover Processor object and Device+`_UID` declarations, duplicate IDs including `0xff`, missing MADT UP fallback, `_PCT`/`PCCH` cpufreq device creation, PBLK length handling, `_SUN` package ID update, CPU hot-add and hot-remove, Xen Dom0 presence checks, `_OSC` fallback to `_PDC`, `_CST` malformed packages, FFH and system-I/O C-states, and C-state control claiming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_tad.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpi_tad.c

## Purpose
`acpi_tad.c` implements the ACPI Time and Alarm Device driver for `ACPI000E`. It exposes AC/DC wake timer controls and optional real-time clock functionality through sysfs and, when RTC support is enabled, registers an RTC class device.

## Important APIs, Types, And Functions
Important capability bits include `ACPI_TAD_AC_WAKE`, `ACPI_TAD_DC_WAKE`, `ACPI_TAD_RT`, `ACPI_TAD_RT_IN_MS`, and S4/S5 wake flags. Core types are `struct acpi_tad_driver_data` and packed `struct acpi_tad_rt`. Important functions include `acpi_tad_rt_is_invalid()`, `acpi_tad_set_real_time()`, `acpi_tad_evaluate_grt()`, `acpi_tad_get_real_time()`, wake helper methods for `_STV`, `_TIV`, `_STP`, `_TIP`, `_CWS`, and `_GWS`, sysfs handlers for time/caps/ac/dc alarm/policy/status, RTC conversions and ops, `acpi_tad_register_rtc()`, `acpi_tad_remove()`, and `acpi_tad_probe()`.

## Control Flow
Probe obtains the ACPI handle, evaluates `_GCP` capabilities, clears wake capability bits if `_PRW` is missing, suppresses DC wake unless AC wake is supported, allocates driver data, enables wakeup and runtime PM assumptions, registers cleanup, and registers an RTC if real-time support is present. Sysfs time writes parse `year:month:day:hour:minute:second:tz:daylight`, validate ranges, and call `_SRT`; reads call `_GRT`. Alarm and policy writes convert either a special string (`disabled` or `never`) or a numeric value and call `_STV` or `_STP`; reads call `_TIV` or `_TIP`. Status writes accept only zero and call `_CWS`; reads call `_GWS`. RTC alarm programming computes seconds between current TAD time and target alarm, writes AC and optional DC timers, and rolls back AC if DC programming fails while enabling.

## State And Persistence
Driver state is the capability mask and runtime PM/wakeup state. Timer values, wake policies, status bits, and real time live in platform firmware and are accessed via AML methods. Sysfs attribute visibility is derived from capabilities. On removal the driver disables AC/DC timers, clears status, suspends runtime PM, and disables runtime PM.

## Dependencies And Integration Points
It depends on ACPI platform devices, ACPI methods `_GCP`, `_PRW`, `_SRT`, `_GRT`, `_STV`, `_TIV`, `_STP`, `_TIP`, `_CWS`, and `_GWS`, runtime PM, system wakeup, sysfs attribute groups, suspend support, and optional RTC class support.

## Risks
The probe uses `if (ACPI_TAD_AC_WAKE)` instead of checking `caps & ACPI_TAD_AC_WAKE`, so wakeup/runtime driver flags are enabled unconditionally; this may be intentional-by-accident and should be reviewed. Firmware method return codes are collapsed to `-EIO`, limiting diagnostics. The TAD time parser mutates a duplicated string and requires exact colon-separated fields. RTC alarms are relative seconds and reject past or too-far targets. Runtime PM acquire macro behavior must ensure matching release through scoped cleanup.

## Test Signals
Tests should cover capability combinations, missing `_GCP`, missing `_PRW`, AC-only and AC+DC timers, sysfs visibility, all wake methods, special values `disabled` and `never`, invalid time fields, RTC read/set time, RTC alarm enable/disable, rollback when DC alarm programming fails, and removal cleanup disabling timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpi_tad.c -->
