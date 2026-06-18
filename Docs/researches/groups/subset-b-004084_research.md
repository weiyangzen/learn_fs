# subset-b-004084 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.c

Purpose: V4L2 I2C subdevice driver for Allied Vision Alvium CSI-2 cameras. It discovers camera capabilities from the Basic Control Register Map, exposes a single source pad, negotiates media bus formats and crop/selection state, programs CSI-2 lane/clock/frame/format registers, and starts or stops acquisition.

Important APIs/types/functions: `alvium_read()` and `alvium_write()` wrap CCI regmap access and translate BCRM-relative registers through `alvium->bcrm_addr`; `alvium_write_hshake()` writes BCRM controls and polls `REG_BCRM_WRITE_HANDSHAKE_RW`; `alvium_get_hw_info()` reads firmware, BCRM address, CSI limits, feature bits, image/control ranges, available MIPI data formats, and Bayer patterns. `alvium_setup_mipi_fmt()` builds the runtime media-bus format table from camera capability bits. V4L2 entry points are `alvium_enum_mbus_code()`, `alvium_enum_frame_size()`, `alvium_set_fmt()`, `alvium_set_selection()`, `alvium_s_frame_interval()`, and `alvium_s_stream()`. `alvium_ctrl_init()` creates controls conditionally from BCRM feature inquiry bits.

Control flow: `alvium_probe()` allocates state, creates a 16-bit CCI regmap, parses the firmware graph endpoint and link frequency, enables the optional `vcc-ext-in` regulator, waits for the long camera boot, verifies heartbeat, reads all hardware descriptors, initializes CSI lanes/clock/LP2HS, creates available-format storage, enables runtime PM, initializes the media entity/control handler/subdev state, and asynchronously registers the subdevice. Streaming resumes runtime PM, applies controls, writes width/height/offset, writes the MIPI data type and Bayer pattern, then writes acquisition start. Stop writes acquisition stop and drops runtime PM.

State/persistence: Persistent driver state is in `struct alvium_dev`: discovered ranges, available feature and format masks, endpoint data, current link frequency, dynamic format table, V4L2 controls, subdev active state, and `streaming`. Hardware state is persisted in BCRM registers and is restored during runtime resume through `alvium_hw_init()`.

Dependencies/integration: Depends on Linux I2C, CCI regmap, runtime PM, regulators, firmware graph parsing, MIPI CSI-2 media bus codes, V4L2 controls/subdev async registration, and media entity pads. Device-tree compatible is `alliedvision,alvium-csi2`; the endpoint must provide CSI-2 lane data and at least one link frequency.

Risks: `alvium_get_sharpness_params()` reads the maximum from `REG_BCRM_BLACK_LEVEL_MAX_R` instead of `REG_BCRM_SHARPNESS_MAX_R`, which can expose a wrong sharpness range. `alvium_set_ctrl_auto_exposure()` writes `REG_BCRM_WHITE_BALANCE_AUTO_RW`, likely a register mix-up for exposure auto. Capability parsing casts `u64` storage to bitfield structs, so layout is compiler and endian sensitive. `alvium_setup_mipi_fmt()` can allocate a zero-length format array if the camera reports no compatible formats; later enumeration assumes a valid first entry. Several error exits in `alvium_s_stream()` call `pm_runtime_put()` even after a failure that may have occurred before full stream setup, so PM balance and partial hardware writes are important review targets. Boot latency is hard-coded to 7 seconds.

Test signals: Probe should show BCRM and firmware versions, successful async subdev registration, valid `media-ctl -p` topology, `v4l2-ctl --list-subdev-mbus-codes` matching camera capability bits, correct frame size bounds, control ranges from BCRM, and start/stop with CSI-2 receiver lock. Failure tests should cover missing endpoint link frequencies, unsupported lane counts, out-of-range CSI clock clamping, runtime suspend/resume, and invalid format/crop requests while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.h

Purpose: Private interface and register definition header for the Alvium CSI-2 driver. It defines the BCRM and GenCP register addresses, feature bit layouts, supported MIPI/Bayer format enums, per-mode structures, control bookkeeping, and the main `struct alvium_dev` state used by `alvium-csi2.c`.

