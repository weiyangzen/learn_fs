# subset-b-003599 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.c

## Purpose
`intel_psr.c` implements Intel display Panel Self Refresh support for i915 DisplayPort/eDP outputs, including classic PSR1, PSR2 selective update, DisplayPort Panel Replay, Panel Replay selective update, ALPM coordination, DC3CO handling, frontbuffer tracking, IRQ/error handling, and debugfs status/control. The code bridges DP sink DPCD capability discovery, atomic mode computation, hardware register programming, software frontbuffer invalidation/flush callbacks, and runtime workqueue reactivation.

## Important APIs, Types, And Functions
The exported API is declared in `intel_psr.h`. Key entry points are `intel_psr_init()`, `intel_psr_init_dpcd()`, `intel_psr_compute_config()`, `intel_psr_compute_config_late()`, `intel_psr_pre_plane_update()`, `intel_psr_post_plane_update()`, `intel_psr_disable()`, `intel_psr_invalidate()`, `intel_psr_flush()`, `intel_psr_irq_handler()`, `intel_psr_short_pulse()`, and the pipe-update helpers `intel_psr_lock()`, `intel_psr_wait_for_idle_locked()`, and `intel_psr_unlock()`.

Internally, mode selection is represented in CRTC state as `has_psr`, `has_sel_update`, and `has_panel_replay`. Runtime state lives in `intel_dp->psr` (`struct intel_psr` in `intel_display_types.h`) with flags such as `enabled`, `active`, `sel_update_enabled`, `panel_replay_enabled`, `psr2_sel_fetch_enabled`, `su_region_et_enabled`, `busy_frontbuffer_bits`, `sink_not_reliable`, `link_ok`, ALPM wake-line fields, and delayed work state. The file uses register definitions from `intel_psr_regs.h` and DPCD definitions from the DRM DP helpers.

Important internal clusters include DPCD probing (`_psr_init_dpcd()`, `_panel_replay_init_dpcd()`), sink enable programming (`_psr_enable_sink()`, `_panel_replay_enable_sink()`, `intel_psr_enable_sink()`), source activation (`hsw_activate_psr1()`, `hsw_activate_psr2()`, `dg2_activate_panel_replay()`), validation (`intel_psr2_config_valid()`, `intel_sel_update_config_valid()`, `_panel_replay_compute_config()`), selective fetch damage calculation (`intel_psr2_sel_fetch_update()`), and status/debug helpers (`intel_psr_status()`, `i915_psr_sink_status_show()`).

## Control Flow
Initialization starts in `intel_psr_init()`, which checks hardware support, limits older platforms to supported ports, sets source support for eDP PSR or DP/eDP Panel Replay, initializes `psr.lock`, `psr.work`, and `psr.dc3co_work`. DPCD probing through `intel_psr_init_dpcd()` reads PSR and Panel Replay capabilities, records sink support/granularity/DSC support on the connector, and sets `intel_dp->psr.sink_support` or `sink_panel_replay_support`.

During atomic check, `intel_psr_compute_config()` rejects global disables, unreliable sinks, interlaced modes, and joiner modes, then tries Panel Replay first and falls back to PSR. It separately computes selective update eligibility and late guardband checks in `intel_psr_compute_config_late()`. During commit, `intel_psr_pre_plane_update()` disables PSR/Panel Replay when a modeset or incompatible state transition requires it, while `intel_psr_post_plane_update()` enables source and sink if the new state remains valid.

Enable flow is `intel_psr_enable_locked()` -> `intel_psr_enable_sink()` -> `intel_psr_enable_source()` -> `intel_psr_activate()`. Activation selects one mutually exclusive path: PSR1, PSR2, or Panel Replay. Disable flow exits the active mode, waits for the status register to become idle, clears workarounds, disables sink state when appropriate, and resets runtime flags.

