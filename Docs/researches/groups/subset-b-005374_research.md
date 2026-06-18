# subset-b-005374 Research

This grouped report covers the requested NVIDIA Tegra fuse, speedo, APBMISC, PMC, regulator-coupler files and TI SoC build metadata. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra.c

## Purpose

`fuse-tegra.c` is the common Tegra fuse platform driver and early boot initializer. It owns the global `struct tegra_fuse`, exports global SKU data as `tegra_sku_info`, provides an NVMEM provider for SoC eFuses, registers NVMEM cell lookups for consumers, exposes basic SoC revision attributes, and registers a `soc_device` on ARM64. It bridges the early pre-driver mapping used by boot code into the normal platform-device lifetime.

## Important APIs, Types, and Functions

The file exports `tegra_sku_info` and `tegra_fuse_readl()`. Early init helpers are `tegra_fuse_read_spare()`, `tegra_fuse_read_early()`, and `tegra_init_fuse()`. Runtime driver entry points are `tegra_fuse_probe()`, `tegra_fuse_runtime_resume()`, `tegra_fuse_runtime_suspend()`, `tegra_fuse_suspend()`, and `tegra_fuse_resume()`.

`tegra_fuse_match` maps `nvidia,tegra*-efuse` compatible strings to `struct tegra_fuse_soc` descriptors supplied by SoC-specific files. `tegra_fuse_read()` is the NVMEM `reg_read` callback and dispatches every 32-bit word through `fuse->read`. `tegra_soc_device_register()` builds a `soc_device_attribute` from chip ID, platform, revision, and the SoC-specific sysfs attribute group.

## Control Flow

Early boot calls `tegra_init_fuse()` via `early_initcall`. It first initializes APBMISC, locates the FUSE node, or falls back to hardcoded legacy Tegra ARM addresses. It maps CAR registers if available to force-enable the fuse clock before the clock framework exists, maps the FUSE region, selects the `tegra_fuse_soc`, calls its `init()` hook, prints SKU/revision/process data, and adds NVMEM cell lookup aliases.

The platform driver later probes `tegra-fuse`. Probe saves the early mapping for cleanup, remaps the platform resource through devm, handles ACPI-only SoC selection for Tegra194/234/241, gets the optional fuse clock, enables runtime PM, runs any SoC-specific `probe()` hook, registers a read-only NVMEM device named `fuse`, gets and pulses the optional reset, and unmaps the old early mapping.

Runtime reads through `tegra_fuse_readl()` defer until the platform device, clock pointer, and SoC read callback are ready. PM hooks enable/disable the fuse clock, except SoCs marked `clk_suspend_on` keep the clock active across system suspend for RAM re-repair or cluster switching requirements.

## State and Persistence Behavior

The global `fuse` pointer persists across early and normal init. Early state includes a temporary MMIO mapping and SoC descriptor. Runtime state adds `dev`, `phys`, `clk`, `rst`, `nvmem`, duplicated lookup table, and optional SoC-private fields such as Tegra20 APBDMA. The source fuses are one-time-programmed hardware state; this driver is read-only and does not persist data to files.

`tegra_sku_info` persists as a global cached summary of eFuse and APBMISC-derived SoC identity. Consumers such as speed binning, regulators, and SoC bus use that cache after early init.

## Dependencies and Integration Points

The file integrates with OF, ACPI, platform bus, clocks, resets, runtime PM, NVMEM provider/consumer lookup APIs, sysfs SoC bus, APBMISC helpers, and SoC-specific fuse implementations in the same directory. Device-tree consumers reach individual calibration cells by lookup entries installed here or by NVMEM cells from the SoC descriptors.

## Risks and Edge Cases

The singleton `fuse` is shared by early boot, normal probe, exported readers, and ACPI fallback paths. Callers before probe must be prepared for `-EPROBE_DEFER`. The early mapping is replaced during probe and must remain valid until `iounmap(base)` at the end; the devm restore action protects the pointer if probe fails. ACPI SoC selection depends on APBMISC chip ID and supports only explicitly compiled SoCs.

`tegra_fuse_read()` assumes NVMEM byte counts are word-aligned because the NVMEM config uses word size and stride 4. Misaligned future callers would silently truncate `bytes / 4`. Lookup duplication uses `kmemdup_array`; the code does not explicitly remove lookups, relying on process lifetime for this built-in driver.

## Test Signals

Useful validation includes boot on each supported Tegra compatible, legacy Tegra20/30 DT fallback, ACPI boot on Tegra194/234/241, successful `nvmem` registration, consumer lookup resolution for thermal/XUSB/SATA/GPU cells, correct `/sys/devices/soc0` family/revision fields, runtime PM clock transitions, reset pulse success, and exported `tegra_fuse_readl()` returning `-EPROBE_DEFER` before probe but data after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra20.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra20.c

## Purpose

`fuse-tegra20.c` supplies the Tegra20-specific fuse backend. Tegra20 needs APBDMA for safe runtime fuse reads, while early boot reads use direct MMIO. The file also seeds kernel randomness from SKU, straps, chip ID, process IDs, speedo IDs, and unique ID fuse words.

## Important APIs, Types, and Functions

The SoC descriptor is `tegra20_fuse_soc`. It uses `tegra20_fuse_init()` as the early init hook, `tegra20_fuse_probe()` as the runtime probe hook, and `tegra20_fuse_info` to describe a 0x1f8-byte fuse aperture with spare bits at offset 0x100.

`tegra20_fuse_read_early()` directly reads `FUSE_BEGIN + offset`. `tegra20_fuse_read()` performs a DMA_DEV_TO_MEM transfer from the fuse physical address into one coherent 32-bit buffer. `apb_dma_complete()` completes the wait object, and cleanup helpers release the APBDMA channel and coherent buffer through devm actions.

