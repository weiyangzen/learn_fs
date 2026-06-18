# subset-b-005051 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1050.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1050.c

## Purpose
Registers the NXP i.MXRT1050 IOMUXC pin controller with the shared Freescale/NXP i.MX pinctrl core. The file is a SoC description: it names every usable RT1050 pad, exposes those pads to the generic pinctrl subsystem, and binds the description to the `fsl,imxrt1050-iomuxc` device-tree compatible.

## Important APIs, Types, and Functions
The main data is `enum imxrt1050_pads`, `imxrt1050_pinctrl_pads[]`, `imxrt1050_pinctrl_info`, and `imxrt1050_pinctrl_of_match[]`. `IMX_PINCTRL_PIN()` converts enum IDs into `struct pinctrl_pin_desc` entries. `struct imx_pinctrl_soc_info` supplies `.pins`, `.npins`, and `.gpr_compatible = "fsl,imxrt1050-iomuxc-gpr"`. `imxrt1050_pinctrl_probe()` delegates to `imx_pinctrl_probe()`, and `arch_initcall(imxrt1050_pinctrl_init)` registers the platform driver early.

## Control Flow
At boot, the arch initcall registers `imxrt1050_pinctrl_driver`. OF platform matching selects the driver for `fsl,imxrt1050-iomuxc`; probe passes the static SoC info into the common i.MX pinctrl driver. Runtime mux and pad-control operations are handled by `pinctrl-imx.c` using register offsets and pin config cells from device tree, not by logic in this file.

## State and Persistence Behavior
The file maintains no mutable runtime state. Its static pad table is persistent kernel data and must remain aligned with the SoC binding and hardware pad numbering. Per-device state, mapped registers, pin groups, and selected mux/config state are owned by the common i.MX pinctrl core and hardware registers.

## Dependencies and Integration Points
Depends on platform-device, OF matching, `linux/pinctrl/pinctrl.h`, and `pinctrl-imx.h`. It integrates with device-tree pinctrl nodes, the IOMUXC GPR syscon compatible, and all RT1050 peripheral drivers that request pin states through the Linux pinctrl framework.

## Risks
The risk is table correctness. Missing reserve entries, reordered enum values, wrong names, or a mismatched `.gpr_compatible` can make device-tree pin IDs configure the wrong physical pad. Since all behavior is delegated, build regressions are most likely from API changes in `pinctrl-imx.h` or from binding drift.

## Test Signals
Useful signals include driver binding on an RT1050 DT, successful `imx_pinctrl_probe()`, expected pin names in pinctrl debugfs, peripheral pin states applying for EMC, ADC, B-bank, and SD pads, no invalid-pin errors from DT parsing, and suspend/resume or early boot paths that depend on arch-initcall pin setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1050.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1170.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1170.c

## Purpose
Provides the static pin descriptor table and platform-driver registration for the i.MXRT1170 IOMUXC. Like the RT1050 driver, it is a thin SoC descriptor layer over the common i.MX pinctrl implementation.

## Important APIs, Types, and Functions
`enum imxrt1170_pads` declares reserve pads plus EMC_B1/B2, AD, SD_B1/B2, and display-bank pads. `imxrt1170_pinctrl_pads[]` maps them to `struct pinctrl_pin_desc` entries. `imxrt1170_pinctrl_info` points the common core at the pin table and at `fsl,imxrt1170-iomuxc-gpr`. `imxrt1170_pinctrl_of_match[]`, `imxrt1170_pinctrl_probe()`, `imxrt1170_pinctrl_driver`, and `imxrt1170_pinctrl_init()` complete the OF platform-driver binding.

## Control Flow
`arch_initcall()` registers the driver during early platform initialization. When the OF core instantiates an IOMUXC platform device with `fsl,imxrt1170-iomuxc`, the probe path calls `imx_pinctrl_probe(pdev, &imxrt1170_pinctrl_info)`. All parsing of pin groups, mux values, config values, and register writes happens in the common i.MX code.

## State and Persistence Behavior
No dynamic state is stored here. The static SoC info and pin table persist for the life of the kernel. Hardware mux/config state is stored in IOMUXC registers and represented in common-core per-device structures after probe.

## Dependencies and Integration Points
Depends on the generic pinctrl framework, OF platform matching, and `pinctrl-imx.h`. It is consumed by RT1170 board device trees and peripheral drivers using named/default/sleep pinctrl states for memory, analog, SD/MMC, and display pins.

