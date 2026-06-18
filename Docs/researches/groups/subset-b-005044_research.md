# Research Report: subset-b-005044

This grouped report covers the Actions OWL shared pinctrl/GPIO driver, the S500/S700/S900 SoC data drivers, and the Aspeed pinctrl Kconfig/Makefile build metadata. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-owl.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-owl.c

Purpose: Implements the common Actions OWL pin controller core used by the S500, S700, and S900 SoC data files. It registers a Linux pinctrl device, pinmux provider, generic pinconf provider, GPIO chip, and chained GPIO interrupt controller against SoC-specific tables supplied through `struct owl_pinctrl_soc_data`.

Important APIs and types: The central runtime state is `struct owl_pinctrl`, which owns the device pointer, `pinctrl_dev`, embedded `gpio_chip`, raw spinlock, clock, SoC data pointer, MMIO base, parent IRQ count, and parent IRQ array. Public entry is `owl_pinctrl_probe()`. Core helpers include `owl_update_bits()`, `owl_read_field()`, `owl_write_field()`, `get_group_mfp_mask_val()`, `owl_pad_pinconf_reg()`, `owl_group_pinconf_reg()`, and `owl_gpio_get_port()`. Kernel-facing operation tables are `owl_pinctrl_ops`, `owl_pinmux_ops`, `owl_pinconf_ops`, `owl_gpio_irqchip`, and a dynamically filled `gpio_chip`.

Control flow: Platform-specific drivers call `owl_pinctrl_probe()` with their static SoC data. Probe allocates state, maps the register resource, gets and enables the clock, initializes the lock, fills `owl_pinctrl_desc` from SoC pins, installs GPIO callbacks, registers pinctrl, collects platform IRQs, initializes the GPIO IRQ chip, registers the gpiochip, and stores driver data. Pinctrl group/function queries are direct table lookups. `owl_set_mux()` translates a requested function into a mux value by finding its index in the selected group's function list, then writes the field under the raw spinlock. Pin config get/set first map a generic pinconf parameter to a pad or group register field, convert between generic arguments and SoC register encodings, then read or update the field.

State and persistence: Driver state is devm-managed except for the clock enable, which is explicitly disabled on probe failure but has no remove-time disable path in this shared file. Hardware state persists in mux, pull, Schmitt, drive, slew, GPIO data/direction, and interrupt registers until reset or later pinctrl/GPIO calls rewrite them. Register updates are serialized with `raw_spinlock_t` because GPIO and IRQ paths can run in hard IRQ context. The static `owl_pinctrl_desc` is mutated during probe with per-device name and pin arrays, so the design assumes one compatible instance at a time.

Dependencies and integration points: Depends on Linux pinctrl, pinmux, generic pinconf, gpiochip, IRQ domain/chained IRQ, platform device, clock, OF, and MMIO APIs. It consumes SoC data from `pinctrl-s500.c`, `pinctrl-s700.c`, and `pinctrl-s900.c`, and exposes GPIOs through gpiolib and interrupts through gpiochip IRQ helpers. Device tree pinctrl nodes use `pinconf_generic_dt_node_to_map_all()` and the function/group names declared by the SoC files.

Risks: `get_group_mfp_mask_val()` depends on function-list order matching hardware mux encodings; wrong order silently programs the wrong alternate function. Its `if (id > option_num)` wrap condition looks suspicious for exact boundary cases where `id == option_num`. Pad config indexes directly into `soc->padinfo[pin]`, so pin numbers must fit the SoC table. `owl_read_field()` uses `(1 << width)`, which assumes widths smaller than the integer bit width. GPIO interrupt emulation for both edges rewrites interrupt polarity in ACK and can race with rapidly changing inputs. `owl_gpio_irq_handler()` stores a register value in `unsigned long pending_irq` after reading a 32-bit register; this is fine for current port widths but is sensitive to future wider ports. There is no module remove callback in the shared probe path to unregister the gpiochip or disable the clock after successful probe, relying mostly on initcall/platform lifetime.

Test signals: Build each OWL SoC driver, boot a device tree with `actions,s500-pinctrl`, `actions,s700-pinctrl`, or `actions,s900-pinctrl`, verify pin group/function enumeration in debugfs, apply mux and pinconf states from device tree, exercise GPIO request/free and input/output direction, test drive strength and slew-rate group configs where available, test pull and Schmitt settings with readback, and validate GPIO IRQ mask/unmask/ack/type paths for level, rising, falling, and both-edge emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-owl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-owl.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-owl.h

