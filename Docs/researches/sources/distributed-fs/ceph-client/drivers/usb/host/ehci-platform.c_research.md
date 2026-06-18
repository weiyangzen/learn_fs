# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-platform.c

## Purpose
Generic platform/OF/ACPI EHCI glue. It supplies default clock/reset/power handling, supports platform data overrides, parses common DT endian and quirk properties, handles suspend/resume, and includes an R-Car Gen3 polling workaround that rebinds the companion controller when port status sticks.

## Important APIs, types, and functions
`struct ehci_platform_priv` stores up to four clocks, reset array, reset-on-resume flag, and polling timer/work. `ehci_platform_reset()` sets Synopsys/no-watchdog/Broadcom FIFO quirks and calls `ehci_setup()`. `ehci_platform_power_on()`/`power_off()` manage clocks. `ehci_platform_probe()`, remove, suspend, and resume own lifecycle. `quirk_poll_check_port_status()`, `quirk_poll_timer()`, and `quirk_poll_work()` implement the R-Car recovery path.

## Control flow
Probe selects platform data or defaults, coerces a 32-bit or 64-bit DMA mask, creates the HCD, parses DT properties for endian descriptors/registers, spurious over-current, reset-on-resume, integrated TT, Aspeed, and R-Car polling, acquires clocks and resets, validates endian config options, powers on, maps MMIO, sets TPL support, and calls `usb_add_hcd()`. Remove stops poll work, removes the HCD, powers off, asserts resets, drops clocks, and clears default platform data. Suspend stops polling, suspends EHCI, powers down, and asserts reset; resume reverses reset/power, waits for a companion device if present, resumes EHCI, refreshes runtime PM state, and restarts polling.

## State and persistence behavior
State spans `ehci_platform_priv`, platform data callbacks, HCD/EHCI quirk flags, clocks, resets, timer/work items, and hardware registers. Runtime PM active state is reestablished on resume.

## Dependencies and integration points
Depends on OF/ACPI/platform matching, clock/reset frameworks, `usb_ehci_pdata`, USB companion lookup, sys_soc matching, DMA mapping, and EHCI core. It matches generic, VIA/WonderMedia, Cavium Octeon, Aspeed AST2700, and ACPI `PNP0D20`.

## Risks and edge cases
Default platform data is temporarily installed on the device and must be cleared. Clock acquisition handles `-EPROBE_DEFER` specially. Endian DT properties require matching Kconfig support. The R-Car workaround intentionally unbinds/rebinds a companion driver from delayed work, which is powerful and timing-sensitive.

## Test signals
DT and ACPI probe, clock counts from zero to four, reset failures, endian property combinations, 64-bit DMA match data, Aspeed and Broadcom quirks, R-Car stuck-port recovery, suspend/resume with companion wait, TPL support, and failure-path cleanup are important tests.
