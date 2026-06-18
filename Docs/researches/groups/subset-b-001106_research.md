# subset-b-001106 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb-aoclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb-aoclk.c

## Purpose
Implements the Amlogic GXBB always-on clock controller description. The file is a platform-driver wrapper around shared AO clock-controller helpers: it defines the AO register offsets, the AO peripheral gates, the internally generated 32 kHz clock path, CEC and RTC muxes, reset-line numbering, and the sparse clock provider array consumed by the common clock framework.

## Important APIs, Types, And Functions
The central data is a set of `struct clk_regmap` instances using `clk_regmap_gate_ops`, `clk_regmap_gate_ro_ops`, `clk_regmap_mux_ops`, `clk_regmap_mux_ro_ops`, and `meson_clk_dualdiv_ops`. `GXBB_AO_PCLK` expands through `MESON_PCLK` to define simple pclk-derived gate clocks for remote, I2C, UART, and IR blocks. `gxbb_32k_div_table` and `gxbb_ao_32k_div` describe the AO 32 kHz divider programming. `gxbb_ao_reset` maps reset IDs from `dt-bindings/reset/gxbb-aoclkc.h` onto bits in `AO_RTI_GEN_CNTL_REG0`. `gxbb_ao_hw_clks` maps `dt-bindings/clock/gxbb-aoclkc.h` clock IDs to CCF hardware objects. The platform driver uses `meson_aoclkc_probe`.

## Control Flow
There is no custom runtime algorithm in this file. On OF platform-device match for `amlogic,meson-gx-aoclkc`, the driver passes `gxbb_ao_clkc_data.clkc_data` to `meson_aoclkc_probe`. The shared probe registers all clocks through the Meson clock utilities and then registers a reset controller using the reset metadata embedded in `struct meson_aoclk_data`.

## State And Persistence
State is the AO syscon register block reached through the parent syscon node. Clock state is persisted in AO register bits for gates, muxes, dividers, and reset pulses. The 32 kHz path can select external 32 kHz inputs or the internally divided oscillator. The driver keeps no private persistent software state beyond devm-managed registration objects in the shared probe.

## Dependencies And Integration Points
Depends on `meson-aoclk.h`, `meson-clkc-utils.h`, `clk-regmap.h`, `clk-dualdiv.h`, Linux platform driver/module infrastructure, DT clock and reset binding headers, and parent firmware clock names such as `xtal`, `mpeg-clk`, and `ext-32k-*`. Consumers use the AO clock provider IDs and reset provider IDs from Devicetree. The fake CEC parent named `fixme` is an integration workaround for CCF parent probing behavior when the hardware boots with an unknown mux input.

## Risks And Edge Cases
The clock table is sparse and must stay aligned with binding IDs. Parent names are firmware ABI, so DTS names must match. The CEC mux intentionally includes a non-existent parent to force parent discovery; removing it can make boot-time mux state invisible. Reset bits are pulse-style writes handled by the shared AO reset helper, so the bit mapping is high risk. `CLK_IGNORE_UNUSED` keeps historical AO gates on and may hide missing consumers.

## Test Signals
Build with `CONFIG_COMMON_CLK_MESON` and this driver enabled. Boot a GXBB/GXL-family board with `amlogic,meson-gx-aoclkc`; verify clocks appear in `/sys/kernel/debug/clk/clk_summary`, AO UART/I2C/IR/CEC clients can acquire clocks, reset phandles pulse the expected hardware, and CEC/RTC 32 kHz rates resolve correctly for internal and external 32 kHz parent configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb-aoclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb.c

## Purpose
Describes the main EE-domain clock controller for Amlogic GXBB and GXL SoCs. The file publishes the clock tree behind `amlogic,gxbb-clkc` and `amlogic,gxl-clkc`: fixed, system, HDMI, GP0, fractional, MPLL, clk81, audio, MMC/NAND, GPU, VPU/VAPB, video encoder, HDMI, decoder, generic, AO, AIU, and large peripheral gate sets. It is data-heavy driver code whose correctness depends on register offsets, bit positions, parent topology, and DT clock ID alignment.

