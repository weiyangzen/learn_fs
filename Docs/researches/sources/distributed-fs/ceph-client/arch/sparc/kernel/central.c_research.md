<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/central.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/central.c

Purpose: Sunfire/Starfire/Wildfire central clock-board and FireHose Controller platform support, mainly registering LED child devices and normalizing FHC control state.

Important APIs and control flow: `clock_board_probe()` maps clock frequency/control/version resources, determines slot count from status/version registers, creates a `sunfire-clockboard-leds` platform device using the clock control register, and logs system slot count. `fhc_probe()` maps FHC PREGS, identifies central versus board FHC, derives board number from BSR or `board#`, detects JTAG master, optionally registers `sunfire-fhc-leds`, clears power/line control bits, sets `IXIST` for non-central boards, and logs ID fields. `sunfire_init()` registers both platform drivers at `fs_initcall`.

State, dependencies, and risks: state is per-device mapped UPA register pointers and child LED platform devices. Dependencies include OF resources/names, UPA byte/word accessors, `asm/fhc.h`, and platform device registration. Risks include resource-count assumptions, no remove path for child devices, board-number heuristics, and register writes affecting chassis LEDs/power lines. Test signals are Sunfire boot logs, LED child device creation, slot-count detection, and FHC control register state after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/central.c -->
