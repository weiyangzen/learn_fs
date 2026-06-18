# Research group subset-b-003639

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.c

### Purpose

`lsdc_ttm.c` implements Loongson LSDC buffer-object storage on top of DRM TTM. It owns placement selection for VRAM, TT/GTT, and system memory, BO movement and eviction policy, kernel mapping helpers, pinned kernel BO allocation, TTM resource-manager initialization, and debugfs exposure for the VRAM/GTT managers.

### Important APIs, types, and functions

The file exports `lsdc_mem_type_to_str()`, `lsdc_domain_to_str()`, `lsdc_bo_create()`, `lsdc_bo_create_kernel_pinned()`, `lsdc_bo_free_kernel_pinned()`, reserve/unreserve, pin/unpin, ref/unref, `lsdc_bo_gpu_offset()`, `lsdc_bo_size()`, kmap/kunmap/clear, `lsdc_bo_evict_vram()`, `lsdc_ttm_init()`, and `lsdc_ttm_debugfs_init()`. The TTM callback table `lsdc_bo_driver` provides TT creation/populate/unpopulate/destroy, eviction placement, movement, and IO bus reservation.

### Control flow

BO creation allocates `struct lsdc_bo`, initializes the embedded GEM object and TTM BO, selects a BO type from kernel/sg/device inputs, fills `ttm_placement`, then calls `ttm_bo_init_validate()`. Placement prefers requested LSDC domains and falls back to system memory; page-sized objects get TOPDOWN placement. Pinning optionally revalidates to a requested domain, updates `vram_pinned_size` or `gtt_pinned_size`, increments TTM pin count, and returns a GPU offset for non-system placements. Movement waits for fences, handles null/system/TT transitions cheaply, and uses memcpy for real memory moves. Initialization creates the TTM device plus VRAM and TT range managers and registers managed teardown.

### State and persistence behavior

Persistent driver state is in `struct lsdc_bo` placement arrays, maps, pin counts, list linkage, and in `struct lsdc_device` TTM device/resource managers and pinned-size counters. Hardware-visible state is the VRAM bus offset computed from `ldev->vram_base` and resource start pages. Imported scatter-gather BOs use external TT pages and only convert SG entries into DMA address arrays; they are not freed through the TTM pool.

### Dependencies

It depends on DRM GEM lifetime helpers, PRIME SG helpers, drm-managed cleanup, TTM BO/TT/range-manager APIs, DMA reservations/fences, and Loongson device helpers from `lsdc_drv.h`. Debugfs integration depends on the DRM primary minor and TTM resource-manager debugfs helpers.

### Integration points

This is the memory-management backend used by LSDC GEM, framebuffer, scanout, and kernel BO paths. Scanout users reserve and pin BOs, then consume `lsdc_bo_gpu_offset()`. Device teardown reaches `lsdc_ttm_fini()` through `drmm_add_action_or_reset()`. Debugfs exposes `vram_mm` and `gtt_mm` beneath the DRM minor root.

### Risks

Pinned objects cannot be moved; callers must reserve BOs correctly around pin/unpin. `lsdc_bo_gpu_offset()` returns zero for unpinned or system BOs, which can silently become an invalid scanout address if ignored. Imported/shared BOs are rejected for VRAM pinning, so PRIME sharing paths must tolerate placement limits. Error paths after range-manager initialization do not explicitly unwind earlier managers until managed cleanup is registered, so init ordering matters.

### Test signals

Useful signals include DRM/KMS boot with VRAM scanout, GEM BO creation/import/export, CPU mapping and clear operations on VRAM and TT, pin/unpin accounting under repeated modesets, VRAM eviction under pressure, suspend/remove cleanup, and debugfs `vram_mm`/`gtt_mm` presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.h

### Purpose

`lsdc_ttm.h` declares the Loongson LSDC TTM/GEM buffer-object interface and defines the domain flags used by the driver to describe preferred storage in system memory, TT/GTT, or VRAM.

### Important APIs, types, and functions

The central type is `struct lsdc_bo`, embedding `struct ttm_buffer_object` plus GEM list linkage, `iosys_map`, vmap/sharing counters, kmap state, size, initial domain, and a fixed placement array. Inline helpers convert `drm_gem_object` and `ttm_buffer_object` pointers to `struct lsdc_bo`. Public declarations cover BO allocation, pinned kernel allocation, reservation, pinning, references, GPU offset/size, kernel mapping, clearing, VRAM eviction, TTM init, and debugfs setup.

### Control flow

The header has no runtime flow beyond type-safe conversions. Callers create an LSDC BO, reserve it, pin or map it as needed, and release it through GEM references. The declared TTM initialization entry point is called during LSDC device bring-up.

### State and persistence behavior

The header defines the object fields that persist across BO lifetime: placement policy, current kmap pointer and IO-memory flag, list membership under `gem.mutex`, and counters used by sharing and virtual mapping paths. Actual resource state is owned by TTM.

### Dependencies

It includes Linux list/container/iosys-map headers and DRM GEM/TTM BO, placement, range-manager, and TT headers. It relies on the surrounding LSDC driver for `struct lsdc_device` declarations.

### Integration points

The API is consumed by LSDC GEM, plane, framebuffer, and device initialization code. It is the common contract between object creation, scanout pinning, CPU access, PRIME sharing, and TTM debugfs.

### Risks

The placement array has four entries, so future domain expansion must keep that capacity in sync. `sharing_count` is documented but not managed here; callers must coordinate cross-device sharing rules. Conversion helpers assume embedded layout and will break if object embedding changes.

### Test signals

Build coverage is the main header-level signal. Runtime validation comes from all users of the declared API: GEM allocation, PRIME import, scanout pinning, CPU mapping, and TTM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Kconfig

### Purpose

`mcde/Kconfig` exposes the ST-Ericsson MCDE DRM/KMS driver as `CONFIG_DRM_MCDE`, selecting the helper subsystems needed for MCDE display, DSI, bridges, panel bridges, KMS helpers, and DMA-backed GEM buffers.

### Important APIs, types, and functions

