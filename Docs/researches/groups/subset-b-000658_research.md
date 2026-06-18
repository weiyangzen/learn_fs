# subset-b-000658 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs-s3c64xx.h

### Purpose
Defines the legacy S3C64xx interrupt number layout used by non-DT ARM machine code. It assigns VIC0/VIC1 lines, linear external interrupt numbers, grouped GPIO interrupt ranges, board IRQ start, and compatibility aliases.

### Important APIs, Types, And Functions
The key macros are `S3C_IRQ()`, `S3C64XX_IRQ_VIC0()`, `S3C64XX_IRQ_VIC1()`, `S3C_EINT()`, `IRQ_EINT()`, `IRQ_EINT_GROUP()`, `IRQ_BOARD_START`, and `S3C64XX_NR_IRQS`. Named IRQ constants cover timers, UARTs, DMA, SDHCI, RTC, ADC/touch, USB, SPI, I2C, display, and media engines.

### Control Flow
There is no runtime flow. The numeric layout is consumed at compile time by irqchip setup, board files, platform device resources, wake mask code, and drivers that still use platform IRQ numbers.

### State, Persistence, And Dependencies
No mutable state is stored here. The persistent contract is the stable IRQ numbering ABI inside this kernel tree. It depends on the ARM legacy IRQ model and the S3C64xx two-VIC hardware topology.

### Integration Points
`s3c64xx.c`, `s3c6410.c`, platform resources, board files such as Cragganmore, and power-management wake masking all rely on these definitions.

### Risks
Shared aliases such as `IRQ_HSMMC2` mapped to `IRQ_SPI1` and SoC-specific overlaps need careful driver use. Changing offsets or group sizes would break platform data and wake handling.

### Test Signals
Boot tests should confirm VIC registration, external interrupt demuxing, SDHCI/SPI shared IRQ behavior, and board-specific GPIO interrupt use. Build tests catch missing aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs.h

### Purpose
Thin compatibility include that exposes `irqs-s3c64xx.h` through the local `mach-s3c` include name.

### Important APIs, Types, And Functions
It exports no new API; all IRQ constants and macros come from `irqs-s3c64xx.h`.

### Control Flow
There is no runtime behavior.

### State, Persistence, And Dependencies
No state. It depends entirely on the S3C64xx IRQ header and exists to preserve include paths used by local C files.

### Integration Points
Included by board, PM, and setup files that refer to local `"irqs.h"` rather than the SoC-specific header.

### Risks
If new S3C-family variants were added, this hard include would select S3C64xx numbering for all users.

### Test Signals
Compile coverage of all local users verifies this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/keypad.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/keypad.h

### Purpose
Declares legacy platform-data hooks for Samsung keypad devices on S3C machines.

### Important APIs, Types, And Functions
`samsung_keypad_set_platdata(struct samsung_keypad_platdata *pd)` copies board keypad data into the platform device. `samsung_keypad_cfg_gpio(unsigned int rows, unsigned int cols)` is the architecture GPIO setup hook.

### Control Flow
Board files prepare a `samsung_keypad_platdata`, call `samsung_keypad_set_platdata()`, and the keypad driver later consumes the copied data. The GPIO callback is called during device setup.

### State, Persistence, And Dependencies
This header holds no state. It depends on `<linux/input/samsung-keypad.h>` for the platform data structure and on arch code providing the GPIO configuration function.

### Integration Points
`mach-crag6410.c` supplies keymaps and uses the setter. `setup-keypad-s3c64xx.c` implements the S3C64xx GPIO mux path.

### Risks
Rows/columns must match the supplied keymap and the physical GPIO muxing. Board data marked `__initdata` is safe only because the setter copies it.

### Test Signals
Matrix key scanning, wake key behavior, and build coverage with `CONFIG_KEYBOARD_SAMSUNG` validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/keypad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c

### Purpose
Implements plug-in Wolfson/Speyside module probing for the Cragganmore S3C6410 board. It reads module IDs from small I2C identification devices and registers the matching audio codec SPI/I2C devices plus GPIO lookup tables.

### Important APIs, Types, And Functions
The central data structure is `gf_mods[]`, mapping module `id`, `rev`, display name, optional I2C devices, SPI devices, and GPIO lookup table. `wlf_gf_module_probe()` reads byte 0 over SMBus, decodes `id` and `rev`, logs the detected module, registers child I2C clients with `i2c_new_client_device()`, registers SPI devices with `spi_register_board_info()`, and adds lookup tables. `wlf_gf_module_register()` installs the I2C driver only on S3C64xx via `device_initcall`.

### Control Flow
At device init, the driver binds to `"wlf-gf-module"` entries registered by the main Crag board file. Probe reads the module EEPROM/ID latch, searches `gf_mods[]`, pre-adds shared Arizona/WM8994 GPIO tables, then conditionally registers the module-specific devices. Unknown IDs are warned but not fatal.

### State, Persistence, And Dependencies
State is mostly static board data: codec platform data, regulator supply data, retune tables, SPI/I2C board-info arrays, and GPIO lookup tables. No persistent storage is modified. Dependencies include the I2C core, SPI board info, gpiod lookup tables, Wolfson MFD/audio platform-data headers, `soc_is_s3c64xx()`, and Crag IRQ/GPIO base definitions.

### Integration Points
The main Crag board registers multiple `"wlf-gf-module"` I2C devices on bus 1. This file expands those module IDs into codec devices such as WM0010, WM5100, WM8996, WM8994/WM8958, WM5102, WM5110, WM2200, and WM9081.

### Risks
The ID decode uses `(ret & 0xfe) >> 2`, so hardware encoding assumptions are critical. Some revisions use `.rev = -1` in a `u8` field, effectively matching 255 rather than a wildcard unless intended through conversion. GPIO lookup tables are globally registered and not removed on probe failure. Duplicate codec addresses on the same bus depend on only one physical module being present.

### Test Signals
Module insertion boot logs, I2C client creation, SPI device enumeration, codec probe success, IRQ routing through the PMIC GPIO IRQ base, and GPIO descriptor lookup by codec drivers are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410.c

### Purpose
Provides the legacy non-DT machine description and board data for the Wolfson Cragganmore 6410 development board.

### Important APIs, Types, And Functions
Static board data describes UARTs, PWM backlight, LCD panel timing, keypad matrix, GPIO keys, DM9000 Ethernet, MMGPIO, fixed regulators, WM831x PMICs, I2C devices, SDHCI hosts, LEDs, DWC2 OTG, and SPI chip selects. Important functions are `crag6410_lcd_power_set()`, `crag6410_map_io()`, `crag6410_cfg_sdhci0()`, and `crag6410_machine_init()`. `MACHINE_START(WLF_CRAGG_6410, ...)` wires the machine to S3C6410 IRQ, mapping, timer, and init callbacks.

### Control Flow
`crag6410_map_io()` maps S3C64xx I/O, sets the 12 MHz crystal, registers UART configs, and selects PWM timers. `crag6410_machine_init()` sets pull-ups and initial GPIO output states, installs platform data for SDHCI/I2C/framebuffer/USB/keypad/SPI, registers I2C board info and GPIO lookup tables, adds PWM lookup entries and platform devices, registers MMGPIO and LEDs, enforces regulator constraints, then initializes S3C64xx PM.

### State, Persistence, And Dependencies
State is static platform data consumed by legacy platform drivers. Runtime side effects configure GPIO direction, pull state, platform device lists, I2C/SPI child devices, regulator constraints, and PM domains. Dependencies span S3C64xx SoC helpers, Samsung framebuffer/SDHCI/I2C/SPI/keypad APIs, gpiolib lookup tables, regulators, WM831x PMIC data, DM9000, DWC2, LED, GPIO-key, and PWM subsystems.

### Integration Points
This board file anchors non-DT Cragganmore boot. It interacts with `mach-crag6410-module.c` through registered `"wlf-gf-module"` I2C devices and depends on S3C6410 CPU init, IRQ setup, and clock/timer initialization.

### Risks
Most behavior is encoded in static platform data, so address, IRQ, GPIO, or regulator mistakes surface only at boot on hardware. GPIO requests do not consistently check errors. Several devices depend on PMIC IRQ-base arithmetic and board-specific lookup names matching driver expectations.

### Test Signals
A successful boot should enumerate I2C/SPI codecs, PMIC regulators, SDHCI, framebuffer/backlight, keypad, DM9000, DWC2, LEDs, and suspend/resume. Hardware smoke tests should check LCD power, SD card detection, module detection, and regulator dependency ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-s3c64xx-dt.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-s3c64xx-dt.c

### Purpose
Provides the flattened-device-tree machine descriptor for Samsung S3C64xx systems.

### Important APIs, Types, And Functions
`s3c64xx_dt_map_io()` initializes early debug I/O, maps common S3C64xx I/O, and sets the timer source to PWM3/PWM4. `DT_MACHINE_START(S3C6400_DT, ...)` binds compatible strings `samsung,s3c6400` and `samsung,s3c6410`.