Important APIs/types/functions: `REG_BCRM_V4L2_*()` macros tag BCRM-relative CCI register definitions so the source file can add the runtime-discovered BCRM base address. Register constants cover BCRM versioning, firmware, handshake, CSI-2 lane/clock setup, acquisition start/stop/frame rate, image geometry, MIPI data type, Bayer pattern, flip controls, exposure/gain/white-balance/color controls, temperature, heartbeat, and GenCP mode switching. Key types are `enum alvium_bcrm_mode`, `enum alvium_mipi_fmt`, `enum alvium_av_bayer_bit`, `enum alvium_av_mipi_bit`, `struct alvium_avail_feat`, `struct alvium_avail_mipi_fmt`, `struct alvium_avail_bayer`, `struct alvium_mode`, `struct alvium_pixfmt`, `struct alvium_ctrls`, and `struct alvium_dev`.

Control flow: The header has no executable control flow, but it encodes how the source driver is organized: read feature inquiry into bitfield structures, map available MIPI/Bayer bits to `struct alvium_pixfmt`, store discovered min/max/inc defaults in `struct alvium_dev`, then expose those through V4L2 controls and pad operations.

State/persistence: `struct alvium_dev` is the persistent in-kernel cache of camera hardware state: BCRM address, endpoint configuration, regulator, regmap, capability flags, geometry/control ranges, active/default mode, link frequency, V4L2 control pointers, current BCRM mode, allocated format table, streaming flag, and frame-interval apply flag.

Dependencies/integration: Includes Linux kernel, regulator, V4L2 CCI, V4L2 common/control/fwnode/subdev headers. It is not a public UAPI header; it is tightly coupled to the source file and the Alvium BCRM firmware contract.

Risks: The `struct alvium_avail_*` bitfields are used over raw register values; bit order assumptions are fragile across endianness/compiler layout. Some register names mix units and access semantics, so source-side mistakes can silently target the wrong BCRM register. Range fields use a mix of `u32`, `u64`, and `s32`, requiring careful casts from CCI reads.

Test signals: Build coverage should catch missing types and macro changes. Runtime tests should verify that each BCRM register macro resolves correctly after `bcrm_addr` relocation and that feature bit decoding matches actual camera-reported capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/alvium-csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.c

Purpose: Shared helper that calculates valid Aptina sensor PLL divisors for a requested external clock and pixel clock. It exports `aptina_pll_calculate()` for sensor drivers that need `N`, `M`, and `P1` values within device-specific limits.

Important APIs/types/functions: `aptina_pll_calculate(struct device *dev, const struct aptina_pll_limits *limits, struct aptina_pll *pll)` validates input clocks, derives the reduced multiplier/divisor ratio using `gcd()`, computes a valid multiplier factor range, then searches even `P1` divisors from high to low. The selected result is written back to `pll->n`, `pll->m`, and `pll->p1`; the symbol is exported with `EXPORT_SYMBOL_GPL`.

Control flow: The function first rejects external clocks outside `[ext_clock_min, ext_clock_max]` and zero or too-high pixel clocks. It reduces `pix_clock / ext_clock` to base `m` and combined `n * p1` divisor. It derives `mf_min` and `mf_max` from multiplier, output clock, and combined divisor limits. For each even `p1`, it computes the compatible multiplier-factor increment, intersects that with internal clock limits, and accepts the first non-empty range.

State/persistence: Stateless helper. It mutates only the caller-provided `struct aptina_pll`; no hardware, global state, or persistent memory is touched.

Dependencies/integration: Uses `linux/gcd.h`, `DIV_ROUND_UP`, `roundup`, `dev_dbg()`, and `dev_err()`. It integrates through `aptina-pll.h` and is loaded as a GPL module helper for media sensor drivers.

Risks: Several arithmetic expressions multiply clock frequencies and divisors in `unsigned int`, so high limit values can overflow before division. `p1_min == 0` is explicitly rejected, but other zero limits can still create divide-by-zero hazards if callers provide malformed limits. The search prefers the highest even `P1` and lower acceptable multiplier factor, which may not optimize jitter or power for every sensor.

Test signals: Unit-style tests should feed known Aptina clock tables and verify exact `N/M/P1` results, boundary rejection for invalid ext/pixel clocks, no valid-divisor cases, and low/high internal/output clock limits. Dynamic debug logs should show the selected factors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.h

Purpose: Public helper header for Aptina sensor PLL calculation used by media I2C sensor drivers.