The file defines one tristate symbol, `DRM_MCDE`, with prompt text for the Multichannel Display Engine. It depends on DRM, CMA, ARM or compile-test builds, OF, and common clock support. It selects MFD syscon, DRM client selection, MIPI DSI, bridge, panel bridge, KMS helper, and GEM DMA helper support.

### Control flow

There is no runtime control flow. Kconfig resolution controls whether `mcde_drm.o` is built and whether the required helper symbols are available.

### State and persistence behavior

The symbol persists in kernel configuration and determines module or built-in availability. No runtime state is defined here.

### Dependencies

The dependencies match the driver’s use of DT platform probing, regulators/clocks, syscon PRCMU reset, CMA/DMA GEM framebuffers, MIPI DSI host/bridge APIs, and DRM atomic helpers.

### Integration points

`CONFIG_DRM_MCDE` drives the `mcde/Makefile` object selection. If built as a module, the help text says the module name is `mcde_drm`.

### Risks

Missing selected helpers would break linking or probing. The `ARM || COMPILE_TEST` dependency reflects platform reality; enabling on non-ARM only through compile testing may not provide runnable hardware.

### Test signals

Useful signals are `allyesconfig`/`COMPILE_TEST` build coverage, ARM DT boot with `ste,mcde`, and module build/load tests when configured as `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Makefile

### Purpose

`mcde/Makefile` defines the object composition for the MCDE DRM module.

### Important APIs, types, and functions

The module aggregate `mcde_drm-y` contains `mcde_drv.o`, `mcde_dsi.o`, `mcde_clk_div.o`, and `mcde_display.o`. `obj-$(CONFIG_DRM_MCDE)` links the aggregate as `mcde_drm.o`.

### Control flow

There is no runtime flow. Kbuild includes this directory’s module only when `CONFIG_DRM_MCDE` is enabled.

### State and persistence behavior

The file contributes build graph state only. Runtime state lives in the C files.

### Dependencies

It depends on the Kconfig symbol and on each listed source file compiling against DRM, clock, DSI, and platform helpers.

### Integration points

The aggregate links the platform driver, DSI component, internal clock divider, and simple display pipe into one module, matching the module name advertised by Kconfig.

### Risks

Omitting one object would cause unresolved symbols such as `mcde_dsi_driver`, `mcde_display_init()`, or `mcde_init_clock_divider()`. Adding new MCDE components requires updating this aggregate.

### Test signals

Build tests with `CONFIG_DRM_MCDE=y` and `m` verify object aggregation and module linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_clk_div.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_clk_div.c

### Purpose

`mcde_clk_div.c` registers two internal MCDE clock-divider providers for FIFO A and FIFO B. These clocks let the display path request a DPI pixel clock through common-clock APIs while programming MCDE FIFO control registers.

### Important APIs, types, and functions

`struct mcde_clk_div` stores a `clk_hw`, MCDE pointer, register offset, and cached divider bits. `mcde_clk_div_ops` implements `.enable`, `.recalc_rate`, `.determine_rate`, and `.set_rate`. The exported entry point is `mcde_init_clock_divider()`, which registers `fifoa` and `fifob` clocks and stores them in `struct mcde`.

### Control flow

Rate determination scans possible dividers and optionally asks the parent to round its rate. `set_rate()` computes and caches CRX1 divider bits without touching hardware, which allows rate selection before the MCDE power domain is accessible. `enable()` locks `fifo_crx1_lock`, selects the LCD PLL parent, marks internal clocking, applies cached divider bits, and writes the FIFO A/B CR1 register. `recalc_rate()` returns a default divide-by-two when EPOD is off because registers cannot be read.

### State and persistence behavior

The divider caches desired register bits in `cr_div`. Hardware state is persisted in MCDE `CRA1`/`CRB1` clock-select, bypass, and divider fields while the EPOD power domain is enabled. The shared spinlock protects register read-modify-write with other display code.

### Dependencies

It depends on Linux common-clock provider APIs, regulator state checks, MMIO accessors, and MCDE register definitions from `mcde_display_regs.h`.

### Integration points

`mcde_display_init()` calls `mcde_init_clock_divider()`. DPI enable code uses `clk_round_rate()`, `clk_set_rate()`, and `clk_prepare_enable()` on `mcde->fifoa_clk`.

### Risks

Only the PLL72/LCD parent is implemented despite comments about other parents. Divider encoding is unusual: bypass for divide-by-one, zero field meaning divide-by-two. Reading registers while EPOD is disabled is avoided, so stale cached state must be trusted across power cycles.

### Test signals

Test with DPI panels: requested pixel clock close to mode clock, FIFO A clock enable/disable across modesets, suspend/resume after EPOD power loss, and lockdep coverage around concurrent CR1 updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_clk_div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display.c

### Purpose

`mcde_display.c` implements the MCDE simple display pipe. It programs one framebuffer pipeline from external source 0 through overlay 0, channel 0, FIFO A, and either DSI formatter 0 or DPI formatter 0; it handles IRQ/vblank reporting, FIFO flow control, format setup, timing setup, and framebuffer base updates.

### Important APIs, types, and functions

The file exposes `mcde_display_irq()`, `mcde_display_disable_irqs()`, and `mcde_display_init()`. Important helpers configure external sources, overlays, channels, FIFOs, DSI formatters, DPI timing, DSI packet sizing, FIFO enable/disable/drain, flow start, and framebuffer addresses. `mcde_display_funcs` supplies DRM simple-pipe `.check`, `.enable`, `.disable`, `.update`, and vblank hooks.

### Control flow

Atomic check validates 32-bit framebuffer address alignment, requires pitch to equal `hdisplay * cpp`, and forces a mode change if the framebuffer format changes. Enable powers EPOD, clears IRQs, computes DPI or DSI timing, drains FIFO A/channel 0, configures EXTSRC/overlay/channel/FIFO, enables either the FIFO DPI clock or the DSI bridge plus formatter, enables TE capture if the flow mode uses TE, starts vblank, starts FIFO flow unless in one-shot mode, and sets MCDE enable/autoclock bits. Update arms or fakes vblank events, writes EXTSRC base addresses, and starts flow when needed. Disable stops vblank, drains FIFO flow, disables DPI clock or DSI bridge, sends pending events, disables EPOD, and waits for power-down.

### State and persistence behavior

Runtime state is in `struct mcde`: `flow_mode`, `flow_active`, `stride`, bridge/DSI pointers, FIFO clocks, and locks. Hardware state persists in MCDE external source, overlay, channel, FIFO, formatter, timing, IRQ, and global control registers until power is cut through EPOD. `flow_lock` protects software accounting and FIFO flow toggles.

### Dependencies

It depends on DRM simple KMS helpers, DRM GEM DMA framebuffer helpers, MIPI DSI format helpers, bridge/panel connector metadata, regulators, clocks, and MCDE register definitions.

### Integration points

`mcde_drv.c` calls `mcde_display_init()` during modeset setup. `mcde_display_irq()` is invoked by the top-level MCDE IRQ handler and delegates DSI IRQ status to `mcde_dsi_irq()`. DSI enable/disable calls are intentionally made from this display path because MCDE formatter and DSI link sequencing are tightly coupled.

### Risks

The implementation supports only one pipeline and makes many hardcoded routing choices. Pitch changes other than tight scanout are rejected. TE/one-shot flow control is sequence-sensitive, and comments mark uncertainty around BTA TE, DSI command-mode triggering, bus format mapping, and several packet timing values. DPI muxing is hardcoded to a known board setup. Power-domain register access must stay inside EPOD-enabled windows.

### Test signals

Useful validation includes MCDE boot on DSI video panels, DSI command/TE panels, DPI panels with RGB888 bus format, page flips with real and fake vblank events, framebuffer format changes, FIFO drain timeout absence, TE IRQ handling, suspend/resume power cycling, and mode timings around porch/sync polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display_regs.h

### Purpose

`mcde_display_regs.h` is the MCDE display-engine register map used by `mcde_display.c` and the FIFO clock divider. It names interrupt, external-source, overlay, channel, FIFO, DPI/TV timing, and DSI formatter registers and fields.

### Important APIs, types, and functions

The header exports macros only. Major groups include PP/overlay/channel IRQ registers, `MCDE_EXTSRC*` source address/config/control fields, `MCDE_OVL*` overlay config/control/crop/composition fields, `MCDE_CHNL*` channel sync/config/status/mux fields, DPI/TV timing registers, FIFO `CTRLA/B` and `CRA/CRB` control fields, CRX1 clock divider and output-bpp fields, sync configuration, and DSI formatter frame/packet/command fields.

### Control flow

There is no runtime control flow. Consumers select the register for a chosen source, overlay, channel, FIFO, or formatter and compose field values before MMIO writes.

### State and persistence behavior

The macros describe persistent MCDE MMIO state. Values configure framebuffer fetch addresses, pixel format, watermark levels, routing, timing, FIFO flow, formatter packing, and interrupt masks/status until overwritten or lost by EPOD power cycling.

### Dependencies

The header requires Linux bit macros from including code and is semantically tied to MCDE hardware revision v3/U8500v2 as checked by `mcde_drv.c`.

### Integration points

It is included by `mcde_display.c` and `mcde_clk_div.c`. Correct definitions are essential for MCDE’s single-pipe setup and the common-clock FIFO divider.

### Risks

Many fields have similar per-instance offsets for A/B, 0..5, or 0..9 blocks. Wrong group offsets or field shifts can route data to the wrong channel or formatter. Some macros cover unimplemented hardware capabilities, so future users must verify against hardware rather than assuming they were exercised by current driver paths.

### Test signals

Signals include successful modeset, correct scanout colors/formats, stable FIFO flow, vblank/TE IRQ status, DPI timing on a scope or panel, DSI formatter packet correctness, and register readback traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drm.h

### Purpose

`mcde_drm.h` is the shared internal MCDE driver header. It defines top-level MCDE control/error registers, display flow modes, the driver-private `struct mcde`, and cross-file function declarations.

### Important APIs, types, and functions

The key type is `struct mcde`, embedding `struct drm_device` plus device, panel/bridge/connector/simple-pipe, DSI device, DPI flag, stride, flow mode/accounting, MMIO base, clocks, FIFO clock handles, locks, and regulators. `enum mcde_flow_mode` models one-shot command, TE command, BTA+TE command, video TE, video formatter, and DPI formatter flows. Declarations connect DSI, display, and clock-divider modules.

### Control flow

The header has only inline flow classification through `mcde_flow_is_video()`. Real control flow is split across `mcde_drv.c`, `mcde_display.c`, `mcde_dsi.c`, and `mcde_clk_div.c`.

### State and persistence behavior

`struct mcde` is the long-lived per-device state allocated by `devm_drm_dev_alloc()`. It persists DRM object ownership, output routing, flow mode, flow-active count, clock/regulator references, and MMIO base through device lifetime.

### Dependencies

It includes DRM simple KMS helper types and relies on MIPI DSI, bridge, panel, clock, regulator, and MMIO types from including C files.

### Integration points

Every MCDE source file includes this header. It establishes the private object conversion via `to_mcde()` and the function contract between the top-level platform driver, the DSI component, the display pipe, and FIFO clock registration.

### Risks

The shared state assumes a single active DSI device and simple display pipe. Flow mode is global, so supporting multiple concurrent outputs would require structural changes. `mcde_flow_is_video()` intentionally treats DPI as not DSI video except through its own flow mode.

### Test signals

Build and runtime integration tests should cover DSI and DPI probe paths, output selection, flow mode selection from attached DSI mode flags, and component teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drv.c

### Purpose

`mcde_drv.c` is the MCDE DRM platform driver. It allocates the DRM device, powers and clocks the MCDE block for probing, validates hardware revision, populates and binds DSI components, initializes DRM mode configuration, registers the device, and handles remove/shutdown.

### Important APIs, types, and functions

Important objects are `mcde_drm_driver`, `mcde_mode_config_funcs`, `mcde_mode_config_helpers`, component master ops, `mcde_driver`, and module init/exit functions. Main routines are `mcde_probe()`, `mcde_drm_bind()`, `mcde_modeset_init()`, `mcde_irq()`, `mcde_drm_unbind()`, `mcde_remove()`, and `mcde_shutdown()`.

### Control flow

Module init registers child component drivers first, then the MCDE platform driver. Probe allocates `struct mcde`, enables EPOD/VANA regulators and the main MCDE clock, maps MMIO, requests IRQ, reads and verifies PID `0x03000800`, disables/clears IRQs, populates DT child devices, builds a component match for DSI children, then deliberately powers EPOD off before registering the component master. Bind initializes mode config, binds components, finds a DSI or fallback DPI bridge, initializes vblank and the display pipe, attaches the bridge, registers the DRM device, and starts DRM clients. Remove/unbind unregister DRM, shut down atomic state, unbind components, and release clocks/regulators.

### State and persistence behavior

Device state persists in devm-managed `struct mcde`, regulators, clocks, MMIO mapping, IRQ, component relationships, and DRM mode objects. EPOD is toggled during probe to reset the display subsystem; display enable later re-powers it.

### Dependencies

It depends on Linux component framework, platform/OF population, regulators, clocks, IRQ/MMIO, DRM atomic/GEM DMA/fbdev/client helpers, bridge/panel helpers, and MCDE display/DSI internals.

### Integration points

The driver matches `ste,mcde`. It owns the top-level IRQ and delegates display IRQ handling to `mcde_display_irq()`. Component matching binds `mcde_dsi_driver` children. Mode setup falls back to a direct DPI panel or bridge if no DSI bridge is installed.

### Risks

Only one hardware revision is accepted. If no DSI components match, probe fails before DPI fallback can be used because component matching is mandatory. Probe has careful power-state transitions; failures after EPOD is disabled require special cleanup. Bridge selection is intentionally simple and assumes one output path.

### Test signals

Signals include module load/unload, DT probing with DSI child nodes, DPI fallback, PID rejection on unsupported hardware, IRQ request and clearing, DRM device registration, fbdev/client setup, shutdown blanking, and regulator/clock balance under probe failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi.c

### Purpose

`mcde_dsi.c` implements the MCDE MIPI DSI host and bridge component. It handles MIPI host attach/detach/transfer, DSI IRQ decoding, TE requests, DSI PHY/link startup, video-mode timing programming, bridge attachment, panel bridge discovery, PRCMU reset, and component binding to the main MCDE device.

### Important APIs, types, and functions

`struct mcde_dsi` stores device, MCDE pointer, bridge, panel, MIPI host/device, current mode, LP/HS clocks and rates, MMIO, and PRCMU regmap. Exported functions used by the display core are `mcde_dsi_irq()`, `mcde_dsi_te_request()`, `mcde_dsi_enable()`, and `mcde_dsi_disable()`. Host ops are attach, detach, and transfer. Bridge ops are attach and mode_set.

### Control flow

Probe maps DSI registers, finds the PRCMU syscon, logs hardware ID, registers a MIPI DSI host, and adds a component. Bind obtains LP/HS clocks, discovers a child panel or bridge, wraps panels with a DSI panel bridge, adds the MCDE DSI bridge, and installs it as `mcde->bridge`. Host attach validates one or two data lanes and selects MCDE flow mode: video formatter for video panels or command TE for command panels. Display enable sets LP/HS rates, enables clocks, toggles PRCMU reset, starts the DSI link, optionally programs video timing, and enables video or command mode. Transfers program direct-command settings and data registers, retry up to three times, and support writes up to 16 bytes and reads up to four bytes.

### State and persistence behavior

State persists in `struct mcde_dsi`, attached `mipi_dsi_device`, current display mode, selected clock rates, PRCMU reset state, and DSI controller registers. IRQ status is latched in DSI status registers and cleared explicitly. The bridge is owned by DRM bridge registration and points to the downstream panel bridge.

### Dependencies

It depends on DRM bridge/panel/MIPI DSI helpers, component framework, common-clock APIs, syscon/regmap PRCMU reset, OF child discovery, MIPI packet constants, and DSI register definitions.

### Integration points

The DSI component binds under the MCDE master and supplies the output bridge consumed by `mcde_modeset_init()`. `mcde_display.c` calls enable/disable from its pipe sequencing and routes DSI IRQ/TE handling through `mcde_dsi_irq()` and `mcde_dsi_te_request()`.

### Risks

The code supports only one active DSI link and hardcodes reset bit DSI0 despite a FIXME. Direct-command reads beyond four bytes and writes beyond 16 bytes are unsupported. Many DSI video timing formulas are copied from vendor behavior with documented uncertainty. Clock enable error handling logs but does not always abort. Non-panel bridges are detected but rejected.

### Test signals

Test DSI host attach, panel probe, command writes/reads, TE IRQs, video-mode panels, command-mode panels, LP/HS clock programming, reset sequencing, lane-ready/PLL-lock polling, display disable waits, and error IRQ logging for missing sync/data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi_regs.h

### Purpose

`mcde_dsi_regs.h` defines the MCDE DSI controller register map and bitfields used by the DSI host/bridge implementation.

### Important APIs, types, and functions

The header exports preprocessor constants for main data/PHY/enable/status registers, DPHY timeout/static/ULP timing, command-mode status/control, direct command send/read/write/status registers, TE and command-mode interrupt control/clear fields, video-mode main control, size/timing/blanking/VCA registers, DPHY lane trim, and ID/status registers.

### Control flow

There is no runtime flow. `mcde_dsi.c` composes these fields to start the link, issue direct MIPI commands, request TE, configure command/video modes, program video timing, enable errors, poll status, and clear latched IRQs.

### State and persistence behavior

The macros describe persistent DSI hardware state: link enable, lane count, continuous clocking, ULPM behavior, timeout values, direct-command payload/status, video packet layout, sync/blanking sizes, burst limits, and status interrupt masks. State remains until reset, power loss, or explicit rewrites.

### Dependencies

The header expects standard `BIT()` definitions and MIPI constants in consumers. Semantically it is tied to the ST-Ericsson MCDE DSI hardware.

### Integration points

It is included only by `mcde_dsi.c` and is the low-level contract between DSI host operations, video mode setup, TE handling, and MCDE display sequencing.

### Risks

Wrong masks or shifts can corrupt DSI command payloads or timing, producing panel hangs. Several fields are used in read-clear flows; incorrect clear bits can lose or retain interrupts. Video timing fields mix bytes, pixels, lanes, and clock cycles, so field naming alone is not enough to prevent misuse.

### Test signals

Signals include DSI register readback, command transfer success, TE status clear behavior, lane-ready polling, video-mode sync stability, burst/non-burst panels, and error interrupt injection or observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Kconfig

### Purpose

`mediatek/Kconfig` defines the MediaTek DRM/KMS driver family and optional DisplayPort and HDMI subdrivers.

### Important APIs, types, and functions

The file defines `DRM_MEDIATEK`, `DRM_MEDIATEK_DP`, `DRM_MEDIATEK_HDMI_COMMON`, `DRM_MEDIATEK_HDMI`, and `DRM_MEDIATEK_HDMI_V2`. The base driver depends on DRM, MediaTek architecture or compile-test, common clocks, ARM SMCCC or compile-test, OF, and MTK MMSYS; it selects DRM client, GEM DMA, KMS, display helpers, bridge connector, MIPI DSI, panel, and videomode helpers.

### Control flow

There is no runtime control flow. Kconfig choices drive which objects in `mediatek/Makefile` are compiled and which helper subsystems are guaranteed available.

### State and persistence behavior

Configuration symbols persist in the kernel config and determine module availability. No driver runtime state is stored here.

### Dependencies

The dependencies mirror driver use of DT-described MMSYS/DDP components, clocks, SMCCC, MIPI DSI, DRM bridge/panel/display helpers, HDMI codec/display helpers, and DP AUX/helper infrastructure.

### Integration points

`CONFIG_DRM_MEDIATEK` builds the core `mediatek-drm` aggregate; HDMI and DP symbols add their output-specific modules. HDMI v1 selects the common HDMI library and CEC/DDC pieces, while HDMI v2 selects a separate v2 implementation.

### Risks

Optional symbols must align with Makefile objects and exported namespaces. Compile-test coverage may not catch missing runtime dependencies such as DT graph or power domains.

### Test signals

Signals include build matrix coverage for base-only, HDMI v1, HDMI v2, DP, built-in and module configurations, plus boot/probe on supported MediaTek SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Makefile

### Purpose

`mediatek/Makefile` defines the MediaTek DRM object graph for the core display pipeline and optional HDMI/DP modules.

### Important APIs, types, and functions

The `mediatek-drm-y` aggregate includes CRTC, DDP component registry, display blocks such as AAL/CCORR/COLOR/GAMMA/MERGE/OVL/RDMA/ETHDR/PADDING, DRM core, DSI, DPI, MDP RDMA, and plane support. Optional objects are selected by `CONFIG_DRM_MEDIATEK_HDMI_COMMON`, `CONFIG_DRM_MEDIATEK_HDMI`, `CONFIG_DRM_MEDIATEK_HDMI_V2`, and `CONFIG_DRM_MEDIATEK_DP`.

### Control flow

There is no runtime flow. Kbuild links the selected objects into either the core `mediatek-drm` module or separate output modules.

### State and persistence behavior

The file only affects build state. Runtime state is owned by the individual drivers.

### Dependencies

It depends on Kconfig selecting helper subsystems and on cross-object symbols declared mainly in `mtk_disp_drv.h`, `mtk_crtc.h`, and `mtk_ddp_comp.h`.

### Integration points

The aggregate ensures display component implementations are linked with the DDP registry and CRTC code. HDMI v1 includes CEC, HDMI, and DDC; HDMI v2 includes v2 HDMI/DDC; DP builds `mtk_dp.o`.

### Risks

Missing an object from `mediatek-drm-y` can break DDP function tables. Moving a helper between optional and core modules requires symbol export and namespace review.

### Test signals

Build tests across MediaTek display configurations verify linkage. Runtime probe tests should confirm all DT-selected components have corresponding platform drivers or aggregate functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.c

### Purpose

`mtk_cec.c` implements the MediaTek HDMI v1 CEC/HPD support block used to detect hotplug state and notify the HDMI driver.

### Important APIs, types, and functions

`struct mtk_cec` stores MMIO, clock, IRQ, cached HPD state, callback, HDMI device pointer, and a spinlock. Exported namespace functions are `mtk_cec_set_hpd_event()` and `mtk_cec_hpd_high()`. Internal helpers set/clear/mask bits, initialize/enable/disable hotplug IRQs, clear IRQ status, deliver callbacks, and service the threaded IRQ.

### Control flow

Probe allocates state, maps MMIO, gets clock and IRQ, registers a shared low-triggered threaded IRQ, enables the CEC clock, initializes 32 kHz hotplug IRQ routing, and enables HDMI power/hotplug interrupts. The IRQ thread clears all hotplug-related status, samples `RX_EVENT`, compares with cached `cec->hpd`, and invokes the registered callback if state changed. Remove disables HPD IRQs and the clock.

### State and persistence behavior

Runtime state includes cached HPD level and callback fields protected by `cec->lock`. Hardware state includes CEC clock gate, hotplug IRQ enable bits, status/clear bits, and RX event bits. Callback registration persists until replaced by HDMI code.

### Dependencies

It depends on platform/OF probing, clocks, threaded IRQs, MMIO access, and the MediaTek HDMI v1 exported namespace contract.

### Integration points

The file registers `mediatek-cec` for `mediatek,mt8173-cec`. HDMI v1 code calls the exported functions to register HPD callbacks and query current HPD state. Symbols are exported under namespace `DRM_MTK_HDMI_V1`.

### Risks

The driver is HPD-oriented and does not implement a full CEC messaging stack. IRQ handling is shared and low-triggered, so clear sequencing is important to avoid interrupt storms. Callback pointers are protected while copied but the callback runs after lock release, so lifetime is owned by the HDMI driver.

### Test signals

Signals include HDMI cable plug/unplug events, `mtk_cec_hpd_high()` matching hardware state, callback invocation exactly on state changes, IRQ clear behavior under repeated toggles, clock enable/disable balance, and module unload safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.h

### Purpose

`mtk_cec.h` declares the small HPD-facing API exposed by the MediaTek HDMI v1 CEC block.

### Important APIs, types, and functions

It forward-declares `struct device` and declares `mtk_cec_set_hpd_event()` plus `mtk_cec_hpd_high()`. The callback signature passes a boolean HPD level and the HDMI device pointer supplied during registration.

### Control flow

There is no runtime flow in the header. HDMI code registers a callback, and the CEC driver calls it from the hotplug IRQ thread when HPD changes.

### State and persistence behavior

The header owns no state. Registered callback state is stored in `struct mtk_cec` in `mtk_cec.c`.

### Dependencies

It depends only on Linux types and a device forward declaration, keeping the HDMI/CEC boundary light.

### Integration points

The declarations are implemented by `mtk_cec.c` and consumed by HDMI v1 code built under `CONFIG_DRM_MEDIATEK_HDMI`.

### Risks

The API exposes HPD only, despite the CEC filename, so callers must not expect full CEC transmit/receive functionality. Callback lifetime must be managed by the caller.

### Test signals

Build coverage with HDMI v1 enabled and runtime callback registration during HDMI probe are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.c

### Purpose

`mtk_crtc.c` implements MediaTek DRM CRTC objects over DDP component pipelines. It creates planes from component capabilities, powers/clocks and connects DDP paths, coordinates mutex/MMSYS routing, applies modes and plane updates, supports CMDQ-assisted register programming, handles vblank/page-flip completion, and exposes color management through gamma/CTM components.

### Important APIs, types, and functions

Main state is `struct mtk_crtc` and `struct mtk_crtc_state`. Public functions include `mtk_crtc_create()`, `mtk_crtc_plane_check()`, `mtk_crtc_plane_disable()`, `mtk_crtc_async_update()`, `mtk_crtc_dma_dev_get()`, and `mtk_ddp_comp_for_plane()` inside the file. DRM hooks cover reset/duplicate/destroy state, mode validation/fixup/set, atomic begin/flush/enable/disable, vblank enable/disable, and CRTC destroy.

### Control flow

Creation validates that every path component exists, allocates the CRTC and DDP component array, gets a display mutex, registers vblank callbacks, counts component planes, creates DRM planes, initializes the CRTC, enables color management if gamma/CTM components are present, and optionally creates a CMDQ mailbox packet. Atomic enable powers the first component, updates connector-dependent route tail, initializes hardware by resuming runtime PM, preparing the mutex, enabling component clocks, connecting components through component hooks or MMSYS fallback, adding them to the mutex, enabling the mutex, configuring/starting all components, and programming initial disabled plane state. Flush marks dirty plane/config state, programs directly or builds CMDQ commands, and defers completion to vblank/CMDQ callbacks. Atomic disable disables all planes, waits for CMDQ/vblank, shuts off vblank, stops components, removes/disconnects routes, disables clocks/mutex/runtime PM, and powers off.

### State and persistence behavior

Software state includes pending config dimensions, pending plane flags, event pointer, enabled state, CMDQ packet/vblank timeout counters, locks, component path, connector routes, and DMA device. Hardware state persists in DDP component registers, MMSYS routes, display mutex membership, clocks, and power domains until disable or suspend.

### Dependencies

It depends on DRM atomic/vblank helpers, MediaTek MMSYS/mutex/CMDQ APIs, runtime PM, mailbox, DMA sync, and DDP component wrappers from `mtk_ddp_comp.h`.

### Integration points

`mtk_drm_drv.c` calls `mtk_crtc_create()` for SoC-defined paths. Plane code calls plane check/disable/async update. DDP component drivers provide callbacks for config, layer programming, vblank, color management, connection, and DMA device selection.

### Risks

The commit path has several concurrency points: `hw_lock`, `config_lock`, CMDQ callback, vblank IRQ, and pending event ownership. CMDQ timeout is based on three vblanks and can leave pending state if callbacks fail. Connector route switching mutates the final DDP component based on encoder masks. Disable removes components in two loops, so duplicate remove fallback behavior must remain harmless. Plane-to-component mapping assumes first two components provide layers.

### Test signals

Signals include atomic modeset/page-flip IGT, vblank events, async plane updates, CMDQ and CPU-register paths, suspend/resume, connector route changes, gamma/CTM application, multi-plane composition, runtime PM balance, and error-free CRTC disable while planes are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.h

### Purpose

`mtk_crtc.h` declares the MediaTek CRTC interface used by the DRM core driver and plane code.

### Important APIs, types, and functions

It defines color-management bounds `MTK_MAX_BPC` and `MTK_MIN_BPC`. It declares `mtk_crtc_commit()`, `mtk_crtc_create()`, `mtk_crtc_plane_check()`, `mtk_crtc_plane_disable()`, `mtk_crtc_async_update()`, and `mtk_crtc_dma_dev_get()`.

### Control flow

There is no runtime flow in the header. Callers create CRTCs from SoC DDP paths, validate/configure planes through CRTC helpers, and query the DMA device for buffer mapping.

### State and persistence behavior

The header owns no state. State is held in private `struct mtk_crtc` instances in `mtk_crtc.c`.

### Dependencies

It includes DRM CRTC types and MediaTek DDP, DRM-private, and plane headers so signatures can reference route and plane-state types.

### Integration points

The declarations connect `mtk_drm_drv.c`, `mtk_plane.c`, DDP component code, and DMA mapping paths.

### Risks

`mtk_crtc_commit()` is declared here but not in the researched `mtk_crtc.c` content, so users must rely on the full tree for its definition or dead declaration status. Header coupling to several MediaTek internals means changes in route or plane-state types propagate widely.

### Test signals

Build coverage across the MediaTek DRM driver and plane update tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.c

### Purpose

`mtk_ddp_comp.c` is the MediaTek DDP component registry and generic component helper implementation. It maps SoC component IDs to component types and function tables, provides CMDQ-aware register write helpers, implements simple block handlers for dither/DSC/OD/postmask/UFOE, resolves possible CRTCs, and initializes generic component state.

### Important APIs, types, and functions

Public functions include `mtk_ddp_write()`, `mtk_ddp_write_relaxed()`, `mtk_ddp_write_mask()`, `mtk_dither_set_common()`, `mtk_ddp_comp_get_id()`, `mtk_find_possible_crtcs()`, and `mtk_ddp_comp_init()`. Key tables are `ddp_aal`, `ddp_ccorr`, `ddp_color`, `ddp_dither`, `ddp_dpi`, `ddp_dsc`, `ddp_dsi`, `ddp_gamma`, `ddp_merge`, `ddp_od`, `ddp_ovl`, `ddp_postmask`, `ddp_rdma`, `ddp_ufoe`, `ddp_ovl_adaptor`, `mtk_ddp_comp_stem`, and `mtk_ddp_matches`.

### Control flow

Register writes go through CMDQ packet commands when a packet is provided, otherwise direct MMIO. Component initialization validates the component ID, installs ID/function table data, resolves the platform device from DT, defers if missing, and for generic components maps MMIO, obtains a clock, gets CMDQ client registers, and stores private data. Components with dedicated drivers skip generic MMIO setup. `mtk_find_possible_crtcs()` scans all MMSYS private paths and connector routes to return the CRTC bitmask containing a device.

### State and persistence behavior

Persistent state includes `struct mtk_ddp_comp` fields (`dev`, `id`, `encoder_index`, callbacks) and generic `struct mtk_ddp_comp_dev` MMIO/clock/CMDQ metadata. Hardware state for generic helpers includes dither, DSC bypass/enable, OD relay/dither, postmask relay, and UFO bypass registers.

### Dependencies

It depends on OF/platform helpers, clocks, CMDQ, DRM logging, MediaTek MMSYS route data, mutex APIs through function tables, and display block functions declared in `mtk_disp_drv.h`.

### Integration points

`mtk_crtc.c` uses the function tables through inline wrappers in `mtk_ddp_comp.h`. SoC driver data supplies path arrays and connector routes indexed by `DDP_COMPONENT_*` IDs. Dedicated component platform drivers provide their own `dev_get_drvdata()` payloads.

### Risks

Component ID, OF alias, and function-table mappings are central contracts; mistakes route planes or encoders incorrectly. Some component types have NULL function tables and rely on fallback behavior. Generic and dedicated components have different private-data shapes, so a function table must match the owning driver. CMDQ and direct-write paths must remain equivalent.

### Test signals

Signals include DT probe ordering with `-EPROBE_DEFER`, path availability detection, CRTC possible-mask correctness, CMDQ/direct register write parity, dither/DSC/postmask behavior, and modeset coverage for every component ID used by supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.h

### Purpose

`mtk_ddp_comp.h` defines the common MediaTek DDP component abstraction used by CRTCs, planes, and display block drivers.

### Important APIs, types, and functions

It defines `enum mtk_ddp_comp_type`, `struct mtk_ddp_comp_funcs`, and `struct mtk_ddp_comp`. The function table covers power, clock, config/start/stop, vblank callbacks, plane/layer capabilities and programming, gamma/CTM, background color, DMA device selection, formats/blend/AFBC, MMSYS connect/disconnect, mutex add/remove, encoder index, and mode validation. Inline wrappers provide default PM/runtime behavior and no-op fallbacks.

### Control flow

Callers operate through wrappers such as `mtk_ddp_comp_power_on()`, `mtk_ddp_comp_config()`, `mtk_ddp_comp_layer_config()`, `mtk_ddp_gamma_set()`, `mtk_ddp_comp_connect()`, and `mtk_ddp_comp_encoder_index_set()`. If a callback is missing, the wrapper usually returns a safe default or falls back to runtime PM.

### State and persistence behavior

`struct mtk_ddp_comp` persists the device pointer, IRQ, component ID, encoder index, and callback table pointer for each component in a DRM private path. The header itself stores no runtime data.

### Dependencies

It depends on Linux IO, runtime PM, CMDQ, MMSYS, mutex, and DRM mode types. It forward-declares DRM and MediaTek plane/CRTC state types to keep component callbacks typed.

### Integration points

This is the main contract between `mtk_crtc.c`, `mtk_ddp_comp.c`, and individual display-block drivers such as OVL, RDMA, AAL, CCORR, COLOR, DSI, DPI, MERGE, and OVL adaptor.

### Risks

Silent no-op defaults are useful for optional blocks but can hide missing callbacks. `mtk_ddp_comp_power_on()` contains an unreachable `return 0` after the fallback return. Function tables must match each component driver’s private data type. Missing layer count or format callbacks can prevent plane creation.

### Test signals

Build coverage, CRTC creation, plane count/format discovery, runtime PM balance, vblank callback delivery, color-management updates, connector route switching, and SoC-specific component path tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_aal.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_aal.c

### Purpose

`mtk_disp_aal.c` implements the MediaTek DISP_AAL display block, including clock control, size programming, optional gamma LUT programming, start/stop, and component registration.

### Important APIs, types, and functions

`struct mtk_disp_aal` stores clock, MMIO, CMDQ register metadata, and match data. Public component functions are `mtk_aal_clk_enable()`, `mtk_aal_clk_disable()`, `mtk_aal_config()`, `mtk_aal_gamma_get_lut_size()`, `mtk_aal_gamma_set()`, `mtk_aal_start()`, and `mtk_aal_stop()`. Match data currently marks MT8173 as having gamma support.

### Control flow

Probe allocates state, obtains clock and MMIO, optionally obtains CMDQ client register metadata, stores platform data, and adds a component. Config writes input and output size through CMDQ or MMIO. Gamma setup exits if unsupported or no LUT is present, converts DRM LUT entries to 10-bit RGB fields, writes 512 LUT registers directly, then enables gamma LUT and disables relay mode. Start writes `AAL_EN`; stop clears it.

### State and persistence behavior

Software state is the device-private clock/MMIO/CMDQ/data pointer. Hardware state includes size registers, output size, gamma LUT table, config relay/gamma bits, and enable bit.

### Dependencies

It depends on component framework, clocks, OF match data, platform MMIO, CMDQ helpers, DRM color LUT helpers, and DDP write helpers.

### Integration points

`mtk_ddp_comp.c` references these functions in the `ddp_aal` function table. `mtk_crtc.c` invokes config/start/stop and gamma operations through DDP wrappers.

### Risks

Gamma LUT writes bypass CMDQ and direct-write 512 registers, so synchronization with atomic updates relies on call context. Only SoCs with `has_gamma` expose LUT size. Incorrect LUT bit extraction or relay/gamma bits affects color output.

### Test signals

Signals include component probe, clock enable/disable, size programming, gamma LUT property tests on MT8173, relay mode disabled after gamma set, and modesets with AAL in the DDP path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_aal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ccorr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ccorr.c

### Purpose

`mtk_disp_ccorr.c` implements the MediaTek DISP_CCORR color-correction block, providing clock control, size/config programming, start/stop, DRM CTM programming, and component registration.

### Important APIs, types, and functions

`struct mtk_disp_ccorr` stores clock, MMIO, CMDQ register metadata, and match data containing matrix precision bits. Public functions are `mtk_ccorr_clk_enable()`, `mtk_ccorr_clk_disable()`, `mtk_ccorr_config()`, `mtk_ccorr_start()`, `mtk_ccorr_stop()`, and `mtk_ccorr_ctm_set()`.

### Control flow

Probe allocates state, gets clock/MMIO, optionally obtains CMDQ metadata, loads SoC match data, and registers as a component. Config writes size and enables the CCORR engine through DDP write helpers. CTM setup exits without a blob, converts the 3x3 DRM S31.32 matrix into signed fixed-point coefficients using SoC-specific precision, and writes five packed coefficient registers. Start/stop toggle the enable register.

### State and persistence behavior

Hardware state includes size, config engine enable, coefficient registers, and enable bit. Software state persists matrix precision and command-queue metadata.

### Dependencies

It depends on DRM color management helpers, component/OF/platform support, clocks, CMDQ, and MediaTek DDP write helpers.

### Integration points

The DDP registry’s `ddp_ccorr` table exposes config/start/stop/CTM callbacks to `mtk_crtc.c`, which calls CTM updates during atomic flush when color management changes.

### Risks

Coefficient precision differs by SoC, so wrong match data changes color transforms. CTM writes use a NULL CMDQ packet and therefore direct MMIO in this implementation. Missing CTM blobs leave previous hardware coefficients untouched.

### Test signals

Signals include CTM DRM property tests, coefficient readback, color transform visual validation, component clock balance, and modesets on MT8183/MT8192 CCORR paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ccorr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_color.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_color.c

### Purpose

`mtk_disp_color.c` implements the MediaTek DISP_COLOR block used in DDP pipelines for basic color engine startup and frame-size programming.

### Important APIs, types, and functions

`struct mtk_disp_color` stores CRTC pointer, clock, MMIO, CMDQ metadata, and platform data. Public functions are `mtk_color_clk_enable()`, `mtk_color_clk_disable()`, `mtk_color_config()`, and `mtk_color_start()`. Match data supplies SoC-specific start/width/height register offsets for MT2701, MT8167, and MT8173.

### Control flow

Probe allocates state, obtains clock and MMIO, optionally obtains CMDQ metadata, stores match data, and adds a component. Config writes width and height registers through DDP write helpers. Start enables bypass-all and sequence selection in `DISP_COLOR_CFG_MAIN`, then writes one to the SoC-specific start register.

### State and persistence behavior

Software state persists the SoC register offset table. Hardware state includes width/height, bypass/sequence config, and start bit until the component is reset or powered down.

### Dependencies

It depends on component framework, clocks, OF match data, platform MMIO, CMDQ helpers, and DDP write helpers.

### Integration points

`mtk_ddp_comp.c` exposes these functions through the `ddp_color` function table. `mtk_crtc.c` configures and starts COLOR when it appears in a SoC DDP path.

### Risks

Register offsets vary by SoC; incorrect match data writes the wrong block. The driver starts COLOR in bypass mode, so advanced color processing is not configured here. There is no stop callback in the DDP table for COLOR.

### Test signals

Signals include component probe for each compatible, correct width/height readback, display scanout through paths containing COLOR, clock balance, and no visual corruption when bypass mode is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_drv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_drv.h

### Purpose

`mtk_disp_drv.h` declares cross-component MediaTek display-block functions used to populate DDP component function tables.

### Important APIs, types, and functions

The header declares clock/config/start/stop and feature callbacks for AAL, CCORR, COLOR, DITHER, DPI, DSI, GAMMA, MERGE, OVL, OVL adaptor, RDMA, MDP RDMA, and PADDING. It also declares plane-layer operations, vblank callback registration, format/blend/AFBC queries, color management operations, mutex connection helpers, mode validation, and CMDQ-aware start/stop/config variants for some blocks.

### Control flow

There is no runtime flow in the header. `mtk_ddp_comp.c` binds these declarations into per-component callback tables, and `mtk_crtc.c` invokes them indirectly through DDP wrappers.

### State and persistence behavior

The header owns no state. State is stored in each display block driver and in DDP component structures.

### Dependencies

It includes CMDQ, MMSYS, mutex, MDP RDMA, and plane headers because declarations reference those types. It also relies on DRM mode/color types being visible through included headers and consumers.

### Integration points

This is the broad internal ABI for the MediaTek display pipeline. It connects the DDP registry to implementation files for display processing blocks, encoders, and plane-capable components.

### Risks

The header is wide and tightly couples many display blocks. Signature changes require coordinated edits across the registry and drivers. Optional features are represented by missing function-table callbacks, so declarations alone do not imply a component supports the operation.

### Test signals

Build coverage of the full `mediatek-drm` aggregate, plus runtime modeset, vblank, plane, color-management, route, and output tests, validate this internal contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_drv.h -->
