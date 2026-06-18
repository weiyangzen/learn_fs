# subset-b-000655 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sr_device.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sr_device.c

### Purpose
`sr_device.c` prepares OMAP SmartReflex platform data from hwmod or SoC-specific instance names. It links SmartReflex sensors to voltage domains and fills eFuse-derived N-value tables used by the SmartReflex driver for adaptive voltage compensation.

### Important APIs, Types, And Functions
The main entry point is `omap_devinit_smartreflex()`. Helpers are `sr_init_by_name()`, `sr_dev_init()`, and `sr_set_nvalues()`. It consumes global `omap_sr_pdata[]`, `struct omap_sr_data`, `struct omap_volt_data`, and `struct omap_sr_nvalue_table`.

### Control Flow
Initialization selects hard-coded OMAP4/DRA7 SmartReflex instances or walks hwmods of class `smartreflex`. Each instance name maps to MPU, CORE, or IVA SmartReflex data, looks up a matching `voltagedomain`, gets its voltage table, reads eFuse offsets, and records only nonzero eFuse values. OMAP4 eFuse reads are byte-wise because the fields are 24-bit aligned.

### State, Persistence, And Dependencies
State is retained in the global SmartReflex platform data array, including dynamically allocated N-value tables and voltage-domain pointers. It depends on SoC detection, OMAP control-module reads, voltage-domain registration, hwmod metadata, and SmartReflex platform definitions.

### Integration Points
The SmartReflex device driver later consumes this platform data to tune voltage error limits and sensor parameters. `voltdm_lookup()` and `omap_voltage_get_volttable()` must already be usable for meaningful data.

### Risks
Missing voltage domains or voltage tables only log errors and still return success from `sr_init_by_name()`, so a SmartReflex instance can be partially initialized. `kasprintf()` strings for OMAP4/DRA7 names are not freed because they are boot-time data. Boards with unset eFuse values get empty N-value tables.

### Test Signals
Boot logs should show no unknown SmartReflex instances or missing voltage-domain errors. Useful validation is checking SmartReflex registration on OMAP3, OMAP4, and DRA7, including systems with zero eFuse rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sr_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.c

### Purpose
`sram.c` detects accessible OMAP internal SRAM, maps it executable, and copies small timing-critical routines into SRAM so SDRAM and clock-controller changes can run while external memory is unsafe.

### Important APIs, Types, And Functions
Public APIs are `omap_sram_init()`, `omap_sram_push()`, `omap2_sram_ddr_init()`, `omap2_sram_reprogram_sdrc()`, `omap2_set_prcm()`, and `omap3_sram_restore_context()`. Internal state includes `omap_sram_start`, `omap_sram_size`, `omap_sram_base`, `omap_sram_skip`, and `omap_sram_ceil`.

### Control Flow
`omap_sram_init()` detects public versus full SRAM depending on device type and security/firewall state, maps the region with `__arm_ioremap_exec()`, clears usable SRAM, marks it read-only executable, and pushes SoC-specific assembly functions for OMAP242x or OMAP243x. OMAP3 restore resets the allocator ceiling and repushes idle code through `omap_push_sram_idle()`.

### State, Persistence, And Dependencies
The file keeps a bump allocator that grows downward from the SRAM ceiling. Pushed function pointers persist in static function-pointer variables and are called by wrappers that `BUG_ON()` if initialization failed. Dependencies include `fncpy`, ARM page permission helpers, SoC detection, PRM/SDRC register addresses, and assembly symbols from `sram242x.S` and `sram243x.S`.

### Integration Points
Clock, SDRAM, idle, and power-management code call the wrapper APIs when hardware changes must be executed from SRAM. The code also interacts with OMAP RAM firewall registers to unlock GP-device SRAM.

### Risks
SRAM sizing or firewall mistakes can hang the system because secure SRAM cannot be probed safely. The allocator has no free path and only logs out-of-space failures. Page permission toggling around `fncpy()` must stay correct or copied code may be writable/executable at the wrong time. Calling wrappers before `omap_sram_init()` panics through `BUG_ON()`.

### Test Signals
Boot on OMAP2420, OMAP2430, and OMAP3 should show successful SRAM mapping and no wrapper BUGs. Suspend/resume and DVFS tests should cover OMAP3 SRAM context restore and repeated function repush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.h

### Purpose
`sram.h` declares OMAP2/3 SRAM-resident routine interfaces and physical SRAM base addresses shared between C setup code and assembly implementations.

### Important APIs, Types, And Functions
It declares generic wrappers such as `omap2_sram_ddr_init()`, `omap2_sram_reprogram_sdrc()`, `omap2_set_prcm()`, `omap_sram_init()`, and `omap_sram_push()`, plus the raw OMAP242x/243x assembly symbols and their `_sz` size labels. It also exposes `omap_push_sram_idle()` when power management is enabled.

### Control Flow
There is no runtime flow in the header. The declarations let `sram.c` copy assembly routines and let callers invoke the copied wrappers instead of directly calling code in normal memory.

### State, Persistence, And Dependencies
The header itself has no state. It depends on callers including suitable integer and init annotations, and it defines `OMAP2_SRAM_PA` and `OMAP3_SRAM_PA` as shared constants.

### Integration Points
The header is the contract between OMAP SRAM management, SDRAM/PRCM assembly, and idle/power-management code.

### Risks
Size symbols must continue to match the assembly entry ranges; otherwise `omap_sram_push()` can copy too little or too much code. The `CONFIG_PM` stub means callers must not assume idle code is pushed when PM is disabled.

### Test Signals
Build coverage should include OMAP2420, OMAP2430, OMAP3 with PM, and OMAP3 without PM to validate conditional declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram242x.S -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram242x.S

### Purpose
`sram242x.S` contains OMAP242x assembly routines that must execute from internal SRAM during DDR, SDRC, DPLL, PRCM, and voltage transitions.

### Important APIs, Types, And Functions
Exported entry points are `omap242x_sram_ddr_init`, `omap242x_sram_reprogram_sdrc`, and `omap242x_sram_set_prcm`, with matching size labels. Local helpers include DLL wait loops and voltage-shift routines that write PRCM voltage control and poll the 32 kHz sync timer.

### Control Flow
DDR init shifts frequency and voltage down, locks the DLL, records DLL status, shifts voltage and frequency back up, restores DLL control, and returns the measured value through the caller pointer. SDRC reprogramming barriers memory, adjusts voltage before or after speed changes, rewrites refresh timing, and relocks DDR DLLs when needed. PRCM setup enters fast-relock bypass, writes divider values, optionally relocks the DPLL, updates refresh timing, and relocks DLLs.

### State, Persistence, And Dependencies
The routines preserve registers on the stack but directly mutate PRCM, CM, SDRC, and timer registers. They depend on absolute register macros, ARM coprocessor barriers, no TLB misses while SDRAM is unavailable, and being copied to SRAM by `sram.c`.

### Integration Points
`sram.c` copies these routines and exposes them through generic OMAP2 wrapper APIs used by clock and memory timing code.

### Risks
Any new memory reference can cause a page-table walk while SDRAM is inaccessible, which can crash intermittently. Delay-loop constants encode hardware timing assumptions. Register offsets are OMAP242x-specific and must not be reused on other SoCs.

### Test Signals
Validation requires real OMAP242x hardware exercising frequency, voltage, and SDRAM timing changes under stress; static build tests only catch symbol and macro breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram242x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram243x.S -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram243x.S

### Purpose
`sram243x.S` provides the OMAP243x variant of SRAM-resident DDR, SDRC, PRCM, DPLL, and voltage-transition routines.

### Important APIs, Types, And Functions
It exports `omap243x_sram_ddr_init`, `omap243x_sram_reprogram_sdrc`, `omap243x_sram_set_prcm`, and their `_sz` symbols. The code mirrors the 242x routines but uses OMAP2430 register address macros and timer base values.

### Control Flow
The routines lower frequency and voltage for safe DLL initialization, capture DLL status, restore high-performance settings, reprogram SDRC refresh when moving between full and half speed, and control PRCM DPLL bypass/relock around divider updates.

### State, Persistence, And Dependencies
The only persistent effect is hardware register state. Correctness depends on being executed from SRAM, preserving registers, avoiding unsafe SDRAM accesses, and using the 243x-specific CM, PRCM, SDRC, and 32 kHz timer addresses.

### Integration Points
`omap243x_sram_init()` in `sram.c` copies these entry ranges into internal SRAM and binds the generic wrapper function pointers to the copied code.