Purpose: Defines the shared data model and table-construction macros for Actions OWL pinctrl drivers. It is the contract between the generic implementation in `pinctrl-owl.c` and the SoC-specific static descriptions in `pinctrl-s500.c`, `pinctrl-s700.c`, and `pinctrl-s900.c`.

Important APIs and types: Macro families `MUX_PG()`, `DRV_PG()`, and `SR_PG()` construct `struct owl_pingroup` entries for mux, drive-strength, and slew-rate groups. `FUNCTION()` constructs `struct owl_pinmux_func`. `PAD_PULLCTL_CONF()`, `PAD_ST_CONF()`, and the `PAD_INFO*()` macros bind pins to pull-control and Schmitt-trigger register metadata. `OWL_GPIO_PORT()` constructs `struct owl_gpio_port` entries. Public structs are `owl_pullctl`, `owl_st`, `owl_pingroup`, `owl_padinfo`, `owl_pinmux_func`, `owl_gpio_port`, and `owl_pinctrl_soc_data`. The only declared function is `owl_pinctrl_probe()`.

Control flow: The header has no executable control flow. It shapes runtime behavior by encoding register offsets, bit shifts, widths, group membership, and callback pointers into static tables. The shared driver later walks these tables for pinctrl operation dispatch, pinconf register selection, GPIO port lookup, and IRQ parent mapping.

State and persistence: All data described here is immutable configuration once compiled, except that the register fields it describes are written by the shared driver into persistent hardware state. `owl_pinctrl_soc_data` includes SoC callbacks for converting generic pinconf arguments to and from hardware values, which keeps SoC-specific pull encoding out of the shared core.

Dependencies and integration points: Assumes the including SoC file defines register offset macros such as `MFCTL0`, `PAD_DRV0`, `PAD_SR0`, `PAD_PULLCTL0`, and `PAD_ST0` before using the table macros. It depends on kernel pinctrl descriptors and platform-device declarations through included users. The enum and macros integrate with Linux generic pinconf parameters for bias, input Schmitt, drive strength, and slew rate.

Risks: The macros paste register-name tokens, so typo or missing register defines fail at compile time, while incorrect shift/width/group data compiles but misprograms hardware. `struct owl_pingroup` uses mutable `unsigned int *` pointers even though the tables are static, making const-correctness weaker than necessary. `owl_pinctrl_soc_data` documents `@nfunction` but the field is `nfunctions`, a minor comment drift. Port indexes are fixed to A-F; a future SoC with sparse or additional ports would need header changes.

Test signals: Compile all current SoC files with `W=1`, verify that group and function counts match the arrays generated by these macros, run pinconf readback tests for every `PAD_INFO*()` variant, and test GPIO port mappings for all populated `OWL_GPIO_PORT_*` indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-owl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s500.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s500.c

Purpose: Provides the Actions Semi S500 SoC-specific pin descriptions, mux groups, function maps, pad configuration metadata, GPIO port layout, and platform-driver binding for the common OWL pinctrl core.

Important APIs and types: The file defines S500 register offsets for `MFCTL0..3`, `PAD_PULLCTL0..2`, `PAD_ST0..1`, `PAD_CTL`, and `PAD_DRV0..2`; GPIO/pad numbering macros from `_GPIOA()` through `_GPIOE()` plus `_PIN()`; `s500_pads`; `enum s500_pinmux_functions`; `s500_groups`; `s500_functions`; `s500_padinfo`; `s500_gpio_ports`; pad conversion callbacks `s500_pad_pinconf_arg2val()` and `s500_pad_pinconf_val2arg()`; `s500_pinctrl_data`; and the `pinctrl-s500` platform driver.

Control flow: At `arch_initcall`, `s500_pinctrl_init()` registers the platform driver. A device tree node compatible with `actions,s500-pinctrl` calls `s500_pinctrl_probe()`, which delegates all runtime setup to `owl_pinctrl_probe()`. Thereafter the shared driver uses the static tables to resolve mux groups and pinconf register fields. The mux table contains 61 `MUX_PG()` groups and 32 `DRV_PG()` groups; function arrays map peripherals such as RMII/SMII Ethernet, SPI0-3, UART0-6, I2S, PCM, keypad, JTAG, PWM, SD0-2, I2C, DSI, LVDS, USB30, CSI, NAND, SPDIF, transport stream, and LCD0 to those groups.