### Control Flow
On DT boot, the machine descriptor calls the map callback before normal OF platform population. Interrupt and device discovery are delegated to DT-aware irqchip, pinctrl, clock, and platform code rather than legacy board files.

### State, Persistence, And Dependencies
No persistent state. It relies on `debug_ll_io_init()`, `s3c64xx_init_io()`, and `s3c64xx_set_timer_source()`.

### Integration Points
Used instead of `s3c64xx.c` legacy board setup when booting with populated DT. It shares common I/O mapping and timer variant setup with non-DT paths.

### Risks
Only the map/timer base setup is done here; missing DT nodes or drivers will not be compensated by legacy platform devices. The machine name says S3C6400 but covers S3C6410 too.

### Test Signals
DT boot should reach console output, initialize timer/clocksource, and populate devices from compatible DT nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-s3c64xx-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-base.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-base.h

### Purpose
Defines the shared high virtual-address base layout for legacy Samsung S3C/S5P ARM I/O mappings.

### Important APIs, Types, And Functions
Important macros include `S3C_ADDR_BASE`, `S3C_ADDR()`, `S3C_VA_IRQ`, `S3C_VA_SYS`, `S3C_VA_MEM`, `S3C_VA_UART`, `S3C_VA_TIMER`, `S3C_VA_WATCHDOG`, `S3C_VA_USB_HSPHY`, and related virtual regions.

### Control Flow
There is no runtime flow; machine map descriptors use these constants during `iotable_init()`.

### State, Persistence, And Dependencies
No mutable state. The file persists a virtual memory contract between early boot code, register headers, and mapping setup.

### Integration Points
Included by map wrappers and register headers for clock, GPIO, system controller, watchdog, timer, UART, and USB PHY bases.

### Risks
Changing the layout can break early debug, exception-safe mappings, and register macros before `ioremap()` is available.

### Test Signals
Early boot console, timer init, IRQ init, and register access before driver probing validate the mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c.h

### Purpose
Provides S3C-family physical address constants and virtual aliases for legacy platform setup.

### Important APIs, Types, And Functions
It builds on `map-base.h` and defines address constants such as UART, timer, watchdog, and peripheral bases used by S3C platform devices.

### Control Flow
No runtime flow.

### State, Persistence, And Dependencies
No state; it preserves board-file and SoC-helper address contracts.

### Integration Points
Consumed by S3C64xx map headers, device resources, and setup helpers.

### Risks
Incorrect physical base constants produce silent MMIO access to the wrong hardware.

### Test Signals
Boot-time platform device resource registration and successful MMIO probing by UART/timer/watchdog drivers validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c64xx.h

### Purpose
Defines S3C64xx physical address and virtual address mappings for legacy board and SoC code.

### Important APIs, Types, And Functions
Macros cover S3C64xx system controller, GPIO, VICs, SROM/memory controller, modem, watchdog, USB high-speed PHY, DMA, SDHCI, SPI, framebuffer, I2C, and media peripheral physical bases, plus virtual aliases such as `S3C64XX_VA_GPIO` and `S3C64XX_VA_MODEM`.

### Control Flow
No runtime flow. `s3c64xx.c` turns selected constants into `map_desc` entries and platform resources use the physical bases.

### State, Persistence, And Dependencies
No mutable state. It depends on the shared map base layout and S3C64xx hardware address map.

### Integration Points
Used by register headers, S3C64xx common init, power management, and device resource declarations.

### Risks
The register macros assume the mapped virtual ranges exist early. Device driver resources and static maps must stay consistent or drivers may access unmapped or wrong regions.

### Test Signals
Successful UART, GPIO, VIC, timer, USB PHY, and SDHCI initialization on S3C6410 hardware are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s5p.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s5p.h

### Purpose
Provides S5P-family mapping aliases needed by shared Samsung ARM code.

### Important APIs, Types, And Functions
It includes common map base definitions and defines S5P virtual address aliases used by register headers and early machine code.

### Control Flow
No runtime flow.

### State, Persistence, And Dependencies
No state. It depends on the shared Samsung map base.

### Integration Points
Used by older S5P code paths that share S3C-style address macros.

### Risks
Mixing S3C and S5P aliases can obscure which SoC address map is active.

### Test Signals
Compile coverage and early S5P boot mapping validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s5p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map.h

### Purpose
Compatibility wrapper that includes `map-s3c64xx.h`.

### Important APIs, Types, And Functions
No new symbols; all mappings come from the S3C64xx map header.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on `map-s3c64xx.h`.

### Integration Points
Used by local files that include `"map.h"` for the currently supported S3C64xx platform.

### Risks
It hard-selects S3C64xx mappings for generic-looking local include users.

### Test Signals
Build coverage of S3C64xx common and PM code validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pl080.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pl080.c

### Purpose
Registers the two S3C64xx PL080S DMA controllers as AMBA devices with channel metadata and DMA slave maps.

### Important APIs, Types, And Functions
`s3c64xx_dma0_info[]` and `s3c64xx_dma1_info[]` describe physical/logical channels and signal IDs. `s3c64xx_dma*_slave_map[]` maps peripheral names and DMA directions to request signals. `s3c64xx_dma*_plat_data` configures PL08x callbacks, memcpy channel, bus widths, and slave maps. `s3c64xx_pl080_init()` registers the AMBA devices at `arch_initcall`.

### Control Flow
During arch init, the function exits unless running on S3C64xx. It applies a 32-bit coherent DMA mask to both AMBA devices and registers DMA0 and DMA1. Later PL08x and DMAengine clients use the slave maps to request channels for UART, SPI, I2S, PCM, AC97, and other peripherals.

### State, Persistence, And Dependencies
Static channel tables are persistent kernel data. Runtime state lives in the AMBA/PL08x DMA driver. Dependencies include `linux/amba/bus.h`, `amba/pl080.h`, DMAengine slave mapping, and S3C64xx IRQ/address constants.

### Integration Points
Platform device drivers request DMA by device name and channel map entry. This file bridges legacy S3C device names to PL080 request lines.

### Risks
Slave map names must exactly match device names. Channel signal assignment is hardware-specific, and wrong mappings cause hung or corrupt DMA. `get_xfer_signal` simply returns the assigned signal and `put_xfer_signal` is empty, so allocation policy is entirely table-driven.

### Test Signals
DMA-backed UART/SPI/audio transfers, memcpy DMA, AMBA device registration, and DMAengine channel lookup tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pl080.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/platformdata.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/platformdata.c

### Purpose
Provides helpers that copy platform data into Samsung legacy platform devices safely during early board setup.

### Important APIs, Types, And Functions
The main helper pattern allocates or copies board-provided platform data into a target `platform_device.dev.platform_data`, allowing board data to be declared `__initdata`.

### Control Flow
Board-specific setter functions call the helper before platform devices probe. The copied data persists after init memory is discarded.

### State, Persistence, And Dependencies
State is the copied platform data attached to platform devices. Dependencies include platform device structures, allocation helpers, and Samsung device declarations.

### Integration Points
Used by keypad, SDHCI, framebuffer, I2C, and other legacy board files that provide platform data at init time.

### Risks
Copy size must match the target structure. Embedded pointers inside platform data still need valid lifetime unless the specific setter deep-copies them.

### Test Signals
Boot with init memory freed and successful later driver probe validates that copied platform data does not reference discarded structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/platformdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.c

### Purpose
Implements shared register save/restore helpers for Samsung S3C suspend paths.

### Important APIs, Types, And Functions
`s3c_pm_do_save()` reads each `sleep_save.reg` into `sleep_save.val`. `s3c_pm_do_restore()` writes saved values back with debug logging. `s3c_pm_do_restore_core()` performs a minimal restore without debug side effects.

### Control Flow
SoC PM code prepares arrays of `struct sleep_save` entries with `SAVE_ITEM()`. Suspend preparation calls save; resume calls restore or core restore depending on how early and fragile the restore point is.

### State, Persistence, And Dependencies
The only state is the per-entry saved MMIO value. It depends on raw MMIO accessors and `S3C_PMDBG`.

### Integration Points
`pm-s3c64xx.c` uses these helpers for memory-controller and system registers. Similar logic appears independently in S5PV210 PM.

### Risks
Restore order matters for clock and memory registers. Debug output is intentionally absent from `s3c_pm_do_restore_core()` because peripherals may not be usable.

### Test Signals
Suspend/resume with register checks, PM debug logs, and peripheral function after resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.h

### Purpose
Declares the shared S3C register save structure and helper APIs.

### Important APIs, Types, And Functions
`struct sleep_save` stores an MMIO register pointer and saved value. `SAVE_ITEM(x)` initializes an entry. The declared helpers are `s3c_pm_do_save()`, `s3c_pm_do_restore()`, and `s3c_pm_do_restore_core()`.

### Control Flow
No direct flow; SoC PM files build arrays and pass them to the helpers.

