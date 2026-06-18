# subset-b-003745 research

Grouped research report for the DRM scheduler KUnit mock, Sitronix panel drivers, Solomon SSD13xx drivers, Unisoc SPRD display stack, and STI AWG utilities. Each section is source-tree aligned for reconciliation into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/mock_scheduler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/mock_scheduler.c

Purpose: implements the mock GPU backend used by DRM scheduler KUnit tests. It allocates mock scheduler entities and jobs on the KUnit lifetime, exposes manual and timer-driven completion, and wires a `drm_sched_backend_ops` implementation into the core scheduler.

Important APIs and types: `drm_mock_sched_new()` wraps `drm_sched_init()` with all scheduler priorities, a very high credit limit, configurable timeout, and a single hang limit. `drm_mock_sched_entity_new()` initializes `drm_sched_entity` instances against the mock `drm_gpu_scheduler`. `drm_mock_sched_job_new()` initializes `drm_sched_job`, completion, list link, and an hrtimer. `mock_sched_run_job()`, `mock_sched_timedout_job()`, `mock_sched_free_job()`, and `mock_sched_cancel_job()` are the backend callbacks. Hardware fences are implemented with `dma_fence_ops` and the scheduler spinlock.

Control flow: tests create a scheduler, entities, jobs, arm jobs, and push them to entities. The scheduler calls `mock_sched_run_job()`, which initializes a hardware fence, queues the job in `sched->job_list`, and optionally schedules an hrtimer based on `duration_us`. Timer completion walks the ordered job list until it finds a non-duration or unfinished job. Manual completion uses `drm_mock_sched_advance()` to advance `cur_seqno` and signal eligible fences.

State and persistence: all state is in memory and KUnit-owned. `hw_timeline.context`, `next_seqno`, and `cur_seqno` model an ordered DMA fence timeline. Per-job flags record done, timeout, reset-skip, and no-reset intent. Pending jobs hold a fence reference while linked.

Dependencies and integration: depends on DRM GPU scheduler, DMA fences, hrtimers, completions, KUnit allocation/assertions, and spinlocks. It is consumed by `tests_basic.c` through `sched_tests.h`.

Risks: fence reference ownership is central: run paths take a list reference, completion paths must signal under the scheduler lock, timeout/free/cancel paths put references in complementary places. Timer completion assumes job list ordering by `finish_at`; inserting manual jobs with no duration stops timer-driven completion behind them. Timeout cleanup calls `drm_sched_job_cleanup()` directly, so tests relying on later free callbacks must align with scheduler semantics.

Test signals: KUnit tests validate scheduling, manual advancement, timed completion, cancellation on `drm_sched_fini()`, timeout behavior, reset skipping, priorities, scheduler migration, and credit-limit enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/mock_scheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/sched_tests.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/sched_tests.h

Purpose: shared header for DRM scheduler KUnit tests. It declares the mock scheduler, mock entity, and mock job structures, helper casts, lifecycle functions, and inline job helpers used by test cases.

Important APIs and types: `struct drm_mock_scheduler` embeds `struct drm_gpu_scheduler` and tracks a spinlock-protected job list plus a simulated hardware timeline. `struct drm_mock_sched_entity` embeds `struct drm_sched_entity`. `struct drm_mock_sched_job` embeds `struct drm_sched_job`, a completion, flags, hrtimer, duration/finish time, and a DMA fence. Public functions create/finalize schedulers, create/destroy entities, create jobs, and advance the mock timeline.

Control flow: tests include this header, create entities/jobs, then call `drm_mock_sched_job_submit()` which arms the DRM scheduler job and pushes it to the entity. Timing is controlled either with `drm_mock_sched_job_set_duration_us()` or with explicit `drm_mock_sched_advance()`. Waiting helpers observe the scheduler fence and mock completion.

State and persistence: no persistent state. The header defines job flag bits as the observable state contract between the backend and tests: `DONE`, `TIMEDOUT`, `DONT_RESET`, and `RESET_SKIPPED`.

Dependencies and integration: includes KUnit, atomics, completions, DMA fences, hrtimers, lists, and `drm/gpu_scheduler.h`. Cast helpers rely on embedded base objects and `container_of()`.

Risks: inline helpers assume the underlying mock backend has initialized `job->base.s_fence` before scheduled/finished waits. `drm_mock_sched_job_wait_scheduled()` asserts the job is not already done before waiting, which is correct for ordering tests but can fail if a duration is very short or the scheduler runs faster than expected.

Test signals: all scheduler tests use this header as their ABI. Any field layout or helper semantic change should be validated by the KUnit suites in `tests_basic.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/sched_tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/tests_basic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/tests_basic.c

Purpose: KUnit basic and smoke tests for the DRM GPU scheduler using the mock backend. It covers ordinary submission, dependency chains, entity cleanup, cancellation, timeout handling, priority behavior, scheduler migration, and credit limits.

Important APIs and types: `drm_sched_basic_init()` and `drm_sched_timeout_init()` create mock schedulers with infinite or short timeout. Parameterized cases use `struct drm_sched_basic_params` and `KUNIT_ARRAY_PARAM`. Test helpers call `drm_mock_sched_entity_new()`, `drm_mock_sched_job_new()`, `drm_sched_job_add_dependency()`, `drm_sched_entity_set_priority()`, `drm_sched_entity_modify_sched()`, and `drm_mock_sched_advance()`.

Control flow: simple tests submit jobs, wait for scheduling, assert non-completion before advancement, then advance the mock timeline. Parameterized tests submit queues across one or more entities, optionally chaining each job to the previous job's finished fence. Cleanup tests destroy entities while work remains. Timeout tests let a job exceed `MOCK_TIMEOUT`; reset-skip tests mark `DONT_RESET` then manually complete. Priority and modify-scheduler tests mutate scheduling state while long queues drain.

State and persistence: state is per KUnit case. Scheduler/entity/job allocations are KUnit-managed except explicit scheduler finalization and entity destruction. The tests inspect mock job flags and fence errors as the result state.

Dependencies and integration: depends on the mock scheduler implementation, DRM scheduler core, KUnit, `linux/delay.h`, and DMA fence dependencies. The final `kunit_test_suites()` registers six suites.

Risks: several tests use timing (`HZ`, `usleep_range()`, job durations) and can be sensitive to slow or overloaded environments. `drm_sched_cancel` defines suite init/exit while also allocating/finalizing its own scheduler inside the test, which means the suite-private scheduler is separate from the one under assertion. Slow cases are marked with `KUNIT_CASE_SLOW` where they spin on priority or credit behavior.

Test signals: this file itself is the test signal. A healthy scheduler should pass all suites: `drm_sched_basic_tests`, `drm_sched_basic_timeout_tests`, `drm_sched_basic_cancel_tests`, `drm_sched_basic_priority_tests`, `drm_sched_basic_modify_sched_tests`, and `drm_sched_basic_credits_tests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/tests_basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Kconfig

