# subset-b-004239 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-core.c

## Purpose
This is the shared MFD core for the Cirrus Logic CS40L50 haptic device. It owns common register access policy, regulator/reset sequencing, DSP firmware bring-up, DSP command queue helpers, IRQ demultiplexing, runtime hibernate control, and creation of the `cs40l50-codec` and `cs40l50-vibra` child devices. I2C and SPI wrappers allocate the `struct cs40l50` and then delegate here.

## Important APIs, types, and functions
`cs40l50_regmap` is exported for bus drivers and configures 32-bit big-endian register/value access with 4-byte register stride. `cs40l50_probe()` and `cs40l50_remove()` are exported entry points for the transport drivers. `cs40l50_dsp_write()` is exported as the common DSP queue command helper; it retries writes that may fail while the device is hibernating, then polls the queue register until the firmware clears it as an ACK. `cs40l50_pm_ops` exposes runtime suspend/resume hooks to bus drivers.

The internal flow is centered on `cs40l50_dsp_init()`, `cs40l50_reset_dsp()`, `cs40l50_request_firmware()`, and `cs40l50_dsp_bringup()`. The DSP is configured as a Halo core with packed PM/XM/YM and unpacked 24-bit memory regions. `cs40l50_wseq_init()` locates firmware controls for standby, active, and power-on write sequences. `cs40l50_dsp_config()` writes internal VAMP and IRQ mask overrides to both hardware and the power-on write sequence so settings survive firmware-managed power transitions. `cs40l50_dsp_post_run()` performs post-firmware configuration and adds the MFD children.

IRQ handling uses `cs40l50_irq_chip`, `cs40l50_reg_irqs`, and `cs40l50_irqs`. `cs40l50_irq_init()` creates a regmap IRQ chip and requests one threaded handler per virtual IRQ. The DSP queue IRQ uses `cs40l50_dsp_queue()`; all hardware error IRQs share `cs40l50_hw_err()`.

## Control flow
Probe initializes the mutex, obtains an optional reset GPIO, enables `vdd-io`, satisfies reset and control-port timing delays, releases reset, verifies device/revision, initializes the DSP object, configures runtime PM, installs IRQ handling, asynchronously requests `cs40l50.wmfw`, and drops the runtime PM reference for autosuspend. Firmware loading is two-stage: the WMFW callback stores the firmware pointer and requests optional wavetable `cs40l50.bin`; the wavetable callback stores the optional pointer, resets/powers/runs the DSP, reads `CS40L50_NUM_WAVES`, registers devm DSP stop/power-down cleanup, and releases both firmware objects.

DSP reset is serialized by `cs40l50->lock`: stop running firmware, power down booted firmware, send shutdown, power up with firmware/bin blobs, send system reset, prevent hibernation, and run the DSP. Hardware error interrupts also take the same mutex before logging the matching error name and writing the global error release set/clear sequence. The DSP queue handler loops until read and write pointers match, logs each payload, wraps the read pointer at queue end, and writes the new read pointer back.

## State and persistence behavior
Persistent driver state lives in `struct cs40l50`: regmap, IRQ, reset GPIO, firmware pointers during async bring-up, DSP object, write sequences, IRQ data, device/revision, and a mutex. Hardware state is restored partly through firmware write sequences: internal VAMP config and IRQ mask overrides are written into the power-on sequence as well as current registers. Runtime suspend writes `CS40L50_ALLOW_HIBER`; runtime resume uses the ACK-polled DSP helper to send `CS40L50_PREVENT_HIBER`. Remove simply asserts reset; devm actions unwind DSP and IRQ resources.

## Dependencies and integration points
The file depends on Linux MFD, regmap IRQ, regulator, GPIO, runtime PM, firmware loading, and the Cirrus `cs_dsp`/WMFW framework. It exports common symbols to `cs40l50-i2c.c`, `cs40l50-spi.c`, and child drivers under the input/sound stacks. Firmware names are `cs40l50.wmfw` and optional `cs40l50.bin`; the child devices rely on successful `cs_dsp` post-run.