### State, Persistence, And Dependencies
State is carried in caller-owned arrays. It depends on `void __iomem` and unsigned long register storage.

### Integration Points
Included by S3C64xx PM and any other Samsung S3C PM implementation using the common save/restore contract.

### Risks
Register width assumptions follow `unsigned long` and raw 32-bit register behavior. The macro does not validate register addresses.

### Test Signals
Compile coverage and successful suspend/resume register restoration validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core-s3c64xx.h

### Purpose
Provides S3C64xx-specific inline hooks and wake-mask constants used by generic Samsung PM code.

### Important APIs, Types, And Functions
Inline hooks include `s3c_pm_debug_init_uart()`, `s3c_pm_arch_prepare_irqs()`, `s3c_pm_arch_stop_clocks()`, `s3c_pm_arch_show_resume_irqs()`, `s3c_pm_restored_gpios()`, and `samsung_pm_saved_gpios()`. `s3c_irqwake_eintallow` and `s3c_irqwake_intallow` define wake-capable IRQ masks when sleep support is enabled.

### Control Flow
The generic PM path calls these architecture hooks around suspend/resume phases. Most are no-ops for S3C64xx except GPIO save/restore notification hooks and wake mask constants.

### State, Persistence, And Dependencies
No direct state. It depends on PM sleep configuration and GPIO PM helpers.

### Integration Points
Included through the PM core wrapper selected for S3C64xx.

### Risks
No-op hooks mean any required hardware-specific preparation must live elsewhere. Wake-mask constants must match hardware wake capability.

### Test Signals
Suspend with selected external and internal wake sources validates allowed masks and hook ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core.h

### Purpose
Compatibility wrapper selecting `pm-core-s3c64xx.h`.

### Important APIs, Types, And Functions
No new API is defined; the included file supplies PM hooks and wake masks.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on `pm-core-s3c64xx.h`.

### Integration Points
Used by generic-looking local PM code to bind to the S3C64xx implementation.

### Risks
Hard selection would be wrong if shared with another S3C variant without updating the wrapper.

### Test Signals
S3C64xx PM build and suspend coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-gpio.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-gpio.c

### Purpose
Saves, restores, and diagnoses Samsung GPIO controller state across suspend for 1-bit, 2-bit, and 4-bit GPIO configuration formats.

### Important APIs, Types, And Functions
Exports `samsung_gpio_pm_1bit`, `samsung_gpio_pm_2bit`, and `samsung_gpio_pm_4bit` operation tables. `samsung_pm_save_gpios()` walks all registered Samsung GPIO chips and saves state. `samsung_pm_restore_gpios()` restores state. Format-specific helpers save `CON`, `DAT`, and `PUD/UP` registers and report configuration changes.

### Control Flow
During suspend, every Samsung GPIO chip is visited and its PM ops save relevant registers. During resume, the same chip list is restored. The 2-bit and 4-bit paths compare old and current configuration to preserve sleep-selected GPIO function where appropriate and log changes.

### State, Persistence, And Dependencies
Saved state lives in each `samsung_gpio_chip` PM fields. Dependencies include Samsung GPIO registration, MMIO accessors, GPIO config encodings, and PM debug macros.

### Integration Points
S3C64xx PM invokes these through PM core hooks. GPIO bank definitions select the correct PM ops when chips are registered.

### Risks
The code must understand each bank's bit packing. Incorrect masks can restore pins to active outputs or alternate functions, causing hardware faults. Logging assumes GPIO chips and bases are initialized.

### Test Signals
Suspend/resume should preserve GPIO output values, pull settings, alternate functions, wake pins, and board-specific power rails. PM debug output should show intentional bootloader or sleep-state changes only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-s3c64xx.c

### Purpose
Implements S3C64xx power domains and suspend-to-RAM CPU/system preparation for legacy board boots.

### Important APIs, Types, And Functions
`struct s3c64xx_pm_domain` wraps a generic PM domain with enable/status bits. `s3c64xx_pd_off()` and `s3c64xx_pd_on()` manipulate `S3C64XX_NORMAL_CFG`. `s3c_pm_save_core()`, `s3c_pm_restore_core()`, `s3c_pm_configure_extint()`, `s3c64xx_cpu_suspend()`, `s3c64xx_pm_prepare()`, and `s3c64xx_pm_init()` implement suspend mechanics and domain registration.

### Control Flow
`s3c64xx_pm_initcall()` sets generic PM callbacks for S3C64xx. Board init calls `s3c64xx_pm_init()`, which initializes common PM and registers always-on and controllable genpd domains. On suspend, the common PM path saves registers, syncs wake masks, writes the resume address to `INFORM0`, clears wake status, configures WFI as sleep, drains write buffers, and executes the low-power instruction.

### State, Persistence, And Dependencies
State includes saved register arrays, `pm_cpu_prep`, `pm_cpu_sleep`, PM domain registration, wake masks, and system controller registers. It depends on `pm.c`, `pm-common.c`, wake-mask helpers, S3C64xx register headers, generic PM domains, and CPU resume assembly.

### Integration Points
Used by Cragganmore and other non-DT S3C64xx boards. It adds the framebuffer device to the F power domain when available.

### Risks
Power-domain status polling can time out. Wake mask synchronization must avoid masking all wake sources. Resume address and register restore order are hardware-critical. DT systems bypass much of this path.

### Test Signals
Power-domain on/off tests, framebuffer domain association, suspend/resume cycles, RTC/touch/SD wake events, and PM debug register checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.c

### Purpose
Provides the generic Samsung S3C suspend framework used by S3C64xx-specific PM code.

### Important APIs, Types, And Functions
Global state includes `s3c_pm_flags`, `s3c_irqwake_intmask`, `s3c_irqwake_eintmask`, `pm_cpu_prep`, and `pm_cpu_sleep`. `s3c_irqext_wake()` updates external wake masks. `s3c_pm_enter()` is the suspend entry callback. `s3c_pm_prepare()`, `s3c_pm_finish()`, and `s3c_pm_init()` install platform suspend operations.

### Control Flow
Suspend validation accepts memory suspend. Prepare calls PM debug checking. Enter verifies CPU callbacks, saves UARTs/GPIOs/core state, calls the SoC prepare hook, flushes caches, stores debug checks, invokes `cpu_suspend()`, then restores core/GPIO/UART state and runs debug validation. Finish cleans up checks.

### State, Persistence, And Dependencies
Wake masks and CPU callback pointers persist after SoC init. Runtime register/device state is saved by delegated UART/GPIO/core helpers. Dependencies include Linux suspend core, ARM `cpu_suspend()`, Samsung PM debug helpers, UART save/restore, GPIO PM, and SoC-specific hooks.

### Integration Points
`pm-s3c64xx.c` sets `pm_cpu_prep` and `pm_cpu_sleep` and calls `s3c_pm_init()`. IRQ code calls `s3c_irqext_wake()` through irqchip wake callbacks.

### Risks
If all wake sources are masked the system may not resume. Missing CPU callbacks abort suspend. GPIO/core restore ordering can affect peripherals. Global masks are legacy and not per-device-driver friendly.

### Test Signals
`echo mem > /sys/power/state`, wake-source enable/disable tests, UART state after resume, GPIO retention, and PM debug check output validate the framework.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.h

### Purpose
Declares internal S3C PM globals, callbacks, and helper functions shared across common and SoC-specific PM files.

### Important APIs, Types, And Functions
The header exposes `s3c_pm_flags`, wake mask globals, `pm_cpu_prep`, `pm_cpu_sleep`, `s3c_irqext_wake()`, `s3c_pm_init()`, core save/restore hooks, GPIO save/restore hooks, UART save/restore helpers, and PM debug/check hooks.

### Control Flow
No direct runtime flow; it defines the linkage used by the suspend sequence.

### State, Persistence, And Dependencies
State is held in extern globals implemented in `pm.c` and SoC PM files. Conditional declarations depend on PM and debug configuration.

### Integration Points
Included by S3C64xx PM, GPIO PM, and IRQ wake code.

### Risks
Global callback pointers and masks make initialization order important. Missing config stubs can hide untested PM paths.

### Test Signals
Compile coverage across PM enabled/disabled configs and suspend/resume runtime tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pwm-core.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pwm-core.h

### Purpose
Declares S3C64xx timer/PWM selection support for the Samsung PWM clocksource.

### Important APIs, Types, And Functions
`enum s3c64xx_timer_mode` names PWM timer channels. `s3c64xx_set_timer_source()` selects which timers are reserved for event/source clock roles.

### Control Flow
Board or DT map code calls the setter before `s3c64xx_timer_init()` initializes the PWM clocksource.

### State, Persistence, And Dependencies
The selected timer mask is stored in the S3C64xx PWM variant in `s3c64xx.c`. Dependencies include Samsung PWM clocksource support.

### Integration Points
Cragganmore and S3C64xx DT setup select PWM3/PWM4 before timer initialization.

### Risks
Choosing a timer used by board PWM consumers can conflict with backlight or other PWM users.

