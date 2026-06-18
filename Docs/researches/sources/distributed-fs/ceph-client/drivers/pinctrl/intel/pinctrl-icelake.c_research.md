# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-icelake.c

## Purpose

`pinctrl-icelake.c` supports Intel Ice Lake-LP and Ice Lake-N PCH GPIO/pinctrl controllers. It maps two hardware variants behind different ACPI IDs and provides rich LP mux groups for SPI, I2C, and UART functions.

## Important APIs, Types, And Functions

The file defines separate register offset families, `ICL_LP_*` and `ICL_N_*`, and community macros `ICL_LP_COMMUNITY()` and `ICL_N_COMMUNITY()`. `icllp_soc_data` includes pin groups/functions; `icln_soc_data` is mostly pin and community topology. ACPI IDs `INT3455` and `INT34C3` select LP and N data respectively. Several pad groups use `INTEL_GPIO_BASE_NOMAP` or `INTEL_GPIO_BASE_ZERO`, exercising the common core's special GPIO base handling.

## Control Flow

`module_platform_driver()` registers `icelake-pinctrl`. `intel_pinctrl_probe_by_hid()` passes the matched variant data to `intel_pinctrl_probe()`. The core copies communities, maps BARs, normalizes explicit pad groups via `intel_pinctrl_add_padgroups_by_gpps()`, registers mux/group callbacks, and creates GPIO ranges only for mapped pad groups.

## State And Persistence

Static state covers Ice Lake-LP pins 0-240 and Ice Lake-N pins 0-212. Runtime state lives in `struct intel_pinctrl`, including MMIO register pointers and suspend/resume contexts. NOMAP groups such as HVCMOS, JTAG, and SPI pads intentionally do not become GPIO lines.

## Dependencies And Integration Points

The driver integrates with ACPI, the common Intel pinctrl core, GPIO/pinctrl frameworks, and PM. LP function groups are consumed by board/device pinctrl states for SPI/I2C/UART. GPIO bases are sparse and hardware-defined; this matters for firmware resources, gpiolib line numbering, and IRQ domains.

## Risks

GPIO base special values create sharp edges: a group marked NOMAP cannot be requested through gpiolib, while `INTEL_GPIO_BASE_ZERO` forces a group to start at GPIO 0. Incorrect use would break existing firmware GPIO resources. LP per-pin SPI mode arrays must stay aligned with pin arrays. Variant mixups between `INT3455` and `INT34C3` would map different pad names and register offsets.

## Test Signals

Probe should distinguish LP and N by ACPI ID. GPIO range enumeration should skip NOMAP groups and correctly map base-zero GPP_G on Ice Lake-N. Pinmux validation should cover LP SPI0/SPI1/SPI2 mode arrays and I2C/UART groups. IRQ tests should include sparse GPIO bases and ACPI-owned pad rejection.
