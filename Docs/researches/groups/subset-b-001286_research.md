# Research: subset-b-001286

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_rw.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_rw.c

## Purpose
This file is a KUnit test suite for Cirrus Logic `cs_dsp` coefficient control read/write behavior. It validates that controls discovered from WMFW algorithm metadata are backed by the correct DSP memory addresses, respect volatile and access flags, use cached values when appropriate, reject invalid ranges, and behave consistently across ADSP2 16-bit, ADSP2 32-bit, and HALO DSP memory maps.

The test creates synthetic firmware and synthetic XM algorithm headers, powers up a mock DSP through the normal `cs_dsp_power_up()` path, then exercises public coefficient helpers such as `cs_dsp_coeff_lock_and_read_ctrl()` and `cs_dsp_coeff_lock_and_write_ctrl()`. It is therefore a behavioral regression suite for the control API rather than a standalone mock parser.

## Important APIs, Types, And Functions
`struct cs_dsp_test_local` holds per-test synthetic state: the mock XM header, WMFW builder, and WMFW version. `struct cs_dsp_ctl_rw_test_param` drives the parameterized cases with memory type, algorithm id, DSP-word offset, byte length, control type, and WMFW control flags.

`cs_dsp_ctl_rw_test_algs` defines four mock algorithms with distinct IDs and XM/YM/ZM base and size windows. `_find_alg_entry()` and `_get_alg_mem_base_words()` map test parameters into the expected algorithm memory base. `mock_coeff_template` is the base coefficient descriptor, usually overridden per case with memory, offset, length, and flags.

`_create_dummy_wmfw()` initializes a WMFW builder and always adds an XM header block, reflecting the driver assumption that firmware metadata can be resolved from XM. `cs_dsp_ctl_rw_test_common_init()` allocates `struct cs_dsp_test`, registers a KUnit device, initializes the mock regmap, creates the XM header, initializes ADSP2 or HALO DSP support, and registers cleanup actions for `put_device()` and `cs_dsp_remove()`.

Core exercised APIs are `cs_dsp_power_up()`, `cs_dsp_run()`, `cs_dsp_stop()`, `cs_dsp_power_down()`, `cs_dsp_coeff_lock_and_read_ctrl()`, `cs_dsp_coeff_lock_and_write_ctrl()`, `regmap_raw_read()`, and `regmap_raw_write()`. The mock utility layer contributes address conversion and cache assertions such as `cs_dsp_mock_base_addr_for_mem()`, `cs_dsp_mock_reg_addr_inc_per_unpacked_word()`, `cs_dsp_mock_regmap_drop_bytes()`, and `cs_dsp_mock_regmap_is_dirty()`.

## Control Flow
Each test builds one coefficient descriptor inside an algorithm info block, obtains a `struct firmware` from the builder, calls `cs_dsp_power_up()`, and fetches the first `struct cs_dsp_coeff_ctl` from `dsp->ctl_list`. Tests that need live hardware semantics call `cs_dsp_run()` and add a stop action; cached-control tests start and then stop the DSP so the control cache is populated.

The read/write tests cover several flows:

- Running firmware: writes should update regmap-backed DSP memory and reads should return the current register contents.
- Volatile control before run, after stop, after power-down, or after a different firmware is loaded/running: operations should fail instead of using stale or unrelated memory.
- Nonvolatile cached controls: after the DSP stops, reads and writes should use the cached control data rather than live registers.
- Partial access: offset (`seek_words`) and truncated length operations should operate on exactly the requested word-aligned portion.
- Bounds and permission errors: seek past end, length overflow, combined seek+length overflow, writes to read-only controls, and no register writes on rejected operations.

Suite definitions split ADSP2 and HALO because ADSP2 includes ZM cases while HALO test cases omit ZM. Parameter arrays expand coverage over lengths, offsets, XM/YM/ZM, algorithm IDs, and combinations of `WMFW_CTL_FLAG_READABLE`, `WMFW_CTL_FLAG_WRITEABLE`, `WMFW_CTL_FLAG_VOLATILE`, and `WMFW_CTL_FLAG_SYS`.

## State And Persistence Behavior
State is intentionally short-lived and KUnit-managed. Device references, DSP removal, and optional DSP stop actions are registered with KUnit cleanup wrappers. The driver state under test is the in-memory `dsp->ctl_list`, the mock regmap cache, the DSP running/powered state, and the per-control cache. The file does not persist data outside the test process.