### Test Signals
Clocksource registration, timer interrupts, and PWM consumer availability validate the selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pwm-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock-s3c64xx.h

### Purpose
Defines S3C64xx clock and power-management register addresses and bit fields.

### Important APIs, Types, And Functions
The header maps registers through `S3C_VA_SYS`, including AHB/APB clock gates, `S3C64XX_NORMAL_CFG`, `S3C64XX_BLK_PWR_STAT`, `S3C64XX_PWR_CFG`, `S3C64XX_WAKEUP_STAT`, `S3C64XX_INFORM0`, and related PLL/clock control definitions.

### Control Flow
No runtime flow. PM, clock, and reset code use these macros with raw MMIO accessors.

### State, Persistence, And Dependencies
State is hardware register content. The header depends on S3C64xx system controller virtual mapping.

### Integration Points
Used by S3C64xx common init, PM domain control, suspend preparation, and wake status handling.

### Risks
Wrong bit definitions can power off active domains or prevent resume. Register access assumes `S3C_VA_SYS` was mapped.

### Test Signals
Clock initialization, PM domain toggling, suspend/resume, and wake-stat logging validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock.h

### Purpose
Compatibility wrapper for S3C64xx clock register definitions.

### Important APIs, Types, And Functions
No new definitions; includes `regs-clock-s3c64xx.h`.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on the S3C64xx register header.

### Integration Points
Used by code that includes generic local clock register names.

### Risks
Hard-selects S3C64xx definitions for all users in this folder.

### Test Signals
Compile and PM/clock runtime coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-memport-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-memport-s3c64xx.h

### Purpose
Defines S3C64xx GPIO memory-port drive/control registers used during PM save/restore.

### Important APIs, Types, And Functions
Macros name memory port drive and sleep configuration registers such as `S3C64XX_MEM0DRVCON`, `S3C64XX_MEM1DRVCON`, `S3C64XX_MEM0CONSTOP`, `S3C64XX_MEM1CONSTOP`, and sleep-mode memory control registers.

### Control Flow
No direct flow. `pm-s3c64xx.c` saves and restores these registers around suspend.

### State, Persistence, And Dependencies
State is hardware register content under the S3C64xx GPIO/system register area. Depends on GPIO register base macros.

### Integration Points
Critical for suspend/resume memory bus electrical state and drive strength restoration.

### Risks
Incorrect restore may destabilize external memory or board buses after resume.

### Test Signals
Suspend/resume with memory-intensive stress after wake validates these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-memport-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-s3c64xx.h

### Purpose
Defines S3C64xx GPIO bank base addresses, per-bank register offsets, external interrupt registers, and GPIO helper address macros.

### Important APIs, Types, And Functions
Macros include `S3C64XX_GPIOREG()`, bank bases `S3C64XX_GPA_BASE` through `S3C64XX_GPQ_BASE`, bank register accessors for `CON`, `DAT`, `PUD`, and drive control, plus EINT0 control/mask/pending registers.

### Control Flow
No runtime flow; GPIO, IRQ, setup, and PM code use these constants for MMIO.

### State, Persistence, And Dependencies
State is in hardware GPIO/EINT registers. The header depends on `S3C64XX_VA_GPIO` mapping and Samsung GPIO encoding.

### Integration Points
Used by external interrupt setup in `s3c64xx.c`, GPIO PM restore, setup helpers for I2C/SDHCI/keypad/framebuffer/SPI, and board GPIO calls.

### Risks
Register layout differs by bank; wrong offsets or pull definitions can misconfigure pins, break wakeup, or short board signals.

### Test Signals
GPIO direction/value/pull tests, external interrupt type tests, and peripheral pinmux validation are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio.h

### Purpose
Compatibility wrapper for S3C64xx GPIO register definitions.

### Important APIs, Types, And Functions
No new API; includes `regs-gpio-s3c64xx.h`.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on S3C64xx GPIO register header.

### Integration Points
Used by local code that includes generic `"regs-gpio.h"`.

### Risks
Not suitable for another S3C variant without changing the wrapper.

### Test Signals
Compile and GPIO runtime tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq-s3c64xx.h

### Purpose
Provides S3C64xx interrupt-controller register definitions needed by legacy code.

### Important APIs, Types, And Functions
The header maps IRQ-related register addresses and bit definitions for S3C64xx interrupt handling.

### Control Flow
No direct flow; irqchip setup and EINT handling use register macros from this family.

### State, Persistence, And Dependencies
State is hardware IRQ register state. Depends on mapped S3C64xx MMIO bases.

### Integration Points
Complements `irqs-s3c64xx.h` numeric IRQ definitions and `regs-irqtype.h` trigger encoding definitions.

### Risks
Interrupt mask/pending register mistakes can lose interrupts or cause storms.

### Test Signals
IRQ delivery, masking, acking, and wake events validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq.h

### Purpose
Compatibility wrapper for S3C64xx IRQ register definitions.

### Important APIs, Types, And Functions
No new definitions; includes `regs-irq-s3c64xx.h`.

### Control Flow
No runtime behavior.

### State, Persistence, And Dependencies
No state; depends on S3C64xx IRQ register definitions.

### Integration Points
Used by local code expecting a generic IRQ register include.

### Risks
Hard-selects S3C64xx behavior.

### Test Signals
Compile and IRQ runtime coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irqtype.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irqtype.h

### Purpose
Defines trigger-type encodings used in Samsung external interrupt configuration registers.

### Important APIs, Types, And Functions
Macros define low level, high level, falling edge, rising edge, and both edge encodings: `S3C2410_EXTINT_LOWLEV`, `S3C2410_EXTINT_HILEV`, `S3C2410_EXTINT_FALLEDGE`, `S3C2410_EXTINT_RISEEDGE`, and `S3C2410_EXTINT_BOTHEDGE`.

### Control Flow
No runtime flow. `s3c_irq_eint_set_type()` translates Linux `IRQ_TYPE_*` flags into these encodings.

### State, Persistence, And Dependencies
No state; encodings are written into EINT control registers.

### Integration Points
Used by S3C64xx external interrupt irqchip code.

### Risks
Wrong encoding produces inverted, missing, or constantly asserted interrupts.

### Test Signals
External interrupt type tests for rising, falling, both-edge, low-level, and high-level modes validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-irqtype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-modem-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-modem-s3c64xx.h

### Purpose
Defines S3C64xx modem interface register addresses used by system suspend save/restore.

### Important APIs, Types, And Functions
Key macros include modem MIFP control register definitions such as `S3C64XX_MODEM_MIFPCON`.

### Control Flow
No direct flow; PM code saves and restores the modem interface register.

### State, Persistence, And Dependencies
State is in S3C64xx modem MMIO registers. Depends on `S3C64XX_VA_MODEM`.

### Integration Points
`pm-s3c64xx.c` includes this header for `misc_save[]`.

### Risks
Incorrect modem bus state can affect attached modem or shared bus hardware across suspend.

### Test Signals
Suspend/resume on boards using modem/host interface functions validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-modem-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-sys-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-sys-s3c64xx.h

### Purpose
Defines S3C64xx system controller registers outside the main clock header.

### Important APIs, Types, And Functions
Macros cover system control registers such as `S3C64XX_SPCON` and related system configuration offsets.

### Control Flow
No runtime flow. PM and system setup code access these registers through macros.

### State, Persistence, And Dependencies
State is hardware system-controller content. Depends on mapped system-controller base.

### Integration Points
`pm-s3c64xx.c` saves and restores `S3C64XX_SPCON` during suspend.

### Risks
System configuration bit mistakes can break peripheral routing or resume.

### Test Signals
Peripheral routing after resume and PM register debug output validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-sys-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-syscon-power-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-syscon-power-s3c64xx.h

### Purpose
Defines S3C64xx power-control system-controller registers and bit fields used by suspend and power domains.

### Important APIs, Types, And Functions
Macros describe `S3C64XX_NORMAL_CFG`, `S3C64XX_PWR_CFG`, `S3C64XX_WAKEUP_STAT`, `S3C64XX_BLK_PWR_STAT`, domain enable bits, WFI sleep mode encoding, wake disable bits for RTC/touch/SD/MMC/modem/HSI, and `INFORM0`.

### Control Flow
No direct flow. PM domain code toggles domain bits; suspend preparation writes wake masks, resume address, and WFI mode.

### State, Persistence, And Dependencies
State is in always-on system controller registers. Depends on the S3C64xx system virtual base.

### Integration Points
Core to `pm-s3c64xx.c` and wake-mask synchronization.

### Risks
Power bits are destructive if wrong: they can gate active domains, block wake sources, or make WFI enter the wrong low-power mode.

### Test Signals
Domain power-cycle tests, suspend entry, wake-stat reads, and wake-source matrix testing validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-syscon-power-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-usb-hsotg-phy-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-usb-hsotg-phy-s3c64xx.h

### Purpose
Defines S3C64xx USB high-speed OTG PHY control register offsets and bit fields.