## Important APIs, Types, And Functions
Most declarations are static `struct clk_regmap`, `struct clk_fixed_factor`, `struct pll_params_table`, `struct reg_sequence`, and parent arrays. Important helpers and ops include `meson_clk_pll_ops`, `meson_clk_pll_ro_ops`, `meson_clk_mpll_ops`, `meson_vid_pll_div_ro_ops`, `clk_regmap_gate_ops`, `clk_regmap_mux_ops`, and divider variants. `GXBB_PCLK` and `GXBB_AIU_PCLK` generate many gate clocks through `MESON_PCLK`. `gxbb_hw_clks` and `gxl_hw_clks` expose sparse ID-to-clock maps from `dt-bindings/clock/gxbb-clkc.h`. `gxbb_clkc_data` and `gxl_clkc_data` are passed to `meson_clkc_syscon_probe` by the platform driver.

## Control Flow
At platform probe, OF matching chooses GXBB or GXL data. `meson_clkc_syscon_probe` obtains the parent syscon regmap and registers each non-null `clk_hw` in the selected array, then installs the OF clock provider. Rate changes are delegated to CCF ops supplied by the individual clock nodes. Some paths use parent name fallbacks, for example `gp0_pll`, `mpll0`, and `vid_pll_div`, so one common downstream node can bind to GXBB- or GXL-specific upstream hardware.

## State And Persistence
Hardware state lives in HHI registers in the parent syscon region. PLL lock, enable, reset, fractional, mux, divider, and gate bits persist in those registers and may also be touched by display firmware or drivers. Several video clocks carry `CLK_GET_RATE_NOCACHE` because HDMI/display code directly programs PLL registers outside this provider. Critical and ignored-unused clocks preserve boot-critical state for clk81, fclk dividers, video, VPU/VAPB, and historical peripheral gates.

## Dependencies And Integration Points
Depends on Linux CCF, platform-driver OF matching, Meson regmap clock helpers, PLL/MPLL/video-divider helpers, and clock binding IDs. It integrates with DTS clock provider nodes, display/HDMI, DRM/VPU/VAPB, MMC/NAND, SAR ADC, audio AIU and IEC958, USB, Ethernet, UART, reset-controller consumers, RNG, and video decoder drivers. Parent firmware names include `xtal`, while many internal parents are direct `clk_hw` links.

## Risks And Edge Cases
The highest risks are sparse array ID drift, SoC-specific differences sharing common names, and undocumented parent choices. GXL differs in HDMI PLL divider locations, GP0 parameters/init registers, and MPLL0 SDM enable placement. The file deliberately avoids using precious MPLL/GP0 parents for some MMC/NAND and GPU choices. Many gates use `CLK_IGNORE_UNUSED` for historical reasons, which can hide unmodelled dependencies but prevents regressions on boards whose consumers are incomplete. Video clocks using no-cache indicate possible races or stale rates if direct register writers are not coordinated.