Purpose: declares build-time configuration for Sitronix DRM panel/controller drivers: ST7567/ST7571 core plus I2C/SPI transports, ST7586, ST7735R/ST7715R, and ST7920.

Important entries: `DRM_ST7571` is the common ST7567/ST7571 DRM core and selects shmem GEM, KMS helpers, client setup, and videomode helpers. `DRM_ST7571_I2C` and `DRM_ST7571_SPI` depend on the core and select appropriate regmap support. `DRM_ST7586` and `DRM_ST7735R` depend on SPI and select DMA GEM plus MIPI DBI. `DRM_ST7920` depends on DRM, SPI, and MMU and selects shmem GEM, KMS helpers, and REGMAP_SPI.

Control flow: Kconfig only controls symbol visibility and module selection. Bus wrappers are intentionally separate from the ST7571 core, so selecting the core alone does not bind hardware.

State and persistence: no runtime state. The selected symbols decide module objects and helper dependencies.

Dependencies and integration: integrates with the DRM menu, SPI/I2C stacks, regmap, MIPI DBI, backlight support for ST7735R, and DRM client setup for fbdev/emulation clients.

Risks: users must select the matching ST7571 bus driver or no transport will probe. Help text mentions ST7565 in transport descriptions while the compatible/core naming is ST7567/ST7571, which may confuse configuration audits.

Test signals: compile coverage with each symbol as built-in and module, especially the split ST7571 namespace import/export relationship.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Makefile

Purpose: maps Sitronix Kconfig symbols to object files.

Important APIs/types/functions: no C API. It builds `st7571.o`, `st7571-i2c.o`, `st7571-spi.o`, `st7586.o`, `st7735r.o`, and `st7920.o` based on the matching `CONFIG_DRM_*` symbols.

Control flow: Kbuild includes each object in the DRM subtree when its config symbol is enabled.

State and persistence: no runtime state.

Dependencies and integration: must stay aligned with Kconfig symbol names and module import namespaces. The ST7571 bus objects depend on symbols exported by `st7571.o`.

Risks: any renamed source or Kconfig symbol will silently break module inclusion. ST7571 transport modules require the core object to be built.

Test signals: `make M=drivers/gpu/drm/sitronix` or full kernel builds with each symbol combination should verify object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-i2c.c

Purpose: I2C transport wrapper for the ST7567/ST7571 DRM core. It creates a regmap over custom I2C writes, probes the shared core, and registers OF/I2C IDs.

Important APIs and types: `struct st7571_i2c_transport` holds the `i2c_client` and an `ignore_nak` policy. `st7571_i2c_regmap_write()` sends the full regmap buffer with `i2c_transfer()`. `st7571_i2c_regmap_read()` returns `-EOPNOTSUPP` because the core writes only. `st7571_i2c_probe()` allocates transport state, enables `I2C_M_IGNORE_NAK` when protocol mangling exists, initializes regmap, and calls `st7571_probe()`.

Control flow: probe builds the transport, creates a regmap with 8-bit register/value fields and single writes, then stores the returned core device as client data. remove calls `st7571_remove()`.

State and persistence: transport state is devm-managed; core device lifetime is tied to `devm_drm_dev_alloc()` in the core and explicit unplug on remove. `ignore_nak` is immutable after probe.

Dependencies and integration: depends on I2C, regmap custom bus, device tree compatibles `sitronix,st7567` and `sitronix,st7571`, and the `DRM_ST7571` exported namespace.

Risks: the write helper returns success for many failed transfers when `ignore_nak` is false because it returns 0 for any non-negative or negative non-ignore path; this is intentional around NAK ambiguity but can hide bus failures. The probe error message after `st7571_probe()` says regmap initialization failed even though the core failed.

Test signals: I2C probe/remove, NAK-tolerant panels, and error injection on `i2c_transfer()` should be covered. Module loading should verify `MODULE_IMPORT_NS("DRM_ST7571")`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-spi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-spi.c

Purpose: SPI transport wrapper for the shared ST7567/ST7571 DRM core.

Important APIs and types: `st7571_spi_regmap_config` configures an 8-bit register/value SPI regmap with multi-write support. `st7571_spi_probe()` initializes regmap with `devm_regmap_init_spi()`, calls `st7571_probe()`, and stores the core pointer as SPI driver data. OF and SPI IDs cover `st7567` and `st7571`.

Control flow: probe delegates all device parsing, DRM object creation, and display initialization to the core. remove retrieves the stored pointer and calls `st7571_remove()`.

State and persistence: no local persistent runtime state beyond SPI driver data and the regmap owned by devres.