### Risks
The routine structure is timing-sensitive and duplicate-like with 242x, so fixes must be applied to the correct SoC variant. Infinite waits are possible if DPLL or DLL status never reaches the expected state.

### Test Signals
Hardware DVFS and SDRAM timing tests on OMAP2430 are the meaningful signal; build coverage verifies only exported assembly labels and macro availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sram243x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx-restart.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx-restart.c

### Purpose
`ti81xx-restart.c` implements the TI81xx SoC restart hook by requesting a cold global reset through PRM registers.

### Important APIs, Types, And Functions
The sole API is `ti81xx_restart(enum reboot_mode mode, const char *cmd)`. It writes `TI81XX_GLOBAL_RST_COLD` into `TI81XX_PRM_DEVICE_RSTCTRL` using `omap2_prm_set_mod_reg_bits()`.

### Control Flow
The function sets the cold-reset request bit and then spins forever, relying on the hardware reset to interrupt execution.

### State, Persistence, And Dependencies
Persistent state is the PRM reset-control bit. It depends on TI81xx PRM addressing and the common ARM restart path wiring this function as the machine restart callback.

### Integration Points
Machine setup code uses this as the restart method for TI81xx-class OMAP platforms.

### Risks
There is no timeout or fallback path if the reset request fails. The comment notes warm reset is not used because it may require clock bypass preparation.

### Test Signals
The observable test is a clean reboot from kernel restart paths on TI81xx hardware, with no return from the restart callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx.h

### Purpose
`ti81xx.h` defines base physical addresses for TI81xx control, PRCM, slow L4, TAP, and interrupt-controller blocks.

### Important APIs, Types, And Functions
It exposes address macros such as `L4_SLOW_TI81XX_BASE`, `TI81XX_CTRL_BASE`, `TI81XX_PRCM_BASE`, `TI81XX_TAP_BASE`, and `TI81XX_ARM_INTC_BASE`.

### Control Flow
There is no executable flow. The derived TAP base compensates for common OMAP revision-check code adding a fixed offset while TI81xx places the device ID elsewhere.

### State, Persistence, And Dependencies
The header has no state and depends on TI81xx control-module offset definitions from included OMAP headers.

### Integration Points
SoC revision detection, control-module access, PRCM access, and interrupt-controller mapping use these constants.

### Risks
Incorrect base constants break early boot mappings and SoC identification. The TAP adjustment is subtle and tied to implementation details of `omap3_check_revision`.

### Test Signals
Early boot on TI81xx should identify the device revision correctly and map PRCM/control/interrupt blocks without faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/timer.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/timer.c

### Purpose
`timer.c` initializes the OMAP5/DRA7 realtime counter and ARM architected timer frequency so kernel timekeeping uses a calibrated master counter.

### Important APIs, Types, And Functions
External functions are `omap5_realtime_timer_init()` and `set_cntfreq()`. The core helper is `realtime_counter_init()`, which programs numerator and denominator registers at `REALTIME_COUNTER_BASE`.

### Control Flow
Initialization starts OMAP clocks, maps the realtime-counter registers, reads `sys_clkin`, selects numerator/denominator values by input clock rate, handles DRA7 erratum i856 when speed-select bits indicate an emulated 32 kHz clock, writes incrementer registers, computes `arch_timer_freq`, calls secure monitor code to set CNTFRQ, unmaps registers, and finally calls `timer_probe()`.

### State, Persistence, And Dependencies
The file persists `arch_timer_freq` in a static variable and programs hardware counter registers. It depends on clock lookup, OMAP control reads, secure monitor call `omap_smc1()`, and generic clocksource probing.

### Integration Points
This is the platform timer init path for OMAP5/DRA7 systems using the ARM architected timer.

### Risks
Unsupported `sys_clkin` values silently fall back to 38.4 MHz programming. Incorrect erratum detection causes measurable clock drift. Secure firmware must accept the CNTFRQ SMC call.

### Test Signals
Boot should report stable clocksource registration. Timekeeping drift tests on DRA7 boards with and without a real 32.768 kHz crystal are high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.c

### Purpose
`usb-tusb6010.c` configures GPMC chip-select windows and timings for a TI TUSB6010 USB controller exposed as a platform MUSB device.

### Important APIs, Types, And Functions
The board-facing API is `tusb6010_setup_interface()`. Timing helpers are `tusb_set_async_mode()`, `tusb_set_sync_mode()`, and `tusb6010_platform_retime()`. Static platform state includes async/sync chip selects, reference-clock period, GPMC settings, resources, DMA mask, and `tusb_device`.

### Control Flow
Setup requests async and sync GPMC chip selects, programs wait pins and 16-bit multiplexed address/data settings, calculates conservative timings from the TUSB6010 datasheet, registers platform resources, stores MUSB platform data, and registers the `musb-tusb` platform device. Retiming can switch timing calculations between reference-clock and 60 MHz oscillator modes.

### State, Persistence, And Dependencies
Chip-select numbers and reference clock period persist in static globals after setup. The file depends on the OMAP GPMC timing API, MUSB platform data, and platform-device registration.

### Integration Points
Board files call `tusb6010_setup_interface()` during init. The `musb-tusb` driver consumes the two memory resources and can call the retime hook through platform data behavior.

### Risks
The `dmachan` argument is unused here, so DMA channel expectations must be handled elsewhere. Failed setup after the first GPMC request does not unwind all earlier reservations. Timing constants are hardware-specific and should not be generalized.

### Test Signals
Board boot should register `musb-tusb`, map both async and sync resources, and survive clock-mode changes with USB enumeration and DMA/PIO transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.h

### Purpose
`usb-tusb6010.h` declares the board setup interface for attaching a TUSB6010 controller to OMAP GPMC.

### Important APIs, Types, And Functions
It declares `tusb6010_setup_interface(struct musb_hdrc_platform_data *data, unsigned int ps_refclk, unsigned int waitpin, unsigned int async_cs, unsigned int sync_cs, unsigned int dmachan)`.

### Control Flow
There is no runtime flow in the header. It supplies the prototype used by board files that provide MUSB platform data and GPMC wiring information.

### State, Persistence, And Dependencies
The header has no state and depends on `struct musb_hdrc_platform_data` being visible to callers.

### Integration Points
It bridges board setup code and `usb-tusb6010.c`.

### Risks
Callers must pass a valid reference clock period, wait pin, chip selects, and platform data; the implementation rejects missing clock/data at runtime.

### Test Signals
Builds of board files using TUSB6010 should type-check this prototype, and runtime setup should register the MUSB device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/usb-tusb6010.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.c

### Purpose
`vc.c` implements the OMAP Voltage Controller layer: PMIC I2C channel setup, bypass voltage scaling, sleep/off voltage signaling, and voltage-ramp timing calculation for OMAP3/4 voltage domains.

### Important APIs, Types, And Functions
Public APIs are `omap_vc_init_channel()`, `omap_vc_pre_scale()`, `omap_vc_post_scale()`, `omap_vc_bypass_scale()`, `omap3_vc_set_pmic_signaling()`, and `omap4_vc_set_pmic_signaling()`. Important internal structures include `omap_vc_channel_cfg`, `omap3_vc_timings`, and the static `vc` state used for PMIC signaling.

### Control Flow
Channel init validates PMIC and register callbacks, chooses default or mutant channel bit layouts, programs PMIC slave/register addresses, writes command voltage values, configures I2C mode and timing, and then applies OMAP3 or OMAP4 sleep/off timing setup. Bypass scaling updates the ON command value, writes a VC bypass command, waits for the valid bit, and delays for the PMIC slew interval.

### State, Persistence, And Dependencies
The file persists a global `vc` signaling state and one-time I2C initialization flags. It mutates per-domain `omap_vc_channel` fields and PRM/SCRM/control-module registers. Dependencies include PMIC conversion callbacks, voltage tables, power-domain state constants, oscillator timing from PM code, and SoC-specific VC register data.

### Integration Points
`omap_voltage_late_init()` calls `omap_vc_init_channel()` and may set a domain's scale method to `omap_vc_bypass_scale()`. VP force-update paths reuse `omap_vc_pre_scale()` and `omap_vc_post_scale()`.

### Risks
The global `vc` state assumes only one domain seeds PMIC sleep signaling. The bypass wait loop has fixed retry counts and returns timeout if the valid bit never settles. Unsupported sysclk values skip OMAP4 high-speed I2C timing programming. PMIC min/max clamping can hide requested off-range voltages except for warnings.