Frontbuffer tracking calls `intel_psr_invalidate()` when rendering starts and `intel_psr_flush()` when rendering finishes. Invalidation tracks dirty pipe frontbuffer bits and exits PSR or configures full-frame selective fetch updates. Flush clears busy bits, handles flip/DC3CO special cases, forces updates, and queues `intel_psr_work()` to reactivate once hardware is idle and no dirty frontbuffers remain.

## State And Persistence Behavior
PSR state is not persistent across driver initialization, but the sink/source capability bits, connector DPCD caches, and `intel_dp->psr` runtime fields persist for the lifetime of the connector/DP object. `psr.lock` serializes all runtime PSR transitions. Workqueue callbacks deliberately drop/reacquire the lock around idle waits and then revalidate that PSR is still enabled and unpaused. `sink_not_reliable` is sticky once set after AUX, DPCD, capability-change, ALPM, or sink error signals, preventing future enable until a larger reinitialization path clears/recreates state.

## Dependencies And Integration Points
The file integrates with DP AUX/DPCD (`drm_dp_dpcd_read*`, `drm_dp_dpcd_writeb()`), atomic state and plane damage helpers, frontbuffer tracking, DSB programming, ALPM (`intel_alpm_*`), DMC/DC power state code, VRR, DSC, HDCP, display workarounds, debugfs, display IRQ routing, and register MMIO helpers. `intel_dp.c` calls the compute/probe/init paths, `intel_frontbuffer.c` calls invalidate/flush, `intel_display_irq.c` routes PSR IRQs, `intel_crtc.c` uses the lock/idle helpers around pipe updates, and `intel_vrr.c` consumes PSR guardband requirements.

## Risks
The main risks are hardware sequencing and race bugs: PSR is sensitive to vblank timing, AUX wake timing, ALPM wake lines, workqueue reactivation, dirty frontbuffer accounting, and platform-specific workarounds. Selective fetch can under-update if damage rectangles, cursor coverage, DSC slice alignment, or early transport sizing are wrong. Error handling intentionally marks sinks unreliable, which is conservative for display correctness but can disable power-saving features until re-probe. Debugfs mode changes force fastsets and can perturb active pipelines. Many checks are platform/stepping-specific, so adding new display versions without auditing register bit layouts and workarounds is high risk.

## Test Signals
Useful signals include debugfs `i915_psr_status`, `i915_psr_sink_status`, `i915_edp_psr_status`, PSR event logs, DPCD sink error status, PSR/PSR2 status registers, performance counters, frontbuffer invalidation/flush behavior, suspend/resume and hotplug/short-pulse tests, pipe CRC interactions, DSC/VRR/HDCP combinations, selective fetch damage tests with cursor, plane movement, rotation/scaling rejection, and platform power-state residency checks for DC5/DC6/DC3CO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.h

## Purpose
`intel_psr.h` is the public header for i915 display PSR, PSR2 selective update, Panel Replay, ALPM-related PSR queries, and debugfs registration. It exposes the PSR lifecycle and atomic-commit hooks used by the rest of the display driver.

## Important APIs, Types, And Functions
The header forward-declares display objects used by the API and defines `CAN_PANEL_REPLAY(intel_dp)`, which requires both source and sink Panel Replay support. Exported functions cover capability checks (`intel_encoder_can_psr()`, `intel_psr_enabled()`, `intel_psr_link_ok()`), DPCD/init (`intel_psr_init_dpcd()`, `intel_psr_init()`), atomic config (`intel_psr_compute_config()`, `intel_psr_compute_config_late()`, `intel_psr_get_config()`), commit sequencing (`intel_psr_pre_plane_update()`, `intel_psr_post_plane_update()`, `intel_psr_disable()`), frontbuffer tracking (`intel_psr_invalidate()`, `intel_psr_flush()`), selective fetch programming, IRQ/short-pulse handling, pause/resume, and debugfs setup.