Dependencies and integration: depends on SPI regmap and the ST7571 core export namespace. It binds to `sitronix,st7567` and `sitronix,st7571`.

Risks: as with the I2C wrapper, the error message after a failed core probe says regmap initialization failed. Multi-write support is enabled, but the core still uses many single-byte writes in update paths because of controller limitations noted in comments.

Test signals: SPI probe/remove, module autoload via SPI IDs, and core namespace import should be validated along with display updates through the shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571.c

Purpose: shared DRM/KMS driver for Sitronix ST7567/ST7571 monochrome and 2-bit grayscale dot-matrix LCD controllers. Bus-specific modules provide regmap access; this file handles DT parsing, framebuffer conversion, DRM object setup, and panel command sequences.

Important APIs and types: exported `st7571_probe()` and `st7571_remove()` are the transport ABI. Exported `st7567_config` and `st7571_config` provide panel-specific init, parse, and constraints. Format strategies are in `struct st7571_panel_format`: monochrome supports XRGB8888/R1, grayscale supports XRGB8888/R1/R2. The DRM driver uses shmem GEM and fbdev shmem helpers.

Control flow: `st7571_probe()` allocates `struct st7571_device`, obtains `device_get_match_data()`, parses DT timing/properties, validates constraints, allocates `hwbuf` and `row`, initializes mode config, plane, CRTC, encoder, connector, registers the DRM device, then starts DRM client setup. Atomic plane updates begin CPU access, iterate damage, convert the shadow framebuffer into controller-friendly storage, and write only damaged page-aligned regions. Encoder enable runs the panel init sequence and sends display-on; disable sends display-off.

State and persistence: persistent device state includes display dimensions, offsets, `grayscale`, `inverted`, `bpp`, fixed display mode, regmap, reset GPIO, and scratch buffers. Runtime framebuffer content is not persisted beyond scratch buffers.

Dependencies and integration: uses DRM atomic helpers, damage helpers, shmem GEM, fixed connector modes, display-timing parsing, GPIO reset, regmap, and fbdev client setup. Bus modules import the `DRM_ST7571` namespace.

Risks: `st7571_transform_xy()` assumes fixed row layout and uses `row_len = 16 * bpp`, which matches 128 columns but is coupled to constraints. `st7571_fb_clear_screen()` loops single-byte bulk writes and ignores write errors. Update paths contain TODOs about failed multi-byte writes and also ignore many `regmap_bulk_write()` returns. DT validation is strict about panel size and grayscale support; missing reset GPIO is fatal for ST7571 but not parsed for ST7567.

Test signals: DT parsing for ST7567/ST7571, grayscale and monochrome modes, R1/R2/XRGB8888 conversions, damaged region alignment to 8-row pages, reset/init command ordering, and remove/unplug paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571.h

Purpose: shared ABI and state definitions for the ST7567/ST7571 core and its I2C/SPI transport modules.

Important APIs and types: `enum st7571_color_mode` distinguishes grayscale from black/white controller mode. `struct st7571_panel_constraints` encodes valid row/column limits and grayscale capability. `struct st7571_panel_data` provides init and DT parse callbacks plus constraints. `struct st7571_panel_format` provides framebuffer preparation/update callbacks and supported DRM formats. `struct st7571_device` embeds DRM plane/CRTC/encoder/connector objects and stores parsed panel properties, regmap, reset GPIO, and scratch buffers.

Control flow: transport drivers call `st7571_probe()` with a regmap and later call `st7571_remove()`. The core uses `st7567_config` or `st7571_config` selected through OF match data.

State and persistence: all runtime state needed by the core lives in `struct st7571_device`; transport-local state is intentionally excluded except for regmap.

Dependencies and integration: includes DRM connector/CRTC/driver/encoder/format helper headers and Linux regmap.

Risks: the flexible array `formats[]` in `struct st7571_panel_format` requires static const initializers with correct `nformats`. The shared structure exposes many internal fields, so transport modules could accidentally rely on internals, though current transports only keep opaque pointers.

Test signals: compile tests for both transports ensure exported symbols and structure declarations are complete. Runtime tests should verify match data selects the correct config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7586.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7586.c

Purpose: DRM SPI/MIPI-DBI style driver for Sitronix ST7586 grayscale LCD panels, specifically the LEGO EV3 LCD.

Important APIs and types: `struct st7586_device` embeds `mipi_dbi_dev` plus explicit DRM plane/CRTC/encoder/connector objects. `st7586_xrgb8888_to_gray332()` converts XRGB8888 into the ST7586 unusual 3-pixels-per-byte grayscale encoding using `st7586_lookup`. `st7586_fb_dirty()` sets column/page windows and writes converted memory. CRTC enable programs the ST7586-specific init sequence.

Control flow: probe allocates the device, gets reset and `a0` GPIOs, initializes MIPI DBI SPI, disables read commands, initializes DBI with a calculated tx buffer size, builds DRM modeset objects, registers the DRM device, and starts client setup. Atomic plane update merges damage and flushes the converted rectangle. CRTC enable powers on/resets, runs OTP and panel commands, configures rotation, display duty, partial rows, and display-on.

State and persistence: persistent state is mostly held by `mipi_dbi_dev`, including tx buffer, rotation, reset GPIO, mode, and DBI bus details. No nonvolatile state is changed.

Dependencies and integration: depends on SPI, GPIO, DRM MIPI DBI helpers, DMA GEM, damage helpers, and fixed 178x128 mode. OF compatible is `lego,ev3-lcd`.

Risks: the conversion assumes the damaged width is rounded to a multiple of 3 before reading three source pixels per output byte. `bufsize = (vdisplay + 2) / 3 * hdisplay` appears dimensionally suspicious for 3-horizontal-pixels-per-byte packing; update paths use `(end - start) * height`. Command return values in enable are mostly ignored after initialization starts, so partial failures may only be logged in dirty updates.