The most important persistence behavior is semantic: nonvolatile controls retain cached data across stop, while volatile controls require the original firmware to be actively running. The tests also verify that failed writes do not dirty the mock regmap, which protects against partial side effects on validation errors.

## Dependencies And Integration Points
The file depends on KUnit, regmap, Linux random helpers, `linux/firmware/cirrus/cs_dsp.h`, `wmfw.h`, and `cs_dsp_test_utils.h`. It integrates with the exported KUnit-only Cirrus DSP mock framework and the real `cs_dsp` initialization and firmware load paths. The module namespaces are imported by the companion `cs_dsp_tests.c` utility module.

## Risks And Edge Cases
The test matrix is large and marked `KUNIT_SPEED_SLOW`; it can be expensive in full KUnit runs. It depends heavily on mock utility correctness, so address calculation bugs in the mocks could mask or misreport driver bugs. It also assumes word-aligned access lengths; byte-granular behavior outside whole DSP words is not the focus.

High-value risk coverage includes stale firmware ownership, volatile controls after stop/power-down, read-only/write-only flag interpretation, out-of-bounds offsets, length overflow, cache versus live-register divergence, and unexpected writes detected through dirty-regmap checks.

## Test Signals
Passing suites indicate that `cs_dsp` coefficient controls correctly resolve WMFW descriptors to DSP memory, enforce access and bounds validation, maintain nonvolatile control caches, reject stale volatile access, and avoid dirtying registers on failure across the supported ADSP2 and HALO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw.c

## Purpose
This file is the positive-path KUnit suite for loading WMFW firmware data blocks into the Cirrus `cs_dsp` mock regmap. It validates that `cs_dsp_power_up()` parses synthetic WMFW files and writes payloads to the expected DSP memory locations for ADSP2 and HALO devices, including unpacked memories, HALO packed memories, mixed packed/unpacked edge cases, large PM payloads, sparse unordered blocks, and informational blocks.

The test method is explicitly cache-oriented: the mock regmap is initialized in cache-only mode, firmware loading writes into that cache, expected written regions are read back and dropped, and a final dirty-cache assertion detects unexpected writes.

## Important APIs, Types, And Functions
`struct cs_dsp_test_local` stores the synthetic XM header, WMFW builder, and selected WMFW version. `struct cs_dsp_wmfw_test_param` parameterizes memory type and number of register blocks. `cs_dsp_wmfw_test_mock_algs` defines a single mock algorithm with XM/YM/ZM sizes so the XM header can satisfy driver metadata discovery.

The main test bodies are grouped by payload shape:

- `wmfw_write_xm_header_unpacked()` checks that the mandatory XM header is written and readable from unpacked XM.
- `wmfw_write_one_payload()`, `wmfw_write_multiple_oneblock_payloads()`, `wmfw_write_multiple_oneblock_payloads_reverse()`, and `wmfw_write_multiple_payloads_sparse_unordered()` verify single, contiguous, reverse-ordered, and sparse data block writes.
- `wmfw_write_all_unpacked_pm()` and `wmfw_write_all_packed_pm()` cover full PM region downloads.
- `wmfw_write_multiple_unpacked_mem()` and `wmfw_write_multiple_packed_unpacked_mem()` cover mixed memory regions with varying offsets and lengths.
- The `wmfw_write_packed_*_unpacked_*()` family tests HALO packed XM/YM data followed or preceded by one to three unpacked words, including separate single-word blocks.
- `wmfw_load_with_info()` verifies that WMFW info text blocks can appear before, between, and after data blocks without disrupting payload writes.

`cs_dsp_wmfw_test_common_init()` is the shared setup: allocate KUnit state, create a KUnit device, initialize the mock regmap, build and add the XM header block, initialize ADSP2 or HALO DSP operations, register `cs_dsp_remove()`, and static-stub `cs_dsp_can_emit_message()` to reduce log noise outside DEBUG builds.

## Control Flow
Each case builds one or more WMFW data or info blocks using `cs_dsp_mock_wmfw_add_data_block()` and `cs_dsp_mock_wmfw_add_info()`, converts the builder into a `struct firmware`, then invokes `cs_dsp_power_up()`. After load, the test computes the expected regmap address from the DSP memory base, register stride, packed/unpacked block size, and DSP-word offset, reads back the bytes with `regmap_raw_read()`, compares against the original random payload, drops the expected bytes from the mock regmap cache, drops the mandatory XM-header writes, and asserts the cache is clean.