## Risks and edge cases
Firmware bring-up is asynchronous; child devices are unavailable until DSP post-run succeeds. If `request_firmware_nowait()` succeeds but firmware contents are missing or invalid, probe can still return success while later bring-up logs errors. `cs40l50_dsp_bringup()` assigns `cs40l50->bin` to a possibly NULL optional wavetable and always releases it, which is valid for `release_firmware(NULL)` but important for audit. DSP queue handling trusts firmware-provided read pointers and only wraps after incrementing past `CS40L50_DSP_QUEUE_END`; bad firmware pointers would turn into arbitrary regmap reads. The static `cs40l50_irqs` table stores virq values globally, so multiple device instances would share the last registered virq values for error-name lookup. Runtime suspend writes the queue directly rather than through `cs40l50_dsp_write()`, so failures caused by an already hibernating device are propagated without retry.

## Test signals
Useful tests include probe deferral for missing regulators/GPIO/IRQ, invalid device ID and pre-B0 revision rejection, asynchronous firmware absence and optional wavetable absence, successful child-device creation after DSP post-run, IRQ handler behavior for DSP queue wrap and hardware error release, runtime suspend/resume hibernate commands, and remove/reset cleanup. KUnit or fault-injection tests around regmap failures in `cs40l50_reset_dsp()` and IRQ setup would exercise most error exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-i2c.c

## Purpose
This is the I2C transport wrapper for the CS40L50 MFD core. It allocates per-device state, binds it to the I2C client, creates an I2C regmap using the shared CS40L50 register format, and delegates all device behavior to `cs40l50_probe()`.

## Important APIs, types, and functions
`cs40l50_i2c_probe()` allocates `struct cs40l50`, stores it with `i2c_set_clientdata()`, copies `dev` and `irq` from the client, initializes `devm_regmap_init_i2c(i2c, &cs40l50_regmap)`, and invokes the core probe. `cs40l50_i2c_remove()` fetches the client data and calls `cs40l50_remove()`. The driver declares I2C ID `"cs40l50"` and OF compatible `"cirrus,cs40l50"`, and attaches `pm_ptr(&cs40l50_pm_ops)` from the core.

## Control flow
Kernel I2C matching enters probe. Allocation or regmap creation failure aborts immediately with standard error reporting. On success, all later hardware initialization, firmware loading, IRQ setup, child MFD creation, and runtime PM setup happen in the core file. Remove is a thin pass-through that asserts reset through the core helper.

## State and persistence behavior
This file owns no durable hardware state beyond allocating and registering the core state pointer for the I2C device. Lifetime is devm-managed except for the explicit remove callback. Runtime PM callbacks are core-owned.

## Dependencies and integration points
It depends on the I2C subsystem, regmap I2C transport helpers, OF matching, and exported symbols from `linux/mfd/cs40l50.h` implemented by `cs40l50-core.c`. It integrates the same MFD core as the SPI wrapper, so behavioral differences should be limited to bus transfer semantics.

## Risks and edge cases
The wrapper passes `i2c->irq` directly; if firmware or board description omits an IRQ, the core IRQ setup will fail later. There is no ACPI match table. Since child device creation is asynchronous in the core, successful I2C probe does not guarantee firmware-run child availability.

## Test signals
Build coverage should verify exported core symbols and PM ops linkage. Runtime tests should cover OF match, missing IRQ, regmap initialization failure injection, and remove path reset assertion. Comparing I2C and SPI probe behavior is useful because they are intended to be symmetric.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-spi.c

## Purpose
This is the SPI transport wrapper for the CS40L50 MFD core. It mirrors the I2C wrapper while using SPI driver data and regmap SPI initialization.