### Test Signals
Useful tests include boot-time VC register dumps, DVFS scale up/down, retention/off-idle PMIC signaling, high-speed I2C timing on each supported sysclk, and forced timeout/error injection for bypass scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.h

### Purpose
`vc.h` defines the OMAP Voltage Controller register metadata, per-channel state, channel flags, exported SoC data objects, and VC operation prototypes.

### Important APIs, Types, And Functions
Core types are `struct omap_vc_common` and `struct omap_vc_channel`. Flags include `OMAP_VC_CHANNEL_DEFAULT` and `OMAP_VC_CHANNEL_CFG_MUTANT`. It declares OMAP3/4 VC channel and parameter objects plus VC init and scaling APIs.

### Control Flow
There is no executable flow. The structures describe how generic VC code writes SoC-specific registers and fields.

### State, Persistence, And Dependencies
State lives in instances declared here and defined in VC data files. It depends on `struct voltagedomain` and shared voltage parameter types from `voltage.h`.

### Integration Points
Voltage-domain data points to these VC channel instances, and `vc.c` uses their masks, offsets, and shifts to program PRM registers.

### Risks
Incorrect bit shifts or flags can corrupt unrelated PRM fields. The header documents that some fields are redundant or awkwardly represented, so future changes need careful compatibility review.

### Test Signals
Build coverage across OMAP3/4 validates object declarations; runtime register programming tests validate masks and shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc3xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc3xxx_data.c

### Purpose
`vc3xxx_data.c` supplies OMAP3 Voltage Controller register metadata, MPU/core channel instances, and default sleep/off voltage parameters.

### Important APIs, Types, And Functions
It defines `omap3_vc_common`, `omap3_vc_mpu`, `omap3_vc_core`, `omap3_mpu_vc_data`, and `omap3_core_vc_data`.

### Control Flow
There is no active flow. Generic VC code consumes these objects during voltage-domain late init.

### State, Persistence, And Dependencies
The channel structures are mutable because `vc.c` fills runtime PMIC addresses and channel config bits. The file depends on OMAP3 PRM register offsets and bit masks.

### Integration Points
OMAP3 voltage-domain data references these channel and parameter objects for `mpu_iva` and `core`.

### Risks
Default voltages are board/PMIC-sensitive and may not match every product. Register metadata must align with OMAP34xx/36xx PRM layout.

### Test Signals
OMAP3 boot should initialize both VC channels, produce expected PRM_VC register values, and scale MPU/core domains correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc44xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc44xx_data.c

### Purpose
`vc44xx_data.c` provides OMAP4 Voltage Controller metadata for MPU, IVA, and CORE voltage channels plus default voltage command parameters.

### Important APIs, Types, And Functions
It defines `omap4_vc_common`, `omap4_vc_mpu`, `omap4_vc_iva`, `omap4_vc_core`, and `omap4_{mpu,iva,core}_vc_data`.

### Control Flow
The file is declarative; `vc.c` uses the exported structures when voltage-domain late init configures VC channels.

### State, Persistence, And Dependencies
The VC channel structures persist and receive PMIC runtime fields. Dependencies are OMAP4 PRM offsets and bitfield masks from `prm44xx.h` and `prm-regbits-44xx.h`.

### Integration Points
OMAP4 and OMAP5 voltage-domain data reuse these VC channel definitions.

### Risks
The MPU channel is flagged as both default and mutant, reflecting nonstandard channel bit layout; clearing or misusing those flags would program the wrong channel fields. The default off voltage is zero, which relies on PMIC support and correct board scripts.

### Test Signals
Register dumps on OMAP443x/446x should show channel-specific PMIC addresses and command values in the expected PRM offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc44xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.c

### Purpose
`voltage.c` implements the OMAP voltage-domain registry and common voltage-management APIs used by DVFS, SmartReflex, VC, and VP code.

### Important APIs, Types, And Functions
Public APIs include `voltdm_get_voltage()`, `voltdm_reset()`, `omap_voltage_get_volttable()`, `omap_voltage_get_voltdata()`, `omap_voltage_register_pmic()`, `omap_voltage_late_init()`, `voltdm_lookup()`, and `voltdm_init()`. The internal list is `voltdm_list`.

### Control Flow
`voltdm_init()` registers SoC-provided voltage-domain objects. Late init walks scalable domains, obtains the system clock rate, initializes VC and/or VP blocks, and assigns the scale callback. Scaling chooses the first OPP voltage greater than or equal to the target, calls the domain scale method, and updates the nominal voltage on success.

### State, Persistence, And Dependencies
Voltage-domain objects persist on a global list and hold PMIC data, OPP voltage tables, current nominal voltage, sysclk rate, and register callbacks. Dependencies include clock lookup, debug/logging, SoC PRM register helpers, VC/VP modules, power domains, and OPP voltage data.

### Integration Points
SmartReflex uses voltage tables and domain lookup, PMIC code registers `omap_voltdm_pmic`, and DVFS paths use domain scale/reset behavior.

### Risks
`_voltdm_register()` does not check duplicates. Late init can return early on one clock failure and skip later domains. If both VC and VP exist, VP force-update overwrites the scale callback after VC init. Nominal voltage starts at zero unless initialized elsewhere.

### Test Signals
Boot should register expected domains, late init should resolve sysclk for all scalable domains, and DVFS tests should verify target rounding, nominal voltage update, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.h

### Purpose
`voltage.h` defines the core OMAP voltage-domain data model, PMIC callback contract, voltage processor/controller parameters, limits, and public voltage-management APIs.

### Important APIs, Types, And Functions
Key types are `struct voltagedomain`, `struct omap_voltdm_pmic`, `struct omap_vp_param`, `struct omap_vc_param`, and `struct omap_vfsm_instance`. It declares voltage-domain init functions for OMAP2/3/4/5 and common lookup/register/query APIs.

### Control Flow
The header has no runtime flow. Its function pointers define how generic voltage code reads, writes, and read-modify-writes SoC PRM registers and how domains scale voltage.

### State, Persistence, And Dependencies
Instances of `struct voltagedomain` carry persistent platform state, current nominal voltage, PMIC data, voltage tables, and VC/VP pointers. The header depends on VC/VP definitions and platform voltage data.

### Integration Points
Every OMAP voltage-domain data file, VC/VP implementation, PMIC registration code, and SmartReflex setup uses this contract.

### Risks
The `sys_clk` union changes meaning from clock name during init to rate after late init, so callers must respect initialization phases. PMIC callbacks are mandatory for scalable domains, and missing callbacks produce runtime failures.

### Test Signals
Builds across OMAP2/3/4/5 configurations validate the structure relationships; runtime voltage scaling validates PMIC callback behavior and domain registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains2xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains2xxx_data.c

### Purpose
`voltagedomains2xxx_data.c` registers minimal OMAP2 voltage-domain names for core and wakeup domains.

### Important APIs, Types, And Functions
It defines static `voltagedomain` objects for `"core"` and `"wakeup"` and exports `omap2xxx_voltagedomains_init()`.

### Control Flow
The init function calls `voltdm_init()` with a null-terminated OMAP2 domain list.

### State, Persistence, And Dependencies
The domains are static and not marked scalable, so they persist only as lookup records without VC/VP behavior. The file depends on the common voltage-domain registry.

### Integration Points
OMAP2 platform init uses this to make voltage-domain names available to other platform code.

### Risks
No register callbacks, PMIC data, or OPP tables are provided, so callers must not expect DVFS scaling through these domains.

### Test Signals
Boot on OMAP2 should register `core` and `wakeup`, and no voltage late-init scaling should be attempted for them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains2xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains3xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains3xxx_data.c

### Purpose
`voltagedomains3xxx_data.c` defines OMAP3 and AM35xx voltage-domain objects and wires OMAP3 MPU/core scalable domains to VC/VP data and OPP voltage tables.

### Important APIs, Types, And Functions
It exports `omap3xxx_voltagedomains_init()`. Important objects are `omap3_voltdm_mpu`, `omap3_voltdm_core`, `omap3_voltdm_wkup`, AM35xx non-scalable alternatives, OMAP3 VFSM instances, and the `voltagedomains_omap3`/`voltagedomains_am35xx` lists.

### Control Flow
Init selects OMAP34xx or OMAP36xx OPP voltage data when `CONFIG_PM_OPP` is enabled, assigns VP/VC parameter pointers, selects the AM35xx or normal OMAP3 list, sets each domain's sysclk name to `sys_ck`, and registers the domains.

### State, Persistence, And Dependencies
Static voltage-domain objects persist in the global registry. Scalable OMAP3 domains carry PRM read/write/rmw callbacks, VC channels, VFSM register masks, VP instances, voltage tables, and sysclk names.