The suite definitions run a HALO WMFW v3 suite and ADSP2 16-bit/32-bit suites for WMFW versions 0, 1, and 2. Parameter tables cover PM, XM, YM, ZM for ADSP2 and packed PM/XM/YM plus unpacked XM/YM for HALO over block counts from small values through boundary values such as 12-16.

## State And Persistence Behavior
All state is KUnit-scoped. Large PM payloads use `vmalloc()` and register a `vfree()` cleanup action. Firmware builders and payload allocations are per-case. No persistent system state is modified.

The behavioral persistence under test is the regmap write cache after firmware download. A clean final cache after dropping expected regions is the key invariant: it means firmware loading wrote exactly the intended payloads and no additional memory ranges.

## Dependencies And Integration Points
The file depends on KUnit, KUnit static stubs, regmap, random data generation, vmalloc, Cirrus `cs_dsp` core headers, WMFW format definitions, and `cs_dsp_test_utils.h`. It exercises the real `cs_dsp_power_up()` path and the memory-region metadata supplied by ADSP2 and HALO mock region tables. The packed/unpacked tests are tightly integrated with the mock helpers that translate packed HALO memory types to unpacked memory types and calculate block sizes.

## Risks And Edge Cases
The high-risk area is address translation between WMFW DSP-word offsets and regmap byte/register addresses, especially for packed HALO memories and mixed packed/unpacked writes. The tests intentionally stress unordered blocks, sparse placement, full-region PM writes, boundary block counts, and XM-header avoidance when writing XM test data.

One notable test fragility is the dependence on random payloads and mock block-size arithmetic; failures will usually signal either driver placement errors or mock metadata drift. The suite is slow by design.

## Test Signals
Passing suites signal that positive WMFW loading writes payload data into expected memory windows, correctly tolerates info blocks, handles packed HALO formats, preserves mixed memory region semantics, and does not perform unexpected regmap writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw_error.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw_error.c

## Purpose
This file is the negative-path KUnit suite for Cirrus `cs_dsp` WMFW parsing. It constructs valid synthetic firmware, mutates specific fields into malformed states, and verifies that `cs_dsp_power_up()` either rejects the file with an error, usually `-EOVERFLOW`, or safely tolerates cases that should be tolerated, such as unknown block types and unterminated legacy V1 names that are parsed but not stored.

The suite is focused on parser robustness: truncated files, bogus lengths, wrong magic/core type, malformed block payloads, malformed algorithm metadata, malformed coefficient metadata, and unknown blocks.

## Important APIs, Types, And Functions
`struct cs_dsp_test_local` holds the mock XM header, WMFW builder, and WMFW version. Unlike the positive WMFW suite, setup pre-populates the mock XM header directly into the regmap with `cs_dsp_mock_xm_header_write_to_regmap()` so malformed WMFW files do not need to carry the XM blob. `struct cs_dsp_wmfw_test_param` parameterizes raw block type for truncation and block-length tests.

Important test functions include:

- `wmfw_load_with_unknown_blocks()` verifies unknown block types are skipped and later valid payloads still load.
- `wmfw_err_wrong_magic()`, `wmfw_err_too_short_for_header()`, `wmfw_err_bad_header_length()`, and `wmfw_err_bad_core_type()` validate top-level WMFW header rejection.
- `wmfw_too_short_for_block_header()`, `wmfw_too_short_for_block_payload()`, and `wmfw_block_payload_len_garbage()` validate region block boundary checks.
- `wmfw_too_short_for_alg_header()` verifies algorithm info truncation handling.
- V1 tests check coefficient count overflow and legacy fixed-size name arrays without NUL terminators.
- V2/V3 tests mutate variable-length algorithm names/descriptions, coefficient counts, coefficient block size, short name, full name, and description lengths so they exceed the containing block.

`cs_dsp_wmfw_err_test_common_init()` sets up the KUnit device, mock regmap, XM header, WMFW builder, ADSP2/HALO initialization, cleanup action, and static stub for `cs_dsp_can_emit_message()` to suppress expected error logs outside DEBUG builds.