State and persistence: The file contributes static configuration only. Hardware state is persisted by the shared driver in S500 mux, pull, Schmitt, drive, GPIO, and interrupt registers. S500 exposes 132 GPIOs across ports A-D with 32 pins each and port E with 4 pins, then defines additional non-GPIO pads for CSI, NAND, PORB, CLKO, BSEL, and package pins. Pad bias conversion is two-state: pull-down maps to `0`, pull-up maps to `1`; Schmitt input is normalized to 0/1.

Dependencies and integration points: Includes the generic pinconf and pinctrl kernel headers plus `pinctrl-owl.h`. Integrates with device tree through `actions,s500-pinctrl` and with the shared Actions OWL driver through `s500_pinctrl_data`. Consumers name functions/groups in DT pinctrl states; GPIO and IRQ behavior is handled by the shared core using `s500_gpio_ports`.

Risks: This file is table-heavy, so most defects are silent data errors: wrong pad number, wrong mux option order, wrong register shift/width, or missing padinfo capability. Several enum entries and function mappings are commented out, including I2C2 and SIRQ functions, while some function arrays contain repeated options or reserved placeholders; those choices should be checked against the datasheet before reuse. Shared mux fields are represented as separate single-pad groups, so two clients selecting conflicting alternatives on pads controlled by the same field can overwrite each other. Pull controls for NAND data lines share a single bit, which is intentional hardware modeling but can surprise per-pin users.

Test signals: Build and boot with an S500 DT, verify `actions,s500-pinctrl` probe, enumerate 132 GPIOs, apply DT states for Ethernet, UART console, SD0/SD1, I2C, SPI0, NAND, LCD/DSI/LVDS, and CSI, read back pull-up/down and Schmitt configs, test drive-strength groups at 2/4/8/12 mA, and validate GPIO IRQs on each port parent interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s700.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s700.c

Purpose: Supplies the Actions Semi S700 pinctrl description for the common OWL core. It is structurally close to S500 but adjusts pin numbering, Ethernet width, extra dummy groups, Bluetooth/SIRQ exposure, and GPIO interrupt register layout for S700 hardware.

Important APIs and types: Defines the S700 register offsets, GPIO numbering macros for ports A-E, `s700_pads`, `enum s700_pinmux_functions`, `s700_groups`, `s700_functions`, `s700_padinfo`, `s700_gpio_ports`, conversion callbacks `s700_pad_pinconf_arg2val()` and `s700_pad_pinconf_val2arg()`, `s700_pinctrl_data`, and the `pinctrl-s700` platform driver. The group table contains 65 mux groups and 31 drive-strength groups.

Control flow: `s700_pinctrl_init()` registers the driver at `arch_initcall`. Matching `actions,s700-pinctrl` devices call `s700_pinctrl_probe()`, which hands `s700_pinctrl_data` to `owl_pinctrl_probe()`. Runtime pinmux and pinconf operations are entirely delegated to the shared OWL implementation. Function mapping covers NOR, RGMII/SGMII-labeled Ethernet functions, SPI0-3, sensors, UART0-6, I2S, PCM, keypad, JTAG, PWM, SD0-2, I2C0-3, DSI, LVDS, USB30, clock output, MIPI CSI, NAND, SPDIF, SIRQ0-2, Bluetooth, and LCD0.

State and persistence: The file stores immutable S700 tables; actual mux, pull, Schmitt, drive, GPIO, and IRQ state persists in hardware after common-driver writes. S700 exposes 136 GPIOs: ports A-D with 32 pins and port E with 8 pins. Pull conversion is the same two-state encoding as S500, while Schmitt enable remains 0/1.

Dependencies and integration points: Uses `pinctrl-owl.h` macros and Linux pinctrl/generic pinconf APIs. Device tree integration is through `actions,s700-pinctrl`. The GPIO interrupt map differs from S500: ports share `intc_ctl` at `0x204`, use per-port pending/mask/type offsets, and port E has a comment noting `INTC_GPIOD_TYPE1` use to fit the generic shared driver model.