### Integration Points
The file links OMAP3-specific voltage data with generic `voltage.c`, `vc.c`, `vp.c`, SmartReflex, and OPP data.

### Risks
AM35xx domains are intentionally non-scalable; code assuming all OMAP3-like platforms have VC/VP will fail. Without `CONFIG_PM_OPP`, voltage tables remain unset and late scaling cannot proceed.

### Test Signals
Boot should register `mpu_iva`, `core`, and `wakeup` on OMAP3, but only non-scalable domains on AM35xx. DVFS/SmartReflex tests should cover OMAP34xx and OMAP36xx voltage tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains44xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains44xx_data.c

### Purpose
`voltagedomains44xx_data.c` defines OMAP4 scalable MPU, IVA, and CORE voltage domains plus wakeup domain metadata.

### Important APIs, Types, And Functions
It exports `omap44xx_voltagedomains_init()` and defines VFSM instances, `omap4_voltdm_mpu`, `omap4_voltdm_iva`, `omap4_voltdm_core`, `omap4_voltdm_wkup`, and the OMAP4 domain list.

### Control Flow
Init selects OMAP443x or OMAP446x OPP voltage tables if available, attaches OMAP4 VP and VC parameter structures to each scalable domain, sets sysclk name to `sys_clkin_ck`, and registers the list.

### State, Persistence, And Dependencies
Static domain objects persist and include OMAP4 PRM register callbacks, VC/VP pointers, VFSM setup registers, OPP tables, and clock-name state. Dependencies include OMAP4 PRM headers and OPP data.

### Integration Points
Generic voltage late init uses these objects to initialize VC/VP for OMAP4 DVFS and low-power transitions.

### Risks
Unsupported OMAP4 variants may not receive voltage tables. Incorrect sysclk naming prevents late init from calculating VC/VP timing. OMAP4 and OMAP5 share some VC/VP data, so changes have cross-SoC impact.

### Test Signals
OMAP443x and OMAP446x boots should register all domains and initialize VC/VP with a valid `sys_clkin_ck` rate; DVFS should scale MPU, IVA, and CORE independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains44xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains54xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains54xx_data.c

### Purpose
`voltagedomains54xx_data.c` defines OMAP5 voltage domains and maps them onto reused OMAP4 VC/VP channel instances.

### Important APIs, Types, And Functions
It exports `omap54xx_voltagedomains_init()` and defines `omap5_voltdm_mpu`, `omap5_voltdm_mm`, `omap5_voltdm_core`, `omap5_voltdm_wkup`, OMAP5 VFSM instances, and `voltagedomains_omap5`.

### Control Flow
Init assigns the `sys_clkin` clock name to every domain in the list and registers the domains with `voltdm_init()`.

### State, Persistence, And Dependencies
Static domain objects persist in the voltage-domain registry. Scalable domains use OMAP4 PRM VC/VP access callbacks and OMAP4 VC/VP instances while using OMAP54xx VFSM register offsets.

### Integration Points
OMAP5 voltage setup uses these domains as input to generic late init, PMIC registration, and OPP/voltage scaling.

### Risks
This file does not attach OPP voltage tables or VP/VC parameter structures, so successful scaling depends on data being supplied elsewhere or by reused structures. Reusing OMAP4 VC/VP instances requires register compatibility.

### Test Signals
OMAP5 boot should register `mpu`, `mm`, `core`, and `wkup`; late init should either receive external PMIC/parameter data or clearly log missing data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains54xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.c

### Purpose
`vp.c` implements OMAP Voltage Processor initialization, force-update voltage scaling, error-gain updates, and VP enable/disable operations.

### Important APIs, Types, And Functions
Public APIs are `omap_vp_init()`, `omap_vp_update_errorgain()`, `omap_vp_forceupdate_scale()`, `omap_vp_enable()`, and `omap_vp_disable()`. Internal helper `_vp_set_init_voltage()` writes INITVOLTAGE and toggles INITVDD.

### Control Flow
Init validates PMIC callbacks and register access, computes timeout and wait times from sysclk and PMIC slew data, clamps VP min/max to PMIC limits, and programs VP_CONFIG, VSTEPMIN, VSTEPMAX, and VLIMITTO. Force-update scaling performs VC pre-scale setup, clears stale transaction-done status, loads the target voltage, asserts FORCEUPDATE, waits for transaction done, runs VC post-scale delay, clears status, and drops FORCEUPDATE.

### State, Persistence, And Dependencies
The `enabled` flag persists in each `omap_vp_instance`. Hardware state persists in VP registers and transaction-done status. Dependencies include PMIC voltage conversion, VC pre/post scale helpers, voltage OPP data for error gain, and SoC-specific VP ops.

### Integration Points
`omap_voltage_late_init()` initializes VP and selects `omap_vp_forceupdate_scale()` as the domain scale callback when VP is present. SmartReflex class drivers use VP enable/disable.

### Risks
Timeouts are fixed constants and may not match all PMIC latency. `omap_vp_forceupdate_scale()` logs but still returns success if transaction done never sets after FORCEUPDATE. `_vp_set_init_voltage()` uses `char vsel`, so unusually high VSEL values deserve attention.

### Test Signals
DVFS force-update tests should verify transaction-done set/clear behavior, error-gain updates per OPP, VP enable/disable idempotence, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.h

### Purpose
`vp.h` defines the OMAP Voltage Processor metadata model, operation callbacks, timeout constants, exported SoC instances, and VP API prototypes.

### Important APIs, Types, And Functions
Key types are `struct omap_vp_ops`, `struct omap_vp_common`, and `struct omap_vp_instance`. It declares OMAP3/4 VP instances and parameters plus `omap_vp_init()`, `omap_vp_enable()`, `omap_vp_disable()`, `omap_vp_forceupdate_scale()`, and `omap_vp_update_errorgain()`.

### Control Flow
The header has no runtime flow; it describes the register offsets, bit masks, and status callbacks used by `vp.c`.

### State, Persistence, And Dependencies
Each `omap_vp_instance` carries a persistent `enabled` flag and per-domain register offsets. The header depends on voltage-domain declarations and SoC-specific data definitions.

### Integration Points
Voltage-domain data points to these VP instances, and SmartReflex/voltage scaling code calls the declared operations.

### Risks
Wrong masks or shifts can corrupt VP register fields. Timeout constants are global, not per-PMIC or per-SoC.

### Test Signals
Build coverage across OMAP3 and OMAP4 validates declarations; runtime register and DVFS tests validate offsets and masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp3xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp3xxx_data.c

### Purpose
`vp3xxx_data.c` supplies OMAP3 Voltage Processor register metadata, MPU/core VP instances, and min/max voltage limits.

### Important APIs, Types, And Functions
It defines `omap3_vp_ops`, `omap3_vp_common`, `omap3_vp_mpu`, `omap3_vp_core`, `omap3_mpu_vp_data`, and `omap3_core_vp_data`.

### Control Flow
There is no active flow. Generic VP code consumes these structures during OMAP3 voltage-domain late init.

### State, Persistence, And Dependencies
VP instances persist and hold runtime `enabled` state. The file depends on OMAP3 PRM register offsets, bitfield definitions, and `omap_prm_vp_check_txdone`/`omap_prm_vp_clear_txdone` callbacks.

### Integration Points
OMAP3 voltage-domain data attaches these objects to MPU and core domains.

### Risks
Voltage limits must align with silicon and PMIC capabilities; generic VP init clamps against PMIC limits but bad values still affect safe operating range.

### Test Signals
OMAP3 DVFS should program VP1 and VP2 registers with expected bounds and transaction-done callbacks should work for both IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp3xxx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp44xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp44xx_data.c

### Purpose
`vp44xx_data.c` defines OMAP4 Voltage Processor metadata for MPU, IVA, and CORE voltage domains.

### Important APIs, Types, And Functions
It defines `omap4_vp_ops`, `omap4_vp_common`, `omap4_vp_mpu`, `omap4_vp_iva`, `omap4_vp_core`, and `omap4_{mpu,iva,core}_vp_data`.

### Control Flow
The file is declarative. Generic VP code reads these objects when initializing and scaling OMAP4-class voltage domains.

### State, Persistence, And Dependencies
VP instances persist and track enabled state. Dependencies include OMAP4 PRM offsets, VP bit masks, and common PRM VP transaction-done helpers.

### Integration Points
OMAP4 voltage-domain data uses these directly, and OMAP5 voltage-domain data reuses them for compatible domains.