## Control Flow

Early init sets `fuse->read_early`, initializes revision data, calls Tegra20 speedo binning, and calls `tegra20_fuse_add_randomness()`. Runtime probe requests a DMA slave channel filtered to `nvidia,tegra20-apbdma`, allocates a coherent one-word buffer, initializes slave config, completion, and mutex, and installs `fuse->read = tegra20_fuse_read`.

Each runtime read resumes the fuse device, serializes through `apbdma.lock`, programs the source address, configures the DMA channel, prepares a one-word slave transfer, waits up to 50 ms, terminates on timeout, copies the value from the coherent buffer, unlocks, and drops runtime PM.

## State and Persistence Behavior

Runtime persistent state is the Tegra20 `apbdma` substructure in `struct tegra_fuse`: DMA channel, slave config, one-word coherent buffer, completion, and mutex. Fuse data itself is immutable hardware OTP. The file mutates the global `tegra_sku_info` indirectly via `tegra_init_revision()` and `tegra20_init_speedo_data()`.

## Dependencies and Integration Points

The backend depends on DMAengine, coherent DMA allocation, runtime PM, APBDMA device-tree compatibility, Tegra APBMISC/fuse public helpers, and speedo code in `speedo-tegra20.c`. The common driver calls the SoC hooks and NVMEM eventually exposes reads through this backend.

## Risks and Edge Cases

Runtime reads return zero if `pm_runtime_resume_and_get()` fails because the error is returned as `u32`. DMA setup failures also fall through to zero. That behavior can hide transient read errors from NVMEM consumers. The DMA channel filter accepts by controller compatible only, so systems with multiple matching channels rely on DMAengine channel allocation policy. Timeout warns and terminates the channel, but callers see zero rather than an error.

## Test Signals

Test APBDMA probe deferral, coherent allocation failure handling, NVMEM reads across the full Tegra20 fuse range, runtime suspend/resume around repeated reads, 50 ms timeout fault injection, early UID randomness contribution, and correct speedo/revision output on Tegra20 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra30.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra30.c

## Purpose

`fuse-tegra30.c` provides the shared direct-MMIO fuse backend for Tegra30 and newer SoCs, plus the SoC descriptor tables for Tegra30, Tegra114, Tegra124/132, Tegra210, Tegra186, Tegra194, Tegra234, and Tegra241. It declares NVMEM cells, lookup aliases, keepout ranges, fuse aperture sizes, spare offsets, speedo hooks, SoC sysfs attribute groups, and suspend clock policy.

## Important APIs, Types, and Functions

The main read callbacks are `tegra30_fuse_read_early()` and `tegra30_fuse_read()`. Early init uses `tegra30_fuse_init()` and `tegra30_fuse_add_randomness()`. Public SoC descriptors include `tegra30_fuse_soc`, `tegra114_fuse_soc`, `tegra124_fuse_soc`, `tegra210_fuse_soc`, `tegra186_fuse_soc`, `tegra194_fuse_soc`, `tegra234_fuse_soc`, and `tegra241_fuse_soc`, gated by architecture config.

NVMEM cell arrays expose thermal sensor calibration, XUSB pad calibration, SATA calibration, GPU calibration/configuration, and selected GPU PDI fields depending on SoC. Lookup arrays map those cells to platform device IDs and connection IDs such as padctl calibration, thermal sensor CPU/GPU/MEM channels, SATA calibration, and GPU calibration. Keepout arrays hide reserved fuse ranges from generic NVMEM reads on newer SoCs.

## Control Flow

For Tegra30+ SoCs, early init installs both early and runtime direct-MMIO read callbacks, initializes revision, runs an optional speedo hook, and adds manufacturing/random identity words to kernel randomness. Runtime reads enable runtime PM, read `FUSE_BEGIN + offset`, and release runtime PM.

The common fuse driver selects the SoC descriptor by compatible string or ACPI chip ID. That descriptor drives NVMEM size, spare bit location, cell table, lookup aliases, keepout table, sysfs attributes, speedo init, and whether the fuse clock must stay enabled during system suspend.

## State and Persistence Behavior

This file is mostly static immutable SoC metadata. Runtime state lives in the common `struct tegra_fuse`. eFuse contents are read-only OTP. `tegra30_fuse_init()` updates global SKU/process/speed data through `tegra_init_revision()` and SoC-specific speedo init functions. NVMEM keepouts persist as provider policy for reserved regions.

## Dependencies and Integration Points

The file depends on Linux NVMEM provider/consumer data structures, runtime PM, Tegra public fuse APIs, and speedo implementations. Consumer integration is explicit: thermal, XUSB padctl, SATA, and GPU drivers can request named cells without embedding fuse offsets.

## Risks and Edge Cases

Direct runtime reads return zero when runtime PM resume fails, hiding errors from consumers. Keepout correctness is security- and stability-sensitive on newer SoCs: missing a reserved range could expose or read protected fuse fields; overly broad keepouts can break consumers. Cell offsets differ subtly between Tegra114, Tegra124, and Tegra210 thermal layouts. Tegra241 uses a very large aperture and a broad keepout from 0x0c to 0x1600c, so boundary testing matters.

## Test Signals

Validate NVMEM provider size and keepout enforcement on every descriptor, lookup resolution for each named consumer, direct reads under runtime PM, early randomness paths, speedo hook invocation, suspend behavior for Tegra124 `clk_suspend_on`, and DT/ACPI matching for Tegra186+ systems. Thermal, XUSB, SATA, and GPU probe success are practical integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse.h -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse.h

## Purpose