Risks: Because many S700 tables were derived from the S500 shape, copy/paste drift is a key risk, especially around names such as `S700_MUX_ETH_RGMII` assigned to `FUNCTION(eth_rmii)` and `S700_MUX_ETH_SGMII` assigned to `FUNCTION(eth_smii)`. Dummy groups for NAND and SIRQ functions are placeholders that expose function names without normal pad lists; consumers need datasheet confirmation. The shared mux-field conflict risk remains for groups that point at the same MFCTL bits. GPIO interrupt register offsets and `shared_ctl_offset` values are subtle and should be validated on hardware.

Test signals: Build with S700 enabled, boot a DT node using `actions,s700-pinctrl`, verify all 136 GPIOs, test Ethernet including the extra TXD2/TXD3/RXD2/RXD3 pads, validate UART/BT and SIRQ pin states, exercise I2C0-3, SD, NAND, display, CSI, and PWM muxes, read back pull and Schmitt settings, test 2/4/8/12 mA drive-strength groups, and trigger GPIO IRQs on each parent line including port E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s900.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s900.c

Purpose: Provides the Actions OWL S900 SoC-specific pinctrl data and platform binding. Compared with S500/S700 it models a larger six-port GPIO space, two CSI blocks, two NAND banks, SGPIO pins, richer pull encodings, and dedicated slew-rate configuration groups.

Important APIs and types: Defines S900 register offsets including `PAD_SR0..2`, GPIO numbering for ports A-F, `s900_pads`, `enum s900_pinmux_functions`, `s900_groups`, `s900_functions`, `s900_padinfo`, `s900_gpio_ports`, pad conversion callbacks `s900_pad_pinconf_arg2val()` and `s900_pad_pinconf_val2arg()`, `s900_pinctrl_data`, and the `pinctrl-s900` platform driver. The group table contains 61 mux groups, 33 drive-strength groups, and 28 slew-rate groups.

Control flow: At `arch_initcall`, `s900_pinctrl_init()` registers `pinctrl-s900`. A matching `actions,s900-pinctrl` platform device calls `s900_pinctrl_probe()`, which delegates setup to the shared OWL core. The shared driver later uses `MUX_PG()` entries for alternate-function selection, `DRV_PG()` entries for generic drive-strength config, and `SR_PG()` entries for generic slew-rate config. Function mapping covers RMII/SMII Ethernet, SPI0-3, UART0-6, I2C0-5, I2S, PCM, JTAG, PWM, SD0-3, sensors, LVDS, USB20/USB30, ERAM, GPU, MIPI CSI0/CSI1, MIPI DSI, NAND0/NAND1, SPDIF, and SIRQ0-2.

State and persistence: S900 static tables describe 146 GPIOs across ports A, B, E with 32 pins, port C with 12 pins, port D with 30 pins, and port F with 8 pins, plus four non-GPIO SGPIO pads. Hardware state persists in MFCTL, pull, Schmitt, drive, slew-rate, GPIO, and interrupt registers. Pull encoding is four-state for supported pads: high impedance, pull-down, pull-up, and bus-hold. Schmitt enable still normalizes to 0/1. Slew-rate groups write `PAD_SR*` fields through the shared group pinconf path.

Dependencies and integration points: Includes generic pinconf and `pinctrl-owl.h`. Device tree binding uses `actions,s900-pinctrl`. GPIO IRQ metadata uses six `OWL_GPIO_PORT()` entries with varied control/pending/mask/type offsets and `shared_ctl_offset` set to 0 for all ports. Linux consumers interact through standard pinctrl, pinconf, and gpiolib APIs.

Risks: S900 has the broadest table surface and therefore high risk of silent mux/register metadata errors. Four-state pull support depends on device tree users choosing parameters that are valid for the pad; pads without pull metadata return `-EINVAL`. Slew-rate support is group-based, so unrelated pads in a shared slew group can be affected together. All GPIO ports use shared control offset 0 despite different `intc_ctl` offsets; incorrect assumptions here would break interrupt enable/ack behavior. The enum includes sentinel-like values such as `S900_MUX_AUX_START` and `S900_MUX_MAX`; any future function additions must preserve table indexes used by group function arrays.

Test signals: Build and boot S900 pinctrl, verify `actions,s900-pinctrl` probe, enumerate 146 GPIOs plus non-GPIO pads, validate mux states for Ethernet, UART, I2C0-5, SD0-3, NAND0/1, CSI0/1, DSI/LVDS, USB, ERAM, and SGPIO, test pull high-Z/down/up/hold where supported, test Schmitt readback, verify drive-strength and slew-rate group settings, and exercise GPIO IRQs on every port with level and edge triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/pinctrl-s900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Kconfig