## Control Flow
Callers use this header to stitch PSR into connector probing, atomic checking, pipe update locking, frontbuffer invalidation, IRQ handling, and debugfs. The expected sequence is capability discovery, atomic mode computation, pre-plane disable if necessary, post-plane enable, frontbuffer-driven exit/re-entry during rendering, and explicit disable before pipe shutdown.

## State And Persistence Behavior
The header does not define storage except through referenced structs. It exposes functions that operate on persistent `intel_dp->psr` state owned by `struct intel_dp`. State mutation is serialized in the implementation by `psr.lock`.

## Dependencies And Integration Points
It depends only on Linux integer types and forward declarations, minimizing include fan-out. Integration points include `intel_dp.c`, `intel_crtc.c`, `intel_cursor.c`, `intel_frontbuffer.c`, `intel_display_irq.c`, `intel_display_debugfs.c`, ALPM, VRR, and DSB paths.

## Risks
Because this header is a broad cross-subsystem contract, signature changes have a large blast radius across atomic commit, IRQ, frontbuffer, and debugfs paths. The macro `CAN_PANEL_REPLAY()` assumes `intel_dp` is valid and that source/sink capability bits have already been initialized.

## Test Signals
Build coverage is the primary signal for declaration consistency. Runtime signals come from successful connector probe, atomic modesets, PSR debugfs registration, IRQ routing, and frontbuffer callbacks compiling and linking against these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr_regs.h

## Purpose
`intel_psr_regs.h` centralizes MMIO register addresses and bitfield definitions for PSR1, PSR2, selective update tracking, Panel Replay/ALPM controls, PSR events, status registers, and port ALPM LFPS programming.

## Important APIs, Types, And Functions
This is a macro-only register definition header. Important register families include `TRANS_EXITLINE()`, `EDP_PSR_CTL()`, `TRANS_PSR_IMR()`, `TRANS_PSR_IIR()`, `EDP_PSR_AUX_CTL()`, `EDP_PSR_STATUS()`, `EDP_PSR_DEBUG()`, `EDP_PSR2_CTL()`, `PSR_EVENT()`, `EDP_PSR2_STATUS()`, `PSR2_MAN_TRK_CTL()`, `LNL_SFF_CTL()`, `LNL_CFF_CTL()`, `PIPE_SRCSZ_ERLY_TPT()`, `PR_ALPM_CTL()`, `ALPM_CTL()`, `ALPM_CTL2()`, `PORT_ALPM_CTL()`, and `PORT_ALPM_LFPS_CTL()`.

## Control Flow
The header has no executable flow. Runtime code uses these macros to pick platform/transcoder-specific registers and compose RMW masks for enabling PSR, selecting idle frames and training-pattern timing, reporting events, programming selective update regions, and configuring ALPM wake/sleep behavior.

## State And Persistence Behavior
The macros describe hardware state stored in display MMIO registers. Values programmed with these masks persist in hardware until later MMIO writes, power transitions, or reset. Several definitions distinguish legacy fixed registers from transcoder-relative registers.

## Dependencies And Integration Points
It includes `intel_display_reg_defs.h` and `intel_dp_aux_regs.h`. Users include `intel_psr.c`, ALPM code, display IRQ/debugfs paths, cursor/plane code, GVT MMIO tables, and virtualization handlers that need register knowledge.

## Risks
Bitfield accuracy is critical. A wrong mask, shift, or generation-specific address can silently program incorrect hardware state, causing display hangs, under-updates, failed low-power entry, or interrupt storms. The macro `EDP_MAX_SU_DISABLE_TIME(t)` appears to use `EDP_MAX_SU_DISABLE_TIME` instead of its mask name and should be treated carefully if used. Platform split points such as display version 20 and 30 require explicit auditing when adding new hardware.

## Test Signals
Signals include register readback through debugfs, PSR status transitions, IRQ mask behavior, selective update correctness, ALPM entry/exit, GVT register coverage, and hardware validation on each supported display generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_psr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.c