## Important APIs, types, and functions
`cs40l50_spi_probe()` allocates `struct cs40l50`, stores it with `spi_set_drvdata()`, copies `dev` and `irq`, creates `devm_regmap_init_spi(spi, &cs40l50_regmap)`, and calls `cs40l50_probe()`. `cs40l50_spi_remove()` retrieves state with `spi_get_drvdata()` and calls `cs40l50_remove()`. The SPI ID and OF compatible are both `"cs40l50"`/`"cirrus,cs40l50"`, and runtime PM is delegated through `cs40l50_pm_ops`.

## Control flow
SPI core matching enters probe, which performs only allocation, state binding, regmap setup, and core delegation. All reset, regulator, device ID, IRQ, firmware, and child-device behavior is core-owned. Remove is a direct pass-through.

## State and persistence behavior
No independent persistent state exists in this wrapper. The devm allocation is scoped to the SPI device, while hardware state and runtime PM behavior are maintained by the shared core.

## Dependencies and integration points
The file depends on the SPI subsystem, regmap SPI helpers, OF matching, and the exported CS40L50 MFD core API. It is the bus-specific entry point for systems wiring the haptic part over SPI.

## Risks and edge cases
The wrapper assumes `spi->irq` is correctly populated. SPI regmap transfer format must match the shared 32-bit big-endian register/value config; transport-specific quirks are not handled here. Like I2C, probe success can precede asynchronous firmware failure in the core.

## Test signals
Build tests should confirm module registration and PM ops linkage. Runtime tests should include OF/SPI modalias binding, missing IRQ propagation from the core, regmap SPI failure injection, and parity with I2C behavior for reset and child creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-i2c.c

## Purpose
This is the I2C bus front-end for the CS42L43/CS42L43B MFD core. It supplies an I2C regmap configuration, maps firmware-visible variant IDs from OF/ACPI match data, marks I2C devices as immediately attached, and delegates to `cs42l43_dev_probe()`.

## Important APIs, types, and functions
`cs42l43_i2c_regmap` configures 32-bit big-endian register and value access, 4-byte stride, `CS42L43_MCU_RAM_MAX` as the maximum register, Maple cache, the exported default table, and readable/volatile/precious callbacks from the core. `cs42l43_i2c_probe()` allocates `struct cs42l43`, sets `dev`, `irq`, `attached = true`, `variant_id = device_get_match_data()`, creates the regmap with `devm_regmap_init_i2c()`, and calls the core probe. OF compatibles are `"cirrus,cs42l43"` and `"cirrus,cs42l43b"`; ACPI IDs are `"CSC4243"` and `"CSC2A3B"`.

## Control flow
After bus match, probe initializes state and regmap. Because I2C has no SoundWire attach lifecycle, the attached flag starts true and the core wait-for-attach helper becomes effectively a cache transition. All power, firmware update, IRQ, MFD child, and PM behavior is in `cs42l43.c`.

## State and persistence behavior
This wrapper only seeds core state. The Maple cache is configured here but managed by the core around reset, runtime suspend, and resume. The variant ID controls core readable-register ranges and firmware-update register selection.

## Dependencies and integration points
The file depends on I2C, OF/ACPI matching, regmap, PM, and the internal `"cs42l43.h"` declarations exported by the core namespace `MFD_CS42L43`. It integrates with the same core used by SoundWire, but with big-endian I2C register formatting.

## Risks and edge cases
If match data is missing, `variant_id` becomes zero and later core device ID validation will fail. There is no remove callback because devm action cleanup is installed by the core. Incorrect endian or cache callback behavior would affect all child drivers because this regmap is the authoritative register access layer.

## Test signals
Tests should cover OF and ACPI variant matching, missing match data, regmap init failure, core probe delegation, and variant-specific readable ranges for CS42L43 versus CS42L43B. Suspend/resume tests through the I2C driver should verify that PM ops exported by the core are reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-sdw.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-sdw.c

## Purpose
This is the SoundWire bus front-end for CS42L43/CS42L43B. It describes SoundWire ports, configures a little-endian SoundWire regmap, tracks attach/detach status, clears SoundWire-specific interrupt state, constrains PLL-related bus clock changes, and delegates device initialization to the common MFD core.