## Test Signals
Useful signals are successful module build and probe on `amlogic,gxbb-clkc` and `amlogic,gxl-clkc`, complete `/sys/kernel/debug/clk/clk_summary` coverage for binding IDs, stable HDMI/display modes, working MMC/NAND clock rates, audio playback with MPLL-derived rates, GPU/VPU rate changes, and boot without disabling critical fclk/clk81 paths. Static checks should compare `gxbb_hw_clks` and `gxl_hw_clks` against `include/dt-bindings/clock/gxbb-clkc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.c

## Purpose
Provides shared probe and reset-controller support for Amlogic always-on clock controller drivers. SoC-specific AO files supply `struct meson_aoclk_data`; this helper registers their clocks through the generic Meson syscon clock path and adds reset-controller behavior for AO reset registers.

## Important APIs, Types, And Functions
`meson_aoclk_do_reset()` implements the reset callback by writing one reset bit to `data->reset_reg`, where the actual bit index comes from the SoC reset array. `meson_aoclk_reset_ops` exposes only `.reset`, not separate assert/deassert, matching pulse-style AO reset semantics. `meson_aoclkc_probe()` is the exported probe entry point used by AO platform drivers. It calls `of_device_get_match_data()`, `meson_clkc_syscon_probe()`, allocates `struct meson_aoclk_reset_controller`, obtains the parent syscon regmap, fills `reset_controller_dev`, and registers it with `devm_reset_controller_register()`.

## Control Flow
Probe first validates match data, then delegates clock registration to `meson_clkc_syscon_probe`. After clocks are registered, it recovers the enclosing `struct meson_aoclk_data` with `container_of()` from the matched `meson_clkc_data`, resolves the parent syscon regmap, and registers resets. Reset calls later index `data->reset[id]` and write a single `BIT()` to the AO reset register.

## State And Persistence
The helper owns devm-managed software state for the reset controller and uses the parent syscon regmap for all hardware state. Reset operation is write-only pulse state in hardware; there is no cached reset state or persistent driver-owned storage. Clock state is registered by `meson_clkc_syscon_probe`, not by custom code here.

## Dependencies And Integration Points
Depends on `meson-aoclk.h`, `meson-clkc-utils.h`, `clk-regmap.h`, Linux reset-controller framework, OF match data, platform devices, syscon, and regmap. SoC AO drivers integrate by embedding `struct meson_clkc_data` as the first member of `struct meson_aoclk_data` and passing `.data = &foo.clkc_data` from their OF match table.

## Risks And Edge Cases
The reset path does not bounds-check `id` itself; it relies on reset core respecting `nr_resets`. Incorrect `reset` array content or `num_reset` values will write wrong bits. Probe performs clock registration before reset registration, so a reset-registration failure leaves clocks registered through devm. The helper requires the AO node to have a syscon parent; a missing or non-syscon parent fails probe.

## Test Signals
Build users with `MODULE_IMPORT_NS("CLK_MESON")`, boot a matching AO controller, verify clock provider registration succeeds, and exercise reset phandles from consumers. Negative DT tests should cover missing match data and missing parent syscon. Runtime debug signals include successful reset-controller registration and no invalid regmap errors during AO probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.h

## Purpose
Declares the shared data contract for Meson always-on clock controller drivers. It lets SoC-specific AO clock files describe both clock-provider data and reset-controller metadata in a single structure consumed by `meson_aoclkc_probe()`.

## Important APIs, Types, And Functions
`struct meson_aoclk_data` embeds `const struct meson_clkc_data clkc_data`, then adds `reset_reg`, `num_reset`, and `reset` bit mapping. `struct meson_aoclk_reset_controller` wraps a `reset_controller_dev`, a pointer back to the immutable AO data, and the syscon `regmap`. `meson_aoclkc_probe(struct platform_device *pdev)` is the public helper prototype exported by the implementation.

## Control Flow
There is no runtime control flow in the header. Its layout is nevertheless part of the control path: implementation code uses `container_of(clkc_data, struct meson_aoclk_data, clkc_data)`, so `clkc_data` must remain embedded with stable type and identity in every SoC data object.

## State And Persistence
The header defines the software state shape for reset registration and immutable SoC metadata. Hardware state remains in syscon registers identified by `reset_reg` and by the clock data described through `meson_clkc_data`.

## Dependencies And Integration Points
Includes Linux clock provider, platform-device, regmap, and reset-controller headers plus local `clk-regmap.h` and `meson-clkc-utils.h`. SoC files such as `gxbb-aoclk.c` include this header and expose compatible-specific data through OF match tables. The reset framework consumes `reset_controller_dev`; CCF consumes the embedded `meson_clkc_data`.

## Risks And Edge Cases
Any change to `struct meson_aoclk_data` must preserve the `container_of` relationship used by the implementation. Reset arrays are raw bit maps, so signedness and count mismatches can become register writes to the wrong reset line. Header consumers also depend on the `CLK_MESON` exported probe symbol being available.

## Test Signals
Compile all Meson AO drivers that include this header, with namespace imports enabled. Static review should verify each `struct meson_aoclk_data` supplies `.clkc_data`, `.reset_reg`, `.num_reset`, and `.reset` consistently with its DT reset binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.c

## Purpose
Implements common registration utilities for Meson clock-controller drivers. It centralizes OF clock lookup, optional register initialization, per-clock `clk_hw` registration, and probe flows for controllers backed either by a parent syscon regmap or by directly mapped MMIO.

## Important APIs, Types, And Functions
`meson_clk_hw_get()` is the OF clock provider callback. It indexes `struct meson_clk_hw_data` by `clkspec->args[0]`, rejects out-of-range IDs with `ERR_PTR(-EINVAL)`, and returns the selected `clk_hw`. `meson_clkc_init()` reads matched `struct meson_clkc_data`, optionally writes `init_regs` through `regmap_multi_reg_write()`, registers every non-null clock with `devm_clk_hw_register()`, and adds the OF provider with `devm_of_clk_add_hw_provider()`. `meson_clkc_syscon_probe()` obtains the parent syscon regmap. `meson_clkc_mmio_probe()` maps platform resource 0, creates a 32-bit stride-4 regmap, and calls common init.

## Control Flow
Platform drivers call one of the two exported probe helpers. Both resolve a regmap, then call `meson_clkc_init()`. Initialization validates match data, applies static register defaults if present, iterates the sparse hardware clock array, and stops on the first registration failure. OF clock consumers later call back into `meson_clk_hw_get()` for phandle resolution.

## State And Persistence
The utility does not keep global state. Hardware state can be changed by optional init register writes and later by registered clock ops using the same regmap. Registration state is device-managed for platform probes, so clocks and providers are cleaned up with device lifecycle. MMIO regmap lifetime is also devm-managed.

## Dependencies And Integration Points
Depends on Linux CCF, OF device matching, syscon, platform resource mapping, regmap, and local `meson-clkc-utils.h`. It is used by main, AO, and DDR Meson clock controllers. The helper is exported in the `CLK_MESON` namespace for modular drivers.

## Risks And Edge Cases
`meson_clk_hw_get()` assumes one clock cell and uses `args[0]`; incompatible bindings or missing `#clock-cells = <1>` will fail. Sparse arrays are allowed, but a valid in-range ID can return NULL if the SoC did not populate that clock. `meson_clkc_init()` ignores the return value of `regmap_multi_reg_write()`, so failed init writes are not directly reported. MMIO max_register is calculated from resource size minus stride, which assumes a non-empty 4-byte-aligned region.