`fuse.h` is the private header for the Tegra fuse/APBMISC implementation. It defines the common fuse device model, SoC descriptor contract, early/runtime read hooks, NVMEM metadata hooks, Tegra20 APBDMA state, and declarations shared by fuse core, speedo files, APBMISC, and SoC-specific fuse descriptors.

## Important APIs, Types, and Functions

`struct tegra_fuse_info` describes the fuse read callback, NVMEM size, and spare-bit base. `struct tegra_fuse_soc` is the per-SoC operations and metadata table: `init`, `speedo_init`, optional `probe`, `info`, NVMEM lookup/cell/keepout arrays, SoC sysfs attributes, and `clk_suspend_on`. `struct tegra_fuse` stores runtime device state, MMIO base and physical address, clock/reset handles, early and runtime read callbacks, SoC descriptor, Tegra20 APBDMA resources, NVMEM device, and duplicated lookup table.

The header declares APBMISC initialization and revision helpers, early fuse read helpers, SoC attribute groups, speedo init functions, and all SoC descriptor symbols guarded by architecture config.

## Control Flow

No executable logic is present. The header defines the call boundary: common code selects a `tegra_fuse_soc`, calls `init()` during early boot, later calls optional `probe()` during platform probe, and uses `info->read` or `fuse->read` to serve NVMEM and exported reads. Speedo init functions receive a mutable `struct tegra_sku_info`.

## State and Persistence Behavior

The structures describe volatile kernel state around immutable eFuse OTP data. `struct tegra_fuse` persists for the boot lifetime. The APBDMA members persist only for Tegra20 runtime reads. NVMEM cells and keepouts are static metadata used to expose or hide fuse regions.

## Dependencies and Integration Points

The header depends on DMAengine and NVMEM type declarations and integrates with public Tegra SoC headers for `struct tegra_sku_info` and enum/config constants. It is included by fuse core, Tegra20/Tegra30 fuse backends, speedo implementations, and APBMISC code.

## Risks and Edge Cases

Because this is a private cross-file contract, changing fields in `struct tegra_fuse_soc` or `struct tegra_fuse` requires auditing all SoC descriptors and the common probe path. Read callbacks return `u32`, so backend errors cannot be represented directly and commonly collapse to zero. Architecture guards must match the symbols referenced from `tegra_fuse_match`; missing guards cause link failures or unsupported SoCs at boot.

## Test Signals

Build all relevant `CONFIG_ARCH_TEGRA_*` combinations, especially mixed ARM/ARM64 and ACPI-capable configurations. Validate all descriptors link, NVMEM cells compile with the current provider API, and SoC speedo init declarations match their implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra114.c

## Purpose

`speedo-tegra114.c` converts Tegra114 SKU, revision, and speedo fuse values into CPU and SoC speedo IDs and process IDs stored in `struct tegra_sku_info`. These bins are consumed by later voltage, clock, and SoC policy code.

## Important APIs, Types, and Functions

The exported init hook is `tegra114_init_speedo_data()`. Internal logic is `rev_sku_to_speedo_ids()`, which maps SKU IDs to CPU/SoC speedo IDs and threshold table index. Static threshold arrays `cpu_process_speedos` and `soc_process_speedos` define two process corners per threshold index.

## Control Flow

The common fuse init path calls `tegra114_init_speedo_data()` after revision/SKU data is known. The function checks threshold-table sizes at build time, derives speedo IDs from SKU, applies an A01-specific fuse override for CPU speedo ID, reads CPU speedo from fuse 0x12c plus 1024 and SoC speedo from fuse 0x134, then scans the threshold arrays to assign process IDs.

## State and Persistence Behavior

The only mutable state is the caller-provided `tegra_sku_info`: CPU speedo ID, SoC speedo ID, CPU process ID, and SoC process ID. Fuse values are read-only and threshold tables are immutable.

## Dependencies and Integration Points

It depends on early fuse reads and the revision/SKU values already populated by APBMISC/fuse core. It integrates through `tegra114_fuse_soc.speedo_init` in `fuse-tegra30.c`.

## Risks and Edge Cases

Unknown SKUs log an error and fall back to speedo IDs 0/0 and threshold index 0, which may be conservative but can mis-bin unusual silicon. The A01 override reads two raw fuse offsets and sets CPU speedo ID to 0 if both are zero. Threshold arrays include a zero row for one index, so any positive speedo value selects process ID 1 for that SKU class.

## Test Signals