## Risks
The enum and pin descriptor array must match the binding include files and hardware reference manual. Any missing pad, reserve-count error, or bank-name mismatch can shift pin numbers and misconfigure unrelated hardware. The driver also assumes the common i.MX backend understands the RT1170 binding format and GPR syscon.

## Test Signals
Probe on RT1170 hardware or DT emulation, correct `/sys/kernel/debug/pinctrl` pin names, successful pinctrl state selection for SD, EMC, AD, and display pads, no OF pin-parse failures, and regression builds with `CONFIG_PINCTRL_IMXRT1170` or the enclosing Freescale pinctrl options are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imxrt1170.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.c

## Purpose
Implements the common pinctrl, pinmux, and pinconf backend for Freescale MXS-family controllers such as i.MX23/i.MX28. It parses MXS-specific device-tree child nodes, registers pin groups/functions dynamically, and writes MUXSEL, DRIVE, and PULL registers through MMIO.

## Important APIs, Types, and Functions
`struct mxs_pinctrl_data` keeps the device, `pinctrl_dev`, MMIO base, and SoC data. Pinctrl callbacks include `mxs_get_groups_count()`, `mxs_get_group_name()`, `mxs_get_group_pins()`, `mxs_dt_node_to_map()`, and `mxs_dt_free_map()`. Pinmux callbacks include `mxs_pinctrl_set_mux()`. Pinconf callbacks include `mxs_pinconf_group_get()` and `mxs_pinconf_group_set()`. DT parsing is handled by `mxs_pinctrl_probe_dt()` and `mxs_pinctrl_parse_group()`. The exported entry point is `mxs_pinctrl_probe()`.

## Control Flow
The SoC-specific driver calls `mxs_pinctrl_probe()` with `struct mxs_pinctrl_soc_data`. Probe maps the first MMIO resource with `of_iomap()`, fills `mxs_pinctrl_desc`, stores driver data, parses DT children into functions/groups, and registers the pinctrl device. During DT mapping, a node with `reg` becomes a mux group named `node.reg`; a node without `reg` is treated as pure pin configuration. Applying mux iterates group pins and writes two-bit mux selections. Applying config writes drive strength, voltage, and pull bits only when their presence bits are set.

## State and Persistence Behavior
Runtime state is per-platform-device `mxs_pinctrl_data` plus devm-allocated function/group arrays and per-group pin/mux arrays. The current group config is cached in `mxs_group.config` for debug/get operations, but authoritative state is in hardware registers. The MMIO mapping is manually released with `iounmap()` only on probe failure; successful lifetime is tied to the platform device.

## Dependencies and Integration Points
Depends on OF, `of_address`, MMIO accessors, Linux pinctrl/pinmux/pinconf APIs, and the MXS definitions in `pinctrl-mxs.h`. It integrates with DT properties `fsl,pinmux-ids`, `fsl,drive-strength`, `fsl,voltage`, `fsl,pull-up`, child `reg`, and sibling GPIO nodes compatible with `fsl,imx23-gpio` or `fsl,imx28-gpio`.

## Risks
Function grouping assumes same-name function nodes are contiguous; non-contiguous nodes emit a warning and only the first contiguous cluster is reliable. Config encodings are custom, not generic pinconf parameters. Register math relies on correct bank/pin extraction and SoC register offsets. `mxs_dt_node_to_map()` allocates group/config map data manually, so error paths and `dt_free_map` ownership must stay matched.

## Test Signals
DT probe with mux-only, config-only, and combined nodes; successful grouping of repeated function nodes; warnings for non-contiguous function nodes; register writes for MUXSEL/DRIVE/PULL; pinctrl debugfs showing group config; GPIO child nodes being skipped; invalid/missing `fsl,pinmux-ids` failures; and pin states for real MXS peripherals are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.h

## Purpose
Defines the shared data model and encoding helpers for the MXS pinctrl backend and its SoC-specific frontends. It documents how MXS device-tree mux IDs and packed config values are decoded and supplies the structures consumed by `pinctrl-mxs.c`.

## Important APIs, Types, and Functions
Important macros are register aliases `SET`, `CLR`, `TOG`; `MXS_PINCTRL_PIN()`; `PINID(bank, pin)`; mux decoders `MUXID_TO_PINID()` and `MUXID_TO_MUXSEL()`; pin decoders `PINID_TO_BANK()` and `PINID_TO_PIN()`; config presence bits `PULL_PRESENT`, `VOL_PRESENT`, `MA_PRESENT`; and config extractors `PIN_CONFIG_TO_PULL()`, `PIN_CONFIG_TO_VOL()`, and `PIN_CONFIG_TO_MA()`. Types include `struct mxs_function`, `struct mxs_group`, `struct mxs_regs`, and `struct mxs_pinctrl_soc_data`. The public probe hook is `mxs_pinctrl_probe()`.