## Control Flow
Most cases follow a pattern: generate valid firmware, optionally sanity-check that it loads, power down, mutate bytes in the returned `struct firmware`, and call `cs_dsp_power_up()` again expecting failure. Header tests modify `struct wmfw_header`; block tests locate `struct wmfw_region` after the header; algorithm and coefficient tests cast the region payload to V1 fixed structs or V2+ `__le32` layouts and mutate count/length fields.

Parameterized block-type tables split valid ADSP2 block types, valid HALO block types, and intentionally invalid raw block types. Version-specific case arrays select the relevant metadata format checks: v0 has no algorithm metadata tests, v1 uses legacy algorithm/coeff structures, and v2/v3 use variable-length descriptors.

## State And Persistence Behavior
All persistent effects are KUnit-scoped. The main stateful concern is that a valid firmware load may alter DSP state before a mutation is tested, so cases call `cs_dsp_power_down()` after the sanity load. Parser failures are expected not to create usable controls or leave the DSP successfully powered with malformed firmware.

Unknown-block handling is intentionally permissive: after unknown blocks are skipped, a later valid YM payload is written and verified. Unterminated V1 names are also intended not to crash or overread; successful load with a created control and zero `subname_len` is the expected safe behavior.

## Dependencies And Integration Points
The suite depends on KUnit, KUnit static stubs, regmap, random helpers, vmalloc, Cirrus DSP/WMFW headers, and `cs_dsp_test_utils.h`. It reaches into WMFW binary layouts from `wmfw.h`, so it is tightly coupled to parser format contracts. It also uses `../cs_dsp.h` for the static-stubbed message hook.

## Risks And Edge Cases
The primary risks covered are parser overread, integer overflow, accepting malformed block lengths, stale assumptions about core type, and string length handling in both fixed V1 arrays and V2+ variable fields. The tests use boundary values such as `0x7fffffff`, `0x80000000`, `0xffffffff`, maximum byte-sized names, and maximum 16-bit descriptions.

One visible issue in the test definitions is repeated use of `wmfw_too_short_for_block_header` where payload or garbage-length invalid-block variants might have been intended. This still exercises invalid block truncation, but it leaves a narrower signal for invalid-block payload-length behavior than the naming pattern suggests.

## Test Signals
Passing suites indicate that malformed WMFW files fail closed, known unknown-block behavior remains permissive, legacy unterminated string parsing does not overrun, and variable-length V2/V3 metadata is bounded by its containing block across ADSP2 and HALO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_tests.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_tests.c

## Purpose
This is a tiny utility module for the Cirrus Logic DSP KUnit test collection. It does not define test cases itself; it provides module metadata and namespace imports needed by the separate KUnit test translation units that exercise `cs_dsp`.

## Important APIs, Types, And Functions
The file includes only `<linux/module.h>` and uses module metadata macros:

- `MODULE_DESCRIPTION("KUnit tests for Cirrus Logic DSP driver")`
- `MODULE_AUTHOR("Richard Fitzgerald <rf@opensource.cirrus.com>")`
- `MODULE_LICENSE("GPL")`
- `MODULE_IMPORT_NS("FW_CS_DSP")`
- `MODULE_IMPORT_NS("FW_CS_DSP_KUNIT_TEST_UTILS")`
- `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`

There are no functions, local types, mutable globals, init hooks, or exit hooks.

## Control Flow
There is no runtime control flow in this file. Its effect is at module build/load time through metadata and namespace import declarations. The KUnit suites are registered in sibling files with `kunit_test_suites()`.

## State And Persistence Behavior
The file owns no persistent state. The only persistent effect is module metadata in the built object.

## Dependencies And Integration Points
The namespace imports are the integration point. They allow the test module set to reference symbols exported from the Cirrus DSP firmware namespace, the Cirrus KUnit test utility namespace, and symbols explicitly exported for KUnit testing. Without these imports, modpost or runtime module loading can fail when the tests consume namespaced exports.

## Risks And Edge Cases
The main risk is maintenance drift: adding tests that require another namespaced export may require a new `MODULE_IMPORT_NS()` here or in the relevant module. Conversely, removing or renaming namespaces in the production driver or test utility exports will break the KUnit module build.

## Test Signals
A successful build/load of the Cirrus DSP KUnit test module set indicates the required exported namespaces are declared. This file has no direct assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/dmi-id.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/dmi-id.c