### Risks
Reusing these objects for OMAP5 means register compatibility assumptions must hold. Min/max limits are static OMAP4 values and may need SoC-specific review for derivatives.

### Test Signals
OMAP443x/446x DVFS should exercise all three VP instances and validate transaction-done status for MPU, IVA, and CORE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp44xx_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.c

### Purpose
`wd_timer.c` provides OMAP2+ watchdog timer reset and disable helpers for hwmod initialization.

### Important APIs, Types, And Functions
Public APIs are `omap2_wd_timer_disable(struct omap_hwmod *oh)` and `omap2_wd_timer_reset(struct omap_hwmod *oh)`. Important watchdog offsets are `OMAP_WDT_WPS` and `OMAP_WDT_SPR`.

### Control Flow
Disable obtains the watchdog runtime virtual base and writes the required `0xAAAA` then `0x5555` sequence to SPR, polling WPS after each write. Reset performs an OCP softreset, polls SYSS reset-done with `omap_test_timeout()`, honors any reset delay, logs the reset result, and disables the watchdog unless reset timed out.

### State, Persistence, And Dependencies
Persistent effects are watchdog register state and hwmod reset state. The file depends on OMAP hwmod accessors, watchdog platform semantics, and PRM/SYSS reset bits.

### Integration Points
OMAP hwmod/device init can call these helpers to avoid an enabled watchdog rebooting the system after reset.

### Risks
Disable polling has no timeout, so a stuck WPS bit can hang. Reset behavior differs between OMAP2/3 and OMAP4, and the helper is written around the rearm-after-softreset behavior.

### Test Signals
Boot should reset and disable watchdog without spontaneous reboot. Fault-injection or hardware tests should verify timeout logging for failed softreset and WPS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.h

### Purpose
`wd_timer.h` declares OMAP2+ watchdog timer reset and disable helpers.

### Important APIs, Types, And Functions
It declares `omap2_wd_timer_disable()` and `omap2_wd_timer_reset()`, both taking `struct omap_hwmod *`.

### Control Flow
There is no runtime flow. The header provides prototypes for hwmod and platform init code.

### State, Persistence, And Dependencies
The header has no state and depends on `omap_hwmod.h`.

### Integration Points
It bridges watchdog-specific code with OMAP hwmod initialization paths.

### Risks
Callers must pass a valid watchdog hwmod; implementation returns errors for missing base data.

### Test Signals
Build configurations using OMAP watchdog hwmods should compile and boot without undefined symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/wd_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Kconfig

### Purpose
`Kconfig` exposes Marvell Orion5x architecture and board support options.

### Important APIs, Types, And Functions
Key symbols are `ARCH_ORION5X`, `ARCH_ORION5X_DT`, and board options such as `MACH_KUROBOX_PRO`, `MACH_DNS323`, `MACH_TS209`, `MACH_TS409`, `MACH_D2NET_DT`, `MACH_NET2BIG`, `MACH_MSS2_DT`, and `MACH_RD88F5182_DT`.

### Control Flow
Configuration choices select shared platform dependencies such as Feroceon CPU support, GPIOLIB, MVEBU MBUS, PCI quirks, legacy Orion platform support, DT clock/IRQ/timer support, and optional I2C board-info.

### State, Persistence, And Dependencies
Kconfig has no runtime state; it controls build-time inclusion of platform and board files. Dependencies distinguish ATAGS boards from flattened device-tree boards.

### Integration Points
The Makefile and machine descriptors are gated by these symbols.

### Risks
Wrong dependencies can build board code without required subsystems or exclude needed legacy ATAGS paths. Mixed DT/ATAGS support requires consistent board selections.

### Test Signals
Defconfig and allmodconfig builds should cover both `ARCH_ORION5X_DT` and representative ATAGS board options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Makefile

### Purpose
`Makefile` selects Orion5x common, PCI, IRQ, MPP, and board setup objects for the kernel build.

### Important APIs, Types, And Functions
It always builds `common.o`, `pci.o`, `irq.o`, and `mpp.o`, and conditionally builds board setup objects based on `CONFIG_MACH_*` and `CONFIG_ARCH_ORION5X_DT`.

### Control Flow
There is no runtime flow. Build inclusion follows Kconfig symbols; TS209/TS409 also include shared `tsx09-common.o`.

### State, Persistence, And Dependencies
The file has no runtime state. It adds the legacy `plat-orion/include` path through `ccflags-y`.

### Integration Points
It connects Kconfig board selections to actual compiled machine and DT support.

### Risks
Selecting the same setup object for multiple machines, such as Kurobox Pro and Linkstation Pro, requires preprocessor guards inside the C file to avoid unintended machine descriptors.

### Test Signals
Build matrix should include each board config to verify expected object inclusion and no missing shared objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-d2net.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-d2net.c

### Purpose
`board-d2net.c` adds DT-era board-specific setup for LaCie d2 Network and Big Disk Network LEDs.

### Important APIs, Types, And Functions
The exported init hook is `d2net_init()`. Internal pieces are `d2net_gpio_leds_init()`, GPIO LED platform data, and a GPIO lookup table mapping blue and red front LEDs.

### Control Flow
Init configures a CPLD blink-control GPIO so the blue LED can blink with SATA activity, adds lookup entries for `leds-gpio`, registers the LED platform device, and logs that flash writes are unsupported.

### State, Persistence, And Dependencies
Persistent state is GPIO direction/value and the registered `leds-gpio` platform device. Dependencies include Orion GPIO, gpiod lookup tables, and the generic LED GPIO driver.

### Integration Points
`board-dt.c` calls `d2net_init()` when the DT compatible string is `lacie,d2-network`.

### Risks
GPIO request failures only log and continue, potentially leaving LEDs in bootloader state. The setup assumes specific CPLD wiring outside the DT description.

### Test Signals
Booting a d2 Network DT should register two front LEDs and show expected SATA blink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-d2net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-dt.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-dt.c

### Purpose
`board-dt.c` provides the flattened device-tree machine descriptor and common DT initialization path for Orion5x systems.

### Important APIs, Types, And Functions
Important objects/functions are `orion5x_auxdata_lookup`, `orion5x_dt_init()`, `orion5x_dt_compat`, and `DT_MACHINE_START(ORION5X_DT, ...)`.

### Control Flow
DT init identifies the SoC and TCLK, initializes MBUS from DT, sets up PCI/PCIe windows, applies the 88F5281 D0 WFI workaround, runs optional board hooks for MSS2 and d2 Network compatibles, and populates DT platform devices with auxdata names for legacy drivers.

### State, Persistence, And Dependencies
State persists in MBUS windows, CPU idle polling mode, and populated platform devices. Dependencies include OF platform population, MVEBU MBUS, Orion mapping/restart functions, and optional board-specific hooks.

### Integration Points
This is the DT machine entry for `"marvell,orion5x"` and calls common Orion setup while avoiding ATAGS board descriptors.

### Risks
`BUG_ON(mvebu_mbus_dt_init(false))` turns MBUS init failure into a hard boot stop. Auxdata keeps legacy driver naming assumptions alive and must match physical addresses.

### Test Signals
DT boot should identify the SoC, populate SPI/I2C/watchdog/SATA/crypto devices, and execute optional compatible-specific board hooks only on matching boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-mss2.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-mss2.c

### Purpose
`board-mss2.c` supplies Maxtor Shared Storage II board-specific PCI and power-off handling.

### Important APIs, Types, And Functions
Key functions are `mss2_pci_map_irq()`, `mss2_pci_init()`, `mss2_power_off()`, and `mss2_init()`. It defines an `hw_pci` descriptor using common Orion PCI setup and scan functions.

### Control Flow
PCI init runs as a subsystem initcall for the ATAGS MSS2 machine. DT board init can call `mss2_init()`, which registers a power-off callback. The callback enables reset output and asserts CPU soft reset, relying on U-Boot to enter an idle mode on next boot.

### State, Persistence, And Dependencies
Persistent effects are PCI host registration and reset-control register writes during power-off. Dependencies include common Orion PCI, bridge reset registers, and platform power-off registration.

### Integration Points
`board-dt.c` invokes `mss2_init()` for `maxtor,shared-storage-2`; ATAGS code uses `machine_is_mss2()` for PCI init.

### Risks
Power-off is implemented as a reboot into bootloader-managed idle state, so it depends on userspace/U-Boot environment preparation. PCI IRQ mapping adds no board-specific fallback beyond common Orion.

### Test Signals
MSS2 boot should initialize PCI only on the correct machine, and shutdown should reset into the expected U-Boot idle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-mss2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-rd88f5182.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-rd88f5182.c