## Important APIs, types, and functions
`cs42l43_sdw_regmap` mirrors the I2C regmap constraints and cache callbacks but uses little-endian register/value formatting for SoundWire. `CS42L43_SDW_PORT()` defines source/sink `sdw_dpn_prop` entries. `cs42l43_read_prop()` sets wake, paging, domain IRQ, parity quirk, SCP interrupt masks, and source/sink port bitmaps/properties. `cs42l43_sdw_update_status()` updates `cs42l43->attached` and completes either `device_attach` or `device_detach`. `cs42l43_sdw_interrupt()` clears Cirrus GEN interrupt status outside the generic regmap IRQ handling. `cs42l43_sdw_bus_config()` records `sdw_freq` as half the current data rate and rejects frequency changes while `sdw_pll_active` is true. `cs42l43_sdw_probe()` allocates state, stores `sdw`, variant ID from the SDW ID table, initializes regmap, and calls `cs42l43_dev_probe()`.

## Control flow
SoundWire framework first calls property and probe paths, then reports attachment via `update_status()`. The core starts with regcache cache-only and its boot work calls `cs42l43_wait_for_attach()`, which blocks until this wrapper completes `device_attach`. During soft resets, the core waits for `device_detach`, again completed by this file. SoundWire interrupts are first represented through regmap IRQs and then have the SoundWire GEN status cleaned in the callback.

## State and persistence behavior
This file maintains attachment state, detach/attach completion signaling, and SoundWire bus frequency state in `struct cs42l43`. It does not persist register settings itself, but its attach/detach events determine when the core may leave cache-only mode and synchronize register cache. PLL lock state is protected by `pll_lock` shared with child/core users.

## Dependencies and integration points
It depends on the Linux SoundWire slave framework, SoundWire register definitions, regmap SoundWire transport, PM, and the CS42L43 core. It exposes source ports 1-4 and sink ports 5-7, sets `use_domain_irq`, and uses SDW slave IDs for CS42L43 and CS42L43B.

## Risks and edge cases
Attach timeouts in the core depend on this file receiving status callbacks. The SoundWire interrupt cleanup ignores return values from no-PM reads/writes, so bus errors may be hidden after IRQ handling. `bus_config()` rejects frequency changes only while `sdw_pll_active` is true; users must correctly set that flag. Endian differs from I2C, so regressions in regmap format are bus-specific.

## Test signals
Useful tests include SoundWire property enumeration, source/sink port masks, attach and detach completion timing, soft-reset detach wait behavior, interrupt clearing, bus clock change rejection while PLL is active, and runtime suspend/resume through regcache cache-only transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs42l43.c

## Purpose
This is the common MFD core for CS42L43/CS42L43B. It defines register defaults and access policy, manages power/reset sequencing, firmware/MCU update and disable flow, IRQ chip setup, deferred boot, runtime/system PM, and creation of `cs42l43-pinctrl`, `cs42l43-spi`, and `cs42l43-codec` children.

## Important APIs, types, and functions
The exported symbols are `cs42l43_reg_default`, `cs42l43_readable_register()`, `cs42l43_precious_register()`, `cs42l43_volatile_register()`, `cs42l43_dev_probe()`, and `cs42l43_pm_ops` in namespace `MFD_CS42L43`. `struct cs42l43_patch_header` describes the expected `cs42l43.bin` patch format. `cs42l43_reva_patch` is a register patch applied after firmware handling. `cs42l43_regmap_irqs` and `cs42l43_irq_chip` define the child IRQ map over PLL, headset/accessory, amplifier, GPIO, and headphone events. `cs42l43_devs` declares pinctrl, SPI bridge, and codec MFD cells, with `vdd-amp` as a codec parent supply.

