# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.c

## Purpose

`intel_soc_dts_iosf.c` is the shared IOSF sideband implementation for Intel SoC digital thermal sensors, registering two sensor zones and handling programmable thresholds and interrupts.

## Important APIs, Types, and Functions

Exports are `intel_soc_dts_iosf_init()`, `intel_soc_dts_iosf_exit()`, and `intel_soc_dts_iosf_interrupt_handler()`. `update_trip_temp()` writes PTPS/PTMC/TE registers with rollback. `sys_get_curr_temp()` converts DTS distance-to-TjMax into millicelsius. `add_dts_thermal_zone()` registers `soc_dts0`/`soc_dts1`. `set_trip()` initializes thermal trip descriptors.

## Control Flow

Init checks IOSF and TjMax, allocates `struct intel_soc_dts_sensors`, initializes locks, resets trip slots, configures passive or critical trips, and registers/enables each DTS zone. Interrupt handling deasserts APIC status, checks sticky trip bits, clears them, and updates both thermal zones. Exit unregisters zones, restores saved enable state, resets trips, and frees memory.

## State and Persistence Behavior

Per-instance state records TjMax, interrupt type, locks, and two sensor entries with saved enable state. Firmware/PMC registers hold actual sensor enable, threshold, status, and interrupt enable bits.

## Dependencies and Integration Points

It depends on IOSF MBI, Intel TCC, thermal core, and callers such as `intel_soc_dts_thermal.c` and legacy processor thermal PCI DTS support. Interrupt type controls whether APIC and/or MSI bits are set.

## Risks and Test Signals

Risks include rollback writing `store_te_out` to PTMC in one error path, shared threshold programming across sensors, BIOS-used trip slots becoming read-only, interrupt sticky clearing races, and TjMax dependency. Test signals include two-zone registration, writable/read-only trip selection, APIC/MSI interrupt config, interrupt handler zone updates, exit restore, and IOSF error injection.