### Purpose
`board-rd88f5182.c` provides PCI IRQ setup for the Marvell RD-88F5182 NAS reference design under DT.

### Important APIs, Types, And Functions
Key functions are `rd88f5182_pci_preinit()`, `rd88f5182_pci_map_irq()`, and `rd88f5182_pci_init()`, plus the `rd88f5182_pci` `hw_pci` descriptor.

### Control Flow
Subsystem PCI init checks the DT compatible string. Preinit requests GPIOs for PCI IntA/IntB and configures them as level-low IRQ inputs. IRQ mapping uses common Orion PCIe mapping first, then maps slot 0 pin A/B to the configured GPIO IRQs.

### State, Persistence, And Dependencies
State persists in GPIO requests, IRQ trigger type, and PCI host registration. Dependencies include OF machine matching, common Orion PCI setup, and GPIO-to-IRQ mapping.

### Integration Points
This file complements `board-dt.c` for the `marvell,rd-88f5182-nas` compatible.

### Risks
GPIO setup errors only log, but IRQ mapping may still return GPIO IRQ numbers. Slot offset assumptions are board-specific.

### Test Signals
Boot on RD-88F5182 should initialize PCI and route slot 0 interrupts through GPIO 7 and 6 as level-low interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-rd88f5182.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/bridge-regs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/bridge-regs.h

### Purpose
`bridge-regs.h` defines Orion5x CPU bridge register virtual and physical addresses used for reset, interrupts, power management, and timers.

### Important APIs, Types, And Functions
Key macros include `CPU_CONF`, `CPU_CTRL`, `RSTOUTn_MASK`, `CPU_SOFT_RESET`, `BRIDGE_CAUSE`, `POWER_MNG_CTRL_REG`, `MAIN_IRQ_CAUSE`, `MAIN_IRQ_MASK`, and timer base constants.

### Control Flow
There is no executable flow. The macros translate from `ORION5X_BRIDGE_VIRT_BASE` or physical base to register addresses.

### State, Persistence, And Dependencies
The header has no state and depends on `orion5x.h` base-address definitions.

### Integration Points
Common init, IRQ handling, watchdog resources, restart, and board power-off/reset code use these registers.

### Risks
Register address mistakes affect early boot, interrupt delivery, watchdog registration, and restart behavior. `BRIDGE_INT_TIMER1_CLR` is a mask value rather than an address, which can be easy to misuse.

### Test Signals
Boot-time interrupt, timer, watchdog, and restart tests indirectly validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/bridge-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c

### Purpose
`common.c` implements shared Orion5x SoC initialization: IO mapping, fixed TCLK registration, platform-device setup, MBUS windows, timer init, SoC identification, restart, and memory-tag fixups.

### Important APIs, Types, And Functions
Public APIs include `orion5x_map_io()`, `clk_init()`, peripheral init helpers, `orion5x_init_early()`, `orion5x_setup_wins()`, `orion5x_timer_init()`, `orion5x_id()`, `orion5x_init()`, `orion5x_restart()`, and `tag_fixup_mem32()`.

### Control Flow
Early init sets timer base and initializes MBUS based on detected device ID. Main init prints SoC ID/TCLK, programs PCIe/PCI windows, registers the clock root, applies the 5281 D0 WFI workaround, conditionally registers crypto with SRAM MBUS window, and registers the watchdog. Timer init derives TCLK from device ID/reset sample and calls `orion_time_init()`.

### State, Persistence, And Dependencies
Persistent state includes static IO mappings, global `orion5x_tclk`, registered clocks/devices, MBUS address windows, and optional CPU idle polling mode. Dependencies include plat-orion helpers, MVEBU MBUS, platform device APIs, bridge registers, and PCIe ID access.

### Integration Points
Every ATAGS board file and DT machine path calls these helpers for shared SoC bring-up.

### Risks
MBUS and IO window programming is foundational; mistakes break PCI, device bus, crypto SRAM, and peripherals. Restart assumes reset output and CPU soft reset registers behave. Memory tag fixup mutates bootloader ATAGs and must avoid clearing valid RAM.

### Test Signals
Board boot should show correct Orion ID/TCLK, working serial/timer/IRQ, registered watchdog, correct crypto availability, and successful soft restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.h

### Purpose
`common.h` declares shared Orion5x init APIs, MBUS target/attribute constants, PCI helpers, optional DT board hooks, and simple register bit helpers.

### Important APIs, Types, And Functions
It declares SoC init functions, peripheral init functions, PCI setup/scan/map functions, `orion5x_restart()`, `tag_fixup_mem32()`, and macros `orion5x_setbits()`/`orion5x_clrbits()`.

### Control Flow
There is no runtime flow. Conditional inline stubs make optional DT board hooks no-ops when the corresponding board config is disabled.

### State, Persistence, And Dependencies
The header has no state and depends on platform data forward declarations, reboot types, and PCI type declarations.

### Integration Points
All Orion5x board files include this as their shared interface to common SoC code.

### Risks
The register bit helpers are explicitly not preempt-safe; callers must provide locking where concurrent access is possible. MBUS constants are shared by board and common code and must match hardware decode attributes.

### Test Signals
Builds across DT and non-DT board options validate optional hook stubs and declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/dns323-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/dns323-setup.c

### Purpose
`dns323-setup.c` initializes the D-Link DNS-323 NAS across hardware revisions A1, B1, and C1.

### Important APIs, Types, And Functions
Important functions include `dns323_init()`, `dns323_identify_rev()`, `dns323_read_mac_addr()`, revision-specific power-off callbacks, `dns323_pci_init()`, and `dns323c_phy_fixup()`. It defines NOR partitions, Ethernet/SATA data, LED/button platform devices, I2C devices, and MPP mode arrays.

### Control Flow
PCI init only runs for revision A1. Main init calls common Orion setup, identifies revision from SoC ID and PHY ID, applies revision-specific MPP modes, maps/registers NOR flash, installs revision-specific LED/button/I2C data, reads MAC from flash, initializes USB/Ethernet/I2C/UART and SATA for B1/C1, configures power-off GPIOs, and registers a PHY LED fixup for C1 when PHYLIB is built in.

### State, Persistence, And Dependencies
State persists in `system_rev`, platform devices, GPIO directions, flash resource mappings, Ethernet MAC platform data, and registered power-off callbacks. Dependencies include Orion GPIO/MPP, physmap flash, mv643xx Ethernet, SATA, I2C board info, PHYLIB, and flash-stored configuration.

### Integration Points
The `MACHINE_START(DNS323, ...)` descriptor wires this setup into legacy ATAGS boot. Common Orion PCI, IRQ, timer, restart, and memory fixup hooks are used.

### Risks
Revision detection pokes Ethernet SMI registers directly and defaults to B1 on timeouts. MAC parsing assumes a string at a fixed flash offset. Several GPIO setup failures log but do not stop boot. Bootloader mach-type quirks are noted.

### Test Signals
Each revision should boot with correct LED polarity, buttons, I2C devices, MAC address, SATA availability, and power-off behavior; C1 should apply the Marvell PHY LED fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/dns323-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irq.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irq.c

### Purpose
`irq.c` initializes the legacy Orion5x interrupt controller and GPIO interrupt ranges.

### Important APIs, Types, And Functions
The public entry is `orion5x_init_irq()`. The IRQ handler is `orion5x_legacy_handle_irq()`, and `gpio0_irqs[]` maps four GPIO cause groups to main IRQ lines.

### Control Flow
IRQ init initializes the main interrupt controller at IRQ base 1, installs the custom IRQ handler, and registers GPIOs 0-31 with their parent IRQ groups. The handler reads cause and mask registers, finds the highest pending bit with `__fls()`, converts it to Linux IRQ numbering, and calls `handle_IRQ()`.

### State, Persistence, And Dependencies
State persists in the kernel IRQ handler and GPIO IRQ registration. Dependencies include bridge interrupt registers, plat-orion IRQ helpers, and Orion GPIO support.

### Integration Points
ATAGS machine descriptors call this during `.init_irq`; DT mode uses `ORION_IRQCHIP` instead of this legacy path.

### Risks
The handler handles one pending interrupt per entry and silently returns if none are masked pending. IRQ numbering starts at 1, so off-by-one errors are easy.

### Test Signals
Timer, UART, Ethernet, and GPIO interrupt activity on ATAGS boards should dispatch to the expected IRQ numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irqs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irqs.h