Register access policy is variant-aware: common registers are always readable; CS42L43-only MCU/volume ranges require `variant_id == CS42L43_DEVID_VAL`; CS42L43B-only ranges require `variant_id == CS42L43B_DEVID_VAL`. Precious registers include reset, SPI TX/RX, interrupt status, and MCU RAM. Volatile registers include ID/status/interrupt/boot registers and all precious registers.

## Control flow
`cs42l43_dev_probe()` stores driver data, initializes locks/completions/work, puts regmap into cache-only mode, obtains reset and regulators, powers the chip up, installs a devm remove action, enables runtime PM while holding an initial no-resume reference, and queues `cs42l43_boot_work()` on `system_long_wq`. Boot work waits for bus attachment, validates device and variant IDs, reads revision/OTP, runs the MCU update/disable state machine, applies the register patch, configures the regmap IRQ chip, adds MFD children, and finally drops the autosuspend reference.

The MCU update path retries up to five `cs42l43_mcu_update_step()` passes, with attach waits after each `-EAGAIN`. Stage 2 on unpatched devices asynchronously requests `cs42l43.bin`, writes the patch to MCU RAM, signals the MCU, waits for patch applied, and retries. Stage 2 on patched devices advances to stage 3 by clearing NEED_CONFIGS. Stage 3 on patched compatible firmware disables the MCU and soft-resets so the driver can own registers; stage 3 on unpatched firmware returns to stage 2. Stage 4 means no update needed.

Power sequencing enables `vdd-p`, waits, releases reset, enables core supplies (`vdd-a`, `vdd-io`, `vdd-cp`), enables `vdd-d`, and waits again. Power down reverses this and asserts reset. Soft reset sets cache-only, writes reset bypassing cache, waits, and on SoundWire waits for detach.

## State and persistence behavior
Core state includes variant ID, hardware lock flag, reset GPIO, regulators, regmap, IRQ data, SoundWire attachment completions, firmware download completion/error, PLL lock/frequency fields, and boot work. Register persistence is dominated by regcache: cache-only during reset and runtime suspend, dirty marking if resume detects `CS42L43_RELID` canary cleared, and `regcache_sync()` on runtime resume. Firmware state is not persisted by the driver except through patching/disable sequence and `hw_lock` detection.

System suspend resumes the device, disables IRQ, force-suspends runtime PM, drops the runtime ref, and powers down. Noirq suspend temporarily enables IRQ to allow wake signaling; noirq resume disables it before full resume powers the device and reenables IRQ. Runtime suspend does not power the chip down but makes the regmap cache-only so SoundWire can sleep.

## Dependencies and integration points
The core integrates with I2C and SoundWire bus wrappers, regulator/GPIO frameworks, regmap/regmap-irq, firmware loader, runtime PM, MFD, and child drivers for codec, pinctrl, and SPI bridge. It relies on `struct cs42l43` and register constants from public MFD headers and on firmware file `cs42l43.bin`.

## Risks and edge cases
Probe returns before boot work finishes; child devices may never appear if deferred firmware or attach fails. `cs42l43_mcu_load_firmware()` casts firmware data to a header before checking size, and bulk writes `firmware->size / sizeof(u32)` words from firmware data; malformed short or unaligned firmware is a risk area. Several regmap writes in state transitions do not check return values before later polling. Secure unpatched devices are rejected with `-EPERM`. SoundWire attach/detach timing drives reset/update progress and can timeout. System suspend error handling disables IRQ before force suspend; if force suspend fails, the path returns without re-enabling IRQ in that function, relying on higher PM unwinding is a point to audit.

## Test signals
Test coverage should target variant ID mismatch, CS42L43 versus CS42L43B register readability, firmware missing/bad format/update timeout, each MCU boot stage transition, secure unpatched rejection, SoundWire attach/detach timeouts, register-cache dirty sync after reset canary loss, IRQ chip registration, MFD child creation, regulator enable/disable unwinds, and system/runtime PM sequencing. Fault injection on regmap reads/writes and firmware callbacks would provide strong signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs42l43.h

