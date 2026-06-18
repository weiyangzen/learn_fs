# sources/distributed-fs/ceph-client/drivers/soc/ti/pm33xx.c

## Purpose
This file implements AM33xx/AM43xx platform power management glue. It copies suspend code and data into SRAM, coordinates EMIF and RTC-only suspend support, communicates with the WKUP M3 firmware, installs platform suspend operations, and invokes SoC-specific PM platform callbacks.

## Important APIs, Types, And Functions
Important functions include `am33xx_push_sram_idle`, `am33xx_do_sram_idle`, `am33xx_pm_suspend`, `am33xx_pm_begin`, `am33xx_pm_end`, `am33xx_pm_set_ipc_ops`, `am33xx_pm_alloc_sram`, `am33xx_pm_rtc_setup`, `am33xx_pm_probe`, and `am33xx_pm_remove`. State comes through `struct am33xx_pm_platform_data`, `struct am33xx_pm_sram_addr`, `struct wkup_m3_ipc`, genalloc SRAM pools, RTC/nvmem scratch registers, and optional GIC distributor mapping for IRQ retriggering.

## Control Flow
Probe verifies machine compatibility, obtains platform PM ops, maps GIC, gets SRAM function addresses, acquires WKUP M3 IPC, allocates code/data SRAM pools, sets up RTC scratch state, copies WFI/EMIF/data tables to SRAM, programs M3 memory type and resume address, registers suspend ops, enables runtime PM, and calls SoC PM init with the SRAM idle callback. Suspend begin prepares M3 for deep sleep or standby. Enter either performs RTC-only/off-mode sequencing or normal SRAM WFI. End finishes low power, clears RTC magic, optionally retriggers RTC IRQ, and calls platform finish hooks.

## State And Persistence
Global state tracks mapped RTC/GIC bases, clocks, SRAM pool addresses, copied SRAM entry point, suspend flags, RTC-only flags, wake source data, and M3 IPC handle. RTC scratch nvmem persists across low-power transitions for bootloader/ROM resume coordination.

## Dependencies And Integration Points
It depends on OMAP/AMx3 platform data, SRAM genalloc nodes, `ti-emif-sram`, `wkup_m3_ipc`, RTC/OMAP RTC helpers, clocks, nvmem, runtime PM, ARM suspend APIs, and SoC compatibility strings `ti,am33xx`/`ti,am43`.

## Risks And Test Signals
Risks include fragile SRAM symbol offset copying, missing M3/EMIF/RTC dependencies causing probe deferral, RTC-only scratch incompatibility, GIC hard-coded AM43xx base, and suspend/resume data corruption. Test signals are successful probe, suspend/resume through standby and mem, M3 PM status 0, correct wake-source logging, RTC-only resume when supported, and no SRAM allocation/free leaks.