## Test Signals
Compile drivers using both syscon and MMIO helpers. Probe a syscon-backed controller and a direct-MMIO controller, then verify OF phandle lookups by valid and invalid clock IDs. Fault-injection or debug instrumentation should confirm registration errors stop probe and out-of-range lookup logs `invalid index`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.h -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.h

## Purpose
Defines the shared Meson clock-controller data structures, probe-helper prototypes, OF lookup callback, and macro helpers for common peripheral and composite clock declarations.

## Important APIs, Types, And Functions
`struct meson_clk_hw_data` contains the sparse `struct clk_hw **hws` array and its count. `struct meson_clkc_data` adds optional `init_regs`, `init_count`, and `hw_clks`. Public functions are `meson_clk_hw_get()`, `meson_clkc_syscon_probe()`, and `meson_clkc_mmio_probe()`. `MESON_PCLK` and `MESON_PCLK_RO` generate regmap-backed gate clocks with one parent. `MESON_COMP_SEL`, `MESON_COMP_DIV`, and `MESON_COMP_GATE` generate the mux, divider, and gate pieces of a common composite clock chain.

## Control Flow
The header itself has no runtime control flow. The macros expand at compile time into `struct clk_regmap` declarations wired to local parent arrays or previous macro-generated nodes. These declarations are later registered by the utility implementation.

## State And Persistence
Generated clocks persist state in regmap-backed hardware registers through offsets, shifts, masks, bit indexes, and flags supplied to macros. The structures are normally static data in SoC drivers and are not dynamically allocated by the macros.

## Dependencies And Integration Points
Includes OF-device and clock-provider headers and forward-declares `struct platform_device`. Macro users also need `clk-regmap.h` definitions in scope because generated objects use `struct clk_regmap_*_data` and regmap clock ops. The API is used across Meson clock driver files to reduce repeated gate/mux/divider declarations.

## Risks And Edge Cases
Macros create global symbols with names derived from arguments, so naming collisions are possible. `MESON_COMP_SEL` uses `ARRAY_SIZE(_pdata)`, which requires `_pdata` to be an actual array in scope, not a pointer. The generated composite pieces encode a fixed parent order: divider parent is `_prefix##_name##_sel`, gate parent is `_prefix##_name##_div`. Incorrect flags can propagate unwanted rate changes or prevent needed parent changes.