## Purpose
`intel_qp_tables.c` provides static Display Stream Compression rate-control quantization parameter lookup tables for i915. The tables map bits-per-component, buffer range index, target bits-per-pixel index, and 4:4:4 versus 4:2:0 format to DSC range min/max QP values.

## Important APIs, Types, And Functions
The only exported functions are `intel_lookup_range_min_qp()` and `intel_lookup_range_max_qp()`. They use `PARAM_TABLE()` to select one of twelve static `u8` tables: min/max QP for 4:4:4 at 8/10/12 bpc and min/max QP for 4:2:0 at 8/10/12 bpc. Table dimensions are based on `DSC_NUM_BUF_RANGES` and per-format BPP-count constants.

## Control Flow
Callers pass `bpc`, `buf_i`, `bpp_i`, and `is_420`. The lookup macro checks the requested bpc, chooses the 4:2:0 or 4:4:4 table, and returns `table[buf_i][bpp_i]`. Unknown bpc values hit `MISSING_CASE(bpc)` and return 0.

## State And Persistence Behavior
All table data is compile-time constant and read-only. There is no dynamic state, locking, allocation, or persistence beyond the binary image.

## Dependencies And Integration Points
The file includes DRM DSC definitions for `DSC_NUM_BUF_RANGES`, i915 display utility macros for `MISSING_CASE`, and its own header. It is used by DSC parameter calculation code that needs C-model-aligned QP range values for PPS/rate-control programming.

## Risks
The functions do not bounds-check `buf_i` or `bpp_i`; callers must ensure indices match the selected table width and `DSC_NUM_BUF_RANGES`. Incorrect table values or index calculation errors can degrade DSC visual quality or violate sink expectations. Unsupported bpc silently returns 0 after `MISSING_CASE`, which is safe for build coverage but likely wrong for a real mode.

## Test Signals
Useful signals include DSC conformance tests, PPS programming inspection, mode validation across 8/10/12 bpc and RGB/YCbCr420 formats, fuzz or KUnit-style index-bound tests around caller calculations, and visual corruption checks on compressed links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.h

## Purpose
`intel_qp_tables.h` declares the DSC QP lookup API implemented by `intel_qp_tables.c`.

## Important APIs, Types, And Functions
The header includes Linux integer types and declares `intel_lookup_range_min_qp()` and `intel_lookup_range_max_qp()`. Both return `u8` QP values and take `bpc`, DSC buffer range index, BPP index, and a boolean indicating YCbCr420 table selection.

## Control Flow
There is no control flow in the header. It provides declarations for DSC code to call into static table lookups.

## State And Persistence Behavior
No state is declared here. All state is immutable table data in the implementation.

## Dependencies And Integration Points
This header is included by DSC-related display code needing range min/max QP values. It keeps callers independent from the table layout and constants in the `.c` file.

## Risks
The API does not encode table bounds in the type system. Callers must preserve the same BPP-indexing scheme used by the implementation.

## Test Signals
Build/link success validates declarations. Runtime or unit signals should exercise both functions for every supported bpc and format combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.c

## Purpose
`intel_quirks.c` applies platform, subsystem, DMI, and sink-DPCD-specific display quirks for known machines and panels. Quirks compensate for incorrect firmware tables, board-specific electrical needs, panel bugs, or feature incompatibilities.

## Important APIs, Types, And Functions
The exported functions are `intel_init_quirks()`, `intel_init_dpcd_quirks()`, `intel_has_quirk()`, and `intel_has_dpcd_quirk()`. Internal data structures are `struct intel_quirk` for PCI device/subsystem matches, `struct intel_dpcd_quirk` for PCI plus sink OUI/device ID matches, and `struct intel_dmi_quirk` for DMI match tables. Hook functions set bits in `display->quirks.mask` or `intel_dp->quirks.mask`.

