# sources/distributed-fs/ceph-client/include/soc/tegra/pmc.h

## Purpose

`pmc.h` declares the Tegra Power Management Controller API for CPU power, powergate domains, I/O pad power, suspend-mode programming, and legacy powergate wrappers.

## Important APIs, Types, and Functions

It defines powergate IDs for CPU, 3D, PCIe, display, XUSB, VIC, NVDEC, audio, DFD, VE2, and others. `enum tegra_io_pad` identifies many I/O pad groups including audio, camera, CSI/DSI, DP/HDMI, eMMC/SDMMC, PCIe, UFS, USB, UART, SPI, GPIO, and AO/HV pads.

CPU helpers include `tegra_pmc_cpu_is_powered()`, `tegra_pmc_cpu_power_on()`, and `tegra_pmc_cpu_remove_clamping()`. Enabled PMC builds expose `devm_tegra_pmc_get()`, object-oriented `tegra_pmc_powergate_*()` calls, `tegra_pmc_powergate_sequence_power_up()`, I/O pad enable/disable calls, legacy `tegra_powergate_*()` and `tegra_io_pad_*()` wrappers, suspend mode set/enter, and `tegra_pmc_core_domain_state_synced()`. Disabled builds return `-ENOSYS`, no-op, or `false`. `tegra_pmc_get_suspend_mode()` returns the actual mode only when PMC and PM sleep are enabled.

## Control Flow

Power-up usually combines reset, clock, powergate enable, and clamp removal; the sequence helper captures the common order and returns with the clock enabled. I/O pad calls power voltage domains. Suspend calls program and enter PMC-controlled low-power state.

## State and Persistence

State is in PMC hardware registers, rail state, clamp state, and suspend-mode registers. The header only declares accessors.

## Dependencies and Integration Points

The header includes Linux reboot declarations and `soc/tegra/pm.h`, integrating with clocks, reset controls, generic power domains, CPU hotplug, suspend, pinctrl/pad power, PCIe, USB, display, and media drivers.

## Risks

Power sequencing mistakes can leave domains clamped, clocks/reset ordered incorrectly, or pads unpowered. Mixing legacy global APIs and device-managed APIs can complicate lifetime and ownership.

## Test Signals

Test powergate on/off/clamp removal, sequence power-up ordering, I/O pad enable/disable, CPU power-on, suspend-mode get/set/enter, resume after domain power cycles, and disabled-config behavior.