## Control Flow
This header has no execution. SoC drivers provide `mxs_pinctrl_soc_data` with pin descriptors and register offsets, then call `mxs_pinctrl_probe()`. The common driver uses the macros to convert DT `fsl,pinmux-ids` into pin numbers and mux selections and to convert compact config words into hardware writes.

## State and Persistence Behavior
The structures describe persistent per-SoC tables and mutable per-group runtime fields. `mxs_group.config` caches the last group configuration; `pins` and `muxsel` arrays are populated during DT parsing. The header’s bitfield definitions are part of the binding contract and must remain stable.

## Dependencies and Integration Points
Includes platform-device and pinctrl descriptor types. It is shared between common MXS code and SoC-specific MXS pinctrl drivers. The bitfield layout integrates directly with device-tree properties and the MXS hardware register layout.

## Risks
Changing bit positions, presence-bit semantics, or bank/pin conversion macros breaks all MXS DT pinmux IDs. `u8 config` and `u8 *muxsel` assume small hardware fields; widening or adding features needs care. `struct mxs_pinctrl_soc_data` is passed by pointer and modified by probe, so callers should not treat all fields as immutable.

## Test Signals
Build coverage of MXS SoC drivers, DT pinmux IDs decoding to expected bank/pin/mux values, config presence bits applying only requested fields, and pinctrl debug output showing cached config are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-scu.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-scu.c

## Purpose
Provides the System Controller Unit IPC-backed pin configuration helpers used by i.MX SoCs where pad mux/config registers are controlled by firmware rather than direct MMIO. It lets the common i.MX pinctrl core get/set pad state and parse SCU-format pin entries.

## Important APIs, Types, and Functions
Defines SCU pad RPC function IDs, wake IRQ constants, packed RPC messages `imx_sc_msg_req_pad_set`, `imx_sc_msg_req_pad_get`, `imx_sc_msg_resp_pad_get`, and `imx_sc_msg_gpio_set_pad_wakeup`. Exported APIs are `imx_pinctrl_sc_ipc_init()`, `imx_pinconf_get_scu()`, `imx_pinconf_set_scu()`, and `imx_pinctrl_parse_pin_scu()`. A module-global `pinctrl_ipc_handle` stores the SCU IPC handle.

## Control Flow
Initialization enables SCU wake pad IRQ delivery and obtains the global IPC handle. `imx_pinconf_get_scu()` builds an `IMX_SC_RPC_SVC_PAD` / `IMX_SC_PAD_FUNC_GET` request and returns the firmware pad value. `imx_pinconf_set_scu()` treats one config word as a wakeup setting and sends `SET_WAKEUP`; otherwise it expects mux and config words, combines them with `BM_PAD_CTL_IFMUX_ENABLE`, `BM_PAD_CTL_GP_ENABLE`, and `BP_PAD_CTL_IFMUX`, then sends `IMX_SC_PAD_FUNC_SET`. `imx_pinctrl_parse_pin_scu()` consumes three big-endian DT cells: pin ID, mux mode, and config.

## State and Persistence Behavior
The only driver-local mutable state is `pinctrl_ipc_handle`. Actual pad state persists in SCU firmware/hardware. Parsed per-pin state is stored in the common i.MX `struct imx_pin` as SCU mux/config fields. Wakeup configuration may persist according to SCU policy and affects low-power behavior.

## Dependencies and Integration Points
Depends on `linux/firmware/imx/sci.h`, the i.MX pinctrl core, SCU RPC services, and i.MX pad-control bit definitions from `pinctrl-imx.h`. It is exported for SoC-specific i.MX SCU pinctrl drivers and integrates with DT pinctrl entries in SCU format.

## Risks
`pinctrl_ipc_handle` is global, so multiple SCU pinctrl instances assume one SCU endpoint. `num_configs == 1` is overloaded as wakeup configuration; callers must preserve that convention. Packed message sizes and function IDs must match firmware ABI. Failure to initialize IPC before get/set calls will break all pad operations.

## Test Signals
SCU handle acquisition, wake IRQ enablement, successful pad get/set RPCs, correct parsing of three-cell pin entries, wakeup-only configuration calls, mux/config calls with expected firmware values, SCU RPC error propagation, and suspend/resume wake events are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-vf610.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-vf610.c