Important APIs/types/functions: `struct aptina_pll` contains input fields `ext_clock` and `pix_clock` plus calculated output fields `n`, `m`, and `p1`. `struct aptina_pll_limits` describes allowed external, internal, output, and pixel clocks plus min/max ranges for `N`, `M`, and `P1`. `aptina_pll_calculate()` is declared as the only exported API.

Control flow: No executable control flow. The header defines the caller contract: populate clocks and limits, call the calculator, and consume the written divider/multiplier fields on success.

State/persistence: No state of its own. The state boundary is the caller-owned `struct aptina_pll`, which acts as both input and output.

Dependencies/integration: Forward declares `struct device` for logging and avoids pulling in full device headers. Used with the GPL-exported implementation in `aptina-pll.c`.

Risks: Field units are implicit Hertz-style integer frequencies; callers must use consistent units. There is no type-level separation between input and output fields, so callers can accidentally reuse a partially mutated `struct aptina_pll` after an error.

Test signals: Compile users against this header and verify ABI expectations by checking that successful calls update all three output fields and failures do not get programmed into hardware by the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ar0521.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ar0521.c

Purpose: V4L2 subdevice driver for the ON Semiconductor AR0521 MIPI CSI-2 image sensor. It manages power rails, reset, extclk, MIPI lane setup, sensor initialization register tables, format sizing, PLL programming, controls, runtime PM, and stream start/stop.

Important APIs/types/functions: `struct ar0521_dev` stores subdev, pad, clock, regulators, reset GPIO, mutex, active format, controls, lane count, and calculated PLL fields. I2C helpers are `ar0521_write_regs()` and `ar0521_write_reg()` using big-endian 16-bit register/data sequences. Geometry and clock helpers include `ar0521_set_geometry()`, `ar0521_set_gains()`, `calc_pll()`, `ar0521_calc_pll()`, and `ar0521_pll_config()`. V4L2 operations include `ar0521_get_fmt()`, `ar0521_set_fmt()`, `ar0521_s_ctrl()`, `ar0521_pre_streamon()`, `ar0521_s_stream()`, and pad enum operations.

Control flow: Probe parses the CSI-2 endpoint, validates one, two, or four lanes, gets `extclk`, validates its rate, acquires reset GPIO and three regulators, initializes subdev/media entity, creates controls, clamps the default format, registers the subdev, powers on the device, and enables runtime PM. Power-on enables rails in order, enables extclk, releases reset, writes the large `initial_regs[]` table, configures serial format, LP-11 test mode, and row speed. Streaming resumes PM, briefly stops streaming, writes geometry, calculates/programs PLL, applies controls, exits LP-11, and sets the stream bit. Stop resets gain, clears the stream bit, and drops runtime PM.

State/persistence: The driver caches the active `v4l2_mbus_framefmt`, control values, lane count, and PLL dividers under `sensor->lock`. Sensor configuration persists in hardware registers only while powered. Runtime PM replays initialization via `ar0521_power_on()`.

Dependencies/integration: Depends on Linux clock, regulator, GPIO descriptor, runtime PM, firmware graph endpoint parsing, V4L2 controls/subdev/media entity APIs, and a MIPI CSI-2 receiver that honors `pre_streamon` manual LP-11 handling. Compatible string is `onnn,ar0521`.

Risks: Only `MEDIA_BUS_FMT_SGRBG8_1X8` is supported, so higher bit-depth modes and other Bayer orders are unavailable. `ar0521_set_stream()` returns directly on early errors after `pm_runtime_resume_and_get()` before the common `err` path, which can leak a runtime PM usage count for failures in the initial reset or geometry write. Probe cleanup calls `media_entity_cleanup()` both in `disable` and again through fall-through labels, making cleanup ordering worth review. `calc_pll()` is custom and has a TODO for lane-count-dependent VCO reduction. Initial register tables are large opaque magic values, so regressions are hard to localize.

Test signals: Probe should validate regulators, extclk range, endpoint lane count, media entity creation, and async registration. Functional tests should enumerate only SGRBG8, verify min/max frame sizes, exercise hblank/vblank/exposure/gain/color/test-pattern controls with runtime PM both active and idle, check LP-11 pre-stream behavior, and stream on/off across 1/2/4 lane device-tree configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ar0521.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/bt819.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/bt819.c

Purpose: Legacy V4L2 I2C subdevice driver for Brooktree/Rockwell BT819A, BT817A, and BT815A analog video decoders. It configures analog input routing, PAL/NTSC timing, output enable, status detection, and basic image controls.