## Purpose
This file exports selected SMBIOS/DMI identity strings to userspace through the device model, under the `dmi` class as device `id`. It backs the familiar DMI identity attributes such as BIOS vendor/version/date, system vendor, product name/version/serial/UUID/SKU/family, board fields, chassis fields, and a DMI modalias used by udev hardware database matching.

The driver is initialized early with `arch_initcall(dmi_id_init)` and only registers when `dmi_available` is true.

## Important APIs, Types, And Functions
`struct dmi_device_attribute` extends `struct device_attribute` with a DMI field id. `sys_dmi_field_show()` reads the field id from the attribute wrapper, calls `dmi_get_system_info(field)`, and formats the returned string with a newline.

The `DMI_ATTR` and `DEFINE_DMI_ATTR_WITH_SHOW` macros define the static sysfs attributes and attach each one to a DMI field enum. Sensitive identifiers such as product serial, product UUID, board serial, and chassis serial use mode `0400`; less-sensitive descriptive fields use `0444`.

`ascii_filter()` removes spaces/control characters, DEL/non-ASCII bytes, and colon characters for modalias construction. `get_modalias()` builds a stable colon-delimited string beginning with `dmi` and then appends prefixed fields in a compatibility-preserving order. `sys_dmi_modalias_show()` exposes it as the `modalias` attribute, while `dmi_dev_uevent()` emits it as a `MODALIAS=` uevent variable.

`dmi_id_init_attr_table()` dynamically populates `sys_dmi_attributes` only with attributes whose `dmi_get_system_info()` value exists on this machine, then always appends `modalias`. `dmi_id_init()` registers the `dmi` class, allocates a device, attaches the attribute group, and registers the device.

## Control Flow
At init, the code returns `-ENODEV` if DMI is unavailable. It then builds the available-attribute table, registers the class, allocates and names the `id` device, assigns the attribute groups, and calls `device_register()`. Failure paths call `put_device()` or `class_unregister()` as appropriate.

At read time, generic attributes directly call `dmi_get_system_info()` through their stored field id. The modalias path iterates a static prefix/field table, filters each available string through a temporary allocation, appends `:<prefix><value>`, and terminates with a colon. The uevent path reserves the `MODALIAS=` key and writes the same generated modalias into the uevent buffer.

## State And Persistence Behavior
Persistent kernel state consists of the registered `dmi_class`, the allocated `dmi_dev`, and the static attribute pointer table built during init. The actual DMI strings are not copied into this driver; reads dereference the DMI core's system information. There is no module exit path because this is an early built-in style registration via `arch_initcall`.

## Dependencies And Integration Points
The file depends on the Linux DMI core (`dmi_available`, `dmi_get_system_info()`), driver core classes/devices, sysfs attribute groups, uevents, and slab allocation. It integrates with userspace through `/sys/class/dmi/id/...` and through modalias uevents consumed by udev/hwdb matching.

## Risks And Edge Cases
`sys_dmi_field_show()` assumes the attribute table only includes fields that exist; direct use on a missing field would pass NULL to `scnprintf("%s")`, so the dynamic table is important. `get_modalias()` must preserve field ordering because userspace matches on prefix-compatible modalias strings. Allocation failure while filtering a modalias field truncates the modalias rather than failing the whole read path.

Permissions are part of the security model: serial numbers and UUIDs are root-readable only, while general product descriptors are world-readable. Any permission changes can affect privacy expectations and userspace compatibility.

## Test Signals
Runtime signals are sysfs presence and content under `/sys/class/dmi/id`, a correctly generated `modalias`, and a `MODALIAS=dmi...` uevent. Build-time signals include successful registration against the DMI and driver-core APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/dmi-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/dmi-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/dmi-sysfs.c

## Purpose
This module exports raw SMBIOS/DMI table entries to userspace under `/sys/firmware/dmi/entries`. Each DMI structure becomes a kobject named `<type>-<instance>` with generic metadata attributes and an admin-only `raw` binary file. Type 15 System Event Log entries receive a specialized child kobject with decoded fields and a `raw_event_log` binary reader.

The file is distinct from `dmi-id.c`: `dmi-id.c` exposes selected identity strings, while this module exposes structured/raw table entries for privileged inspection.

## Important APIs, Types, And Functions
`struct dmi_sysfs_entry` stores a copy of the DMI header, its kobject, type-specific instance number, global position, list node, and optional child kobject. `entry_list` plus `entry_list_lock` tracks live entries for cleanup, accounting for kobject release latency.