### Purpose
`irqs.h` assigns Linux IRQ numbers for Orion5x main interrupt sources and GPIO interrupts.

### Important APIs, Types, And Functions
It defines constants for bridge, UART, I2C, GPIO groups, PCIe/PCI, USB, Ethernet, IDMA, CESA, SATA, XOR, `IRQ_ORION5X_GPIO_START`, `NR_GPIO_IRQS`, and `ORION5X_NR_IRQS`.

### Control Flow
There is no executable flow; this is a numbering contract.

### State, Persistence, And Dependencies
The header has no state. Values are consumed by common init, IRQ setup, peripheral registration, and board files.

### Integration Points
Machine descriptors use `ORION5X_NR_IRQS`, and platform devices use individual IRQ constants.

### Risks
IRQ numbers are one-based for main controller lines; changing them would break platform data and drivers.

### Test Signals
Boot and peripheral interrupt tests validate that each platform device receives the right IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/kurobox_pro-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/kurobox_pro-setup.c

### Purpose
`kurobox_pro-setup.c` initializes Buffalo/Revogear Kurobox Pro and Buffalo Linkstation Pro/Live Orion5x boards.

### Important APIs, Types, And Functions
Important functions are `kurobox_pro_init()`, `kurobox_pro_pci_init()`, `kurobox_pro_power_off()`, and UART microcontroller helpers `kurobox_pro_miconread/write/send()`. The file defines NOR/NAND flash resources, Ethernet/I2C/SATA data, MPP modes, and two machine descriptors.

### Control Flow
PCI init disables legacy PCI for Kurobox Pro, then registers common PCIe/PCI host setup. Board init calls common Orion init, configures MPP, initializes USB, Ethernet, I2C, SATA, UARTs, XOR, maps/registers NOR and optionally NAND, registers RTC board info, and registers a UART1 microcontroller power-off callback.

### State, Persistence, And Dependencies
State persists in platform devices, MBUS device-bus windows, I2C RTC registration, UART1 configuration during power-off, and registered power-off callback. Dependencies include physmap flash, Orion NAND, mv643xx Ethernet, SATA, I2C, serial registers, and common Orion setup.

### Integration Points
`MACHINE_START()` entries wire the same init function to Kurobox Pro and Linkstation Pro/Live when their configs are enabled.

### Risks
Power-off hijacks UART1 and assumes a specific microcontroller ACK/checksum protocol. PCI is explicitly disabled for Kurobox Pro even though the common descriptor still has two controllers. NAND registration only occurs on the Kurobox machine check.

### Test Signals
Boot should expose NOR, optional NAND, Ethernet, SATA, USB, RTC, and UARTs. Shutdown should send microcontroller commands and power off reliably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/kurobox_pro-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.c

### Purpose
`mpp.c` configures Orion5x multi-purpose pins using the generic Orion MPP helper and variant capability masks.

### Important APIs, Types, And Functions
The exported API is `orion5x_mpp_conf(unsigned int *mpp_list)`. Internal helper `orion5x_variant()` maps detected SoC IDs to `MPP_F5181_MASK`, `MPP_F5182_MASK`, or `MPP_F5281_MASK`.

### Control Flow
MPP configuration reads the PCIe device ID, chooses a variant mask, and calls `orion_mpp_conf()` with the board-supplied MPP list, `MPP_MAX`, and the device-bus register base.

### State, Persistence, And Dependencies
Persistent effects are pin mux register values. Dependencies include PCIe ID access, `mpp.h` encodings, plat-orion MPP programming, and mapped device-bus registers.

### Integration Points
ATAGS board files call this after common init and before registering GPIO/peripheral devices.

### Risks
Unknown variants log an error and pass mask zero, likely preventing valid mux programming. Board MPP lists must only request functions available on the detected SoC.

### Test Signals
Board boot should show working GPIOs, UART pins, PCI pins, SATA LEDs, and NAND pins according to each MPP table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.h

### Purpose
`mpp.h` encodes Orion5x multi-purpose pin function definitions and SoC availability masks.

### Important APIs, Types, And Functions
The `MPP()` macro encodes pin number, select value, input/output capability, and availability on F5181, F5182, and F5281 variants. It defines function constants for MPP0 through MPP19 and declares `orion5x_mpp_conf()`.

### Control Flow
There is no executable flow. Board files build null-terminated MPP arrays from these constants.

### State, Persistence, And Dependencies
The header has no state. Its encodings are interpreted by plat-orion MPP code.

### Integration Points
Every Orion5x board setup file uses these constants to describe pin muxing.

### Risks
Some select values differ by SoC variant, and availability bits protect only if the variant mask is correct. The file covers only MPP0-19; boards using higher GPIOs must mark them valid separately.

### Test Signals
Board-level validation should confirm all muxed pins perform their intended GPIO/peripheral role.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mv2120-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mv2120-setup.c

### Purpose
`mv2120-setup.c` initializes HP Media Vault mv2120/mv5100 board devices.

### Important APIs, Types, And Functions
Key functions are `mv2120_init()` and `mv2120_power_off()`. The file defines NOR flash partition/resource data, Ethernet/SATA platform data, GPIO buttons, RTC I2C info, GPIO LEDs, MPP modes, and the `MACHINE_START(MV2120, ...)` descriptor.

### Control Flow
Init calls common Orion setup, configures MPP, initializes USB, Ethernet, I2C, SATA, UART, XOR, maps/registers NOR flash, registers buttons, configures RTC IRQ, registers I2C RTC, registers LEDs, requests the power-off GPIO, and registers the power-off callback.

### State, Persistence, And Dependencies
Persistent state includes registered platform devices, GPIO LED/button/power-off configuration, I2C RTC info, and MBUS flash mapping. Dependencies include physmap flash, mv643xx Ethernet, SATA, GPIO keys/LEDs, and Orion common init.

### Integration Points
The machine descriptor wires the setup into legacy ATAGS boot and uses common Orion IRQ/timer/restart/fixup hooks.

### Risks
Power-off drives GPIO 19 low after initializing it high; wrong polarity would prevent shutdown. RTC IRQ setup failure only warns through missing IRQ behavior.

### Test Signals
Boot should expose NOR flash, buttons, LEDs, RTC IRQ, Ethernet, SATA, USB, and reliable GPIO-based power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mv2120-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/net2big-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/net2big-setup.c

### Purpose
`net2big-setup.c` initializes the LaCie 2Big Network NAS.

### Important APIs, Types, And Functions
Important functions are `net2big_init()`, `net2big_sata_power_init()`, `net2big_gpio_leds_init()`, and `net2big_power_off()`. It defines NOR flash, Ethernet, I2C, SATA, GPIO LED/key data, MPP modes, and machine descriptor data.

### Control Flow
Init calls common Orion setup, configures MPP, initializes USB/Ethernet/I2C/UART/XOR, powers up SATA disks through CPLD GPIO sequencing, initializes SATA, maps/registers NOR flash, registers buttons and LEDs, registers I2C RTC/EEPROM devices, marks high GPIOs valid, configures power-off GPIO, and logs flash-write limitations.

### State, Persistence, And Dependencies
State persists in GPIO directions/values, registered platform devices, I2C board info, MBUS windows, and power-off callback. Dependencies include Orion GPIO, physmap flash, mv643xx Ethernet, SATA, I2C boardinfo, GPIO keys/LEDs, and CPLD-specific wiring.

### Integration Points
The `MACHINE_START(NET2BIG, ...)` descriptor uses this setup under legacy ATAGS boot with common Orion hooks.

### Risks
SATA power sequencing depends on 300 ms CPLD timing and high-numbered GPIO validity. Several LED/SATA GPIO setup failures log and continue. NOR partition is marked read-only pending write support validation.

### Test Signals
Boot should power both disks, register SATA, show correct front/SATA LEDs and rocker-switch inputs, expose RTC/EEPROM, and power off via GPIO 24.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/net2big-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/orion5x.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/orion5x.h

### Purpose
`orion5x.h` defines Orion5x physical/virtual address maps, peripheral register bases, device-bus registers, and supported device/revision IDs.

### Important APIs, Types, And Functions
It defines bases and sizes for on-chip registers, PCIe/PCI IO and memory windows, crypto SRAM, device bus, bridge, PCI, PCIe, USB, XOR, Ethernet, SATA, crypto, GPIO, SPI, I2C, UART, MPP registers, and device IDs/revisions for MV88F5181, MV88F5182, MV88F5281, and MV88F6183.

### Control Flow
There is no executable flow. The macros are address and identity constants.

### State, Persistence, And Dependencies
The header has no state and includes `irqs.h` for platform IRQ definitions.