## Purpose
Registers the Vybrid VF610 IOMUXC pinctrl driver using the common i.MX pinmux/pinconf core and provides the VF610-specific pad list and GPIO direction handling needed for shared mux/config registers.

## Important APIs, Types, and Functions
`enum vf610_pads` and `vf610_pinctrl_pads[]` describe PTA/PTB/PTC/PTD/PTE pads. `vf610_pmx_gpio_set_direction()` is the only custom behavioral callback; it updates bit 1 in the mux/config register through `ipctl->pin_regs[offset].mux_reg`. `vf610_pinctrl_info` sets `SHARE_MUX_CONF_REG`, `ZERO_OFFSET_VALID`, `.gpio_set_direction`, `.mux_mask = 0x700000`, and `.mux_shift = 20`. `vf610_pinctrl_probe()` delegates to `imx_pinctrl_probe()`.

## Control Flow
The arch initcall registers `vf610_pinctrl_driver`. When `fsl,vf610-iomuxc` probes, the common i.MX core receives the VF610 SoC info, maps registers, parses DT pin groups, and handles mux/config writes. GPIO direction requests are routed to `vf610_pmx_gpio_set_direction()`, which reads the pad register, clears bit 1 for input or sets it for output, and writes it back.

## State and Persistence Behavior
This file has no private dynamic state. The pin list and SoC flags are static. Hardware state persists in the shared mux/config register for each pad; the common core owns the per-device `struct imx_pinctrl` and `pin_regs` array.

## Dependencies and Integration Points
Depends on platform/OF matching, MMIO helpers, the generic pinctrl framework, and `pinctrl-imx.h`. It integrates with VF610 board DT pinctrl states, GPIO direction requests through the pinctrl core, and peripheral drivers that depend on mux bits at shift 20.

## Risks
VF610 uses shared mux/config registers, so wrong masks, shifts, or direction bit handling can corrupt unrelated pad-control fields. `pin_reg->mux_reg == -1` returns `-EINVAL`, so invalid or unmapped pins must be covered by DT/core validation. Pad-number table drift can misroute GPIO direction changes.

## Test Signals
VF610 probe, pin state application for PTA-PTE pads, GPIO direction changes with readable on-wire input behavior, validation of mux bits at shift 20, no errors for zero-offset registers, and debugfs pin listings matching the hardware manual are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-vf610.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Kconfig

## Purpose
Defines the Kconfig menu and build-time feature symbols for Intel pinctrl/GPIO drivers. It exposes user-selectable platform drivers and the shared `PINCTRL_INTEL` core dependency used by many newer Intel PCH and SoC pin controllers.

## Important APIs, Types, and Functions
This is Kconfig data rather than C code. Important symbols include `PINCTRL_BAYTRAIL`, `PINCTRL_CHERRYVIEW`, `PINCTRL_LYNXPOINT`, `PINCTRL_INTEL`, `PINCTRL_INTEL_PLATFORM`, `PINCTRL_ALDERLAKE`, `PINCTRL_BROXTON`, `PINCTRL_CANNONLAKE`, `PINCTRL_CEDARFORK`, and later platform symbols such as Elkhart Lake, Gemini Lake, Ice Lake, Meteor Lake, Meteor Point, Sunrise Point, and Tiger Lake. `PINCTRL_INTEL` selects `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIOLIB_IRQCHIP`.

## Control Flow
During kernel configuration, the menu is visible when `(ACPI && X86) || COMPILE_TEST` is true. Selecting a platform driver selects `PINCTRL_INTEL` where applicable. `source "drivers/pinctrl/intel/Kconfig.tng"` includes additional Intel Tangier/Merrifield/Moorefield configuration.

## State and Persistence Behavior
The selected symbols persist in `.config` and determine which objects are compiled built-in or as modules. The hidden `PINCTRL_INTEL` symbol centralizes common framework dependencies for descriptor-style Intel drivers.

## Dependencies and Integration Points
Integrates with the kernel Kconfig system, ACPI/X86 platform discovery, compile-test builds, the Intel pinctrl Makefile, and the Linux pinctrl/GPIO subsystems. Help text identifies the SoC/PCH families served by each option.

## Risks
Missing `select PINCTRL_INTEL` or framework dependencies causes link or runtime registration failures. Overly narrow dependencies can block compile testing; overly broad ones can expose drivers on unsupported systems. Help text and platform lists can drift from ACPI IDs implemented in the C files.