Purpose: Defines kernel configuration symbols for Aspeed pinctrl support. It separates the hidden common Aspeed pinctrl core from selectable generation-specific drivers for G4, G5, and G6 SoCs.

Important APIs and types: `PINCTRL_ASPEED` is a hidden bool selected by generation drivers. It depends on `(ARCH_ASPEED || COMPILE_TEST) && OF` and selects `MFD_SYSCON`, `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, and `REGMAP_MMIO`. User-visible bools are `PINCTRL_ASPEED_G4`, `PINCTRL_ASPEED_G5`, and `PINCTRL_ASPEED_G6`, each depending on the matching `MACH_ASPEED_G*` or `COMPILE_TEST` plus OF, and each selecting the common symbol.

Control flow: Kconfig evaluation enables the common symbol only when at least one generation-specific symbol is selected. The selected symbols drive object inclusion in the Aspeed `Makefile`; there is no runtime logic in this file. Help text notes that GPIO is provided by a separate GPIO driver, so these options cover pinmux/pinconf rather than GPIO ownership.

State and persistence: No runtime state. Persistent effect is the build configuration recorded in `.config`, which determines whether Aspeed pinctrl objects are compiled into the kernel or module build.

Dependencies and integration points: Integrates with the top-level pinctrl Kconfig tree and the Aspeed machine symbols. The selected framework symbols ensure the Aspeed implementation has syscon/regmap MMIO access and generic pinctrl/pinconf infrastructure. Generation-specific drivers compile under `COMPILE_TEST` to catch build drift outside Aspeed platforms.

Risks: Missing selected dependencies would surface as compile failures or missing framework APIs. Because generation options are bools rather than tristates, they follow built-in kernel semantics rather than module selection. The hidden common symbol cannot be enabled directly, so adding a new generation driver must remember to select `PINCTRL_ASPEED`.

Test signals: Run Kconfig builds for `MACH_ASPEED_G4`, `MACH_ASPEED_G5`, `MACH_ASPEED_G6`, and `COMPILE_TEST`; verify that selecting each generation pulls in `PINCTRL_ASPEED` and its framework dependencies; and confirm that GPIO remains provided by the separate Aspeed GPIO configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Makefile

Purpose: Lists the Aspeed pinctrl objects built for the selected Kconfig symbols and applies a local compiler warning flag useful for table-heavy pinmux initialization.

Important APIs and types: `ccflags-y += -Woverride-init` enables diagnostics for overridden initializers in this directory. `obj-$(CONFIG_PINCTRL_ASPEED)` builds the common `pinctrl-aspeed.o` and `pinmux-aspeed.o` objects. `obj-$(CONFIG_PINCTRL_ASPEED_G4)`, `obj-$(CONFIG_PINCTRL_ASPEED_G5)`, and `obj-$(CONFIG_PINCTRL_ASPEED_G6)` add the generation-specific object files.

Control flow: Kbuild expands the `obj-*` assignments according to `.config`. When a generation symbol selects `PINCTRL_ASPEED`, both common objects and the matching generation object are compiled and linked into the kernel build. There is no runtime control flow.

State and persistence: No runtime state. The file affects build artifacts and warning behavior for this directory. Generated object inclusion persists only in the build output selected by the active kernel configuration.

Dependencies and integration points: Tightly coupled to `drivers/pinctrl/aspeed/Kconfig` symbols and to source files named by the object rules. The common objects provide shared infrastructure used by G4/G5/G6 files, while generation objects carry SoC-specific pin tables.

Risks: Object-rule drift can produce link failures if Kconfig symbols are renamed or source files move. If a new generation config selects `PINCTRL_ASPEED` but the Makefile omits its object, the option will build only the common code and no matching device support. `-Woverride-init` may expose intentional duplicate initializer patterns as warnings, but that is useful for detecting table mistakes in pinmux data.

Test signals: Build each `CONFIG_PINCTRL_ASPEED_G4/G5/G6` combination, verify the expected object files appear in the build log, run `make W=1` or equivalent warning builds, and check that common objects are included whenever any generation-specific symbol is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Makefile -->