## Control Flow
At display initialization, `intel_init_quirks()` iterates `intel_quirks[]` and applies hooks whose PCI device, subsystem vendor, and subsystem device match, then evaluates DMI tables. During DP probe, `intel_init_dpcd_quirks()` additionally matches the current PCI IDs and DP sink identity before applying DPCD-scoped hooks. Query helpers test the bitmasks.

## State And Persistence Behavior
Applied quirks persist in bitmasks attached to `struct intel_display` or `struct intel_dp` for the device lifetime. They are not stored to disk. DPCD quirks are per-DP object and depend on sink identity observed during probe.

## Dependencies And Integration Points
The file uses Linux DMI matching, PCI IDs via `to_pci_dev()`, DRM logging, and i915 display/DP types. Quirk consumers include backlight setup, LVDS SSC/refclock paths, panel power sequencing, eDP link-rate limiting, fast-wake programming, and Panel Replay gating.

## Risks
Quirk matching is deliberately specific, but false positives can disable features or change electrical/timing behavior on unrelated systems. False negatives leave known-bad hardware paths active. DPCD sink-device matching treats an all-zero sink device ID in the table as wildcard, so additions must choose OUI/device matching carefully. Hook logging is useful but can become noisy if a broad match is added.

## Test Signals
Signals include boot logs showing expected quirk application, DMI/PCI matching tests on affected machines, panel/backlight behavior, eDP link-rate selection, PSR/Panel Replay availability on quirked sinks, and regression checks on systems sharing subsystem IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.h

## Purpose
`intel_quirks.h` defines the display quirk IDs and the public API for initializing and querying i915 display quirks.

## Important APIs, Types, And Functions
The key type is `enum intel_quirk_id`, with entries for backlight presence/inversion, LVDS SSC disable, increased panel/DDI delays, PPS backlight hook disable, fast-wake sync length, eDP HBR2 rate limiting, and eDP Panel Replay disable. The API consists of `intel_init_quirks()`, `intel_init_dpcd_quirks()`, `intel_has_quirk()`, and `intel_has_dpcd_quirk()`.

## Control Flow
The header itself has no flow. It lets initialization code populate quirk masks and feature code query those masks before choosing hardware behavior.

## State And Persistence Behavior
No state is defined in the header. Consumers store quirk bits in `display->quirks.mask` or `intel_dp->quirks.mask`.

## Dependencies And Integration Points
It forward-declares `intel_display`, `intel_dp`, and `drm_dp_dpcd_ident`, allowing PCI/DMI and DP probe code to share the same quirk IDs without pulling in full type definitions.

## Risks
Adding enum values changes the bit positions used in masks, so existing values should remain stable. Since masks use `BIT(quirk)`, enum growth must stay within the backing mask width.

## Test Signals
Compile coverage validates API use. Runtime signals include expected quirk bits being visible through consumers and correct behavior on affected hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.c

## Purpose
`intel_rom.c` abstracts access to Intel option ROM/VBT storage through either PCI ROM mapping or SPI flash registers. It gives higher-level BIOS/VBT parsing code a common read/find/free interface independent of the transport.

## Important APIs, Types, And Functions
The private `struct intel_rom` stores either PCI ROM state (`pdev`, `oprom`) or SPI state (`uncore`, `offset`), a size, and function pointers for `read32`, `read16`, optional `read_block`, and `free`. Public constructors are `intel_rom_spi()` and `intel_rom_pci()`. Public accessors are `intel_rom_read32()`, `intel_rom_read16()`, `intel_rom_read_block()`, `intel_rom_find()`, `intel_rom_size()`, and `intel_rom_free()`.

