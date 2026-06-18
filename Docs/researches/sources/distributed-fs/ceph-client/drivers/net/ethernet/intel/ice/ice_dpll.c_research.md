# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dpll.c

## Purpose
`ice_dpll.c` implements Intel ice driver integration with the Linux DPLL subsystem. It discovers DPLL/CGU capabilities, registers EEC and PPS DPLL devices and their pins, exposes pin control callbacks through `struct dpll_device_ops` and `struct dpll_pin_ops`, handles SMA/U.FL software-controlled wrapper pins, supports recovered clock (`rclk`) pin-on-pin topology, polls hardware state, and emits DPLL netlink notifications when lock state, active input, or phase offset changes. The file has two major hardware paths: E810-style CGU-owned DPLLs and E825C generic-3K hardware where recovered clock parents can come from firmware-described fwnode pins.

## Important APIs, Types, and Functions
- Local type `enum ice_dpll_pin_type` classifies input, output, recovered-clock input, and software-controlled pins so common callbacks can route to the correct AdminQ command.
- `ice_dpll_is_sw_pin()` hides raw CGU pins that are represented to userspace as logical SMA/U.FL software pins.
- Frequency APIs are implemented by `ice_dpll_pin_freq_set()`, `ice_dpll_frequency_set()`, input/output wrappers, and software-pin wrappers that redirect to the currently active backing input or output pin.
- State APIs are implemented by `ice_dpll_pin_enable()`, `ice_dpll_pin_disable()`, `ice_dpll_pin_state_update()`, `ice_dpll_pin_state_set()`, and input/output/SMA/U.FL/recovered-clock wrappers.
- Priority APIs are implemented by `ice_dpll_hw_input_prio_set()`, `ice_dpll_input_prio_get/set()`, and software-pin priority wrappers.
- Phase APIs include `ice_dpll_pin_phase_adjust_get/set()`, `ice_dpll_phase_offset_get()`, `ice_dpll_is_pps_phase_monitor()`, and `ice_dpll_pps_update_phase_offsets()`.
- Embedded-sync and reference-sync APIs are implemented by `ice_dpll_input_esync_get/set()`, `ice_dpll_output_esync_get/set()`, software wrappers, `ice_dpll_input_ref_sync_get/set()`, `ice_dpll_init_ref_sync_inputs()`, and reference-sync registration.
- Recovered-clock support uses `ice_dpll_rclk_update()`, `ice_dpll_rclk_update_e825c()`, `ice_dpll_synce_update_e825c()`, and `ice_dpll_rclk_state_on_pin_get/set()`.
- DPLL registration uses `ice_dpll_init_dpll()`, `ice_dpll_deinit_dpll()`, `ice_dpll_init_pins()`, `ice_dpll_deinit_pins()`, `ice_dpll_init_rclk_pin()`, `ice_dpll_init_direct_pins()`, `ice_dpll_register_pins()`, and `ice_dpll_release_pins()`.
- E825C fwnode pin support uses `ice_dpll_pin_node_get()`, `ice_dpll_init_fwnode_pin()`, `ice_dpll_pin_notify()`, and `ice_dpll_pin_notify_work()`.
- Public entry points are `ice_dpll_init()` and `ice_dpll_deinit()`, gated by `CONFIG_PTP_1588_CLOCK` in the header.

## Control Flow
Initialization starts at `ice_dpll_init()`, dispatching E825 hardware to `ice_dpll_init_e825()` and other hardware to `ice_dpll_init_e810()`. E810 initialization creates the DPLL mutex, reads CGU abilities with `ice_aq_get_cgu_abilities()`, allocates input/output/priority arrays, initializes pin metadata, registers DPLL devices, registers pins and pin-on-pin recovered clock relationships, and starts a periodic kthread worker when the PF owns CGU support. E825 initialization focuses on fwnode parent pins and recovered clock registration, uses a completion to coordinate notifier work, and sets `ICE_FLAG_DPLL` only after successful setup.