## Purpose
This internal header shares CS42L43 core declarations with the I2C and SoundWire bus front-ends. It is intentionally small and keeps transport files independent of core implementation details beyond the symbols they need.

## Important APIs, types, and functions
`CS42L43_N_DEFAULTS` defines the expected size of the core register-default table. The header forward-declares `struct dev_pm_ops`, `struct device`, `struct reg_default`, and `struct cs42l43`. It declares `cs42l43_pm_ops`, `cs42l43_reg_default`, the three regmap access callbacks, and `cs42l43_dev_probe()`.

## Control flow
There is no executable control flow. The bus wrappers include this header to configure regmap callbacks/defaults and to call the common core probe.

## State and persistence behavior
No state is stored here. The constant default count is a compile-time contract between the header and `cs42l43.c`; a mismatch would break declarations or array assumptions.

## Dependencies and integration points
The header integrates `cs42l43-i2c.c`, `cs42l43-sdw.c`, and `cs42l43.c`. It complements public MFD headers that define `struct cs42l43` and register constants.

## Risks and edge cases
Changing `CS42L43_N_DEFAULTS` without updating the actual default array would create compile-time or data consistency problems. Adding declarations here exposes core details to transport code, so the narrow interface should be preserved.

## Test signals
Build coverage is the main signal: both I2C and SoundWire modules must compile against this header, and `ARRAY_SIZE(cs42l43_reg_default)` in bus regmap configs must match the declared array size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs42l43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs47l15-tables.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs47l15-tables.c

## Purpose
This file provides CS47L15-specific Madera regmap data: a revision patch, 16-bit register defaults, readable/volatile predicates for 16-bit and 32-bit windows, ADSP memory detection, and exported I2C/SPI regmap configurations. It is data/control policy for the Madera core rather than a probing driver.

## Important APIs, types, and functions
`cs47l15_patch()` applies `cs47l15_reva_16_patch` with `regmap_register_patch()` and logs failures. The large `cs47l15_reg_default` table seeds the Maple cache for 16-bit control registers, including tone/haptics, clocks/FLLs, accessory detection, inputs, outputs, AIFs, mixers, EQ/DRC/filter coefficients, GPIOs, and IRQ masks.

`cs47l15_is_adsp_memory()` recognizes DSP1 PM/XM/YM/ZM memory ranges. `cs47l15_16bit_readable_register()` permits the main Madera 16-bit register map, including status, control, audio routing, DSP-facing controls, GPIO, and IRQ registers. `cs47l15_16bit_volatile_register()` marks reset/revision, write sequencer controls, hardware status, sample-rate status, HP/mic/headphone-detect status, output/input status, SPDIF status, FX status, and IRQ status/raw status as uncached volatile. The 32-bit readable and volatile callbacks cover write-sequencer storage, OTP HP detect calibration, DSP1 configuration/status/error registers, and ADSP memory; they treat all 32-bit ranges as volatile.

Four exported regmap configs are provided: `cs47l15_16bit_spi_regmap`, `cs47l15_16bit_i2c_regmap`, `cs47l15_32bit_spi_regmap`, and `cs47l15_32bit_i2c_regmap`. SPI variants include pad bits; 32-bit variants use `reg_stride = 2` and have no defaults.

## Control flow
Runtime control flow is minimal. The Madera parent calls the patch helper during device initialization, then uses the exported regmap configs to decide which registers can be read and cached. The callbacks are pure switch/range classifiers.

## State and persistence behavior
State persistence is through regmap cache defaults and volatility policy. Nonvolatile 16-bit registers can be cached/restored from defaults; volatile registers and 32-bit DSP/memory regions are read from hardware. The register patch changes hardware/cache initialization behavior for affected revision registers.

## Dependencies and integration points
The file depends on Madera core/register headers, Linux regmap, module exports, and device logging. It integrates into Madera bus/core code that selects CS47L15-specific regmaps and patch routines.