## Test Signals
Compile all macro users with sparse arrays and composite clocks enabled. Static review should verify parent arrays passed to `MESON_COMP_SEL` are arrays, gate bits match registers, and generated symbol names are referenced correctly from clock ID arrays. Runtime signals are successful clock registration and expected parent/divider/gate behavior through clk debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson8-ddr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/meson8-ddr.c

## Purpose
Implements the DDR clock controller for Meson8 and Meson8b. It exposes the DDR PLL DCO and divided DDR PLL as read-only clocks backed by a directly mapped register block, then registers a built-in platform driver for `amlogic,meson8-ddr-clkc` and `amlogic,meson8b-ddr-clkc`.

## Important APIs, Types, And Functions
`meson8_ddr_pll_dco` is a `struct clk_regmap` using `meson_clk_pll_ro_ops`, with enable, m, n, lock, and reset fields in `AM_DDR_PLL_CNTL`. Its parent is firmware clock `xtal`. `meson8_ddr_pll` is a read-only power-of-two divider from the DCO, using bits 17:16 of the same register. `meson8_ddr_hw_clks` maps `DDR_CLKID_DDR_PLL_DCO` and `DDR_CLKID_DDR_PLL` from `dt-bindings/clock/meson8-ddr-clkc.h`. `meson8_ddr_clkc_data` is consumed by `meson_clkc_mmio_probe`.

## Control Flow
The built-in platform driver probes matching DT nodes, and `meson_clkc_mmio_probe()` maps resource 0, initializes a regmap, registers the two clocks, and installs the OF provider. The file does not change DDR rates; both clocks are read-only views of bootloader/firmware-programmed DDR PLL state.

## State And Persistence
DDR PLL state persists in the controller's MMIO registers. The driver reads enable/divider/lock-related fields via regmap-backed clock ops but does not actively program the memory clock. Software state is devm-managed by the common MMIO probe helper.

## Dependencies And Integration Points
Depends on Linux CCF, platform-device infrastructure, `clk-regmap.h`, `clk-pll.h`, `meson-clkc-utils.h`, and the DDR clock binding header. It integrates with DTS nodes that provide the MMIO range and clock consumers that need a DDR clock reference.

## Risks And Edge Cases
DDR clock programming is sensitive, so the read-only ops are intentional. Changing these clocks to writable without memory-controller coordination would be high risk. The binding ID array is tiny but must remain aligned. Probe requires an MMIO resource large enough for the regmap helper. The file is built in, not a loadable module, matching early platform needs.

## Test Signals
Build with Meson8 DDR clock support, boot Meson8/Meson8b hardware, verify both DDR clock IDs resolve, and inspect clk debugfs for plausible DDR PLL DCO and divided rates. DT binding checks should ensure one register range and `#clock-cells` usage match the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson8-ddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson8b.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/meson8b.c

## Purpose
Defines the early clock and reset controller for Amlogic Meson8, Meson8b, and Meson8m2 SoCs. It publishes a large HHI clock tree through `CLK_OF_DECLARE_DRIVER` rather than a normal platform driver, including fixed/system/video/HDMI/GPU/VPU/VDEC/audio/peripheral clocks, CPU clock switching support, SoC-specific clock ID arrays, and reset-controller lines in clock registers.

## Important APIs, Types, And Functions
The file declares many `struct clk_regmap`, `struct clk_fixed_factor`, PLL parameter tables, init register sequences, parent arrays, and sparse `clk_hw` ID arrays: `meson8_hw_clks`, `meson8b_hw_clks`, and `meson8m2_hw_clks`. Key reset types are `struct meson8b_clk_reset` and `meson8b_clk_reset_bits`; operations are `meson8b_clk_reset_update()`, `meson8b_clk_reset_assert()`, and `meson8b_clk_reset_deassert()`. CPU rate-change handling uses `struct meson8b_nb_data` and `meson8b_cpu_clk_notifier_cb()`. `meson8b_clkc_init_common()` performs syscon lookup, reset-controller registration, clock registration, notifier setup, and OF provider registration.

## Control Flow
During early OF clock initialization, the compatible-specific wrapper chooses the Meson8, Meson8b, or Meson8m2 clock array and calls common init. Common init obtains the parent HHI syscon regmap, allocates reset state, registers the reset controller, iterates non-null clocks starting at `CLKID_PLL_FIXED`, registers each with `of_clk_hw_register()`, registers a notifier on `cpu_scale_out_sel`, then installs the provider callback. During CPU rate changes, the notifier switches `cpu_clk` to xtal before the rate change and back to `cpu_scale_out_sel` afterward, with a short delay.

