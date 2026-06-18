# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-jasperlake.c

## Purpose

`pinctrl-jasperlake.c` supplies the Jasper Lake PCH pin and community map for the shared Intel pinctrl core. It covers 233 pins across GPP_F, SPI, GPP_B/A/S/R/H/D, vGPIO, GPP_C, HVCMOS, GPP_E, and GPP_G.

## Important APIs, Types, And Functions

The file uses `JSL_COMMUNITY()` with Jasper Lake register offsets and explicit `INTEL_GPP()` pad groups. `jsl_soc_data` contains pins and communities but no named function/group mux tables. ACPI HID `INT34C8` selects the data and the platform driver delegates to `intel_pinctrl_probe_by_hid()`.

## Control Flow

`module_platform_driver()` registers `jasperlake-pinctrl`. Probe retrieves `&jsl_soc_data` from ACPI match data and calls the common probe. The core maps four communities, normalizes explicit GPPs, skips NOMAP groups where configured, and creates GPIO and IRQ infrastructure.

## State And Persistence

Static topology includes GPIO bases such as GPP_F at 320, GPP_B at 32, GPP_A at 64, GPP_S at 96, GPP_R at 128, GPP_H at 160, GPP_D at 192, vGPIO at 224, GPP_C at 256, GPP_E at 288, and GPP_G forced to GPIO base zero. SPI and HVCMOS are NOMAP. Runtime state is held by the common core.

## Dependencies And Integration Points

The file integrates with ACPI `INT34C8`, the Intel core, PM callbacks, and gpiolib/pinctrl via common code. Hardware coverage includes eMMC, SPI flash, eSPI, SoundWire/HDA/I2S, ISH, CNV/vGPIO, display, and SD3 pads.

## Risks

Sparse and non-monotonic GPIO bases are intentional but risky for consumers and table edits. GPP_G uses `INTEL_GPIO_BASE_ZERO`, so it can overlap conceptually with pin numbers unless callers use gpiolib ranges correctly. Since no mux functions are declared, alternate-function selection must rely on firmware or other mechanisms rather than named pinmux functions from this driver.

## Test Signals

Probe on `INT34C8` should register expected sparse GPIO ranges and skip SPI/HVCMOS. GPIO line names should match the table. IRQ tests should cover multiple communities and base-zero GPP_G. Suspend/resume tests should confirm requested lines in sparse ranges restore correctly.