### Important APIs, Types, And Functions
Macros name PHY control, power, clock, reset, and tune fields under `S3C_VA_USB_HSPHY`.

### Control Flow
No direct flow. USB PHY setup code toggles power, reset, clock selection, and suspend bits using these definitions.

### State, Persistence, And Dependencies
State is USB PHY hardware register content. Depends on early mapping of the USB HSPHY virtual base.

### Integration Points
Used by `setup-usb-phy-s3c64xx.c` and DWC2 OTG platform initialization.

### Risks
Incorrect sequencing can leave the PHY in reset, powered down, or clocked from the wrong source.

### Test Signals
USB gadget/host enumeration, PHY suspend/resume, and register-level debug on cable attach validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/regs-usb-hsotg-phy-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c6410.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c6410.c

### Purpose
Implements S3C6410-specific legacy CPU initialization layered on common S3C64xx support.

### Important APIs, Types, And Functions
`s3c6410_map_io()` sets default SDHCI platform data and I2C device names. `s3c6410_init_irq()` initializes VICs with S3C6410 valid IRQ masks. `s3c6410_core_init()` registers the SoC subsystem bus for non-DT boots. `s3c6410_init()` registers the core device.

### Control Flow
Common CPU detection calls the map/init hooks from the CPU table. Core init skips DT boots and non-S3C64xx systems. Board machine descriptors call `s3c6410_init_irq()` as their IRQ initializer.

### State, Persistence, And Dependencies
State includes subsystem bus/device registration and platform-data defaults for SDHCI/I2C. Dependencies include S3C64xx common code, SDHCI helpers, I2C core helpers, and OF detection.

### Integration Points
Used by Cragganmore and other legacy S3C6410 machine descriptions.

### Risks
Defaults are not applied on DT boots, so DT must provide equivalent configuration. VIC0 IRQ7 is masked as missing; wrong masks affect interrupt availability.

### Test Signals
Non-DT S3C6410 boot, SDHCI/I2C driver names, subsystem registration, and IRQ enumeration validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c6410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.c

### Purpose
Provides common non-DT S3C64xx initialization: early I/O maps, CPU table, UART setup, PWM timer setup, core device registration, VIC initialization, and external interrupt demuxing.

### Important APIs, Types, And Functions
Public functions include `s3c64xx_set_xtal_freq()`, `s3c64xx_set_xusbxti_freq()`, `s3c64xx_set_timer_source()`, `s3c64xx_timer_init()`, `s3c64xx_init_io()`, and `s3c64xx_init_irq()`. Internal IRQ functions include `s3c_irq_eint_mask()`, `s3c_irq_eint_unmask()`, `s3c_irq_eint_ack()`, `s3c_irq_eint_set_type()`, demux handlers for EINT groups, and `s3c64xx_init_irq_eint()`.

### Control Flow
Board map code calls `s3c64xx_init_io()` to install static maps, detect CPU ID, initialize CPU-specific hooks, and register PWM platform data. Timer init calls Samsung PWM clocksource setup. IRQ init initializes the two ARM VICs after clock init. An arch initcall registers EINT0-27 as child IRQs and attaches chained handlers to grouped VIC lines on non-DT S3C64xx boots.

### State, Persistence, And Dependencies
State includes early crystal frequency globals, CPU table, static `map_desc` entries, the PWM variant, subsystem device, and IRQ chip registrations. Dependencies include ARM VIC irqchip, Samsung clock/PWM/GPIO code, OF detection, and S3C64xx map/register headers.

### Integration Points
Legacy board files call this during machine setup. DT machines use only selected common mapping/timer helpers while pinctrl handles EINT.

### Risks
Static MMIO mapping must match hardware. EINT type setup uses bank-specific pin mux rules for GPN/GPL/GPM; mistakes break GPIO interrupts. The platform is marked deprecated and scheduled for removal without maintainer feedback.

### Test Signals
Boot logs, clocksource operation, VIC IRQ delivery, EINT trigger-type tests, GPIO interrupt demuxing, and S3C6410 board boot validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.h

### Purpose
Declares common S3C64xx initialization APIs and conditional S3C6410 hooks.

### Important APIs, Types, And Functions
Exports `s3c64xx_init_irq()`, `s3c64xx_init_io()`, crystal setters, timer source/timer init APIs, and S3C6410 `map_io`, `init_irq`, and `init` hooks when configured. It also declares timer mode enum use through `pwm-core.h`.

### Control Flow
No direct flow; board and CPU table code call these functions during machine initialization.

### State, Persistence, And Dependencies
State is held by implementations in `s3c64xx.c` and `s3c6410.c`. Depends on ARM `map_desc` and Samsung SoC config symbols.

### Integration Points
Included by S3C64xx board files, DT machine setup, and CPU-specific init.

### Risks
Config-dependent stubs returning `NULL` require callers to handle disabled CPU support.

### Test Signals
Build coverage for S3C6410 enabled/disabled configs and legacy board boot validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sdhci.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sdhci.h

### Purpose
Declares Samsung SDHCI platform-data setters and S3C64xx default GPIO/platform setup helpers.

### Important APIs, Types, And Functions
Exports `s3c_sdhci[0-3]_set_platdata()`, `s3c64xx_setup_sdhci[0-2]_cfg_gpio()`, default setup helpers for S3C6400/S3C6410, and `s3c_sdhci_setname()`.

### Control Flow
CPU init sets default SDHCI data; board init can override host capabilities, card-detect type, and GPIO config through setters. SDHCI driver consumes platform data at probe.

### State, Persistence, And Dependencies
Copied platform data persists on platform devices. Depends on `linux/platform_data/mmc-sdhci-s3c.h` and board/SoC GPIO setup functions.

### Integration Points
`s3c6410.c` applies defaults, `mach-crag6410.c` overrides hosts 0 and 2, and `setup-sdhci-gpio-s3c64xx.c` implements GPIO muxing.

### Risks
Card-detect, bus width, and pinmux must match hardware. Wrong device names break driver matching.

### Test Signals
MMC enumeration, bus-width negotiation, card-detect behavior, and suspend/resume with `MMC_CAP_POWER_OFF_CARD` validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sdhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-fb-24bpp-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-fb-24bpp-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for a 24-bit framebuffer/LCD interface.

### Important APIs, Types, And Functions
`s3c64xx_fb_gpio_setup_24bpp()` applies special-function modes to the relevant LCD data/control GPIO ranges.

### Control Flow
Framebuffer platform data references this setup function; the framebuffer driver calls it during probe or initialization.

### State, Persistence, And Dependencies
State is GPIO mux/pull configuration in hardware. Depends on S3C64xx GPIO numbering and `s3c_gpio_cfgrange_nopull()`.

### Integration Points
Used by Cragganmore LCD platform data.

### Risks
Incorrect pin ranges produce blank display, color lane swaps, or bus contention.

### Test Signals
Framebuffer probe, visible 24 bpp output, and GPIO mux inspection validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-fb-24bpp-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for I2C bus 0.

### Important APIs, Types, And Functions
`s3c_i2c0_cfg_gpio(struct platform_device *dev)` sets the bus-0 SDA/SCL pins to the proper alternate function and pull state.

### Control Flow
I2C platform data names this callback and the I2C controller setup calls it before bus operation.

### State, Persistence, And Dependencies
State is GPIO mux/pull hardware configuration. Depends on S3C64xx GPIO helpers.

### Integration Points
Cragganmore registers PMIC and RTC devices on bus 0.

### Risks
Wrong pinmux or pull configuration prevents all bus-0 I2C devices from probing.

### Test Signals
I2C bus scan/probe for WM831x/RTC devices validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for I2C bus 1.

### Important APIs, Types, And Functions
`s3c_i2c1_cfg_gpio(struct platform_device *dev)` applies the bus-1 SDA/SCL alternate function and pull configuration.

### Control Flow
The I2C controller platform setup invokes this callback before registering or using bus 1.

### State, Persistence, And Dependencies
State is hardware pinmux. Depends on S3C64xx GPIO helpers and platform I2C data.

### Integration Points
Cragganmore uses bus 1 for module ID devices and audio codecs.

### Risks
Any misconfiguration blocks module probing and codec registration.

### Test Signals
Successful bus-1 device probing, especially `"wlf-gf-module"` and WM8311, validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-keypad-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-keypad-s3c64xx.c

### Purpose
Implements S3C64xx keypad GPIO mux configuration.

### Important APIs, Types, And Functions
`samsung_keypad_cfg_gpio(unsigned int rows, unsigned int cols)` configures row and column GPIO ranges for the Samsung keypad controller.

### Control Flow
The keypad platform data/driver calls this architecture hook using the board-provided row and column counts.

### State, Persistence, And Dependencies
State is GPIO alternate-function configuration. Depends on S3C64xx keypad pin layout and Samsung GPIO helpers.

### Integration Points
Used by Cragganmore keypad platform data from `mach-crag6410.c`.