Important APIs/types/functions: `struct bt819` contains the subdev, control handler, a 32-byte register shadow, current norm, selected input, and output enable flag. Register helpers are `bt819_write()`, `bt819_setbit()`, `bt819_write_block()`, and `bt819_read()`. Core behavior is in `bt819_init()`, `bt819_status()`, `bt819_s_std()`, `bt819_s_routing()`, `bt819_s_stream()`, and `bt819_s_ctrl()`. Control IDs cover brightness, contrast, saturation, and hue.

Control flow: Probe requires SMBus byte-data support, allocates state, initializes the V4L2 I2C subdev, reads chip version register `0x17`, rejects unknown variants, sets NTSC/input 0/enabled defaults, writes the initial register block, creates controls, and applies default controls. Standard changes reset a parent FIFO through `v4l2_subdev_notify()`, update decoder input-format bits, AGC/burst registers, and timing registers from `timing_data[]`, then releases FIFO reset. Routing selects input 0 versus other inputs by toggling mux bits. Stream toggles output disable bit 7 in register `0x16`.

State/persistence: Register writes update the software shadow and the hardware. Norm/input/enable are cached in memory. There is no runtime PM, media pad, or firmware-node state; the parent bridge owns board-level integration.

Dependencies/integration: Uses I2C SMBus byte data and optional raw I2C block writes, V4L2 subdev video ops, V4L2 controls, and `media/i2c/bt819.h` notification constants for FIFO reset coordination with capture bridge drivers.

Risks: No locking protects the register shadow against concurrent control/routing/standard calls. `bt819_write_block()` returns the raw byte count from `i2c_master_send()` rather than normalizing success to zero, although callers only treat negative values as errors. Parent `notify` is only warned about when missing, but calls still proceed. The driver predates modern media-controller endpoint modeling and has no runtime PM.

Test signals: Probe should detect the correct variant from register `0x17`. PAL and NTSC changes should update timing registers and notify FIFO reset low/high. Routing should reject inputs above 7 and visibly switch decoder muxing. Controls should produce expected register values, and status/querystd should report signal loss and PAL/NTSC detection from status register bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/bt819.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/bt856.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/bt856.c

Purpose: Legacy V4L2 I2C subdevice driver for the Brooktree BT856A digital video encoder. It programs a small register set for PAL/NTSC output and selects encoder input source or color bars.

Important APIs/types/functions: `struct bt856` stores the subdev, a six-byte shadow for registers `0xda` through `0xdf`, and current video standard. `bt856_write()` and `bt856_setbit()` maintain the shadow and write SMBus byte data. `bt856_init()` and `bt856_probe()` apply the same default setup. Video ops are `bt856_s_std_output()` and `bt856_s_routing()`.

Control flow: Probe checks SMBus byte-data capability, allocates state, initializes the I2C subdev, defaults to NTSC, and writes the encoder setup bits. `.init` can reapply the same setup. Standard output switches bit 2 of register `0xdc` for NTSC versus PAL. Routing accepts input 0 from BT819, input 1 from ZR36060, and input 2 color bars; it toggles bits in `0xde` and `0xdc` to select video bus or test output.

State/persistence: Hardware register values are mirrored in `encoder->reg[]`; the selected norm is cached. No runtime PM or media graph state exists.

Dependencies/integration: Uses Linux I2C SMBus byte-data APIs and V4L2 subdev core/video ops. It is intended for older bridge drivers that instantiate the I2C device and call routing/standard operations.

Risks: The register shadow indexes by subtracting `BT856_REG_OFFSET`; callers must never pass out-of-range register addresses. There is no locking around shadow updates. The driver has no explicit remove-time hardware shutdown. `bt856_dump()` prints only every other shadow byte because its loop increments by two, limiting debug value.