## Test Signals
`olddefconfig` and `allyesconfig`/`allmodconfig` on X86 and COMPILE_TEST, object inclusion matching selected symbols, no unmet dependency warnings, and successful module builds for each listed platform are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Makefile

## Purpose
Maps Intel pinctrl Kconfig symbols to the object files that implement each driver. It is the build glue for the Intel pinctrl directory.

## Important APIs, Types, and Functions
The file uses standard kbuild `obj-$(CONFIG_...) += ...` assignments. It builds custom legacy drivers such as `pinctrl-baytrail.o` and `pinctrl-cherryview.o`, the shared core `pinctrl-intel.o`, the generic platform driver `pinctrl-intel-platform.o`, and descriptor drivers such as Alder Lake, Broxton, Cannon Lake, Cedar Fork, Denverton, Elkhart Lake, Emmitsburg, Gemini Lake, Ice Lake, Jasper Lake, Lakefield, Lewisburg, Meteor Lake, Meteor Point, Sunrise Point, and Tiger Lake.

## Control Flow
Kbuild evaluates the selected symbols from `.config`. Built-in selections compile into `drivers/pinctrl/intel/built-in.a`; modular selections produce loadable modules. Platform files that import the `PINCTRL_INTEL` namespace rely on `pinctrl-intel.o` being selected through Kconfig.

## State and Persistence Behavior
There is no runtime state. The Makefile controls persistent build artifacts and determines which driver init functions are linked or emitted as modules.

## Dependencies and Integration Points
Integrates with `drivers/pinctrl/Makefile`, the Intel Kconfig file, module namespace imports, and the C driver filenames. It must stay synchronized with Kconfig symbols and actual source files.

## Risks
A stale object mapping causes a selected driver not to build, or a removed file to break the build. Adding a descriptor driver without selecting `PINCTRL_INTEL` in Kconfig can compile the platform file without its shared core. Ordering is generally low risk, but missing the common core object affects all shared-core users.

## Test Signals
Builds with each Intel `CONFIG_PINCTRL_*` symbol as built-in and module, `make drivers/pinctrl/intel/`, module installation output, and absence of unknown-object or unresolved-symbol errors validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-alderlake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-alderlake.c

## Purpose
Describes Alder Lake-family PCH GPIO/pinctrl hardware for the shared Intel pinctrl core. It covers Alder Lake-N, Alder Lake-S class data reused for Raptor Lake and Twin Lake ACPI IDs, including pad names, GPP groups, communities, register offsets, and ACPI matching.

## Important APIs, Types, and Functions
Register offset macros define PAD_OWN, PADCFGLOCK, HOSTSW_OWN, GPI_IS, and GPI_IE locations for ADL-N and ADL-S layouts. `ADL_N_COMMUNITY()` and `ADL_S_COMMUNITY()` expand to `INTEL_COMMUNITY_GPPS()`. Static data includes `adln_pins[]`, `adln_community*_gpps[]`, `adln_communities[]`, `adln_soc_data`, plus corresponding `adls_*` arrays. `adl_pinctrl_acpi_match[]` maps `INTC1056`, `INTC1057`, and `INTC1085` to the right SoC data. The platform driver probes through `intel_pinctrl_probe_by_hid`.

## Control Flow
Module/platform registration exposes `alderlake-pinctrl`. ACPI matching supplies a `struct intel_pinctrl_soc_data` pointer as match data. The shared Intel core maps resources, registers pinctrl/GPIO/IRQ support, interprets communities, and applies power-management callbacks via `intel_pinctrl_pm_ops`.

## State and Persistence Behavior
This file contains immutable descriptor tables only. Runtime state such as pad ownership, locks, GPIO line state, interrupt enables/status, and saved sleep context is managed by `pinctrl-intel.c` and hardware registers.

## Dependencies and Integration Points
Depends on ACPI platform enumeration, `pinctrl-intel.h`, generic pinctrl descriptors, and PM sleep hooks. It integrates with board firmware using Intel ACPI HIDs and with consumers requesting GPIOs or pin states from the shared Intel core.

## Risks
Pin numbering, GPIO base values, and community boundaries are hardware ABI. Errors can mis-map interrupts, expose non-GPIO pads as GPIOs, or hide valid pads. The same data supports multiple product names, so ACPI ID mapping must stay aligned with platform variants.

## Test Signals
Probe on Alder/Raptor/Twin Lake ACPI IDs, pin count and names in debugfs, GPIO ranges matching GPP bases, IRQ delivery through GPI_IS/GPI_IE, suspend/resume save-restore through the shared PM ops, and build coverage with `PINCTRL_ALDERLAKE` are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-alderlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-baytrail.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-baytrail.c