### Risks
Row/column counts outside supported ranges can configure wrong pins. Incorrect muxing causes missing or ghosted keys.

### Test Signals
Matrix key events for every declared key and no ghost events validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-keypad-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-sdhci-gpio-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-sdhci-gpio-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for SDHCI hosts 0, 1, and 2.

### Important APIs, Types, And Functions
`s3c64xx_setup_sdhci0_cfg_gpio()`, `s3c64xx_setup_sdhci1_cfg_gpio()`, and `s3c64xx_setup_sdhci2_cfg_gpio()` configure command/clock/data pins according to the requested bus width.

### Control Flow
SDHCI platform data references these callbacks. The SDHCI driver calls the host-specific function before enabling a host.

### State, Persistence, And Dependencies
State is GPIO mux and pull configuration. Depends on S3C64xx GPIO bank layout and SDHCI platform data.

### Integration Points
S3C6410 defaults and Cragganmore overrides use these callbacks.

### Risks
Width-dependent ranges must be correct for 1-bit/4-bit/8-bit cases. Misconfigured pulls can break card detect or signal integrity.

### Test Signals
Card enumeration, data transfer at configured width, and host-specific GPIO inspection validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-sdhci-gpio-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c

### Purpose
Provides S3C64xx SPI platform setup for GPIO chip selects and bus configuration.

### Important APIs, Types, And Functions
The exported setup helper configures SPI controller platform data, including chip-select count and GPIO lookup usage.

### Control Flow
Board init calls the setup helper before SPI devices are registered so the controller driver can bind with the correct chip-select topology.

### State, Persistence, And Dependencies
State is platform data attached to the SPI controller plus GPIO lookup entries. Depends on `spi-s3c64xx` platform data and GPIO descriptors.

### Integration Points
Cragganmore calls `s3c64xx_spi0_set_platdata(0, 2)` and registers SPI codec devices.

### Risks
Chip-select numbering and lookup table names must match SPI board info. Wrong CS polarity or count prevents device probing.

### Test Signals
SPI controller probe, CS toggling, and WM0010/Arizona codec SPI transactions validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-usb-phy-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-usb-phy-s3c64xx.c

### Purpose
Controls S3C64xx USB high-speed OTG PHY power/reset sequencing for the DWC2 controller.

### Important APIs, Types, And Functions
The setup code uses USB PHY register macros to enable PHY clocks, clear power-down bits, assert/deassert reset, and configure PHY mode for OTG.

### Control Flow
DWC2 platform setup or board code installs platform data; controller initialization calls the PHY setup path before USB operation and may call suspend/powerdown paths later.

### State, Persistence, And Dependencies
State is PHY register configuration and controller platform data. Dependencies include `regs-usb-hsotg-phy-s3c64xx.h`, system clock/power registers, and DWC2 platform hooks.

### Integration Points
Cragganmore attaches `dwc2_hsotg_plat` data for OTG.

### Risks
PHY sequencing is timing-sensitive. Incorrect clock or reset control causes failed enumeration or resume.

### Test Signals
USB gadget/host enumeration, disconnect/reconnect cycles, and suspend/resume with USB wake disabled/enabled validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-usb-phy-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sleep-s3c64xx.S -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sleep-s3c64xx.S

### Purpose
Provides low-level S3C64xx resume assembly support.

### Important APIs, Types, And Functions
The key symbol is the CPU resume entry used as the physical address written into the SoC `INFORM0` resume register before suspend.

### Control Flow
Suspend code writes the resume symbol address, CPU enters sleep, ROM/PM hardware jumps back to the resume entry, and the assembly path restores enough CPU context to return to the generic ARM suspend framework.

### State, Persistence, And Dependencies
State is CPU context and the hardware resume vector. It depends on ARM suspend conventions, cache/MMU state expectations, and the SoC wake path.

### Integration Points
Referenced by `pm-s3c64xx.c` through `__pa_symbol(s3c_cpu_resume)`.

### Risks
Assembly must be position/physical-address safe at resume time. Any mismatch with cache/MMU state or resume address bricks suspend until reset.

### Test Signals
Successful resume from memory sleep and return to the kernel after `cpu_suspend()` validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sleep-s3c64xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/usb-phy.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/usb-phy.h

### Purpose
Declares USB PHY setup interfaces for S3C64xx board and controller code.

### Important APIs, Types, And Functions
The header exposes architecture USB PHY initialization or control hooks used by the DWC2/S3C USB setup code.

### Control Flow
No direct flow; controller/platform code calls the declared hooks during probe, suspend, or resume.

### State, Persistence, And Dependencies
State lives in PHY hardware registers and platform data. Depends on S3C64xx USB PHY register definitions.

### Integration Points
Used with `setup-usb-phy-s3c64xx.c` and Cragganmore OTG platform data.

### Risks
Missing declarations or config mismatches can leave USB setup unhooked.

### Test Signals
Build coverage and DWC2 PHY initialization validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/usb-phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.c

### Purpose
Synchronizes Samsung wake-disable register bits with Linux IRQ wake-enable state.

### Important APIs, Types, And Functions
`samsung_sync_wakemask(void __iomem *reg, const struct samsung_wakeup_mask *mask, int count)` reads a wake mask register, updates bits based on whether mapped IRQs are wake-enabled, ignores `NO_WAKEUP_IRQ` sentinels as always-disabled hardware wake bits, and writes the result back.

### Control Flow
SoC PM prepare code calls this before sleep. The function iterates the mapping table, tests IRQ wake state, clears disable bits for enabled wake IRQs, and sets disable bits otherwise.

### State, Persistence, And Dependencies
State is the SoC wake mask register. Dependencies include IRQ wake state tracking and raw MMIO accessors.

### Integration Points
`pm-s3c64xx.c` maps RTC, touch, MMC, modem, and HSI wake bits through this helper.

### Risks
The register uses disable-bit polarity, so inverted logic would mask desired wake sources. Stale IRQ wake state can either prevent wake or allow unwanted wakeups.

### Test Signals
Per-IRQ wake enable/disable tests and suspend wake-source matrix tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.h

### Purpose
Declares the wake-mask mapping structure and synchronization helper for Samsung suspend code.

### Important APIs, Types, And Functions
`NO_WAKEUP_IRQ` marks wake-mask bits without a Linux IRQ. `struct samsung_wakeup_mask` pairs an IRQ number with a wake-disable bit. `samsung_sync_wakemask()` applies the mapping.

### Control Flow
No direct flow; SoC PM code builds arrays and calls the helper.

### State, Persistence, And Dependencies
The mapping table is caller-owned static data. Depends on Linux IRQ numbers and SoC wake register bit definitions.

### Integration Points
Used by S3C64xx PM preparation.

### Risks
Incorrect IRQ-to-bit mapping directly affects suspend wake behavior.

### Test Signals
Wake source tests for each mapped IRQ validate the table and helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/wakeup-mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Kconfig

### Purpose
Defines build-time configuration for Samsung S5PV210/S5PC110 ARM machine support.

### Important APIs, Types, And Functions
`ARCH_S5PV210` selects the machine family and related Samsung infrastructure. `CPU_S5PV210` enables CPU support and selects required common code, clock, PM, and device-tree dependencies.

### Control Flow
No runtime flow. Kconfig selection controls which source files and features are built.

### State, Persistence, And Dependencies
State is kernel configuration. Dependencies include ARM architecture options, Samsung SoC support, and PM sleep configuration.

### Integration Points
Controls compilation of `s5pv210.c`, PM code, and sleep assembly through the Makefile.

### Risks
Missing selects can produce link failures or runtime boot failures. Over-selection can build legacy code for unsupported configs.

### Test Signals
`olddefconfig`, allyesconfig/COMPILE_TEST builds, and DT boot validate the config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Makefile

### Purpose
Lists S5PV210 machine objects built for the selected kernel configuration.

### Important APIs, Types, And Functions
`obj-y += s5pv210.o` builds the DT machine support. `obj-$(CONFIG_PM_SLEEP) += pm.o sleep.o` adds suspend/resume support when sleep PM is enabled.

### Control Flow
No runtime flow; Kbuild evaluates these object lists during compilation.

### State, Persistence, And Dependencies
State is build graph membership. Depends on Kconfig symbols.

### Integration Points
Ties `Kconfig` selections to compiled machine and PM code.

### Risks
PM declarations in `common.h` must match whether `pm.o` and `sleep.o` are built.

### Test Signals
Builds with and without `CONFIG_PM_SLEEP` validate object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/common.h

### Purpose
Declares common S5PV210 machine and PM entry points.

### Important APIs, Types, And Functions
`s5pv210_cpu_resume()` is the low-level resume symbol. `s5pv210_pm_init()` is declared when PM is enabled and stubbed otherwise.

### Control Flow
No direct flow. DT late init calls `s5pv210_pm_init()`, and PM code writes the physical resume symbol address before suspend.