## Risks and edge cases
The access tables are large and manual; missing readable entries break legitimate child-driver access, while missing volatile entries can cache status or IRQ state incorrectly. Treating all ADSP memory as volatile is conservative but expensive. Patch failure abort behavior depends on callers checking `cs47l15_patch()`. Divergence between I2C/SPI 16-bit configs would be a regression; they should differ only by SPI pad bits.

## Test signals
Useful signals include regmap access-table tests for representative clock/audio/IRQ/DSP addresses, verification that volatile status registers are not cached, patch application failure injection, I2C/SPI config parity, and boot tests with Madera children exercising codec, GPIO, IRQ, and DSP access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs47l15-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs47l24-tables.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cs47l24-tables.c

## Purpose
This file provides CS47L24-specific Arizona regmap data: a revision-A patch, a regmap IRQ chip, register defaults, readable/volatile predicates, ADSP memory range detection, and the exported SPI regmap configuration. It supplies static policy consumed by the Arizona MFD core.

## Important APIs, types, and functions
`cs47l24_patch()` applies `cs47l24_reva_patch` through `regmap_register_patch()`. `cs47l24_irqs` maps Arizona logical IRQ IDs across six interrupt status registers, covering GPIO, DSP RAM ready and DSP IRQs, speaker overheat/shutdown/shorts, write sequencer, DRC/ASRC/FLL/clock events, control-interface errors, mixer dropped samples, headphone completion/short-circuit, and boot done. `cs47l24_irq` exports the regmap IRQ chip with status, mask, and ack bases.

`cs47l24_reg_default` seeds defaults for SPI control, tones, haptics, clocks/FLLs, mic bias, inputs, outputs, AIFs, mixers, EQ/DRC/HPLPF/ASRC/ISRC, DSP2/DSP3 controls, GPIO/pads, and interrupt masks. `cs47l24_is_adsp_memory()` recognizes DSP2 and DSP3 PM/ZM/XM/YM memory ranges. `cs47l24_readable_register()` admits the supported Arizona control, routing, DSP, IRQ, status, and ADSP-memory address set. `cs47l24_volatile_register()` marks reset/revision, write sequencer, haptics/sample-rate/async/HP/input/output/IRQ/raw IRQ/FX/ASRC/DSP status and DMA/scratch/control registers as volatile, plus ADSP memory.

`cs47l24_spi_regmap` configures 32-bit big-endian register addresses, 16-bit big-endian values, 16 pad bits, `CS47L24_MAX_REGISTER` covering DSP3 YM, Maple cache, defaults, and the readable/volatile callbacks.

## Control flow
There is no probe function in this file. The Arizona parent driver imports the patch, IRQ chip, and regmap config during device setup. The patch helper is the only active function; the remaining callbacks classify addresses for regmap access and caching.

## State and persistence behavior
Persistence is governed by the default table and volatility callback. Stable control registers can live in the Maple cache; volatile status/IRQ/DSP/DMA regions are fetched from hardware. IRQ state is acknowledged through regmap-irq using the exported chip configuration.

## Dependencies and integration points
The file depends on Arizona MFD core/register headers, Linux regmap IRQ definitions through included core headers, module exports, and device definitions. It integrates with the Arizona parent and with downstream codec/DSP/GPIO/IRQ users that rely on these access policies.

## Risks and edge cases
Manual register allowlists can silently block valid access or cache changing state if incomplete. `CS47L24_NUM_ISR` is defined but not used in this file, so IRQ register count is governed by `cs47l24_irq.num_regs = 6`; future edits should avoid stale constants. Only an SPI regmap config is exported here; if another bus is added it needs an explicit config. IRQ mapping array size is `ARIZONA_NUM_IRQ`, so logical IRQ enum changes can create sparse or missing mappings.

## Test signals
Test signals include patch application, regmap readable/volatile classification for representative audio, IRQ, DSP2/DSP3 memory, and DMA addresses, regmap IRQ chip registration and virtual IRQ mapping, cache behavior for interrupt/status registers, and hardware boot smoke tests covering Arizona child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cs47l24-tables.c -->