## Purpose
Implements the Intel Bay Trail GPIO/pinctrl driver. Unlike newer Intel descriptor-only drivers, it provides custom pinmux, pinconf, GPIO, IRQ, firmware-workaround, and suspend/resume logic for the SCORE, NCORE, and SUS GPIO banks.

## Important APIs, Types, and Functions
Register macros cover `BYT_CONF0_REG`, `BYT_VAL_REG`, interrupt status, direct IRQ, debounce, pull, mux, direction, and restore masks. Static SoC tables define pins, groups, functions, communities, and ACPI UIDs. Core helpers include `byt_gpio_reg()`, `byt_set_mux()`, `byt_gpio_request_enable()`, `byt_gpio_set_direction()`, `byt_pin_config_get/set()`, GPIO callbacks, IRQ callbacks `byt_irq_ack/mask/unmask/type()`, `byt_gpio_irq_handler()`, direct IRQ sanity helpers, `byt_gpio_probe()`, `byt_pinctrl_probe()`, and PM callbacks `byt_gpio_suspend/resume()`.

## Control Flow
Probe obtains SoC data by ACPI UID, maps the MMIO resource, registers a custom pinctrl descriptor, then registers a gpiochip with optional chained IRQ handling. Pinctrl mux requests write `BYT_PIN_MUX` in CONF0. GPIO request may forcibly switch firmware-misconfigured pads to GPIO mux. Pinconf manages pulls and debounce. IRQ setup clears stale status, masks invalid direct IRQ configurations, and later dispatches pending bits from `BYT_INT_STAT_REG` to gpio irqdomain lines. Suspend saves selected CONF0/VAL bits and resume restores drifted mux, trigger, direction, and level fields.

## State and Persistence Behavior
Runtime state lives in `struct intel_pinctrl`, cloned community descriptors, gpiochip/irqdomain state, and `vg->context.pads` for sleep. A global `byt_lock` serializes MMIO and IRQ updates. Hardware registers hold mux, pull, debounce, level, direction, trigger, and direct-IRQ state.

## Dependencies and Integration Points
Depends on ACPI, gpiolib, pinctrl/pinmux/pinconf-generic, IRQ chips, PM, and shared Intel helper types. It integrates with firmware-created `INT33B2`/`INT33FC` platform devices, consumers using GPIO descriptors, and ACPI/board configurations that may already program direct IRQs.

## Risks
The driver deliberately works around firmware bugs by changing mux or clearing invalid direct IRQ state; regressions can be board-specific. Register fields are active-low for input/output enable, and output direction must be written atomically with level. Direct IRQ pins are excluded from normal GPIO IRQ handling. Suspend restore masks intentionally preserve only selected bits, so changing them can either lose firmware state or restore unsafe state.

## Test Signals
Probe for all three UIDs, GPIO request/direction/value operations, pull strength and debounce pinconf, edge/level IRQ delivery, direct IRQ sanity logs, debugfs GPIO output, suspend/resume state restoration, firmware-misconfigured pad warnings, and Bay Trail board ACPI devices using GPIO interrupts are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-baytrail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-broxton.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-broxton.c

## Purpose
Provides Broxton and Apollo Lake SoC pinctrl/GPIO descriptor data for the shared Intel pinctrl core. It describes multiple ACPI UID-selected communities such as north, northwest, west, southwest, and south banks, including alternate function groups for UART, PWM, I2C, SPI/SSP, eMMC, SDIO, and SD card pins.

## Important APIs, Types, and Functions
The `BXT_*` register offset macros define community register layout. `BXT_COMMUNITY()` uses `INTEL_COMMUNITY_SIZE()` with 32-pin groups and four pad config DWs. Static data includes BXT and APL pin arrays, `intel_pingroup` arrays with modes, `intel_function` arrays, per-bank communities, and `intel_pinctrl_soc_data` arrays for Broxton and Apollo Lake. ACPI IDs `INT3452` and `INT34D1` and platform IDs select the SoC-data list. Probe uses `intel_pinctrl_probe_by_uid`.

## Control Flow
The subsys initcall registers `broxton-pinctrl`. Firmware may enumerate several platform devices with different UIDs; the shared Intel probe selects the matching entry from the data array, maps community resources, and registers pinctrl/GPIO/IRQ support. Function selection and GPIO behavior are then handled by `pinctrl-intel.c` using the group/mode tables.