### State, Persistence, And Dependencies
State lives in the implementation files and hardware registers. Depends on `CONFIG_PM`.

### Integration Points
Used by `s5pv210.c`, `pm.c`, and `sleep.S`.

### Risks
The PM stub means non-PM builds silently skip suspend setup. Resume symbol linkage must match the assembly implementation.

### Test Signals
Builds across PM configs and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/pm.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/pm.c

### Purpose
Implements S5PV210 suspend-to-RAM support for DT-based systems.

### Important APIs, Types, And Functions
Defines local `struct sleep_save`, `s3c_pm_do_save()`, `s3c_pm_do_restore_core()`, `s5pv210_read_eint_wakeup_mask()`, `s5pv210_cpu_suspend()`, `s5pv210_pm_prepare()`, `s5pv210_suspend_enter()`, suspend ops, syscore resume ops, and `s5pv210_pm_init()`.

### Control Flow
Late machine init registers syscore resume and suspend ops. Suspend enter reads EINT wake mask, rejects sleep if all internal and external wake sources are masked, saves UARTs, writes wake masks, writes `s5pv210_cpu_resume` to `S5P_INFORM0`, configures sleep oscillator and WFI sleep mode, disables SYSCON interrupts, saves core registers, flushes caches, and calls `cpu_suspend()`. On resume it restores UARTs, logs wake status, checks PM debug state, and syscore restore replays saved core registers.

### State, Persistence, And Dependencies
State includes `s5pv210_irqwake_intmask`, saved core register values, suspend ops registration, and system controller power registers. Dependencies include Samsung PM debug/UART helpers, ARM suspend/cacheflush, S5PV210 clock/power register definitions, and resume assembly.

### Integration Points
`s5pv210.c` calls `s5pv210_pm_init()` from DT late init. Pinctrl manages the external interrupt wake mask before this code reads it.

### Risks
The internal wake mask is currently a static all-masked value with a TODO for VIC wake support. If both internal and EINT masks are all ones, suspend is aborted. Wrong `INFORM0` or WFI configuration prevents resume.

### Test Signals
DT boot with `mem` suspend, EINT wake through pinctrl, UART restoration, wake-stat logging, and PM debug checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/regs-clock.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/regs-clock.h

### Purpose
Defines S5PV210 clock, power, reset, and PHY-control register addresses and bit fields.

### Important APIs, Types, And Functions
Macros map `S3C_VA_SYS` and `S5P_CLKREG()` to registers for PLL locks/control, clock sources/dividers/gates, status registers, `S5P_SWRESET`, power mode/config registers, wake masks/status, `S5P_INFORM*`, reset status, oscillator config, PHY controls, and sleep/WFI bit encodings.

### Control Flow
No direct flow. DT mapping code maps the clock syscon area, restart writes `S5P_SWRESET`, and PM code configures sleep/wake registers.

### State, Persistence, And Dependencies
State is hardware register content. Depends on early mapping of the S5PV210 clock controller to `S3C_VA_SYS`.

### Integration Points
Used by `s5pv210.c` and `pm.c`.

### Risks
Address or bit errors affect reset, clock gates, suspend, wake, and PHY power. These macros are raw MMIO and have no runtime validation.

### Test Signals
DT boot mapping, software restart, suspend/resume, and PHY/clock users validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/regs-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/s5pv210.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/s5pv210.c

### Purpose
Defines the DT machine descriptor and minimal early platform hooks for Samsung S5PC110/S5PV210 boards.

### Important APIs, Types, And Functions
`s5pv210_fdt_map_sys()` scans the flat DT for the `"samsung,s5pv210-clock"` node and maps its register range to `S3C_VA_SYS`. `s5pv210_dt_map_io()` initializes debug I/O and runs the scan. `s5pv210_dt_restart()` writes `S5P_SWRESET`. `s5pv210_dt_init_late()` registers cpufreq and initializes PM. `DT_MACHINE_START(S5PV210_DT, ...)` binds compatible strings.

### Control Flow
During early DT boot, map IO prepares the system controller mapping before register macros are used. Late init adds a simple cpufreq platform device and installs suspend support. Restart uses the mapped reset register.

### State, Persistence, And Dependencies
State is the static mapping and registered cpufreq device. Dependencies include flat-DT scanning, early `iotable_init()`, S5PV210 clock register definitions, and PM support.

### Integration Points
This is the top-level machine file for S5PV210 DT boots and delegates most devices to DT population.

### Risks
The flat-DT `reg` length check assumes two 32-bit cells via `sizeof(unsigned long) * 2`, which is sensitive to ARM word size assumptions. If the clock node is absent, reset and PM register access will fail.

### Test Signals
DT boot, early debug output, cpufreq device registration, software reboot, and suspend setup validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/s5pv210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/sleep.S -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/sleep.S

### Purpose
Provides low-level S5PV210 CPU resume code used after suspend wake.

### Important APIs, Types, And Functions
Exports `s5pv210_cpu_resume`, the physical resume target written to `S5P_INFORM0` before entering sleep.

### Control Flow
The PM code enters sleep through `cpu_suspend()`. On wake, boot/PM hardware branches to the resume symbol, which restores enough CPU state to re-enter the ARM suspend framework.

### State, Persistence, And Dependencies
State includes CPU context and the hardware resume register. Depends on ARM assembly suspend conventions and S5PV210 wake hardware.

### Integration Points
Referenced by `common.h` and `pm.c`.

### Risks
Resume code must execute correctly before normal virtual mappings and full kernel context are restored.

### Test Signals
Successful return from `cpu_suspend()` after memory sleep validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Kconfig

### Purpose
Defines configuration for Intel/StrongARM SA1100 machine family and supported boards.

### Important APIs, Types, And Functions
The menu enables `ARCH_SA1100` and board options such as Assabet, H3xxx/H3600, Collie, and related expansion-board or peripheral support. Selects pull in GPIO, clock, IRQ, MTD, PCMCIA, framebuffer, and PM dependencies as needed.

### Control Flow
No runtime flow; Kconfig choices decide which board files and common support build.

### State, Persistence, And Dependencies
State is kernel configuration. Dependencies span ARM SA1100 CPU support and board-specific device drivers.

### Integration Points
Controls the Makefile object list for SA1100 common and board code.

### Risks
Board options often encode old platform assumptions; missing selects surface as link errors or missing devices.

### Test Signals
Build coverage for individual board configs and multi-board configs validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Makefile

### Purpose
Defines SA1100 machine object compilation.

### Important APIs, Types, And Functions
Common objects include core generic, clock, GPIO/IRQ/PM support as selected. Board objects are conditionally added for Assabet, Collie, H3600/H3xxx, and related machines.

### Control Flow
No runtime flow; Kbuild compiles objects based on Kconfig symbols.

### State, Persistence, And Dependencies
State is the build graph.

### Integration Points
Maps SA1100 Kconfig board selections to source files.

### Risks
Missing common objects can break board link. Extra objects can register unwanted machine descriptors.

### Test Signals
Per-board kernel builds validate object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c

### Purpose
Implements the Intel Assabet SA1110 development board machine, including board-control GPIO, flash, LCD/video encoder, MCP/audio reset, Neponset expansion detection, CF power, LEDs, keys, UARTs, and machine descriptor setup.

### Important APIs, Types, And Functions
Exports `SCR_value`, `ASSABET_BCR_frob()`, and `assabet_uda1341_reset()`. Important helpers include `assabet_init_gpio()`, ADV7171 bit-bang routines, codec reset helpers, LCD power/backlight callbacks, `assabet_init()`, `map_sa1100_gpio_regs()`, `get_assabet_scr()`, `fixup_assabet()`, `assabet_uart_pm()`, `assabet_map_io()`, and `assabet_init_irq()`.

### Control Flow
Early fixup temporarily maps SA1100 GPIO registers, reads the system configuration register from GPIO pins, and detects Neponset. Map IO installs standard and board mappings, configures memory timing, and registers UARTs. IRQ init initializes SA1100 IRQs and the Assabet board-control GPIO chip. Machine init configures sleep/pin defaults, optionally registers Neponset, registers fixed regulators/CF, keys, LEDs, LCD, flash, MCP, and PCMCIA.

### State, Persistence, And Dependencies
State includes `SCR_value`, board control register shadowing through a GPIO chip, platform data for flash/LCD/MCP/regulators/keys/LEDs, and static I/O maps. Dependencies include SA1100 generic helpers, GPIO/LED/key/regulator/MTD/MCP/framebuffer subsystems, Neponset support, and machine tags.

### Integration Points
The `MACHINE_START(ASSABET, ...)` descriptor connects common SA1100 map, IRQ, timer, late PM, and restart paths with board-specific fixup and init.

### Risks
The SCR read is early and hardware-specific. Board-control register manipulation must be serialized through the GPIO abstraction. Neponset changes RAM/device behavior before paging. Video encoder bit-banging has timing assumptions.