## State And Persistence
Clock and reset state is stored in HHI syscon registers. The code programs clocks through regmap ops and reset lines through `regmap_update_bits()`. Early init uses `kzalloc_obj()` rather than devm allocation, so state persists for the lifetime of the booted kernel. PLL init sequences for HDMI and Meson8m2 GP PLL write hardware defaults through the underlying PLL ops. CPU notifier state is global in `meson8b_cpu_nb_data`.

## Dependencies And Integration Points
Depends on CCF, early OF clock declarations, syscon/regmap, reset-controller framework, local Meson clk-regmap/PLL/MPLL utilities, and binding headers for clock and reset IDs. Integrates with cpufreq/CPU clock consumers, display pipelines, HDMI/LVDS, GPU, VPU, VDEC, NAND, audio AIU/IEC958, peripheral bus gates, AO gates, and reset consumers. The parent syscon node must be present.

## Risks And Edge Cases
This is high-risk table-driven code. ID arrays differ among Meson8, Meson8b, and Meson8m2; Meson8 lacks glitch-free Mali/VPU second paths exposed by later variants, while Meson8m2 adds GP PLL and different VPU parents. The CPU notifier is a workaround for safe rate switching and can destabilize systems if parent ordering changes. Some parent values are skipped due to unstable duty cycle or unknown documentation. Reset lines include both active-high and active-low bits, so polarity errors can hold hardware in reset. Early-init allocation and registration have limited cleanup on partial failure.

## Test Signals
Boot all three compatibles and verify early console, CPU frequency transitions, clk debugfs topology, reset-controller phandles, HDMI/display clocks, GPU/VPU rate changes, VDEC decode clocks, audio clocks, and NAND/peripheral consumers. Static validation should compare all three clock arrays with `dt-bindings/clock/meson8b-clkc.h` and reset bits with `amlogic,meson8b-clkc-reset.h`. CPU stress plus cpufreq transitions is the best signal for the notifier path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/meson8b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/parm.h -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/parm.h

## Purpose
Provides small bitfield helper macros and accessors used by Meson clock code to describe and manipulate register parameters. It abstracts width/shift-based fields into `struct parm` and inline read/write helpers around regmap.

## Important APIs, Types, And Functions
`PMASK(width)`, `SETPMASK(width, shift)`, and `CLRPMASK(width, shift)` build masks. `PARM_GET(width, shift, reg)` extracts a field from a raw register value, while `PARM_SET(width, shift, reg, val)` returns a raw register value with the field replaced. `MESON_PARM_APPLICABLE(p)` treats non-zero width as field presence. `struct parm` stores `reg_off`, `shift`, and `width`. `meson_parm_read()` reads a register and extracts the field. `meson_parm_write()` updates the field with `regmap_update_bits()`.

## Control Flow
The helpers are inline and synchronous. Callers pass a regmap and parameter descriptor; reads perform one `regmap_read()`, writes perform one masked `regmap_update_bits()`. There is no error propagation from either helper.

## State And Persistence
State lives only in hardware registers. `struct parm` is a descriptor, normally static in clock data. The helpers do not cache values and do not allocate software state.

## Dependencies And Integration Points
Depends on Linux `GENMASK()` through `linux/bits.h` and regmap accessors. Meson PLL and clock helpers can use these descriptors to express register fields without open-coding masks and shifts.

## Risks And Edge Cases
Width must be non-zero and valid for `GENMASK(width - 1, 0)`; a zero-width field is only safe when guarded by `MESON_PARM_APPLICABLE`. `PARM_SET` does not mask `val` before shifting, so callers must pass a value that fits the field width. Read/write helpers ignore regmap return codes, which can hide bus or MMIO access failures.

## Test Signals
Compile all users with sparse and W=1 warnings. Unit-style validation can exercise representative widths/shifts and verify `PARM_GET`/`PARM_SET` round trips. Runtime confidence comes from clock rate programming that uses parm descriptors and from regmap debug confirming only intended bits change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/parm.h -->