Test signals: run with rotated EV3 panel, damage rectangles with non-multiple-of-three x bounds, SPI write failures, and remove/shutdown through `drm_atomic_helper_shutdown()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7586.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7735r.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7735r.c

Purpose: DRM SPI driver for ST7715R/ST7735R-compatible color TFT panels using MIPI DBI helpers.

Important APIs and types: `struct st7735r_cfg` provides mode, offsets, write-only behavior, and RGB/BGR ordering per panel. `struct st7735r_device` embeds `mipi_dbi_dev` and DRM objects. Static configs cover Jianda JD-T18003-T01 and Okaya RH128128T. `st7735r_crtc_helper_atomic_enable()` performs the panel power/reset and initialization command sequence.

Control flow: probe selects config from OF match or SPI ID, allocates device, gets reset and dc GPIOs plus optional OF backlight, reads rotation, initializes DBI SPI, applies write-only/read behavior and offsets, initializes DRM mode config and objects, registers, and starts client setup. Atomic updates use standard DRM MIPI DBI plane helpers. Enable exits sleep, programs frame/power/gamma registers, address mode based on rotation and RGB flag, pixel format, display-on, normal mode, and backlight enable.

State and persistence: panel-specific config is immutable after probe. Runtime state is held in DBI helper fields such as left/top offsets, backlight, rotation, and reset GPIO.

Dependencies and integration: depends on SPI, GPIO, backlight, DRM MIPI DBI, DMA GEM, and OF/SPI IDs.

Risks: long fixed delays in enable affect resume latency. Backlight lookup failure aborts probe, so DT must describe it correctly. Read support is disabled only for configs marked write-only; mismatched boards may expose failing read paths. Offsets and RGB bit are panel-specific and visually obvious if wrong.

Test signals: probe both supported compatibles, exercise rotation 0/90/180/270, verify color ordering, offsets, backlight enable/disable, and remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7735r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7920.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7920.c

Purpose: DRM SPI driver for Sitronix ST7920 monochrome 128x64 LCD controllers using shmem GEM and custom serial command framing.

Important APIs and types: `struct st7920_device` embeds DRM objects and stores SPI/regmap/reset state. `struct st7920_plane_state` owns an intermediate converted buffer; `struct st7920_crtc_state` owns a display-sized `data_array`. `st7920_spi_write()` constructs the ST7920 sync/control/nibble stream for commands, GDRAM addresses, and GDRAM data. Modeset callbacks implement custom atomic state allocation/destruction.

Control flow: probe initializes SPI regmap, allocates DRM device, sets default dimensions, gets optional reset GPIO, initializes modeset, registers DRM, and starts client setup. CRTC enable resets hardware and sends basic/display/graphics/clear sequence. Plane atomic check reserves conversion buffers; update intersects damage with destination, converts XRGB8888 to mono, bit-reverses line bytes, writes each scanline address and data. Disable clears display; CRTC disable powers off.

State and persistence: persistent runtime state includes width/height, SPI pointer, reset GPIO, and DRM objects. Per-commit plane/CRTC states allocate temporary buffers and free them in destroy callbacks. The panel itself stores last GDRAM content until cleared or powered down.

Dependencies and integration: depends on SPI, bitrev, GPIO, regmap, DRM shmem GEM, damage helpers, fixed connector modes, and fbdev shmem setup.

Risks: `st7920_update_rect()` currently writes all 64 scanlines regardless of the damage rectangle, so partial damage only affects conversion but not transfer size. CRTC disable calls `drm_dev_enter()` without checking its return. `data_array` allocation occurs on every CRTC atomic check; memory pressure and duplicate state handling are important. Error aggregation through `struct spi7920_error` stops later writes after first failure, but some clear paths ignore errors.

Test signals: conversion and bit order, reset timing, full-screen update performance, optional reset GPIO absence, SPI error injection, and atomic state allocation/free should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7920.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Kconfig

Purpose: declares configuration symbols for the Solomon/Sino Wealth SSD13xx/SH110x DRM OLED driver core and bus transports.

Important entries: `DRM_SSD130X` is the common core and selects backlight, DRM client setup, shmem GEM, and KMS helpers. `DRM_SSD130X_I2C` depends on the core and I2C and selects REGMAP_I2C. `DRM_SSD130X_SPI` depends on the core and SPI and selects generic REGMAP.

Control flow: selecting only the core builds shared logic but requires a bus transport for hardware binding.

State and persistence: no runtime state.

Dependencies and integration: integrates with DRM, MMU, backlight, I2C/SPI, and regmap Kconfig dependency closure.

Risks: SPI transport uses custom regmap callbacks rather than REGMAP_SPI, so the generic REGMAP select is intentional. Users can misconfigure by enabling the core without a transport.

Test signals: compile combinations for core-only, I2C, SPI, and both transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Makefile

Purpose: maps Solomon SSD130x Kconfig symbols to build objects.

Important APIs/types/functions: no runtime API. Builds `ssd130x.o`, `ssd130x-i2c.o`, and `ssd130x-spi.o` from their matching config symbols.

Control flow: Kbuild includes the shared core and selected transports.

State and persistence: no state.

Dependencies and integration: must align with namespace exports/imports in the core and transport modules.

Risks: transport modules require core symbols; incorrect symbol selection would fail module linking or probing.

Test signals: module and built-in builds for each symbol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-i2c.c

Purpose: I2C transport for the shared SSD130x/SSD132x/SSD133x DRM OLED core.

Important APIs and types: `ssd130x_i2c_regmap_config` uses 8-bit reg/value fields; the core treats command/data control bytes as regmap registers. `ssd130x_i2c_probe()` creates an I2C regmap and calls `ssd130x_probe()`. remove and shutdown delegate to the core. The OF table covers SH1106, SSD1305/1306/1307/1309, deprecated `*fb-i2c` compatibles, and SSD1322/1325/1327.

Control flow: probe is thin: regmap init, core probe, clientdata storage. shutdown and remove retrieve the core device pointer and call core shutdown/remove.

State and persistence: no transport state beyond clientdata and devm regmap.

Dependencies and integration: depends on I2C regmap and core symbols in `DRM_SSD130X` namespace.

Risks: I2C table lacks SSD1331 while SPI supports it; this may reflect bus support, but adding an I2C SSD1331 board would require updating this file. Returning raw `PTR_ERR()` from regmap/core probe gives less context than `dev_err_probe()`.

Test signals: OF match data must select the correct variant, deprecated compatibles should still bind, and remove/shutdown should blank/power down through the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-spi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-spi.c

Purpose: 4-wire SPI transport for the shared SSD13xx DRM core, translating regmap command/data control bytes into D/C GPIO state and raw SPI writes.

Important APIs and types: `struct ssd130x_spi_transport` holds `spi_device` and D/C GPIO. `ssd130x_spi_write()` inspects the first byte for `SSD13XX_COMMAND` or `SSD13XX_DATA`, toggles D/C, strips that byte, and writes the remaining payload. `ssd130x_spi_read()` is unsupported. Probe obtains `dc`, allocates transport state, creates a custom regmap, then calls `ssd130x_probe()`.

Control flow: core write helpers call regmap with command/data pseudo-registers. The SPI write handler converts that protocol to hardware D/C signaling. remove and shutdown delegate to the core.

State and persistence: transport state is devm-managed and immutable after probe.

Dependencies and integration: depends on SPI, GPIO, custom regmap callbacks, OF/SPI ID tables, and `DRM_SSD130X` namespace. OF supports SSD1331 in addition to families available over I2C.

Risks: if a write begins with an unexpected control byte, D/C retains its previous state and `spi_write()` still sends data, which could misclassify traffic. The SPI ID table stores numeric variant IDs, but probe relies on OF `device_get_match_data()` through the core; non-OF SPI matching may not provide core match data unless handled elsewhere.

Test signals: command/data toggling on a logic analyzer, SPI ID autoload, SSD1331 binding, unsupported read behavior, and shutdown sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.c

Purpose: shared DRM/KMS driver for Solomon SSD130x, SSD132x, SSD133x, and Sino Wealth SH110x OLED controllers. It provides variant data, property parsing, power sequencing, display initialization, framebuffer conversion, atomic helpers, backlight contrast control, and DRM object setup.

Important APIs and types: exported `ssd130x_variants[]`, `ssd130x_probe()`, `ssd130x_remove()`, and `ssd130x_shutdown()` are the transport ABI. `struct ssd130x_deviceinfo` describes default geometry, clocks, PWM/chargepump needs, page-mode limitations, and family. Family-specific helper arrays select plane, CRTC, and encoder behavior for SSD130X monochrome pages, SSD132X 4-bit grayscale segments, and SSD133X RGB332 color.

Control flow: probe allocates the DRM device, gets variant match data, sets page mode if required, parses `solomon,*` properties, obtains reset GPIO and VCC regulator, registers a backlight, initializes modeset objects, registers DRM, and starts client setup. Encoder enable powers on, initializes the family-specific controller, turns display on, and enables backlight. Plane atomic update begins CPU access, iterates damage, converts XRGB8888 to R1/R8/RGB332 as needed, and writes the family-specific memory layout. Disable clears the display; remove/shutdown call atomic shutdown.

State and persistence: device state includes parsed geometry, offsets, COM/segment remap flags, contrast, clock/precharge/vcom settings, lookup table, cached column/page ranges, reset/regulator/PWM/backlight handles, and DRM objects. Atomic CRTC/plane state owns transient conversion/data buffers.

Dependencies and integration: uses DRM shmem GEM, damage helpers, fixed connector modes, backlight API, PWM, regulator, GPIO, regmap, and firmware properties. Transports provide the regmap protocol.

Risks: family-specific update functions have coordinate range issues: SSD132x/SSD133x row/column end writes use `columns - 1`/`rows - 1` rather than adding x/y starts, which is correct only for zero-origin rectangles. `ssd130x_fb_blit_rect()` ignores `ssd130x_update_rect()` return. `ssd130x_power_off()` disables and puts `pwm` even when no PWM was acquired; API tolerance matters for variants without PWM. Many command writes during enable are serial and fail-fast, but later display-on/backlight calls ignore return values.

Test signals: per-family panel tests should cover page-mode SH1106, horizontal-mode SSD1306, SSD132x grayscale conversion, SSD1331 color conversion, offsets, property defaults/overrides, backlight contrast writes, regulator/PWM failure unwinding, and damage rectangles away from origin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.h

Purpose: public header shared by SSD130x core and bus transports.

Important APIs and types: defines command/data pseudo-register bytes `SSD13XX_DATA` and `SSD13XX_COMMAND`, family and variant enums, `struct ssd130x_deviceinfo`, and `struct ssd130x_device`. The device struct embeds DRM plane/CRTC/encoder/connector state, regmap, variant info, parsed panel options, backlight/PWM/reset/regulator resources, geometry, and cached address ranges.

Control flow: transport drivers call `ssd130x_probe()`, `ssd130x_remove()`, and `ssd130x_shutdown()`. Match tables pass `ssd130x_variants[]` entries through device match data.

State and persistence: defines all core-owned state but no storage of its own. Cached address fields avoid redundant address-range commands during runtime updates.

Dependencies and integration: includes DRM connector/CRTC/driver/encoder and Linux regmap. Core source adds additional dependencies for resources and conversion.

Risks: `struct ssd130x_device` includes an `i2c_client *client` that is unused by SPI and appears unused by the core, suggesting legacy carryover. Variant enum order must remain synchronized with `ssd130x_variants[]` and transport match data.

Test signals: compile both transports and validate every OF table `.data` entry indexes a valid variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Kconfig

Purpose: defines `DRM_SPRD`, the Unisoc/Spreadtrum DRM display driver option.

Important entry: `DRM_SPRD` depends on `ARCH_SPRD || COMPILE_TEST`, DRM, and OF. It selects DMA GEM, KMS helpers, DRM MIPI DSI, and videomode helpers. The module name is `sprd_drm`.

Control flow: enables the master DRM driver plus DPU, DSI, and PLL objects through the Makefile.

State and persistence: no runtime state.

Dependencies and integration: integrates with OF component probing, MIPI DSI panel/bridge ecosystems, DMA GEM buffers, and videomode conversion.

Risks: only OF systems are supported. Runtime PM is implied by the master atomic commit tail helper, so subdrivers must cooperate with power management even though Kconfig does not expose extra clock/reset dependencies.

Test signals: build on ARCH_SPRD and COMPILE_TEST, plus boot-time OF component binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Makefile

Purpose: builds the Unisoc DRM driver as one composite object.

Important APIs/types/functions: `sprd-drm-y` combines `sprd_drm.o`, `sprd_dpu.o`, `sprd_dsi.o`, and `megacores_pll.o`; `obj-$(CONFIG_DRM_SPRD)` emits `sprd-drm.o`.

Control flow: all subcomponents are linked into the same module/built-in unit, allowing `sprd_drm.c` to register platform drivers exported by DPU and DSI sources.

State and persistence: no runtime state.

Dependencies and integration: must remain aligned with extern declarations in `sprd_drm.h` and DSI PLL functions declared in `sprd_dsi.h`.

Risks: omitting any object breaks link-time references between DSI and PLL or master and subdrivers.

Test signals: module link and modpost with `CONFIG_DRM_SPRD=m` and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/megacores_pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/megacores_pll.c

Purpose: calculates and programs Unisoc MIPI D-PHY PLL and timing registers for the SPRD DSI host.

Important APIs and types: `dphy_pll_config()` reads the attached DSI device `hs_rate`, computes PLL fields with `dphy_calc_pll_param()`, and writes test-interface registers via regmap. `dphy_timing_config()` computes LP/HS request, prepare, zero, trail, exit, and clock-post timings from PLL frequency and writes lane timing registers. `struct dphy_pll` fields are declared in `sprd_dsi.h`.

Control flow: DSI enable calls `dphy_pll_config()` and `dphy_timing_config()` from `sprd_dphy_init()`. PLL calculation scales the requested frequency into the valid VCO band by selecting an output divider, chooses VCO band/filter settings, computes integer and fractional N/K values, then writes a fixed list of PHY test registers.

State and persistence: computed PLL fields persist in `ctx->pll` for the life of the DSI context and for timing calculations. Hardware registers persist until DPHY reset/fini.

Dependencies and integration: depends on `regmap` access provided by the DSI PHY test interface, `do_div()`, MIPI DSI `hs_rate`, and register definitions implicit in the PHY.

Risks: valid VCO range is hard-coded for the sharkle PHY; other SoCs may need different bands/refclk. Arithmetic uses integer scaling and can underflow after subtracting constants in timing formulas if parameters are unexpected. `dphy_pll_config()` ignores any error return from individual `regmap_write()` calls inside `dphy_set_pll_reg()`.

Test signals: panel modes at low/high lane rates, PLL lock after configuration, timing register readback, and invalid `hs_rate` error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/megacores_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.c

Purpose: Unisoc display processing unit DRM CRTC and plane implementation. It programs layer registers, DPI/eDPI timing, interrupts, vblank, and component binding.

Important APIs and types: `struct sprd_plane` wraps `drm_plane`; `struct sprd_dpu` and `struct dpu_context` are declared in the header. Format/rotation/blend conversion helpers map DRM plane state to DPU register bits. `sprd_dpu_run()` and `sprd_dpu_stop()` are exported to the DSI encoder. Component bind creates six planes and one CRTC.

Control flow: master component bind calls `sprd_dpu_bind()`, which creates planes, initializes the CRTC, maps registers, requests IRQ, and initializes wait queues. During atomic mode set, `sprd_crtc_mode_set_nofb()` converts DRM mode to videomode and chooses DPI versus EDPI based on the connected DSI slave's video flag. Plane updates program layer addresses, pitch, position, crop, alpha, format, blend, and rotation. CRTC flush triggers register update or run; IRQ signals update/stop events and vblank.

State and persistence: `dpu_context` holds MMIO base, IRQ, interface type, current videomode, stopped flag, wait queue, and event flags. Hardware layer registers persist until disabled or overwritten.

Dependencies and integration: depends on DRM atomic helpers, DMA GEM framebuffer addresses, OF graph, component framework, DSI state, wait queues, IRQ handling, and memory-mapped registers.

Risks: plane creation uses a hard-coded CRTC mask of `1` and six layers. `sprd_plane_atomic_disable()` assumes `old_state->crtc` is valid. DPU waits are interruptible but treat any nonzero return as success, so interrupted waits may look successful. Address programming uses 32-bit DMA addresses, which may not be enough on all DMA configurations. No explicit runtime PM calls are present in the DPU file despite master commit tail using RPM.

Test signals: multi-plane composition, each supported pixel format, alpha/blend/rotation properties, EDPI stop/update timing, IRQ/vblank, underflow warning handling, and OF graph CRTC discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.h

Purpose: DPU internal definitions for the SPRD DRM driver.

Important APIs and types: defines interface enum values `SPRD_DPU_IF_DPI` and `SPRD_DPU_IF_EDPI`, `struct dpu_context`, `struct sprd_dpu`, cast helper `to_sprd_crtc()`, MMIO helpers `dpu_reg_set()`/`dpu_reg_clr()`, layer register helpers, and public `sprd_dpu_run()`/`sprd_dpu_stop()`.

Control flow: DPU and DSI sources share this header so the DSI encoder can start/stop the DPU around PHY/host enable/disable.

State and persistence: `dpu_context` documents the persistent hardware and synchronization state: base, IRQ, interface type, videomode, stopped flag, wait queue, and event booleans.

Dependencies and integration: includes Linux platform/device/videomode headers and DRM CRTC/fourcc/vblank APIs.

Risks: inline register helpers do relaxed read-modify-write without locking, so callers must serialize register programming through atomic commit/enable paths. Layer offset math assumes fixed `DPU_LAY_REG_OFFSET`.

Test signals: compile integration with both DPU and DSI, plus register programming tests for set/clear/layer index offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.c

Purpose: master DRM driver for the Unisoc display subsystem. It allocates the DRM device, binds DPU/DSI components, initializes mode config, vblank, polling, registration, and platform driver lifecycle.

Important APIs and types: `struct sprd_drm` embeds `drm_device`. `sprd_drm_bind()` is the component master bind callback. `sprd_drm_mode_config_init()` sets 0..8192 size limits and DRM atomic/GEM callbacks. `sprd_drm_drivers[]` registers the master, DPU, and DSI platform drivers together.

Control flow: module init skips when firmware drivers only are requested, then registers all platform drivers. The master probe calls `drm_of_component_probe()`. Bind allocates the DRM device, initializes mode config, binds all components, initializes vblank for created CRTCs, resets state, starts HPD polling, and registers the DRM device. Unbind unregisters DRM, stops polling, and unbinds components. Shutdown calls atomic helper shutdown if the DRM device exists.

State and persistence: master state is the devm-managed `sprd_drm`/`drm_device`; subcomponent state is owned by DPU/DSI components. No persistent storage.

Dependencies and integration: depends on OF component framework, DRM DMA GEM, atomic helpers, vblank, KMS polling, and external `sprd_dpu_driver`/`sprd_dsi_driver` symbols.

Risks: on bind failure after component binding, cleanup must unbind all components; the code handles this for vblank/register failures. `drm_kms_helper_poll_init()` is used even though the attached DSI panel may not have HPD. Master max dimensions are broad and not tied to hardware limits.

Test signals: component probe ordering, bind failure unwinding, module init/exit, firmware-driver-only boot, and shutdown with/without completed bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.h

Purpose: shared master declarations for the SPRD DRM module.

Important APIs and types: `struct sprd_drm` embeds the DRM device. The header declares extern platform drivers `sprd_dpu_driver` and `sprd_dsi_driver` so `sprd_drm.c` can register them as one driver set.

Control flow: included by the master, DPU, and DSI sources for shared driver state and logging/atomic headers.

State and persistence: no storage; it defines the top-level DRM container type.

Dependencies and integration: includes DRM atomic and print headers.

Risks: because subdriver symbols are extern declarations, the Makefile must link the matching objects into the same module.

Test signals: module link/build and probe registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.c

Purpose: Unisoc MIPI DSI host, D-PHY control, DRM encoder, panel bridge, and MIPI DSI host operations.

Important APIs and types: `struct sprd_dsi` contains `mipi_dsi_host`, optional slave, DRM encoder, panel bridge, and `dsi_context`. Register helpers modify MMIO fields. `regmap_tst_io_*()` exposes the PHY test interface as an 8-bit regmap for PLL code. Host ops implement attach/detach/transfer. Encoder helpers initialize video/cmd mode, DPHY, and DPU coordination.

Control flow: platform probe allocates `sprd_dsi` and registers a MIPI DSI host. A panel attaches as `slave`, setting work mode and burst mode, then component-add triggers DRM bind. Bind initializes encoder, attaches panel bridge from OF graph port 1, and maps DSI/PHY resources. Encoder enable initializes host registers, configures DPI or EDPI packet timing, initializes DPHY PLL/timing, switches work mode, resets controller state, configures clock lane mode, starts the DPU, and marks enabled. Disable stops DPU, tears down DPHY and host. Host transfer sends generic/DCS packets or reads using FIFO polling.

State and persistence: `dsi_context` stores MMIO base, PHY regmap, PLL fields, videomode, enabled flag, work/burst mode, interrupt masks, timing constants, max read time, and TE/frame ACK options. Attached slave stores lanes, format, rates, and mode flags.

Dependencies and integration: depends on component framework, DRM bridge/panel/OF helpers, MIPI DSI host API, DPU public run/stop functions, and `megacores_pll.c`.

Risks: `sprd_dsi_context_init()` initializes `ctx->enabled = true`, so the first encoder enable will warn and return without programming hardware unless another path clears it; this is a notable behavioral risk. `dphy_pll_config()` return is ignored in `sprd_dphy_init()`. Video packet range programming often uses sizes relative to zero and may mishandle nonzero offsets if ever introduced. FIFO polling is busy-wait based. Host transfer returns 0 for empty messages and count for reads, but write transfers return only 0 or error rather than transmitted length.

Test signals: attach/detach component sequencing, first enable behavior, video and command mode panels, burst/non-burst calculations, PLL lock timeout, read/write packet transfers, continuous and non-continuous clock modes, and bridge removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.h

Purpose: shared DSI/DPHY type and helper declarations for the SPRD DRM DSI host and PLL implementation.

Important APIs and types: defines work mode, video burst mode, color coding, and PLL timing enums. `struct dphy_pll` stores calculated PLL configuration and frequency fields. `struct dsi_context` stores MMIO/regmap, PLL, videomode, mode flags, timing values, masks, and ACK options. `struct sprd_dsi` embeds the MIPI host, slave device pointer, DRM encoder, panel bridge, and context. Public functions are `dphy_pll_config()` and `dphy_timing_config()`.

Control flow: `sprd_dsi.c` owns runtime host/encoder operations; `megacores_pll.c` consumes `dsi_context` and `dphy_pll` to program PHY registers.

State and persistence: defines the persistent DSI state layout used across component bind, panel attach, encoder enable/disable, and host transfers.

Dependencies and integration: includes OF/device/regmap/videomode plus DRM bridge, connector, encoder, MIPI DSI, panel, and print APIs.

Risks: `encoder_to_dsi()` assumes the DRM encoder is embedded in `struct sprd_dsi`. Public enums contain spelling `COLOR_CODE_COMPRESSTION`, so external changes must preserve compatibility or update all references.

Test signals: compile integration between DSI and PLL files, and runtime checks that panel attach fills `slave` before enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Kconfig

Purpose: declares `DRM_STI`, the STMicroelectronics stiH4xx DRM driver option.

Important entry: depends on OF, DRM, and `ARCH_STI || COMPILE_TEST`; selects reset controller, DRM client setup, KMS helpers, DMA GEM, DRM panel, firmware loader, and optionally HDMI codec support when sound SoC support exists.

Control flow: enabling the symbol builds the composite `sti-drm` object with mixer, planes, HDMI, VTG, HDA, TV out, HQVDP, AWG utilities, and driver glue.

State and persistence: no runtime state.

Dependencies and integration: ties the DRM driver to firmware loading, panel/HDMI, reset, and optional audio codec infrastructure.

Risks: broad composite selection means build failures in any STI subcomponent affect the whole driver. Optional HDMI audio depends on sound configuration.

Test signals: COMPILE_TEST builds and boot on stiH4xx hardware with HDMI/panel paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Makefile

Purpose: builds the STMicroelectronics STI DRM driver as a composite object.

Important APIs/types/functions: `sti-drm-y` includes mixer, GDP, VID, cursor, compositor, CRTC, plane, HDMI, HDMI PHY, DVO, AWG utilities, VTG, HDA, TV out, HQVDP, and driver glue. `obj-$(CONFIG_DRM_STI) = sti-drm.o`.

Control flow: Kbuild links all listed STI display components into one module or built-in object.

State and persistence: no runtime state.

Dependencies and integration: must match source filenames and internal symbol references across the STI display stack.

Risks: the assignment uses `=` rather than `+=`, which is valid here but should not be duplicated elsewhere for the same symbol. Removing `sti_awg_utils.o` would break video timing generator helpers that call it.

Test signals: module link and full STI driver build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.c

Purpose: generates firmware-like instruction words for the STI AWG block in data-enable mode, based on display timing parameters.

Important APIs and types: exported `sti_awg_generate_code_data_enable_mode()` fills `struct awg_code_generation_params` using `struct awg_timing`. Internal `enum opcode` names instruction types. `awg_generate_instr()` encodes opcode, argument, mux select, and data-enable bit into 14-bit RAM words, splitting long skip/repeat/replay counts across multiple instructions up to `AWG_MAX_ARG`. `awg_generate_line_signal()` builds one line's data-enable waveform.

Control flow: caller supplies a RAM buffer and zeroed/initial offset. Generation optionally emits trailing-line replay, emits active-line line signal plus replay loops in chunks of `AWG_MAX_ARG`, and optionally emits blanking-line replay. Line generation handles trailing pixels, active pixels, and blanking pixels with `SET`/`RPLSET`/`SKIP` instructions and an `AWG_DELAY` adjustment.

State and persistence: state is the caller-provided `ram_code` array and `instruction_offset`. Hardware programming is not done here; this file only generates code.

Dependencies and integration: depends on DRM logging and `sti_awg_utils.h`. It is linked into the STI DRM composite driver and likely consumed by VTG/HDMI/DVO timing code.

Risks: return values are OR-aggregated, so the first negative error remains negative but multiple errors are not distinguished. Instruction overflow is checked against `AWG_MAX_INST`; callers must provide a buffer of that size. The `while (arg_tmp > 0)` logic can return early for zero/negative skip cases and mutates `opcode` from SKIP to SET for one-pixel skips, so edge timings need careful tests.

Test signals: unit-level generation for zero/one/large trailing, active, and blanking intervals; instruction count overflow; and expected RAM opcodes for known display timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.h

Purpose: public declarations for STI AWG instruction generation helpers.

Important APIs and types: defines `AWG_MAX_INST` as 64, `struct awg_code_generation_params` with output RAM pointer and instruction offset, `struct awg_timing` with total/active/blanking/trailing line and pixel counts plus blanking level, and `sti_awg_generate_code_data_enable_mode()`.

Control flow: callers populate timing and generation parameters, call the generator, then program generated RAM words elsewhere.

State and persistence: no storage in the header. The generated state is caller-owned through `ram_code` and `instruction_offset`.

Dependencies and integration: includes `linux/types.h`; implemented by `sti_awg_utils.c` and linked into `sti-drm.o`.

Risks: the API assumes `ram_code` points to at least `AWG_MAX_INST` 32-bit entries. `instruction_offset` is 8-bit, which is enough for 64 entries but should remain aligned with `AWG_MAX_INST`.

Test signals: compile users against this header and verify generator output stays under `AWG_MAX_INST` for supported display timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.h -->