## Control Flow
`intel_rom_spi()` allocates a ROM object, configures the primary SPI region from `SPI_STATIC_REGIONS`, reads the option ROM offset, fixes size to 2 MiB, and installs SPI read functions. SPI reads write `PRIMARY_SPI_ADDRESS` and read `PRIMARY_SPI_TRIGGER`. `intel_rom_pci()` maps the PCI ROM with `pci_map_rom()` and installs IO memory read functions. `intel_rom_read_block()` uses a native block reader when available, otherwise reads 32-bit words in a loop. `intel_rom_find()` linearly scans 32-bit aligned offsets for a signature.

## State And Persistence Behavior
ROM objects are heap allocated and caller-owned. PCI mappings persist until `intel_rom_free()` calls the transport-specific `free` callback and then `kfree()`. SPI constructor programs uncore registers but does not maintain a mapping. The code does not cache ROM contents.

## Dependencies And Integration Points
The file depends on PCI ROM APIs, DRM device conversion helpers, i915 uncore MMIO access, and option ROM register definitions. `intel_bios.c` uses this API to locate and read VBT data, trying SPI flash and PCI ROM paths.

## Risks
The fallback block reader assumes the requested size can be read as 32-bit chunks; callers should avoid unaligned/trailing-byte assumptions. `intel_rom_find()` only checks 4-byte-aligned signatures. SPI size is hard-coded to 2 MiB, so future platforms with different regions need validation. All reads assume offsets were validated by callers against `intel_rom_size()`.

## Test Signals
Signals include successful VBT discovery from SPI and PCI ROM, correct fallback when one transport is absent, kmemleak/resource checks around map/unmap/free, and negative tests for missing signatures or invalid ROM sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.h

## Purpose
`intel_rom.h` declares the opaque option ROM access API used by i915 display BIOS/VBT parsing code.

## Important APIs, Types, And Functions
It forward-declares `struct intel_rom` and `struct drm_device`, then declares constructors for SPI and PCI ROM transports plus read, block-read, signature-find, size, and free functions.

## Control Flow
No executable flow exists in the header. Callers construct a ROM object with one transport, inspect size/find signatures/read blocks, then release it with `intel_rom_free()`.

## State And Persistence Behavior
The header makes `struct intel_rom` opaque, forcing callers to use the accessor API and keeping transport-specific state private to the implementation.

## Dependencies And Integration Points
It includes Linux types for `u32`, `u16`, `loff_t`, and `size_t`. The primary integration point is `intel_bios.c`.

## Risks
The API returns raw integer reads without explicit error returns, so construction failure and offset validation are caller responsibilities. Callers must always pair successful construction with `intel_rom_free()`.

## Test Signals
Build coverage validates declaration consistency. Runtime signals include VBT load success, fallback behavior across ROM transports, and absence of leaked PCI ROM mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.c

## Purpose
`intel_sbi.c` implements locked access to the LPT/WPT IOSF Sideband Interface used by display code to program ICLK and MPHY sideband registers, especially for PCH refclock/SSC setup.

## Important APIs, Types, And Functions
The central helper is `intel_sbi_rw()`, which performs one read or write transaction. Public functions are `intel_sbi_init()`, `intel_sbi_fini()`, `intel_sbi_lock()`, `intel_sbi_unlock()`, `intel_sbi_read()`, and `intel_sbi_write()`. The destination enum is declared in `intel_sbi.h`.

## Control Flow
Callers are expected to acquire `display->sbi.lock` with `intel_sbi_lock()`. `intel_sbi_rw()` waits up to 100 ms for `SBI_CTL_STAT` to report ready, writes `SBI_ADDR`, writes `SBI_DATA` for writes, composes a command for ICLK or MPHY and read/write operation, marks the transaction busy, waits for completion, checks `SBI_RESPONSE_FAIL`, and reads back `SBI_DATA` for reads. Public read/write wrappers ignore the internal error code except that reads return 0 on failure.

## State And Persistence Behavior
The only software state is `display->sbi.lock`, initialized and destroyed by the init/fini functions. Hardware state is whatever sideband registers callers modify. Lockdep asserts that transactions occur with the mutex held.