### Integration Points
Common init, board files, PCI, IRQ, MPP, watchdog, and peripheral registration all use these constants.

### Risks
Address-map constants underpin static mappings and MBUS windows; mistakes can break all device access. Device/revision IDs drive clock and erratum decisions.

### Test Signals
Successful boot with working serial, timer, PCI, Ethernet, USB, SATA, and restart validates the map indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/orion5x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/pci.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/pci.c

### Purpose
`pci.c` implements Orion5x PCIe and legacy PCI host-controller setup, config-space access, resource window setup, IRQ fallback mapping, and root-complex fixups.

### Important APIs, Types, And Functions
Public APIs are `orion5x_pcie_id()`, `orion5x_pci_disable()`, `orion5x_pci_set_cardbus_mode()`, `orion5x_pci_sys_setup()`, `orion5x_pci_sys_scan_bus()`, and `orion5x_pci_map_irq()`. Important internal pieces include `pcie_ops`, `pci_ops`, config access locks, `pcie_setup()`, `pci_setup()`, `orion5x_setup_pci_wins()`, and `rc_pci_fixup()`.

### Control Flow
PCIe setup initializes the controller, applies the Orion-1/NAS config-read workaround when needed, remaps IO space, and adds memory resources. Legacy PCI setup programs DDR decode windows, enables master/slave, forces host ordering, remaps IO space, and adds memory resources. Scan setup assigns bridge ops for controller 0 as PCIe and controller 1 as legacy PCI unless disabled.

### State, Persistence, And Dependencies
Persistent state includes PCI/PCIe bus numbering, resource windows, MBUS workaround window, host bridge resources, root-complex class fixups, and `orion5x_pci_disabled`/CardBus flags. Dependencies include plat-orion PCIe helpers, MVEBU MBUS DRAM info, Linux PCI core, and common register bit helpers.

### Integration Points
Board files provide `hw_pci` descriptors that call these setup/scan helpers and add board-specific IRQ mapping.

### Risks
Config cycles require spinlock atomicity. The workaround path only supports non-extended config space. Resource allocation failures panic. Bus-number logic and CardBus filtering are hardware-specific and easy to regress.

### Test Signals
PCIe endpoint enumeration, legacy PCI card enumeration, CardBus mode, Orion-1/NAS workaround boards, and root-complex resource/class fixups should all be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/terastation_pro2-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/terastation_pro2-setup.c

### Purpose
`terastation_pro2-setup.c` initializes Buffalo Terastation Pro II/Live boards.

### Important APIs, Types, And Functions
Important functions are `tsp2_init()`, `tsp2_pci_preinit()`, `tsp2_pci_map_irq()`, `tsp2_pci_init()`, `tsp2_power_off()`, and UART microcontroller helpers. The file defines NOR flash, PCI IRQ GPIO, Ethernet data, RTC I2C data, MPP modes, and a machine descriptor.

### Control Flow
Subsystem PCI init configures the PCI IRQ GPIO as level-low and registers common Orion PCI host setup. Board init calls common Orion setup, configures MPP, maps/registers NOR flash, initializes USB/Ethernet/I2C/UARTs, configures RTC IRQ, registers I2C RTC, and installs UART1 microcontroller power-off.

### State, Persistence, And Dependencies
Persistent effects include GPIO IRQ setup, PCI host registration, platform flash registration, I2C RTC info, UART1 state during shutdown, and power-off callback. Dependencies include physmap flash, mv643xx Ethernet, I2C, serial register access, and common Orion setup.

### Integration Points
The ATAGS `MACHINE_START(TERASTATION_PRO2, ...)` descriptor wires this board to common Orion map/IRQ/timer/restart/fixup hooks.

### Risks
Power-off depends on an ACK/checksum protocol over UART1 and has limited retry handling. PCI IRQ mapping assumes a single slot at offset 7 with GPIO 11. RTC IRQ failure only warns.

### Test Signals
Boot should enumerate PCI SATA controller, flash, Ethernet, USB, UARTs, and RTC, and shutdown should power off through the microcontroller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/terastation_pro2-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts209-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts209-setup.c

### Purpose
`ts209-setup.c` initializes QNAP TS-109/TS-209 Orion5x boards.

### Important APIs, Types, And Functions
Key functions are `qnap_ts209_init()`, `qnap_ts209_pci_preinit()`, `qnap_ts209_pci_map_irq()`, and `qnap_ts209_pci_init()`. It defines NOR partitions, PCI IRQ GPIOs, RTC data, GPIO keys, SATA data, MPP modes, and a machine descriptor.

### Control Flow
PCI init configures two PCI interrupt GPIOs and registers common Orion PCI setup. Board init calls common Orion setup, configures MPP, maps/registers NOR flash, initializes USB, reads the MAC address from the NAS Config partition through shared TSx09 code, initializes Ethernet/I2C/SATA/UARTs/XOR, registers keys, configures RTC IRQ, registers I2C RTC, and installs shared QNAP power-off.

### State, Persistence, And Dependencies
State persists in flash platform data, PCI IRQ GPIOs, Ethernet MAC platform data, buttons, RTC IRQ, SATA platform data, and power-off callback. Dependencies include common Orion PCI/init, `tsx09-common`, physmap flash, SATA, I2C, and GPIO keys.

### Integration Points
The ATAGS machine descriptor uses common Orion hooks and the shared QNAP TSx09 helper for MAC and power-off.

### Risks
Flash partition order intentionally differs from physical order for firmware compatibility. PCI IRQ slot offsets are board-specific. Power button is handled by the PIC microcontroller rather than GPIO keys.

### Test Signals
Boot should expose correct MTD partitions, PCI devices, SATA ports, Ethernet MAC, USB copy/reset buttons, RTC IRQ, and shared QNAP power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts209-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts409-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts409-setup.c

### Purpose
`ts409-setup.c` initializes QNAP TS-409 Orion5x boards.

### Important APIs, Types, And Functions
Key functions are `qnap_ts409_init()`, `qnap_ts409_pci_map_irq()`, and `qnap_ts409_pci_init()`. It defines NOR partition/resource data, RTC info, SATA status LEDs, GPIO keys, MPP modes, and a machine descriptor.

### Control Flow
PCI init registers common Orion PCIe/PCI host setup while board-specific mapping only accepts common PCIe IRQs because legacy PCI is not used. Board init calls common Orion setup, configures MPP, maps/registers NOR flash, initializes USB, reads MAC from NAS Config through shared TSx09 code, initializes Ethernet/I2C/UARTs, registers keys, configures RTC IRQ, registers I2C RTC, registers GPIO LEDs, and installs shared QNAP power-off.

### State, Persistence, And Dependencies
State persists in platform flash/LED/key devices, Ethernet MAC data, RTC IRQ, and power-off callback. Dependencies include common Orion setup, `tsx09-common`, physmap flash, I2C, GPIO LEDs/keys, and PCI core.

### Integration Points
The ATAGS `MACHINE_START(TS409, ...)` descriptor wires this setup into legacy boot and common Orion hooks.

### Risks
PCI legacy bus is unused, so incorrect fallback IRQ mapping would hide problems. Flash partition order is compatibility-sensitive. Power button is outside GPIO key handling.

### Test Signals
Boot should register TS-409 partitions, four SATA status LEDs, reset/copy buttons, Ethernet MAC, RTC IRQ, PCIe SATA controller, and shared power-off behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts409-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-fpga.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-fpga.h

### Purpose
`ts78xx-fpga.h` defines FPGA ID values and capability structures for Technologic Systems TS-78xx FPGA-attached devices.

### Important APIs, Types, And Functions
It defines `TS7800_FPGA_MAGIC`, `FPGAID()`, enum `fpga_ids`, `struct fpga_device`, `struct fpga_devices`, and `struct ts78xx_fpga_data`.

### Control Flow
There is no executable flow. The header provides data contracts for TS-78xx setup code to identify FPGA revisions and supported devices.

### State, Persistence, And Dependencies
The header has no state. Runtime users store FPGA ID, state, and support flags for RTC, NAND, and RNG devices in `ts78xx_fpga_data`.

### Integration Points
TS-78xx board setup and FPGA probing code include this header to decide which FPGA-backed platform devices are present and initialized.

### Risks
FPGA IDs are externally assigned and the comment warns not to invent or borrow IDs. Misidentifying support flags could register unavailable devices.

### Test Signals
TS-78xx boot should read a known FPGA ID and register only the supported RTC, NAND, and RNG devices for that revision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-fpga.h -->