Validate known Tegra114 SKUs 0x00, 0x10, 0x05, 0x06, 0x03, and 0x04, A01 override behavior, unknown SKU logging, and resulting regulator/clock OPP selection derived from `tegra_sku_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra124.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra124.c

## Purpose

`speedo-tegra124.c` bins Tegra124/Tegra132 silicon by reading CPU, GPU, SoC speedo and IDDQ fuses and mapping SKU IDs into CPU/GPU/SoC speedo IDs plus process IDs.

## Important APIs, Types, and Functions

The public hook is `tegra124_init_speedo_data()`. `rev_sku_to_speedo_ids()` maps SKU values to speedo IDs and threshold index. Constants name fuse offsets for CPU speedo words, SoC speedo words, CPU/SOC/GPU IDDQ, and FT revision. Threshold arrays cover CPU, GPU, and SoC process corners.

## Control Flow

The hook verifies threshold array dimensions, reads `FUSE_CPU_SPEEDO_0`, and returns early with a warning if it is zero. It reads GPU speedo from `FUSE_CPU_SPEEDO_2`, SoC speedo from `FUSE_SOC_SPEEDO_0`, derives speedo IDs from SKU, stores CPU IDDQ, and scans GPU, CPU, and SoC threshold arrays to assign process IDs. It logs GPU speedo ID/value at debug level.

## State and Persistence Behavior

The function mutates `tegra_sku_info` fields for CPU/GPU/SOC speedo IDs, speedo values, process IDs, and CPU IDDQ. It does not persist anything outside the boot-lifetime SKU cache.

## Dependencies and Integration Points

It depends on early fuse reads and is selected by the Tegra124/132 fuse descriptor. Downstream consumers include OPP, voltage, thermal, and GPU/CPU policy code that consults the global SKU information.

## Risks and Edge Cases

A missing CPU speedo fuse causes an early return after `WARN_ON(1)`, leaving many fields at previous/default values. Unknown SKUs log an error and use default speedo IDs/thresholds. Some named fuse offsets such as `FUSE_FT_REV`, `FUSE_CPU_SPEEDO_1`, `FUSE_SOC_SPEEDO_1/2`, `FUSE_SOC_IDDQ`, and `FUSE_GPU_IDDQ` are defined but unused, so future changes should avoid assuming all available calibration words are incorporated.

## Test Signals

Exercise known SKU cases 0x00, 0x0f, 0x23, 0x83, 0x1f, 0x87, 0x27, 0x81, 0x21, 0x07, 0x49, 0x4a, and 0x48. Validate zero CPU speedo behavior, assigned GPU process IDs, CPU IDDQ capture, and OPP/regulator behavior for Tegra124 and Tegra132 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra20.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra20.c

## Purpose

`speedo-tegra20.c` derives Tegra20 CPU and SoC process bins from spare fuse bits. It handles redundant speedo bit storage, revision/SKU-based speedo ID selection, and threshold lookup for early boot SKU state.

## Important APIs, Types, and Functions

The public hook is `tegra20_init_speedo_data()`. Macros define CPU and SoC speedo bit ranges, redundant bit offsets, a `SPEEDO_MULT` of 4, and SKU/revision speedo-ID selection rules. Static threshold arrays map three speedo IDs to four process corners for CPU and SoC.

## Control Flow

The hook chooses `soc_speedo_id` from revision and SKU: older revisions get ID 0, most SKUs get ID 1, and a small SKU set gets ID 2. It then reads CPU speedo bits from MSB to LSB, ORing primary and redundant spare bits, multiplies the accumulated value by four, logs it, and scans the CPU threshold row to assign `cpu_process_id`. It repeats the same pattern for SoC speedo bits and `soc_process_id`.

## State and Persistence Behavior

The function mutates the boot-lifetime `tegra_sku_info` fields for SoC speedo ID, CPU process ID, and SoC process ID. It reads immutable spare fuse bits only.

## Dependencies and Integration Points

It depends on `tegra_fuse_read_spare()` and the revision/SKU fields initialized by fuse/APBMISC code. It is selected by `tegra20_fuse_soc.speedo_init` and indirectly used by Tegra20 voltage and frequency policy.

## Risks and Edge Cases

Redundant bits are ORed with primary bits, so any blown redundant bit can force a one. The code sets only `soc_speedo_id`; CPU thresholds also index by that same value, which is intentional for this SoC but easy to misread. SKU selection macros encode historical SKU exceptions and need hardware validation before updates.

## Test Signals

Validate speedo extraction from spare bits including redundant-bit cases, process IDs for all three speedo ID rows, SKU exception handling for 20/23/24/27/28, and downstream Tegra20 regulator nominal voltage selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra210.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra210.c

## Purpose

`speedo-tegra210.c` bins Tegra210 CPU, GPU, and SoC silicon using speedo revision spare bits, raw speedo fuse words, revision/SKU rules, and threshold arrays. It supports multiple speedo fusing revisions with different calibration formulas.

## Important APIs, Types, and Functions

The public hook is `tegra210_init_speedo_data()`. `get_speedo_revision()` reads spare bits 2..4. `rev_sku_to_speedo_ids()` maps chip revision and SKU to CPU/GPU/SoC speedo IDs and threshold index. `get_process_id()` scans threshold arrays. Constants name CPU and SoC speedo fuse offsets plus IDDQ offsets.

## Control Flow

The init hook reads three CPU speedo words and three SoC speedo words, derives speedo revision, and computes final CPU/GPU/SoC speedo values. Revision >= 3 uses raw values; revision 2 applies linear correction formulas; older revisions use defaults for CPU/SoC and GPU as CPU_SPEEDO_2 minus 75. If any resulting value is nonpositive, the function warns and returns. Otherwise it assigns speedo IDs from SKU/revision and computes process IDs with per-domain threshold arrays.

## State and Persistence Behavior

The function mutates `tegra_sku_info` fields for speedo values, speedo IDs, and process IDs. It does not currently store IDDQ values despite defining IDDQ offsets. All source calibration data is immutable fuse state.

## Dependencies and Integration Points

It depends on early fuse reads and the global revision/SKU initialization. `tegra210_fuse_soc` wires this function as its speedo hook. Consumers include Tegra210 OPP, clock, GPU, thermal, and regulator policy.

## Risks and Edge Cases

`gpu_process_speedos` rows contain `UINT_MAX` for both corners, so valid GPU speedo values select process ID 0 with current data. `get_process_id()` can return `-EINVAL` if no threshold is greater, and those negative process IDs are stored directly. Unknown SKUs log errors but retain default speedo IDs and thresholds. Older speedo revisions use hardcoded default CPU/SoC values, so silicon binning accuracy depends on the correctness of revision detection.

## Test Signals

Test speedo revisions 0, 2, and 3+, all known SKUs for A02+ and pre-A02 handling, nonpositive fuse value warning, negative process-ID paths, and downstream OPP/regulator choices. Debug logs should report speedo revision and GPU speedo ID/value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra30.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra30.c

## Purpose

`speedo-tegra30.c` implements Tegra30 speedo calibration and binning. It decodes CPU/G and LP speedo values from fuse calibration words and spare bits, maps revision/SKU/package combinations to speedo IDs and threshold rows, and assigns CPU/SoC process IDs.

## Important APIs, Types, and Functions

The public hook is `tegra30_init_speedo_data()`. `fuse_speedo_calib()` reads `FUSE_SPEEDO_CALIB_0`, `FUSE_TEST_PROG_VER`, and correction spare bits to produce CPU/G and LP speedo values. `rev_sku_to_speedo_ids()` handles revision, SKU, and package ID mapping. Threshold arrays cover 12 threshold indices with CPU and SoC process corners.

## Control Flow

The init hook validates threshold table dimensions, maps revision/SKU/package into CPU speedo ID, SoC speedo ID, and `threshold_index`, reads calibrated speedo values, logs them, scans CPU thresholds to set `cpu_process_id`, and scans SoC thresholds to set `soc_process_id`. If either scan underflows to -1, it warns and forces process ID 0 and speedo ID 1 for that domain.

`fuse_speedo_calib()` multiplies two 16-bit fields by four, then either appends low correction bits from spare fuses for ATE program version >= 26 or forces both low bits to one for older test program versions.

## State and Persistence Behavior

The file mutates `tegra_sku_info` speedo IDs and process IDs. `threshold_index` is static `__initdata`, used only during boot. No persistent storage is written.

## Dependencies and Integration Points

It depends on early fuse reads, spare fuse reads, package info, test program version, and revision/SKU data from common fuse init. The Tegra30 SoC descriptor selects it through `speedo_init`.

## Risks and Edge Cases

The mapping table is complex and SKU/package-specific. Unknown package IDs log errors but may leave speedo IDs and threshold index at whatever was previously assigned in that switch path. CPU/SOC process assignment intentionally stores `i - 1`, making underflow possible and handled afterward. The help string has no direct effect, but binning mistakes can propagate into voltage/frequency policy.

## Test Signals

Validate all documented SKU/package combinations, ATE version below and above 26, spare-bit correction paths, unknown SKU/package warnings, underflow handling, and resulting Tegra30 regulator nominal voltage and OPP choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/tegra-apbmisc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/tegra-apbmisc.c

## Purpose

`tegra-apbmisc.c` initializes and exposes Tegra APBMISC and strapping registers used for chip ID, revision, platform type, RAM code, and selected error-response control. It supports early device-tree initialization, legacy ARM hardcoded addresses, and ACPI initialization for newer systems.

## Important APIs, Types, and Functions

Exported/global APIs include `tegra_read_chipid()`, `tegra_get_chip_id()`, `tegra_get_major_rev()`, `tegra_get_minor_rev()`, `tegra_get_platform()`, `tegra_is_silicon()`, `tegra_read_straps()`, `tegra_read_ram_code()`, `tegra194_miscreg_mask_serror()`, `tegra_init_revision()`, `tegra_init_apbmisc()`, and `tegra_acpi_init_apbmisc()`.

Static state includes `apbmisc_base`, `long_ram_code`, `strapping`, and `chipid`. `apbmisc_match` covers Tegra20 APBMISC and Tegra186/194/234/264 misc compatibles.

## Control Flow

`tegra_init_apbmisc()` locates a matching DT node or legacy Tegra ARM addresses, extracts APBMISC and strap resources, maps APBMISC long-term, reads chip ID from offset 4, maps straps briefly, reads strap value, and records whether DT requested a long RAM code mask. `tegra_acpi_init_apbmisc()` finds ACPI HID `NVDA2010`, reads memory resources, and initializes the same cached state.

`tegra_init_revision()` derives `tegra_sku_info.revision` from the APBMISC minor revision, handles Tegra20 A03 prime detection via spare fuses 18/19, reads SKU from fuse offset 0x10, and stores platform.

## State and Persistence Behavior

`chipid`, `strapping`, and `long_ram_code` are boot-lifetime cached hardware values. `apbmisc_base` remains mapped for exported register writes such as `tegra194_miscreg_mask_serror()`. No file-backed persistence exists. `tegra194_miscreg_mask_serror()` writes the ERD config register to mask inband errors on Tegra194 only.

## Dependencies and Integration Points

This file integrates with OF/ACPI resource discovery, Tegra common SoC helpers, public fuse APIs, and users of chip/revision/platform/RAM-code data throughout the Tegra SoC code. The fuse driver calls APBMISC init before revision and speedo binning.

## Risks and Edge Cases

`tegra_init_apbmisc()` calls `of_property_read_bool(np, ...)` after the legacy path where `np` may be NULL; current OF helper behavior tolerates NULL on many kernels, but it is a fragile pattern. Accessors warn if `chipid` is zero but still return cached zero-derived fields. `tegra194_miscreg_mask_serror()` is guarded by machine compatibility and base availability; callers must handle `-EPROBE_DEFER` and `-EOPNOTSUPP`.

## Test Signals

Validate DT and ACPI init, legacy ARM fallback, chip ID/revision/platform decoding, RAM code short and long masks, Tegra20 A03 prime detection, and `tegra194_miscreg_mask_serror()` success/failure on Tegra194 versus other SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/tegra-apbmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/pmc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/pmc.c

## Purpose

`pmc.c` is the central NVIDIA Tegra Power Management Controller driver. It handles early PMC register access, powergate control, generic PM domains, core-domain OPP/regulator synchronization, CPU powergate helpers, I/O pad deep-power-down and voltage pinconf, wake IRQ routing, suspend wake-status handling, PMC clocks, reboot/power-off scratch programming, reset reason sysfs, USB sleepwalk regmap exposure, and SoC data tables for Tegra20 through Tegra264.

## Important APIs, Types, and Functions

Public/exported APIs include `devm_tegra_pmc_get()`, `tegra_pmc_powergate_power_on/off()`, legacy global `tegra_powergate_power_on/off()`, `tegra_pmc_powergate_remove_clamping()`, `tegra_powergate_remove_clamping()`, `tegra_pmc_powergate_sequence_power_up()`, `tegra_powergate_sequence_power_up()`, CPU helpers `tegra_pmc_cpu_is_powered()`, `tegra_pmc_cpu_power_on()`, `tegra_pmc_cpu_remove_clamping()`, I/O pad helpers `tegra_pmc_io_pad_power_enable/disable()` and global wrappers, suspend helpers under PM sleep, and `tegra_pmc_core_domain_state_synced()`.

Key private structures are `struct tegra_pmc`, `struct tegra_pmc_soc`, `struct tegra_powergate`, `struct tegra_pmc_core_pd`, `struct tegra_io_pad_soc`, `struct tegra_io_pad_vctrl`, `struct tegra_pmc_regs`, and `struct tegra_wake_event`. SoC descriptors encode powergate names, CPU gate IDs, pad tables, wake events, reset strings, register offsets, TrustZone-only possibility, clock support, USB sleepwalk support, and per-SoC callbacks.

## Control Flow

`tegra_pmc_early_init()` runs at early init, maps PMC MMIO, matches SoC data, detects TrustZone-only access on Tegra210-like systems by scratch write/read probing, initializes the powergate availability bitmap, and applies interrupt polarity. Later the built-in platform driver probes, parses suspend DT properties, remaps normal resources, maps wake/aotag/scratch apertures or aliases them for single-aperture SoCs, registers reboot and sys-off handlers, caches `pclk` rate with a clock notifier, initializes SoC-specific PMC state, configures thermal trip scratch registers, adds reset sysfs files, registers pinctrl, regmap, powergates/genpd, IRQ domain, replaces the early mapping, registers PMC clocks, initializes suspend, sets wake filters, and creates debugfs `powergate`.

Powergate sequencing asserts resets, toggles powergate state through Tegra20 or Tegra114+ register protocols, temporarily lowers clock rates to a safe 100 MHz before enabling, removes clamps, deasserts resets, runs Tegra210 MBIST workaround if needed, disables clocks if requested, and restores rates. Power-down reverses this through reset assertion, clock disable, powergate off, and rate restoration. OF powergate nodes become generic PM domains and are removed from legacy direct API availability.

I/O pad operations find pad metadata, optionally program DPD sample timing from `pclk`, write OFF/ON request codes, poll status, and expose low-power mode and power-source pinconf. Wake IRQ flow allocates a hierarchical IRQ domain, maps PMC wake IDs to parent GIC IRQs or GPIO/simple wake endpoints, programs wake masks/types, handles dual-edge wake polarity flipping on suspend, reads wake status on resume, and replays mapped IRQs through hard IRQ work.

## State and Persistence Behavior

The singleton `pmc` persists from early boot. It caches MMIO bases, clock rate, suspend timers and mode, LP0 vector, available powergate bitmap, lock, pinctrl and IRQ domain, wake bitmaps, wake status, reboot notifier, syscore state, and SoC descriptor. Hardware state persists in PMC registers: powergate state, clamp state, wake masks/types/status, scratch reboot reason, reset source/level, DPD pad state, pad voltage controls, thermal reset scratch values, and PMC clock mux/gate state.

No file-backed persistence is used, but scratch registers intentionally communicate reboot mode to firmware/bootloader and may survive warm resets depending on hardware. `core_domain_state_synced` becomes true only after driver sync-state for SoCs that support the core domain and is used by regulator couplers to relax boot voltage limits.

## Dependencies and Integration Points

The driver integrates with OF platform resources, ARM SMCCC, clocks and clock providers, resets, generic PM domains, OPP/regulators, pinctrl/pinconf, IRQ domains, wake IRQ hierarchy, syscore suspend/resume, reboot/sys-off, power supply, debugfs, regmap, USB sleepwalk consumers, Tegra clock MBIST workaround, Tegra fuse/APBMISC/common suspend helpers, and DT bindings for Tegra powergates, I/O pads, GPIOs, and interrupts.

## Risks and Edge Cases

This driver is high blast-radius hardware code. The global singleton and early mapping handoff require careful ordering; public APIs can be called before full platform probe. TrustZone-only detection writes scratch registers during early boot and must restore them. Powergate sequencing depends on correct reset arrays, clocks, rate restoration, and SoC-specific clamp behavior; a failure can leave devices reset, clocks changed, or domains unavailable. `tegra_pmc_powergate_sequence_power_up()` allocates `pg->clk_rates` but on that allocation failure attempts `kfree(pg->clks)` even though `pg->clks` was never allocated in that path, which is harmless for NULL but signals a stale cleanup pattern.

Wake handling is subtle for dual-edge events: suspend samples raw state, flips polarity for asserted dual-edge wake sources, clears status, and later replays wake IRQs. Incorrect wake event tables or parent IRQ mappings can break suspend/resume. SoC tables are large and offset-heavy; wrong DPD/status/vctrl offsets can cut power to active pads or misreport voltage. `tegra_pmc_sync_state()` marks core-domain sync only when DT contains `core-domain` and the SoC supports it, so regulator couplers must tolerate older DTs staying unsynced.

## Test Signals

Validation should cover early init and probe on every compatible, TrustZone-only Tegra210 access, reset reason/level sysfs, reboot commands `recovery`, `bootloader`, and `forced-recovery`, power-off handler on Nexus 7 charger mode, legacy and genpd powergate on/off, reset/clamp sequencing, MBIST workaround paths, pclk rate-change notifier locking, I/O pad low-power and 1.8V/3.3V pinconf, wake IRQ set_wake/type for Tegra210 and Tegra186+, SC7 suspend/resume wake replay, USB sleepwalk regmap access ranges, PMC clock output mux/gate operations, and `sync_state` regulator synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra20.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra20.c

## Purpose

`regulators-tegra20.c` registers a Tegra20-specific regulator coupler that keeps CPU, core, and RTC rails within hardware voltage relationships across DVFS, suspend, and reboot. It compensates for incomplete core-voltage scaling by holding safe minimum voltages until PMC core-domain state is synchronized.

## Important APIs, Types, and Functions

The file defines `struct tegra_regulator_coupler` with a generic `regulator_coupler`, attached core/CPU/RTC regulator devices, reboot and suspend notifiers, cached boot/min voltages, and requested/current reboot/suspend mode flags. The coupler callbacks are `tegra20_regulator_attach()`, `tegra20_regulator_detach()`, and `tegra20_regulator_balance_voltage()`.

Important helpers include `tegra20_core_limit()`, `tegra20_core_rtc_max_spread()`, `tegra20_cpu_nominal_uV()`, `tegra20_core_nominal_uV()`, `tegra20_core_rtc_update()`, `tegra20_core_voltage_update()`, `tegra20_cpu_voltage_update()`, and suspend/reboot preparation notifiers.

## Control Flow

At `arch_initcall`, the file checks `of_machine_is_compatible("nvidia,tegra20")`, registers reboot and PM notifiers, and registers the coupler. Regulator attach identifies rails by DT boolean properties `nvidia,tegra-core-regulator`, `nvidia,tegra-rtc-regulator`, and `nvidia,tegra-cpu-regulator`.

On balance, the coupler verifies the regulator and `PM_SUSPEND_ON` state, snapshots requested reboot/suspend flags, and either updates CPU then core/RTC or updates core/RTC based on the initiating rail. CPU changes raise core/RTC before CPU when CPU voltage rises, and lower CPU before core/RTC when CPU voltage falls. Core/RTC updates step both rails while respecting RTC-core max spread, CPU-to-core/RTC minimum offset, regulator constraints, consumer constraints, suspend nominal voltages, and reboot restoration of boot CPU voltage.

## State and Persistence Behavior

The coupler caches `core_min_uV` from boot or board constraints until `tegra_pmc_core_domain_state_synced()` allows full scaling. It caches `cpu_min_uV` boot voltage for reboot restoration. Reboot/suspend flags are communicated through `WRITE_ONCE`/`READ_ONCE`. Hardware regulator voltages persist until changed by the regulator framework, suspend, reboot, or bootloader.

## Dependencies and Integration Points

It depends on the regulator coupler internals, regulator constraints/consumer APIs, PM/reboot notifier chains, OF machine compatibility, `tegra_sku_info.soc_speedo_id`, and `tegra_pmc_core_domain_state_synced()`. It requires DT coupling metadata including max-spread entries and rail-identifying boolean properties.

## Risks and Edge Cases

The RTC rail cannot be changed directly; attempts return `-EPERM`. Missing max-spread falls back to 150 mV with an error. If no CPU consumers exist, CPU voltage is held at current value to avoid undervolting a running CPU at unknown frequency. The code logs existing constraint violations but proceeds to calculate a safe sequence. Notifier registration warnings do not abort coupler registration.

## Test Signals

Test attach/detach for all three rails, CPU voltage raise/lower sequencing, core-only updates, missing max-spread fallback, suspend prepare/post suspend nominal voltage transitions, reboot boot-voltage restoration, unsynced versus synced PMC core-domain behavior, regulator constraint failure injection, and no-consumer CPU rail behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra30.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra30.c

## Purpose

`regulators-tegra30.c` registers a Tegra30 regulator coupler for the CPU and core rails. It enforces Tegra30 CPU/core voltage spread and process-bin-specific core limits during DVFS, suspend, and reboot.

## Important APIs, Types, and Functions

`struct tegra_regulator_coupler` stores the generic coupler, core and CPU regulator devices, reboot/suspend notifiers, cached minimum voltages, and requested/current system mode flags. Coupler callbacks are `tegra30_regulator_attach()`, `tegra30_regulator_detach()`, and `tegra30_regulator_balance_voltage()`.

Key helpers are `tegra30_core_limit()`, `tegra30_core_cpu_limit()`, `tegra30_cpu_nominal_uV()`, `tegra30_core_nominal_uV()`, `tegra30_voltage_update()`, `tegra30_regulator_prepare_suspend()`, and `tegra30_regulator_prepare_reboot()`.

## Control Flow

At `arch_initcall`, the file checks for `nvidia,tegra30`, registers reboot and PM notifiers, and registers the coupler. Attach binds regulators identified by `nvidia,tegra-core-regulator` and `nvidia,tegra-cpu-regulator`.

Every balance request validates that the initiator is CPU or core and active state is `PM_SUSPEND_ON`, snapshots system mode flags, and calls `tegra30_voltage_update()`. That function obtains max spread and max step constraints with fallbacks, holds the core minimum until PMC core-domain sync, applies consumer constraints, computes CPU minimum from core spread and consumers, caches boot CPU voltage, calculates core minimum required for the current and target CPU voltage via `tegra30_core_cpu_limit()`, applies reboot/suspend overrides, then loops CPU and core voltages toward target values in bounded steps while maintaining spread limits.

## State and Persistence Behavior

The coupler caches the boot/current CPU voltage in `cpu_min_uV` and a boot-derived safe `core_min_uV` until safe core-domain sync. Reboot and suspend requested flags persist through notifier transitions and are observed during the next balance. Actual voltage changes persist in regulator hardware.

## Dependencies and Integration Points

It depends on OF machine compatibility, the regulator coupler framework, regulator constraints/consumer APIs, PM/reboot notifiers, Tegra fuse-derived `tegra_sku_info.cpu_speedo_id` and `soc_speedo_id`, and PMC core-domain sync state. Device tree must provide coupled regulator constraints and identifying properties.

## Risks and Edge Cases

Missing max-spread or max-step constraints fall back to 300 mV and 150 mV with error logs, which may be conservative but may not match board hardware. `tegra30_core_cpu_limit()` returns `-EINVAL` for CPU voltages >= 1.25 V, aborting updates. If no CPU consumers exist, the CPU rail is held no lower than current. Reboot/suspend notifiers set flags and force regulator syncs; failures propagate through notifier errno and may block transitions.

## Test Signals

Test voltage increase/decrease sequences with max-step limits, spread violation repair, speedo-ID branches for nominal voltages and core limits, missing DT constraint fallbacks, no-consumer CPU rail protection, suspend prepare/post paths, reboot restoration, and behavior before and after PMC core-domain sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/regulators-tegra30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/Kconfig

## Purpose

`drivers/soc/ti/Kconfig` defines the TI SoC driver configuration menu and feature symbols for Keystone Navigator QMSS/DMA, AMx3 power management, Wakeup M3 IPC, K3 ring accelerator, K3 SoC info, PRUSS platform support, and the internal TI SCI Interrupt Aggregator MSI domain.

## Important APIs, Types, and Functions

This is build metadata, not C code. Top-level `menuconfig SOC_TI` gates most visible TI SoC driver options. Symbols include `KEYSTONE_NAVIGATOR_QMSS`, `KEYSTONE_NAVIGATOR_DMA`, `AMX3_PM`, `WKUP_M3_IPC`, `TI_K3_RINGACC`, `TI_K3_SOCINFO`, `TI_PRUSS`, and `TI_SCI_INTA_MSI_DOMAIN`.

Dependencies encode architecture and subsystem requirements: Keystone options depend on `ARCH_KEYSTONE`; AMx3 PM depends on AM33xx/AM43xx plus Wakeup M3 IPC, EMIF SRAM, SRAM, and OMAP RTC; WKUP M3 IPC depends on remoteproc and mailbox support; K3 RingACC depends on K3 or compile test plus TI SCI INTA irqchip; K3 SoC info selects `SOC_BUS` and `MFD_SYSCON`; PRUSS covers AM33xx/AM43xx/DRA7xx/Keystone/K3 or compile test.

## Control Flow

Kconfig evaluation exposes `SOC_TI`; if selected, it exposes the driver options inside the menu. Selected/tristate values drive `drivers/soc/ti/Makefile` object inclusion. `TI_SCI_INTA_MSI_DOMAIN` sits outside the menu as an internal bool selected by code that needs the MSI domain.

## State and Persistence Behavior

The file contributes to persistent kernel build configuration in `.config`. It does not create runtime state. Symbol values determine whether code is built in, modular, or absent.

## Dependencies and Integration Points

It integrates with architecture symbols, mailbox, remoteproc, SRAM, RTC, TI SCI interrupt aggregator, MFD syscon, SOC bus, and PRUSS users. The matching Makefile maps these symbols to concrete objects.

## Risks and Edge Cases

Incorrect dependencies can expose drivers on unsupported platforms or hide them from valid builds. `TI_SCI_INTA_MSI_DOMAIN` is invisible and must be selected by its users; otherwise `ti_sci_inta_msi.o` will not build. The Keystone DMA help text contains a typo ("Say y tp") but this is documentation-only.

## Test Signals

Run Kconfig build coverage for Keystone, AM33xx/AM43xx, K3, PRUSS, and `COMPILE_TEST` combinations. Confirm expected prompts, selected dependencies, module/built-in object inclusion, and absence of unmet direct dependency warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/ti/Makefile

## Purpose

`drivers/soc/ti/Makefile` maps TI SoC Kconfig symbols to built objects. It is the build glue for Keystone Navigator, AMx3 PM, Wakeup M3 IPC, K3 RingACC, K3 SoC info, PRUSS, TI SCI INTA MSI, and OMAP SmartReflex.

## Important APIs, Types, and Functions

This file has no executable APIs. Object mappings include `knav_qmss.o` from `knav_qmss_queue.o` and `knav_qmss_acc.o`, `knav_dma.o`, `pm33xx.o`, `wkup_m3_ipc.o`, `ti_sci_inta_msi.o`, `k3-ringacc.o`, `k3-socinfo.o`, `pruss.o`, and `smartreflex.o`.

## Control Flow

Kbuild evaluates each `obj-$(CONFIG_...)` line after Kconfig. Tristate symbols produce built-in or module objects, while bool symbols produce built-in objects when enabled. `knav_qmss-y` composes the QMSS object from queue and accumulator implementation files.

## State and Persistence Behavior

The Makefile only affects build outputs. It does not define runtime state or persistence. The resulting object/module inclusion is determined by the persistent kernel `.config`.

## Dependencies and Integration Points

It integrates directly with `drivers/soc/ti/Kconfig` symbols and Kbuild. `CONFIG_POWER_AVS_OMAP` links `smartreflex.o` even though that symbol is owned outside this TI SoC Kconfig snippet.

## Risks and Edge Cases

Symbol/object drift between Kconfig and Makefile will cause enabled drivers not to build or stale objects to be referenced. Composite object naming for `knav_qmss-y` requires the final `knav_qmss.o` line to stay aligned. Module naming changes can affect autoload and packaging.

## Test Signals

Build all TI SoC symbol combinations as built-in and module where allowed. Confirm `knav_qmss.o` contains both queue and accumulator objects, and that each enabled Kconfig symbol contributes exactly the expected object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ti/Makefile -->