## State and Persistence Behavior
This file is static descriptor data. Runtime state is in the common Intel driver and hardware registers. The `.uid` fields persist as the selector that binds each ACPI instance to one bank’s pin map.

## Dependencies and Integration Points
Depends on ACPI/platform IDs, `pinctrl-intel.h`, the generic pinctrl framework, and Intel shared PM ops. It integrates with LPSS/I2C/UART/PWM/storage peripherals whose ACPI pin states refer to these groups and with GPIO consumers on Broxton/Apollo Lake boards.

## Risks
UID-to-bank mapping is critical; a wrong UID gives a device the wrong pin table. Group mode arrays must align one-to-one with their pin arrays. Community pin ranges and GPIO bases affect IRQ and GPIO numbering. Broxton and Apollo Lake share driver code but have different banks, so accidental cross-use is a high-risk edit.

## Test Signals
Probe for `INT34D1` and `INT3452`, one gpiochip per expected ACPI UID, pinmux selection for UART/I2C/PWM/storage groups, GPIO numbering across communities, IRQ delivery, suspend/resume via shared PM ops, and build/module init under `PINCTRL_BROXTON` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-broxton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cannonlake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cannonlake.c

## Purpose
Describes Cannon Lake-H and Cannon Lake-LP PCH pinctrl/GPIO hardware for the shared Intel pinctrl core. It supplies pad names, function groups, community layouts, register offsets, and ACPI IDs for the platform driver.

## Important APIs, Types, and Functions
`CNL_LP_*` and `CNL_H_*` macros define register offsets for ownership, lock, host software ownership, interrupt status, and interrupt enable. `CNL_LP_COMMUNITY()` and `CNL_H_COMMUNITY()` create `intel_community` entries. Static arrays include `cnlh_pins[]`, `cnlh_groups[]`, `cnlh_functions[]`, `cnlh_communities[]`, `cnlh_soc_data`, plus the corresponding LP arrays `cnllp_*`. ACPI IDs `INT3450` and `INT34BB` select H or LP data. The driver delegates probe to `intel_pinctrl_probe_by_hid`.

## Control Flow
When ACPI enumerates a Cannon Lake pinctrl device, match data gives the shared Intel core the correct SoC descriptor. The common core registers pinctrl, GPIO, IRQ, and PM handling. Function groups define legal mux operations for SPI, UART, I2C, and related pads; plain pins/GPP entries expose GPIO-capable ranges.

## State and Persistence Behavior
Only immutable tables live here. Runtime pad ownership, locks, mux state, GPIO values, IRQ masks/status, and sleep context live in hardware and the shared Intel core.

## Dependencies and Integration Points
Depends on ACPI platform devices, `pinctrl-intel.h`, pinctrl descriptors, and shared Intel PM operations. It integrates with Cannon Lake ACPI firmware, GPIO consumers, and peripheral drivers that rely on SPI/I2C/UART pin groups.

## Risks
H and LP variants have different register layouts and pin ranges; mapping an ACPI ID to the wrong descriptor can corrupt GPIO numbering and register access. Mixed-mode SPI groups require correct per-pin mode arrays. Non-GPIO groups marked with `INTEL_GPIO_BASE_NOMAP` must not become GPIO lines.

## Test Signals
Probe for both ACPI IDs, debugfs pin and group visibility, SPI/I2C/UART mux selection, GPIO interrupt handling through shared registers, non-GPIO groups excluded from GPIO numbering, suspend/resume state retention, and `PINCTRL_CANNONLAKE` builds are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cannonlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cedarfork.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cedarfork.c

## Purpose
Provides Cedar Fork PCH pinctrl/GPIO descriptor data for the shared Intel pinctrl core. It covers the server-oriented West/East pad groups, including networking, NCSI, SMBus, error, debug, SPI/eSPI, power-management, and eMMC pins.

## Important APIs, Types, and Functions
`CDF_PAD_OWN`, `CDF_PADCFGLOCK`, `CDF_HOSTSW_OWN`, `CDF_GPI_IS`, and `CDF_GPI_IE` define the community register offsets. `CDF_COMMUNITY()` expands to `INTEL_COMMUNITY_GPPS()`. `cdf_pins[]` names pads 0 through 236. `cdf_community0_gpps[]` and `cdf_community1_gpps[]` divide West and East groups into GPP ranges with GPIO bases. `cdf_soc_data` packages pins and communities. ACPI ID `INTC3001` binds to the descriptor; probe delegates to `intel_pinctrl_probe_by_hid`.