Test signals: Probe should write defaults and log the chip address. Standard switching should modify `0xdc` bit 2. Routing should accept only 0, 1, or 2 and produce color bars for input 2. SMBus capability absence should fail probe with `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/bt856.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/bt866.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/bt866.c

Purpose: Legacy V4L2 I2C subdevice driver for the Brooktree BT866 video encoder. It writes encoder setup and overlay color registers, handles input routing, and exposes standard-output selection.

Important APIs/types/functions: `struct bt866` stores the subdev and a 256-byte register shadow. `bt866_write()` writes a two-byte subaddress/data transfer with up to three retries and updates the shadow. V4L2 video ops are `bt866_s_std_output()` and `bt866_s_routing()`.

Control flow: Probe allocates the encoder and initializes it as a V4L2 I2C subdevice. Routing writes a fixed initialization table, including scaling/mode registers and overlay color palettes, then adjusts `CBSWAP` in register `0xdc` for input 0 versus others and `OSDBAR` in register `0xcc` for color bars. It accepts inputs 0, 1, and 2 after writing the setup and rejects others. Standard output currently accepts only standards containing `V4L2_STD_NTSC`, despite a stale comment saying only PAL is supported.

State/persistence: Register values are cached in `encoder->reg[]` and mirrored to hardware on writes. No controls, runtime PM, or media entity state are maintained.

Dependencies/integration: Uses raw `i2c_master_send()` rather than SMBus helpers, V4L2 subdev video ops, and bridge-driver instantiation. Retry waits use `schedule_timeout_interruptible()`.

Risks: `bt866_write()` updates the shadow before confirming I2C success, so software state can diverge from hardware after repeated failures. The retry sleep occurs without explicitly setting task state outside `schedule_timeout_interruptible()`, relying on helper behavior. `bt866_s_routing()` writes the entire initialization table before validating `input`, causing invalid routing requests to still perturb hardware. Standard support/comment mismatch can mislead board integration.

Test signals: Routing inputs 0, 1, and 2 should write the initialization table and toggle `CBSWAP`/`OSDBAR` as expected; invalid input should be checked for unintended writes. I2C fault injection should exercise all three retry attempts and confirm error propagation. Standard selection tests should confirm only NTSC-containing IDs are accepted by current code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/bt866.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.c

Purpose: Generic PLL calculator for MIPI CCS, SMIA, and SMIA++ camera sensors. It computes video-timing and operational PLL front/back branch dividers, pixel rates, and CSI bus rates from sensor limits and requested bus/link parameters.

Important APIs/types/functions: Exported API is `ccs_pll_calculate()`. Helper groups include divider normalization (`clk_div_even()`, `clk_div_even_up()`, `is_one_or_even()`), validation (`bounds_check()`, `check_fr_bounds()`, `check_bk_bounds()`, `check_ext_bounds()`), debug printing (`print_pll()`, `print_pll_flags()`), VT divisor search (`ccs_pll_find_vt_sys_div()`, `__ccs_pll_calculate_vt_tree()`, `ccs_pll_calculate_vt_tree()`, `ccs_pll_calculate_vt()`), and OP branch search (`ccs_pll_calculate_op()`).

Control flow: `ccs_pll_calculate()` normalizes lane counts for non-lane-speed mode, chooses OP limit/state pointers depending on dual-PLL/no-OP-clock flags, validates required inputs, rejects non-integer OP pixel divisors unless flexible division is allowed, computes SDR OP system clock from link frequency and bus type, derives CSI pixel rate, computes OP pre-PLL divider bounds, reduces the desired clock ratio with `gcd()`, and iterates valid pre-PLL divisors. Each candidate computes OP PLL multiplier/sys/pix divisors, validates OP bounds, computes or later separately computes VT clocks, checks FIFO derating/overrating constraints, and exits on the first valid configuration. Dual-PLL mode then runs a separate VT-tree calculation.

State/persistence: Stateless calculation helper. It mutates caller-provided `struct ccs_pll` output fields and logs debug data; it does not touch sensor hardware.

Dependencies/integration: Uses Linux `gcd`, `lcm`, device logging, integer division helpers, and `ccs-pll.h`. Sensor drivers provide `struct ccs_pll_limits` and input bus configuration, then program returned fields into sensor registers.

Risks: The algorithm is integer-heavy and many frequency products are 32-bit, so unusual high-frequency limits can overflow. It returns the first valid search result, not necessarily a globally optimal clock tree. Flexible OP pixel division, DDR flags, C-PHY constants, FIFO derating/overrating, and dual PLL branching create a broad matrix where regressions are easy. Bounds debug strings include a few naming inconsistencies but do not affect calculation.

Test signals: Known-good CCS/SMIA sensor tables should verify exact output branches and pixel rates for D-PHY, C-PHY, dual PLL, no OP clocks, DDR flags, flexible divisors, and FIFO derating/overrating. Fuzz or property tests should assert output fields stay within all declared limits and return `-EINVAL` for zero required inputs or impossible divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.h

Purpose: Public data contract for the generic CCS/SMIA PLL calculator.

Important APIs/types/functions: Defines bus types `CCS_PLL_BUS_TYPE_CSI2_DPHY` and `CCS_PLL_BUS_TYPE_CSI2_CPHY`, calculation flags such as `CCS_PLL_FLAG_LANE_SPEED_MODEL`, `CCS_PLL_FLAG_DUAL_PLL`, `CCS_PLL_FLAG_NO_OP_CLOCKS`, `CCS_PLL_FLAG_FLEXIBLE_OP_PIX_CLK_DIV`, FIFO rate flags, and OP DDR flags. `struct ccs_pll_branch_fr` and `struct ccs_pll_branch_bk` represent front-end PLL and back-end sys/pix dividers. `struct ccs_pll` contains input bus/lane/binning/scaling/bpp/link/extclk fields plus calculated VT/OP branches and pixel rates. `struct ccs_pll_limits` nests front/back branch limits and line-length limits. `ccs_pll_calculate()` is the exported function.

Control flow: No executable logic. The header describes how callers must populate input fields and limits before calculation and which output fields become valid after success.

State/persistence: No local state. All persistence is caller-owned in `struct ccs_pll` and sensor-specific limits.

Dependencies/integration: Includes `linux/bits.h` for flag definitions and forward declares `struct device` for the calculator logging argument. Included by `ccs-pll.c` and sensor drivers using the helper.

Risks: The flag matrix is dense; invalid combinations can produce `-EINVAL` or surprising pixel rates. Units are encoded only in field names, so callers must consistently use Hz, lane counts, scaling ratios, and bit depths. `flags` is `u16`, leaving limited room for future expansion.

Test signals: Compile-time users should initialize all mandatory input and limit fields. Runtime calculator tests should verify that every flag documented here has at least one passing and one rejecting scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Kconfig

Purpose: Kconfig entry enabling the generic MIPI CCS/SMIA/SMIA++ camera sensor driver.

Important APIs/types/functions: Defines `config VIDEO_CCS` as a tristate named "MIPI CCS/SMIA++/SMIA sensor support". It depends on `HAVE_CLK` and selects `V4L2_CCI_I2C` and `VIDEO_CCS_PLL`.

Control flow: Build configuration only. When enabled as built-in or module, it causes the CCS driver objects from the sibling Makefile to be built and ensures required CCI and PLL helper support are selected.

State/persistence: No runtime state. The selected symbol persists only in kernel build configuration.

Dependencies/integration: Integrates the CCS sensor driver with the media I2C Kconfig tree. The `VIDEO_CCS_PLL` selection connects this driver family to `ccs-pll.c`.

Risks: Selecting `VIDEO_CCS_PLL` makes the PLL helper available whenever the sensor driver is enabled, but hidden dependencies in the broader tree must still provide I2C/media infrastructure. The short help text does not mention device-tree/ACPI binding requirements.

Test signals: `make menuconfig` should show the option when `HAVE_CLK` is true. Kernel config builds should include `CONFIG_VIDEO_CCS` and automatically include `CONFIG_VIDEO_CCS_PLL` and `CONFIG_V4L2_CCI_I2C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Makefile

Purpose: Kbuild recipe for the modular CCS camera sensor driver.

Important APIs/types/functions: `ccs-objs` aggregates `ccs-core.o`, `ccs-reg-access.o`, `ccs-quirk.o`, `ccs-limits.o`, and `ccs-data.o` into the logical `ccs.o` module. `obj-$(CONFIG_VIDEO_CCS) += ccs.o` connects the object to the Kconfig symbol. `ccflags-y += -I $(srctree)/drivers/media/i2c` adds the parent I2C media directory to include search paths.

Control flow: Build-time only. Enabling `CONFIG_VIDEO_CCS` compiles and links the listed object files as the CCS driver.

State/persistence: No runtime state. The file controls build products and compiler include paths.

Dependencies/integration: Integrates the CCS subdirectory into Linux kbuild and allows source files to include shared media I2C headers such as `ccs-pll.h` from the parent directory.

Risks: Object list ordering can matter if initialization data or symbols are expected during linking. The include-path addition couples the subdirectory to parent-directory private headers, so moving the driver tree requires Makefile updates.

Test signals: A build with `CONFIG_VIDEO_CCS=m` should produce `ccs.ko` from all five component objects. A built-in config should link the same object set into the kernel image with no missing include errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Makefile -->