At runtime, userspace DPLL netlink callbacks enter the registered ops tables. Most setters reject operations during PF reset through `ice_dpll_is_reset()`, acquire `pf->dplls.lock`, issue a CGU AdminQ or register-level command, update cached pin state, then release the lock. Software SMA/U.FL callbacks first update the PCA9575 SMA control register, then enable or disable the backing CGU input/output pin and notify the paired logical pin because one physical routing change can affect two exposed pins.

Periodic monitoring runs through `ice_dpll_periodic_work()`. It skips polling during reset, locks the DPLL state, updates EEC and PPS state with `ice_dpll_update_state()`, optionally reads PPS phase offset measurements, unlocks, emits device/pin notifications, and reschedules at 500 ms or 10 ms on transient update failure. After too many consecutive CGU acquisition failures it disables further periodic work.

Deinitialization clears `ICE_FLAG_DPLL`, stops the worker for CGU-owned devices, unregisters pin relationships, releases DPLL pins/devices, frees allocated arrays, and destroys the mutex. E825 fwnode deinit unregisters notifiers, flushes workqueue work, drops fwnode pin references, and destroys the single-thread workqueue.

## State and Persistence Behavior
The file maintains runtime-only driver state in `pf->dplls`, including cached input/output pin arrays, SMA/U.FL logical pin structures, recovered-clock pin state, DPLL indices, input priorities, current and previous active input, current and previous lock status, phase offsets, and periodic worker counters. Hardware configuration persists in device CGU state via AdminQ commands and CGU/SMA control registers, but the driver-side cache is rebuilt at probe/init. `ICE_FLAG_DPLL` is the primary initialized-state flag; `dpll_init` completion coordinates asynchronous fwnode notifier work. There is no disk persistence.

## Dependencies and Integration Points
This file depends on Linux DPLL APIs, kernel work/kthread primitives, PCI DSN clock-id generation, fwnode properties, netdevice pin association, and the ice AdminQ/CGU helpers for CGU abilities, input/output pin config, CGU state, phase measurements, recovered clock info, PHY recovered clock output, E825C TSPLL helpers, and SMA control. It integrates with PF reset state, PTP port metadata, device IDs/mac types, and trace/debug logging.

## Risks and Edge Cases
- Many callbacks rely on cached `pin->flags`, `pin->freq`, and state arrays being refreshed before writes; stale cache can preserve or clear the wrong hardware bits.
- Error unwinding must maintain balanced DPLL pin/device reference counts, especially around partial pin registration and fwnode pin discovery.
- Software SMA/U.FL routing is subtle: a change to one logical pin can disable or activate a paired logical pin, so missing peer notifications or backing-pin updates can mislead userspace.
- E825C recovered-clock support depends on firmware fwnode names and asynchronous DPLL pin create/delete notifiers; initialization ordering races are mitigated by the completion but remain test-sensitive.
- The periodic worker disables itself after `ICE_CGU_STATE_ACQ_ERR_THRESHOLD`; transient firmware/AdminQ failures above the threshold leave userspace with stale DPLL state until reinit.
- `ice_dpll_init_info_sw_pins()` writes SMA control defaults during initialization, which changes hardware routing state and can surprise systems expecting firmware defaults.

## Test Signals
- Build with `CONFIG_PTP_1588_CLOCK` and DPLL subsystem enabled, including E810 and E825C coverage.
- Probe/remove and reset-cycle tests should verify no DPLL device/pin references leak and `ICE_FLAG_DPLL` is correct.
- DPLL netlink tests should exercise frequency, state, priority, phase adjust, phase offset monitor, embedded sync, and reference sync get/set paths.
- Hardware or mocked AdminQ tests should inject failures in CGU ability reads, pin get/set commands, DPLL registration, pin registration, fwnode lookup, and worker state polling.
- SMA/U.FL tests should verify direction/state transitions, paired-pin notifications, active/inactive reporting, and backing pin enable/disable behavior.
- Recovered-clock tests should cover both AdminQ PHY recovered clock output and E825C SynCE bypass-mux programming.