`struct dmi_sysfs_attribute` and `DMI_SYSFS_ATTR()` define generic entry attributes: `length`, `handle`, `type`, `instance`, and `position`. `struct dmi_sysfs_mapped_attribute` and `DMI_SYSFS_MAPPED_ATTR()` support specialized attributes that require remapping/refinding the original DMI entry before display.

`find_dmi_entry()` walks DMI tables with `dmi_walk()` and uses type plus instance countdown to find the corresponding entry. `dmi_entry_length()` computes the full entry length, including formatted bytes and the trailing double-NUL string area.

The type 15 System Event Log support defines `struct dmi_system_event_log`, decoded SEL field attributes, I/O-port readers for 8-bit, 2x8-bit, and 16-bit indexed I/O when `CONFIG_HAS_IOPORT` is enabled, a physical-memory reader using `dmi_remap()`, and `raw_event_log_read()`.

`dmi_sysfs_register_handle()` is the DMI walk callback used at module init. It allocates an entry, assigns instance and position, adds a kobject to the `entries` kset, adds type-specific children when applicable, and creates the `raw` binary file.

## Control Flow
`dmi_sysfs_init()` verifies that `dmi_kobj` exists, creates an `entries` kset under it, walks all DMI entries, and registers one sysfs kobject per table entry. Errors during the walk or registration trigger `cleanup_entry_list()` and kset unregister.

Generic sysfs attribute reads call `dmi_sysfs_attr_show()`, require `CAP_SYS_ADMIN`, and dispatch to the stored show callback. Generic binary raw reads call `raw_read()`, which uses `find_dmi_entry()` and `memory_read_from_buffer()` over the full computed DMI entry length.

Specialized type 15 child attributes use parent entry identity to re-find the original DMI table entry and copy the fixed SEL header before printing individual fields. `raw_event_log_read()` re-finds the entry, copies the SEL descriptor, dispatches by access method, and reads bytes either through indexed I/O, mapped physical memory, or rejects unsupported GPNV/unknown methods with ratelimited messages.

`dmi_sysfs_exit()` cleans up all entries and unregisters the kset.

## State And Persistence Behavior
Persistent module state includes `dmi_kset`, global instance counters during init, global position count during init, and `entry_list` for kobject cleanup. Each sysfs entry keeps only the DMI header and identity metadata; full raw reads re-walk the DMI table rather than storing a full copy. Type 15 child kobjects are owned by their parent entry and released via `kobject_put()`.

The module exposes read-only state. It does not modify DMI tables or event logs, but type 15 raw reads may perform hardware I/O or physical memory reads depending on the firmware-provided access method.

## Dependencies And Integration Points
The file depends on the DMI core (`dmi_walk`, `dmi_header`, `dmi_kobj`), sysfs/kobject/kset APIs, capability checks, binary sysfs attributes, `memory_read_from_buffer()`, I/O port accessors, physical mapping helpers (`dmi_remap`, `dmi_unmap`), and module init/exit.

Its userspace integration point is `/sys/firmware/dmi/entries/<type>-<instance>/`, with admin-only generic metadata, raw table bytes, and type 15 `system_event_log` files.

## Risks And Edge Cases
The main risks are malformed firmware tables, kobject lifetime ordering, and unsafe firmware-provided System Event Log access descriptors. `dmi_entry_length()` walks until a double NUL after the formatted area; it relies on the DMI core providing valid bounded table data. Type 15 support checks that the entry is large enough for the fixed SEL structure, but the access method may still point to unavailable I/O ports or physical memory.

Permission checks are central: generic attributes enforce `CAP_SYS_ADMIN`, and binary attributes use `BIN_ATTR_ADMIN_RO`. Removing or weakening that model would expose raw platform identifiers and firmware table data more broadly.

There is a subtle lifetime convention in error paths: entries are added to `entry_list` before all sysfs files/children are created, so cleanup must tolerate partially initialized `child` pointers. The code consistently uses `kobject_put(entry->child)` and `kobject_put(&entry->kobj)` in cleanup paths.

## Test Signals
Runtime signals are successful creation of `/sys/firmware/dmi/entries`, correct per-entry names and metadata, readable admin-only raw data, correct SEL child creation for type 15 entries, and clean module unload. Error-path signals include graceful init failure when `dmi_kobj` is absent and ratelimited messages for unsupported SEL access methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/dmi-sysfs.c -->