### Test Signals
Assabet boot with and without Neponset, flash partitions, LCD/backlight, UART PM, CF power, MCP/audio reset, LEDs/keys, and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/clock.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/clock.c

### Purpose
Registers SA1100 clocks for the common clock framework.

### Important APIs, Types, And Functions
Defines GPIO27 clock enable/disable ops guarded by `tucr_lock`, MPLL rate recalculation from `PPCR`, and `sa11xx_clk_init()` to register fixed-factor/mux/hw clocks.

### Control Flow
`sa1100_init_irq()` calls `sa11xx_clk_init()` after IRQ/GPIO initialization. Clock consumers can then enable GPIO27-derived clock output or query CPU/MPLL rate.

### State, Persistence, And Dependencies
State includes clock framework registrations and protected `TUCR` hardware bits. Dependencies include CCF, SA1100 register macros, spinlocks, and CPU frequency state.

### Integration Points
Used by SA1100 generic initialization and devices requiring clock lookup.

### Risks
GPIO27 clock configuration shares `TUCR`; missing locking would race with other users. Rate calculation must match hardware PLL encoding.

### Test Signals
Clock registration logs, cpufreq rate reporting, and GPIO27 clock consumer enable/disable validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c

### Purpose
Implements the Sharp Zaurus Collie SA1100 board machine with LoCoMo, Scoop, PCMCIA, power/battery GPIOs, UART modem control, flash, LCD, MCP, and machine setup.

### Important APIs, Types, And Functions
Defines exported platform devices `colliescoop_device` and `collie_locomo_device`. Key helpers include `collie_uart_set_mctrl()`, `collie_uart_get_mctrl()`, `collie_uart_probe()`, `collie_uart_init()`, `collie_flash_init()`, `collie_set_vpp()`, `collie_flash_exit()`, `collie_init()`, and `collie_map_io()`.

### Control Flow
`collie_uart_init()` registers a LoCoMo driver at device init. Machine map installs common SA1100 and flash mappings, registers UART functions if LoCoMo is enabled, and maps UART ports. Machine init configures CPU GPIO/PPC/sleep registers, initializes MCP pin routing, adds GPIO lookup tables, registers platform devices, LCD, flash, MCP, and saves SharpSL parameters.

### State, Persistence, And Dependencies
State is board platform data for Scoop, LoCoMo, UCB1x00, MCP, battery/power, keys, flash partitions, and LCD timings. Dependencies include SA1100 generic helpers, LoCoMo, Scoop, SharpSL, GPIO descriptors, MTD, framebuffer, MCP, and machine descriptors.

### Integration Points
`MACHINE_START(COLLIE, ...)` connects Collie-specific map/init to SA1100 IRQ/timer/late PM/restart.

### Risks
LoCoMo modem-control callbacks depend on the driver being probed. GPIO and PPC register initialization is broad and can affect many pins. Flash Vpp and LCD power are board-specific.

### Test Signals
Collie boot, LoCoMo probe, serial modem controls, LCD, flash partitions, power/battery GPIO lookup, PCMCIA/Scoop, and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.c

### Purpose
Provides common SA1100 platform support: CPU speed table, restart/poweroff, common platform devices, MTD/LCD/MCP/PCMCIA registration helpers, fixed regulators, static I/O maps, timer, IRQ, memory-bus control, and wake helpers.

### Important APIs, Types, And Functions
Exports `sa11x0_freq_table`, `sa11x0_getspeed()`, `sa11x0_restart()`, `sa11x0_ppc_configure_mcp()`, `sa11x0_register_mcp()`, `sa11x0_register_lcd()`, `sa11x0_register_pcmcia()`, `sa11x0_register_mtd()`, `sa11x0_init_late()`, `sa11x0_register_fixed_regulator()`, `sa1100_map_io()`, `sa1100_timer_init()`, `sa1100_init_irq()`, `sa1110_mb_disable()`, `sa1110_mb_enable()`, `sa11x0_gpio_set_wake()`, and `sa11x0_sc_set_wake()`.

### Control Flow
`arch_initcall(sa1100_init)` registers poweroff, regulator constraints, watchdog, and common platform devices. Board machine descriptors call common map/timer/IRQ helpers and then board init. Late init initializes PM. Helper functions let board files attach platform data to common devices before drivers probe.

### State, Persistence, And Dependencies
State includes common platform devices/resources, DMA masks, cpufreq table, fixed-regulator init data, static I/O maps, and wake register bits. Dependencies include SA1100 register macros, platform devices, PXA timer, SA11x0 IRQ/GPIO init, clocks, regulators, MTD, framebuffer, MCP, PCMCIA, and PM.

### Integration Points
All SA1100 board files in this subset call these helpers for common hardware and machine descriptors.

### Risks
Raw register writes affect global CPU pin, wake, and memory bus state. Fixed regulator helper allocates init data and does not check platform registration failure. Static maps reserve high virtual regions.

### Test Signals
Board boot, common device probes, cpufreq speed reporting, watchdog/RTC/DMA/UART/MCP/LCD registration, IRQ delivery, timer ticks, and wake-source tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.h

### Purpose
Declares shared SA1100 board support APIs and helpers.

### Important APIs, Types, And Functions
Declares common init functions, restart/late-init hooks, memory bank macro `SET_BANK`, memory bus control, cpufreq helpers, MTD/MCP/LCD/PCMCIA/fixed-regulator registration helpers, `sa11xx_clk_init()`, and PM init stubs.

### Control Flow
No direct flow; board files call these functions from machine map/init/fixup callbacks.

### State, Persistence, And Dependencies
State lives in `generic.c` or board files. Depends on cpufreq, reboot, platform data forward declarations, and config-dependent PM.

### Integration Points
Included by Assabet, Collie, H3600, H3xxx, and common code.

### Risks
The broad helper surface makes board initialization order important. `SET_BANK` assumes a `meminfo` pointer named `mi`.

### Test Signals
Compile coverage across board configs and boot of each board validate declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3600.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3600.c

### Purpose
Defines the Compaq iPAQ H3600 machine-specific LCD setup layered on common H3xxx support.

### Important APIs, Types, And Functions
`h3600_lcd_request()` lazily requests and initializes LCD power GPIOs. `h3600_lcd_power()` toggles LCD power/control rails. `h3600_lcd_info` defines 320x240 16bpp panel timing and RGB layout. `h3600_map_io()` and `h3600_mach_init()` delegate to H3xxx common setup.

### Control Flow
Machine map calls `h3xxx_map_io()`. Machine init calls `h3xxx_mach_init()` then registers the H3600 LCD info. The framebuffer driver calls the LCD power callback as needed.

### State, Persistence, And Dependencies
State includes a static `h3600_lcd_ok` latch and LCD platform data. Dependencies include H3xxx EGPIO definitions, SA1100 framebuffer, GPIO API, and SA1100 generic helpers.

### Integration Points
`MACHINE_START(H3600, ...)` uses SA1100 IRQ/timer/late PM/restart and H3xxx shared board setup.

### Risks
LCD GPIO request failure disables power control. The one-time latch assumes GPIO ownership remains valid. Power rails must be sequenced safely for the panel.

### Test Signals
H3600 boot, framebuffer probe, LCD power on/off, and H3xxx common device probing validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c

### Purpose
Provides common Compaq iPAQ H3100/H3600 board support for flash, UART power/wake, EGPIO, keys, microcontroller ASIC, PCMCIA GPIO lookup, I/O mapping, and base pin/suspend setup.

### Important APIs, Types, And Functions
Important helpers are `h3xxx_set_vpp()`, `h3xxx_flash_init()`, `h3xxx_flash_exit()`, `h3xxx_uart_pm()`, `h3xxx_uart_set_wake()`, `h3xxx_mach_init()`, and `h3xxx_map_io()`. It exports `h3xxx_micro_asic` as a platform device.

### Control Flow
`h3xxx_mach_init()` installs PCMCIA and UART GPIO lookups, registers SA1100 UART PM/wake callbacks, registers flash, and adds EGPIO, key, and micro ASIC devices. `h3xxx_map_io()` maps SA1100 common I/O and H3600 bank/EGPIO regions, registers UART3 as the common serial port, and initializes PPC/GPIO sleep defaults.

### State, Persistence, And Dependencies
State includes flash partition/platform data, EGPIO platform data, key platform data, micro ASIC resources, GPIO lookup tables, and static map descriptors. Dependencies include SA1100 generic helpers, HTC EGPIO, GPIO keys, MTD CFI, SA11x0 serial, PCMCIA, and H3xxx machine constants.

### Integration Points
Used by `h3600.c` and other H3xxx machine variants as common board support.

### Risks
UART wake modifies global `PWER` bits for GPIO23/GPIO25. Flash Vpp relies on EGPIO availability. Broad GPIO reset in map setup may conflict with bootloader-provided states if assumptions change.

### Test Signals
H3600/H3xxx boot, flash writes with Vpp, serial power management/wake, EGPIO registration, keys, micro ASIC resources, PCMCIA detection, and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c -->