## Control Flow
The subsys initcall registers `cedarfork-pinctrl`. ACPI match passes `cdf_soc_data` to the shared Intel core, which maps resources, registers pinctrl/GPIO/IRQ interfaces, and manages PM. No Cedar Fork-specific runtime callbacks are implemented here.

## State and Persistence Behavior
All data in this file is static. Runtime ownership, lock, GPIO, interrupt, and sleep-save state is maintained by `pinctrl-intel.c` and the hardware.

## Dependencies and Integration Points
Depends on ACPI, platform devices, `pinctrl-intel.h`, module namespace `PINCTRL_INTEL`, and shared Intel PM ops. It integrates with Cedar Fork firmware and board devices needing GPIO or pin ownership metadata.

## Risks
Server PCH pin ranges include many special-purpose and debug pads; wrong GPIO base or GPP boundaries can expose inappropriate pins or break interrupts. Because the file has no function groups, consumers mostly use GPIO/pad configuration, making pin numbering and community offsets especially important.

## Test Signals
Probe on `INTC3001`, correct West/East community registration, GPIO count and bases matching GPP definitions, interrupt enable/status behavior, debugfs pad names, suspend/resume via shared PM, and build/module load under `PINCTRL_CEDARFORK` are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cedarfork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cherryview.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cherryview.c

## Purpose
Implements the Intel Cherryview/Braswell pinctrl and GPIO driver. It provides custom register access, pinmux, pinconf, GPIO, IRQ, ACPI OpRegion, DMI quirk, and noirq suspend/resume handling for Cherryview communities rather than relying solely on the shared Intel core operations.

## Important APIs, Types, and Functions
Register macros describe community interrupt registers and per-pad `CHV_PADCTRL0/1` fields. `struct intel_pad_context` stores saved pad registers; `struct intel_community_context` tracks interrupt-line mappings and saved masks. Static SoC data covers southwest, north, east, and southeast communities. Important helpers include `chv_pctrl_readl/writel()`, `chv_padreg()`, `chv_pinmux_set_mux()`, `chv_gpio_request_enable()`, `chv_config_get/set()`, GPIO callbacks, IRQ callbacks, `chv_gpio_set_intr_line()`, `chv_gpio_irq_handler()`, `chv_gpio_probe()`, ACPI address-space handler, `chv_pinctrl_probe/remove()`, and noirq PM callbacks.

## Control Flow
Probe selects SoC data from ACPI `INT33FF`, maps one MMIO resource, initializes interrupt-line context to invalid, registers pinctrl and gpiochip/irqchip, installs an ACPI address-space handler, and stores driver data. Pinmux refuses locked pads and otherwise writes PMODE/GPIOEN and optional OE inversion. GPIO request enables GPIO mode and clears stale interrupt routing unless locked. IRQ setup maps one of 16 hardware interrupt lines to GPIO offsets, working around shared or BIOS-assigned lines where possible. Suspend saves unlocked pad registers and INTMASK; resume masks interrupts, restores changed pads, clears status, and restores INTMASK.

## State and Persistence Behavior
Runtime state includes `struct intel_pinctrl`, cloned communities, `context.pads`, `context.communities[0].intr_lines`, saved interrupt mask, gpiochip, irqdomain, and a global `chv_lock`. Hardware retains pad mode, GPIO config, pull, open-drain, inversion, interrupt wake config, and interrupt mask/status. Writes are followed by readback for hardware erratum handling.

## Dependencies and Integration Points
Depends on ACPI, DMI, gpiolib, pinctrl, pinconf-generic, IRQ infrastructure, and shared Intel data types. It integrates with ACPI firmware both as a platform driver and via an installed MMIO OpRegion handler. DMI quirks preserve legacy IRQ numbering on selected Chromebooks.

## Risks
Locked pads can only be partially controlled, so ignoring lock checks can fail or corrupt firmware-owned configuration. Interrupt-line sharing and ACPI hardcoded IRQ numbers are board-sensitive. The write-readback sequence is required for Cherryview errata. DMI valid-mask quirks trade correctness for compatibility on known systems. Resume ordering must avoid unmasked interrupts while pad state is inconsistent.

## Test Signals
Probe on `INT33FF`, pinmux and GPIO requests on locked/unlocked pads, pull/open-drain config, GPIO value/direction operations, IRQ startup with BIOS default type, remapping shared interrupt lines, DMI quirk behavior, ACPI OpRegion reads/writes, noirq suspend/resume restore, spurious-interrupt suppression, and build/module unload are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cherryview.c -->