## Dependencies And Integration Points
The file uses `intel_de_*_fw` MMIO helpers, DRM logging, display core state, and register definitions from `intel_sbi_regs.h`. It is initialized from driver setup/teardown and used heavily by `intel_pch_refclk.c`.

## Risks
The wrapper read/write APIs do not propagate transaction errors, so callers may proceed with a 0 read or failed write after logging. Destination-specific command selection is asymmetric: ICLK uses `SBI_CTL_OP_CRRD`, MPHY uses `SBI_CTL_OP_IORD`, and writes add `SBI_CTL_OP_WR`; any future destination or operation needs careful command encoding. Missing locks can race sideband transactions.

## Test Signals
Signals include absence of SBI timeout/error logs, correct refclock/SSC behavior on LPT/WPT systems, lockdep coverage for held locks, and successful display bring-up on platforms that require sideband programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.h

## Purpose
`intel_sbi.h` declares the i915 display Sideband Interface API and destination selector used for LPT/WPT IOSF sideband register access.

## Important APIs, Types, And Functions
The key type is `enum intel_sbi_destination` with `SBI_ICLK` and `SBI_MPHY`. The API exposes init/fini, explicit lock/unlock, and `intel_sbi_read()`/`intel_sbi_write()`.

## Control Flow
The header defines the expected caller pattern: initialize during display driver setup, lock around one or more sideband operations, perform reads/writes to a selected destination, unlock, and destroy during teardown.

## State And Persistence Behavior
No state is declared here. The backing mutex lives in `struct intel_display` and hardware side effects live in sideband registers.

## Dependencies And Integration Points
It includes Linux integer types and forward-declares `struct intel_display`. Users include display driver init/fini and PCH refclock programming.

## Risks
The API exposes manual locking, so callers can omit or mis-balance locks. Read/write functions do not return errors, making log monitoring important for failures.

## Test Signals
Build coverage validates API consumers. Runtime signals include lockdep, SBI timeout logs, and refclock stability on affected chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi_regs.h

## Purpose
`intel_sbi_regs.h` defines MMIO register addresses and bitfields for the display Sideband Interface plus commonly used sideband offsets for spread-spectrum clocking and DBUF configuration.

## Important APIs, Types, And Functions
This header is macro-only. It defines `SBI_ADDR`, `SBI_DATA`, `SBI_CTL_STAT`, address/data/command/status masks, destination encodings for ICLK and MPHY, operation encodings, response/status values, and sideband offsets such as `SBI_SSCDIVINTPHASE`, `SBI_SSCDIVINTPHASE6`, `SBI_SSCDITHPHASE`, `SBI_SSCCTL`, `SBI_SSCCTL6`, `SBI_SSCAUXDIV6`, `SBI_DBUFF0`, and `SBI_GEN0`.

## Control Flow
There is no executable control flow. `intel_sbi.c` uses the command/status macros to drive transactions, while refclock code uses the offset and field macros to update specific sideband registers.

## State And Persistence Behavior
The macros describe hardware-visible state. Values written through SBI persist in the target sideband registers until changed by software, firmware, reset, or power transitions.

## Dependencies And Integration Points
The header includes `intel_display_reg_defs.h` for `_MMIO`, `REG_BIT`, `REG_GENMASK`, and field helpers. It is included by `intel_sbi.c`, PCH refclock code, GVT MMIO tables, and virtualization handlers.

## Risks
Incorrect operation/destination encoding can make all SBI transactions fail or access the wrong sideband target. Several older field macros use raw shifts rather than `REG_FIELD_PREP`, so callers must avoid mixing pre-shifted and unshifted values incorrectly.

## Test Signals
Signals include successful SBI read/write transactions, correct SSC/refclock programming, no `SBI_RESPONSE_FAIL` logs, and GVT register emulation coverage for the defined MMIO registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi_regs.h -->
