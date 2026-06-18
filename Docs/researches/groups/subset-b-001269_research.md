# subset-b-001269 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.c

## Purpose
This file is the hand-written generic-netlink implementation for the Linux DPLL management framework. It translates userspace `dpll` netlink commands into DPLL core object lookups, driver callback calls, state changes, dumps, and multicast notifications. It is the behavioral half paired with the generated family definition in `dpll_nl.c`.

## Important APIs, types, and functions
The public notification APIs are `dpll_device_create_ntf()`, `dpll_device_delete_ntf()`, `dpll_device_change_ntf()`, `dpll_pin_create_ntf()`, `dpll_pin_delete_ntf()`, `__dpll_pin_change_ntf()`, and `dpll_pin_change_ntf()`. Netlink handlers include `dpll_nl_device_id_get_doit()`, `dpll_nl_device_get_doit()`, `dpll_nl_device_get_dumpit()`, `dpll_nl_device_set_doit()`, `dpll_nl_pin_id_get_doit()`, `dpll_nl_pin_get_doit()`, `dpll_nl_pin_get_dumpit()`, and `dpll_nl_pin_set_doit()`. Locking/preload hooks are `dpll_pre_doit()`, `dpll_post_doit()`, `dpll_lock_doit()`, `dpll_unlock_doit()`, `dpll_pin_pre_doit()`, and `dpll_pin_post_doit()`. Helpers serialize device attributes, pin attributes, parent relationships, supported frequency ranges, embedded sync, reference sync, measured frequency, fractional frequency offset, phase offset, phase adjustment, temperature, lock status, mode, and monitoring feature states.

## Control flow
GET paths allocate a reply skb, add a generic-netlink header, locate the requested registered object either by numeric ID or by identity attributes, serialize the object, end the message, and reply. Dump paths iterate `dpll_device_xa` or `dpll_pin_xa` from a saved callback cursor, stopping cleanly on `-EMSGSIZE`. SET paths walk the attributes in the original message and dispatch to narrowly scoped setters. Device setters validate supported mode/monitor operations before calling driver ops. Pin setters validate capability bits, frequency ranges, phase range/granularity, parent object existence, and reference-sync pair availability. Multi-DPLL pin operations such as frequency, phase adjust, esync, and reference sync update every DPLL reference for a shared pin and attempt rollback to the old value on partial failure.

## State and persistence
The file does not own persistent hardware state. It reads and writes framework state stored in `dpll_device`, `dpll_pin`, `dpll_pin_ref`, global xarrays, and driver-private state accessed through DPLL ops. State changes persist only through the lower driver callbacks. `dpll_lock` protects object lookup, serialization, and mutations in doit paths; dump paths lock around each traversal. Notifications update DPLL core notification state before multicasting a snapshot of the changed object.

## Dependencies and integration points
The implementation depends on `dpll_core.h` for object internals and xarrays, `dpll_nl.h` for generated family declarations and policies, `uapi/linux/dpll.h` for ABI constants, and generic netlink helpers. Driver integration is entirely via `struct dpll_device_ops` and `struct dpll_pin_ops`; the ZL3073x driver in this group supplies one such implementation.

## Risks and edge cases
Message construction must preserve ABI units, especially FFO in legacy PPM plus PPT and phase/frequency values using 64-bit netlink attributes. Rollback failures are reported but cannot fully restore a partially updated shared pin. `dpll_pin_available()` filters objects by registration marks and parent availability, so stale pins are hidden but callers must still hold the framework lock. The code assumes mandatory ops exist where the core contract requires them; missing driver ops become `-EOPNOTSUPP` for optional features.

## Test signals
Useful tests are YNL/netlink round trips for every command, dump pagination with small skb sizes, duplicated or missing lookup attributes, invalid modes/states/frequencies, rollback fault injection on multi-DPLL shared pin updates, multicast monitor reception, and lockdep coverage for pre/post hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.h

## Purpose
This small internal header declares the DPLL netlink notification helpers implemented in `dpll_netlink.c` and used by the core framework when DPLL devices or pins are created or deleted.

## Important APIs
It exposes `dpll_device_create_ntf()`, `dpll_device_delete_ntf()`, `dpll_pin_create_ntf()`, and `dpll_pin_delete_ntf()`. Change-notification helpers are exported directly from the C file and are not declared here.

## Control flow and integration
Callers include DPLL core registration paths. Each function updates core-side notification state and sends a generic-netlink multicast event through `dpll_nl_family`.

## State, dependencies, risks, and tests
The header owns no state and relies on forward declarations from included DPLL core types at the use site. The main risk is declaration drift if notification entry points change. Build coverage of DPLL core plus creation/deletion monitor tests provide the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.c

## Purpose
This is generated YNL kernel glue for the DPLL generic-netlink family. It defines netlink attribute policies, split operation tables, multicast groups, and the `dpll_nl_family` descriptor used by `dpll_netlink.c`.

## Important APIs and data
Policy arrays include `dpll_pin_parent_device_nl_policy`, `dpll_pin_parent_pin_nl_policy`, `dpll_reference_sync_nl_policy`, and per-command static policies for device ID/get/set and pin ID/get/set. `dpll_nl_ops[]` binds DPLL commands to the hand-written pre/do/post handlers. `dpll_nl_mcgrps[]` defines the monitor multicast group. `dpll_nl_family` sets the family name/version, `netnsok`, `parallel_ops`, module owner, ops, and groups.

## Control flow
Generic netlink dispatch validates incoming attributes against these policies, then calls the registered pre/do/post handlers. Device and pin ID lookups take only identity attributes and use a global lock helper. Object-specific GET/SET commands use pre-doit hooks to resolve the numeric ID into `info->user_ptr[0]` under `dpll_lock`.

## State and persistence
The file contains static immutable dispatch metadata plus the exported family object. It has no hardware or persistent state.

## Dependencies and integration points
It is generated from `Documentation/netlink/specs/dpll.yaml`, includes generic netlink headers and `uapi/linux/dpll.h`, and declares callbacks implemented in `dpll_netlink.c` through `dpll_nl.h`.

## Risks and test signals
The main risk is generated-code drift from the YAML ABI or mismatched max attribute bounds. Tests should include YNL schema regeneration checks, invalid attribute type/range tests, command capability checks, and module load/unload coverage ensuring the family registers with the intended monitor group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.h

## Purpose
This generated header is the internal contract between the generated DPLL netlink family table and the hand-written DPLL netlink implementation.

## Important APIs and types
It declares the shared nested attribute policy arrays, pre/post locking hooks, all DPLL device and pin netlink command handlers, the `DPLL_NLGRP_MONITOR` multicast group enum, and `extern struct genl_family dpll_nl_family`.

## Control flow and integration
`dpll_nl.c` consumes these declarations when building `dpll_nl_ops[]`; `dpll_netlink.c` provides the functions and uses `dpll_nl_family` for replies and multicast notifications.

## State, dependencies, risks, and tests
The header owns no state. It depends on netlink/genetlink headers and `uapi/linux/dpll.h`. The risk is regeneration mismatch with `dpll_nl.c` or with handler names in `dpll_netlink.c`. Compilation and YNL regeneration diffs are the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Kconfig

## Purpose
This Kconfig file defines build options for the Microchip Azurite/ZL3073x DPLL/PTP/SyncE driver family.

## Important symbols
`ZL3073X` builds the common core and selects `DPLL`, `NET_DEVLINK`, and `REGMAP`. `ZL3073X_I2C` builds the I2C transport and selects `REGMAP_I2C` plus the core. `ZL3073X_SPI` builds the SPI transport and selects `REGMAP_SPI` plus the core.

## Control flow and integration
There is no runtime control flow. The options determine whether `zl3073x.o`, `zl3073x_i2c.o`, and `zl3073x_spi.o` are compiled and which framework dependencies are available.

## State, risks, and tests
No state is stored. Risks are dependency omissions, especially `NET`/devlink/DPLL/regmap selections, or transport options enabling without core support. Build tests should cover built-in and module configurations for core-only, I2C, SPI, and `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Makefile

## Purpose
This Makefile maps ZL3073x Kconfig symbols to kernel objects.

## Important build rules
`obj-$(CONFIG_ZL3073X)` builds `zl3073x.o` from `chan.o core.o devlink.o dpll.o flash.o fw.o out.o prop.o ref.o synth.o`. `CONFIG_ZL3073X_I2C` builds `zl3073x_i2c.o` from `i2c.o`; `CONFIG_ZL3073X_SPI` builds `zl3073x_spi.o` from `spi.o`.

## Integration, risks, and tests
The split keeps transport modules small while sharing the exported `ZL3073X` namespace from the common core. Risks are missing objects when new helpers are added or namespace/export mismatches between transport and core. Test signals are clean module builds and successful modpost namespace checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.c

## Purpose
This file manages cached DPLL channel state for each ZL3073x channel: reference-selection mode, forced reference, per-reference priorities, monitor lock status, and selected-reference status.

## Important APIs
`zl3073x_chan_state_fetch()` reads initial channel configuration and status from hardware. `zl3073x_chan_state_update()` refreshes dynamic monitor/refsel status. `zl3073x_chan_state_get()` returns the cached state. `zl3073x_chan_state_set()` commits mutable channel configuration back to hardware.

## Control flow
Fetch reads `ZL_REG_DPLL_MODE_REFSEL`, status registers, then takes `multiop_lock`, asks the DPLL mailbox to load the channel configuration, and reads the packed priority registers. Set first skips unchanged configuration, writes `mode_refsel` directly when it changed, and only enters the mailbox path if priorities changed. The mailbox path reads current DPLL config, writes changed priority bytes, commits with `ZL_DPLL_MB_SEM_WR`, and updates the cache after success.

## State and persistence
State is stored in `zldev->chan[index]` as `cfg` and `stat` groups. Hardware state persists in device registers/firmware configuration, but the driver cache is runtime-only and rebuilt by fetch after probe/restart.

## Dependencies and integration points
The file depends on register access and mailbox helpers from `core.c` and bitfield accessors in `chan.h`. `dpll.c` uses it for DPLL mode, manual/automatic reference selection, pin priority, and lock status reporting.

## Risks and tests
Mailbox operations require `multiop_lock`; missing serialization can corrupt page/mailbox access. Partial writes before a later mailbox failure can leave hardware and cache out of sync, though the cache is updated only after successful commit. Test with automatic/manual mode switching, priority changes, lock-status polling, and fault injection on mailbox read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.h

## Purpose
This header defines the ZL3073x DPLL channel cache layout and inline bitfield helpers for interpreting and mutating channel registers.

## Important APIs and types
`struct zl3073x_chan` groups mutable `mode_refsel` and `ref_prio[]` configuration separately from status fields `mon_status` and `refsel_status`. Inline helpers get/set channel mode, forced reference, per-reference priority, selectability, lock state, holdover-ready bit, selected-reference state, and selected-reference ID.

## Control flow and state
The header has no executable flow beyond inline field access. The grouping is used by `chan.c` to compare mutable config as a block and to avoid treating status changes as configuration changes.

## Dependencies and integration
It depends on `regs.h` for masks and constants. `core.c` refreshes state periodically, and `dpll.c` uses helpers to map hardware modes and priorities to DPLL netlink state.

## Risks and tests
Incorrect bit masks or P/N priority packing would expose wrong pin state or change the wrong reference. Tests should exercise both even/P and odd/N reference priorities plus all hardware mode values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.c

## Purpose
This is the common ZL3073x core driver. It identifies chip variants, owns the paged regmap configuration, implements typed register access and HW-register access, initializes and starts DPLL subdevices, maintains the periodic monitor worker, and coordinates devlink registration.

## Important APIs and functions
Exported APIs are `zl3073x_regmap_config`, `zl3073x_dev_probe()`, and register/HW helpers declared in `core.h`: `zl3073x_read_u8/u16/u32/u48()`, `zl3073x_write_u8/u16/u32/u48()`, `zl3073x_poll_zero_u8()`, `zl3073x_mb_op()`, `zl3073x_read_hwreg()`, `zl3073x_write_hwreg()`, `zl3073x_update_hwreg()`, `zl3073x_write_hwreg_seq()`, `zl3073x_ref_phase_offsets_update()`, `zl3073x_dev_start()`, `zl3073x_dev_stop()`, and `zl3073x_dev_phase_avg_factor_set()`. Static chip tables map device IDs to channel counts and feature flags.

## Control flow
Probe reads chip ID/revision/FW/config version, selects `zl3073x_chip_info`, creates a random default clock ID, initializes `multiop_lock`, allocates DPLL channel objects and the worker, starts normal operation, and registers devlink. `zl3073x_dev_start(full)` checks the firmware-ready bit; if not ready it leaves only devlink available for flashing. Full start fetches ref/synth/out/channel state, configures phase measurement, registers each DPLL and its pins, applies initial fine phase adjustment, and queues periodic work. Stop cancels the worker and unregisters DPLLs.

## State and persistence
`struct zl3073x_dev` caches invariant and mutable state for refs, synths, outputs, and channels. The cache is runtime-only; persistent device configuration lives in hardware/flash and is re-read after probe or restart. `phase_avg_factor` and `clock_id` are driver state exposed through devlink/DPLL; `clock_id` defaults randomly but can be changed through devlink driverinit reload.

## Dependencies and integration points
Transport drivers provide `regmap` over I2C or SPI. The core integrates with `dpll.c` for DPLL registration and notifications, `devlink.c` for info/reload/flash, `ref/out/synth/chan` state helpers, and `regs.h` for encoded register addresses. Mailbox register pages 10-14 require `multiop_lock` for coherent multi-register operations.

## Risks and edge cases
Regmap page selection and encoded register size checks are critical. `zl3073x_write_hwreg_seq()` appears to test `seq->wait` rather than `seq[i].wait`, so only the first wait field controls all waits; this is worth review for reset/flash sequences. Firmware not ready intentionally suppresses DPLL registration. Periodic work reads and notifies twice a second, so slow/broken buses can delay notifications.

## Test signals
Probe on known IDs, unknown-ID rejection, firmware-not-ready devlink-only behavior, I2C/SPI regmap access, mailbox lockdep, phase measurement setup, periodic notification behavior, reload restart, and flash-mode enter/leave recovery are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.h

## Purpose
This header is the central internal interface for the ZL3073x driver. It defines chip flags, the per-device state container, register/HW access APIs, and inline helpers that translate pin/output/reference IDs into cached hardware properties.

## Important APIs and types
Important types are `enum zl3073x_flags`, `struct zl3073x_chip_info`, `struct zl3073x_dev`, and `struct zl3073x_hwreg_seq_item`. It declares probe/start/stop, typed register helpers, mailbox operation, HW register helpers, phase averaging, and reference phase measurement refresh. Inline helpers map input pins to refs, output pins to output pairs, check P/N identity, read cached ref/out/synth properties, compute output pin frequency, and test output pin enablement under signal-format constraints.

## Control flow and state
The header’s inline helpers are used throughout DPLL pin registration and callbacks. `struct zl3073x_dev` is the driver’s runtime state root, combining the Linux device, regmap, variant info, mailbox serialization mutex, cached hardware state arrays, DPLL list, monitor worker, devlink clock ID, and phase averaging factor.

## Dependencies and integration
It includes `chan.h`, `out.h`, `ref.h`, `regs.h`, and `synth.h`, so it ties the state submodules together. Transport modules call `zl3073x_devm_alloc()` and `zl3073x_dev_probe()` through this interface.

## Risks and tests
Frequency helpers divide by cached divisors; fetch paths must reject zero divisors before these helpers are used. Output pin enablement and frequency depend on signal-format interpretation, so tests should cover differential, 1P, 1N, two-output, and N-div formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.c

## Purpose
This file provides the ZL3073x devlink integration: device info reporting, driver reinit reload, firmware flash update, allocation of `struct zl3073x_dev` inside a devlink instance, and registration of the `clock_id` driverinit parameter.

## Important APIs and functions
External APIs are `zl3073x_devm_alloc()`, `zl3073x_devlink_register()`, and `zl3073x_devlink_flash_notify()`. Devlink ops are `info_get`, `reload_down`, `reload_up`, and `flash_update`. Static helpers prepare and finish flash mode around `zl3073x_fw_flash()`.

## Control flow
Info reads chip ID, revision, firmware version, and custom config version from registers and publishes fixed/running versions. Reload down supports only `DEVLINK_RELOAD_ACTION_DRIVER_REINIT` and stops normal DPLL operation. Reload up reads the driverinit `clock_id`, applies it if changed, and restarts normal operation without full invariant refetch. Flash update parses the provided firmware, stops normal operation, enters flash mode using the utility component, flashes all present components, leaves flash mode, restarts normal operation, frees firmware memory, and sends final status.

## State and persistence
Devlink owns the allocation container for `struct zl3073x_dev`. `clock_id` is driverinit state that persists across DPLL registration after reload but is not stored in device flash by this code. Firmware flashing modifies device flash through `flash.c`.

## Dependencies and integration points
It depends on `core.c` register/start/stop helpers, `fw.c` parsing/flashing orchestration, `flash.c` flash-mode entry/exit, and devlink APIs. Normal DPLL operation is deliberately stopped before flash mode because normal firmware APIs are unavailable there.

## Risks and tests
If flash prepare fails, the code tries to resume normal operation. `zl3073x_flash_mode_leave()` return is ignored in finish prepare paths, so restart errors are the main visible signal. Tests should cover devlink info, invalid zero clock ID, reload with changed clock ID, malformed firmware, missing utility component, interrupted flashing, and restart after flash failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.h

## Purpose
This header declares the devlink-facing allocation, registration, and flash progress notification helpers for the ZL3073x core.

## Important APIs
`zl3073x_devm_alloc()` allocates the devlink instance and returns the embedded device state. `zl3073x_devlink_register()` registers the instance and parameters. `zl3073x_devlink_flash_notify()` wraps devlink flash progress notifications.

## Integration, state, risks, and tests
Transport probe uses allocation before initializing regmap. Core probe calls registration after DPLL setup. Flash and firmware code use the notification helper for user-visible progress. The header owns no state; build coverage catches prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.c

## Purpose
This file adapts ZL3073x hardware state and controls to the Linux DPLL framework. It allocates per-channel DPLL devices, registers eligible input/output pins, implements DPLL device and pin ops, handles automatic/manual mode semantics, exposes phase/frequency monitoring, and sends change notifications from the periodic worker.

## Important APIs, types, and functions
The internal `struct zl3073x_dpll_pin` stores per-registered-pin state, labels, firmware node handles, priority, phase granularity, last pin state, phase offset, FFO, and measured frequency. External APIs are `zl3073x_dpll_alloc()`, `zl3073x_dpll_free()`, `zl3073x_dpll_register()`, `zl3073x_dpll_unregister()`, `zl3073x_dpll_init_fine_phase_adjust()`, and `zl3073x_dpll_changes_check()`. DPLL pin ops cover direction, esync, FFO, frequency, measured frequency, phase offset, phase adjust, priority, ref-sync, and state on DPLL. Device ops cover lock status, mode, supported modes, monitor toggles, averaging factor, and optional die temperature.

## Control flow
Registration creates a `dpll_device`, enumerates input then output pins, filters out disabled pins, N pins for differential signals, inputs on NCO channels, and outputs driven by other channels, then gets DPLL pin objects and registers them with appropriate ops. Firmware-node `ref-sync-sources` are resolved after pins are registered. Device mode maps hardware freerun/holdover/ref-lock/NCO to DPLL manual and hardware auto to DPLL automatic. Pin state changes either force reference lock, return to freerun/holdover, or toggle priority selectability in automatic mode. Output frequency changes recompute output divisors and handle N-div pairs. Esync uses special reference/output registers and currently only exposes a narrow 0/1 Hz range.

## State and persistence
Per-DPLL runtime state is `struct zl3073x_dpll`: registered DPLL pointer, ops, monitor booleans, cached lock status, check counter, pin list, and async change work. Hardware configuration changes persist in device registers/firmware state through `ref_state_set()`, `chan_state_set()`, and `out_state_set()`. Last observed pin measurements are runtime cache used to suppress duplicate notifications.

## Dependencies and integration points
The file depends on cached hardware state from `core/ref/out/synth/chan`, firmware-node properties from `prop.c`, and Linux DPLL core APIs. `core.c` calls registration during start and calls `zl3073x_dpll_changes_check()` from the twice-per-second worker.

## Risks and edge cases
Mode transitions depend on the last cached lock status and selected-reference status. Shared pins can be registered to multiple DPLLs, so generic netlink updates may call these ops for every reference. Ref-sync connect intentionally sets the sync source priority to NONE and does not restore it on disconnect. Phase offset math wraps offsets when comparing references of different frequencies. Output N-div calculations reject zero divisors but can lose precision through integer division.

## Test signals
Exercise DPLL registration for all supported channel counts, firmware-node pin metadata, auto/manual transitions, priority changes, forced reference connect/disconnect, ref-sync connect validation, esync enable/disable, input/output frequency changes, phase adjust, monitor toggles, notification changes, and optional die temperature on flagged chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.h

## Purpose
This header defines the per-channel ZL3073x DPLL object and the registration/monitoring APIs used by the common core.

## Important APIs and types
`struct zl3073x_dpll` stores list linkage, parent `zl3073x_dev`, channel ID, monitor flags, ops copy, registered `dpll_device`, tracker, cached lock status, pin list, and change-notification work. Declared APIs allocate/free, register/unregister, initialize fine phase adjustment, and check for changes.

## Control flow and state
The core allocates one object per hardware channel during probe, registers it during `zl3073x_dev_start()`, and unregisters/frees it through devres cleanup. Periodic work calls `zl3073x_dpll_changes_check()` for each list entry.

## Risks and tests
The structure mixes registration lifetime and periodic work state, so unregister must cancel work before dropping DPLL references. Tests should cover probe failure unwinding and reload/flash stop-start cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.c

## Purpose
This file implements low-level ZL3073x flash-update operations used by devlink firmware update: entering flash mode, downloading words into device memory, executing flash utility commands, flashing sectors/pages, copying pages, checking utility errors, and returning to normal mode.

## Important APIs and functions
External APIs are `zl3073x_flash_mode_enter()`, `zl3073x_flash_mode_leave()`, `zl3073x_flash_page()`, `zl3073x_flash_page_copy()`, and `zl3073x_flash_sectors()`. Internal helpers include `zl3073x_flash_download()`, `zl3073x_flash_error_check()`, `zl3073x_flash_wait_ready()`, `zl3073x_flash_cmd_wait()`, `zl3073x_flash_get_sector_size()`, `zl3073x_flash_block()`, `zl3073x_flash_mode_verify()`, and `zl3073x_flash_host_ctrl_enable()`.

## Control flow
Flash mode entry sends a fixed hardware-register pre-load sequence, downloads the utility image to RAM at `0x20000000`, sends a post-load sequence to start it, verifies the utility family, enables host control, and reports progress. Flashing a block downloads data to RAM, writes image address/size/page/fill-pattern registers, issues a flash operation, waits for completion, checks utility error counters, and sends devlink progress. Sector flashing chooses 4K or 64K sector size from the utility, splits large firmware into aligned blocks, and advances flash pages by block size. Leave mode sets the reset flag, runs the reset sequence, waits, and checks that reset status cleared.

## State and persistence
This code writes persistent device flash. It also temporarily changes CPU/host-control state and uses device RAM for images. No host-side state persists beyond progress notifications and return codes.

## Dependencies and integration points
It uses `core.c` HWREG and typed register helpers, `regs.h` flash-mode register definitions, and devlink notification wrappers. It is invoked only after normal DPLL operation is stopped by `devlink.c`.

## Risks and edge cases
Flashing can be interrupted by signals during long downloads or waits. Utility command waits can timeout. `zl3073x_flash_mode_leave()` intentionally ignores the reset sequence write error because the device CPU reset makes the last write fail. Incorrect sector size, page math, unaligned component sizes, or failed utility error checks can corrupt updates. Progress uses pointer arithmetic over `void *`, which is accepted by GCC but non-standard C.

## Test signals
Use mocked regmap/HWREG fault injection for pre/post sequences, utility verification failure, host-control failure, sector-size variants, command timeout, utility error count reporting, signal interruption, multi-block sector updates, page copy, and restart after failed flash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.h

## Purpose
This header declares the low-level flash-mode and flash-write APIs for ZL3073x firmware update.

## Important APIs
It declares entry/exit with `zl3073x_flash_mode_enter()` and `zl3073x_flash_mode_leave()`, plus page, page-copy, and sector flashing functions. Each API accepts `struct zl3073x_dev` and a netlink extack for devlink error reporting.

## Integration, state, risks, and tests
`fw.c` uses page/sector helpers according to component metadata; `devlink.c` uses mode enter/leave around the entire update. The header owns no state. Compile tests and devlink firmware update paths validate prototype consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.c

## Purpose
This file parses a text-form ZL3073x firmware bundle into named components, validates sizes and duplicates, and dispatches each component to the appropriate low-level flash operation.

## Important APIs and data
External APIs are `zl3073x_fw_load()`, `zl3073x_fw_free()`, and `zl3073x_fw_flash()`. `component_info[]` maps component IDs to names, maximum sizes, flash type, load address, destination page, and optional copy page. Flash types are none, sectors, page, and page-plus-copy.

## Control flow
`zl3073x_fw_load()` loops over the input buffer, calling `zl3073x_fw_component_load()` until no more component header can be parsed or an error occurs. A component header contains a name and word count; data follows as hexadecimal words. Unknown names, oversize components, duplicate components, missing data, and allocation failures abort and free prior components. `zl3073x_fw_flash()` iterates component IDs in fixed order and calls `zl3073x_fw_component_flash()`, which skips the utility component and otherwise chooses sectors/page/page+copy helpers from `flash.c`.

## State and persistence
Host-side firmware state is a heap-allocated `struct zl3073x_fw` with per-component buffers. It is freed after devlink flash update. Persistent effects occur only when flash helpers write device flash.

## Dependencies and integration points
It depends on `flash.c` for actual writes, `core.h` for device context, and devlink extack for user-facing parse/flash errors. `devlink.c` requires the utility component before entering flash mode.

## Risks and tests
The parser assumes text headers and hex words with whitespace; malformed or truncated input must not overrun the firmware buffer. Component order in the input is flexible, but duplicate IDs are rejected. Tests should cover unknown names, maximum-size boundaries, duplicate components, malformed hex, missing utility, page+copy components, and partial flash failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.h

## Purpose
This header defines the in-memory firmware bundle model used by ZL3073x devlink flash update.

## Important APIs and types
`enum zl3073x_fw_component_id` identifies utility, firmware, and config components. `struct zl3073x_fw_component` stores component ID, size, and data pointer. `struct zl3073x_fw` stores an array of optional component pointers. It declares load/free/flash APIs.

## State, dependencies, risks, and tests
The types represent transient heap state only. They depend on `struct zl3073x_dev` from the core at use sites. Tests should confirm all enum entries align with `component_info[]` in `fw.c` and that absent optional components are skipped safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/i2c.c

## Purpose
This file is the I2C transport binding for ZL3073x devices. It allocates the shared core state, creates an I2C regmap, and invokes common probe.

## Important APIs and data
`zl3073x_i2c_probe()` is the probe entry point. The I2C ID table and OF compatible table cover `zl30731` through `zl30735`. `module_i2c_driver()` registers the driver.

## Control flow
Probe calls `zl3073x_devm_alloc()`, initializes `zldev->regmap` with `devm_regmap_init_i2c()` and the exported `zl3073x_regmap_config`, then calls `zl3073x_dev_probe()`.

## State and dependencies
All persistent driver state lives in the shared `zl3073x_dev`; the transport owns only the bus registration and regmap binding. It imports the `ZL3073X` namespace exported by the core.

## Risks and tests
Regmap setup failure must abort before common probe. Tests include OF/I2C ID matching, module namespace checks, probe failure unwinding, and basic register reads over I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.c

## Purpose
This file fetches, exposes, and commits ZL3073x output configuration state. Outputs are shared by P/N output pin pairs and drive DPLL pin frequency, phase adjustment, signal format, and esync behavior.

## Important APIs
`zl3073x_out_state_fetch()` initializes one output cache from hardware. `zl3073x_out_state_get()` returns the cached state. `zl3073x_out_state_set()` validates and commits mutable output configuration through the output mailbox.

## Control flow
Fetch reads the direct output control register, then under `multiop_lock` loads the output mailbox, reads mode, divisor, width, esync/N-div period and width, and phase compensation. Zero output or esync divisors are rejected. Set rejects invariant `ctrl` changes, skips unchanged configs, loads the mailbox, writes only changed mutable fields, commits with `ZL_OUTPUT_MB_SEM_WR`, and updates the cache after success.

## State and persistence
`zldev->out[index]` caches mutable `cfg` fields and invariant `ctrl`. Hardware output settings persist in device configuration; the cache is rebuilt from hardware on full start.

## Dependencies and integration
The file depends on `core.c` register/mailbox helpers and `out.h` masks. `dpll.c` changes output divisor, esync, phase compensation, and frequency through this API.

## Risks and tests
Zero divisors would cause later frequency helpers to divide by zero, so fetch validation is important. N-div and esync share fields, so callers must avoid incompatible combinations. Tests should cover every signal format, divisor changes, esync enable/disable, phase compensation, and mailbox fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.h

## Purpose
This header defines cached output state and inline helpers for ZL3073x output mode, signal format, enablement, N-div, differential status, and synthesizer selection.

## Important APIs and types
`struct zl3073x_out` separates mutable config fields (`div`, `width`, `esync_n_period`, `esync_n_width`, `phase_comp`, `mode`) from invariant `ctrl`. Inline helpers get/set clock type, decode signal format, test differential formats, test output enablement, detect N-div formats, and get the attached synth.

## Control flow and integration
The inline helpers are used by property parsing, DPLL pin registration, output frequency computation, esync control, and output state commits.

## Risks and tests
Signal-format classification directly controls whether N pins are registered and how output frequencies are computed. Tests should cover LVDS/differential/low-VCM, 1P/1N, normal two-output, inverted, and N-div formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.c

## Purpose
This file derives DPLL device and pin properties from cached hardware state plus firmware-node metadata. It supplies labels, pin types, capabilities, supported frequency ranges, esync-control flags, and DPLL channel type.

## Important APIs
`zl3073x_pin_props_get()` allocates and fills a `struct zl3073x_pin_props` for a given input/output pin. `zl3073x_pin_props_put()` releases it. `zl3073x_prop_dpll_type_get()` maps the optional `dpll-types` device property to `DPLL_TYPE_PPS` or `DPLL_TYPE_EEC`. Internal helpers validate frequencies, synthesize package labels, and locate per-pin fwnodes.

## Control flow
Property creation starts with defaults: input pins are external references with state/priority capabilities; output pins default to GNSS and get phase granularity from half the driving synth period. It generates labels such as `REF0P`, `REF0`, `OUT1N`, or `OUT1` depending on differential state. It optionally locates `input-pins` or `output-pins` child nodes by `reg`, then reads `label`, `connection-type`, `esync-control`, and `supported-frequencies-hz`. Supported frequencies become exact min=max DPLL ranges, always including the current frequency, and invalid firmware-provided frequencies are warned and skipped.

## State and persistence
Returned property objects are transient heap allocations used during pin registration. Firmware-node handles are reference-counted until `zl3073x_pin_props_put()`.

## Dependencies and integration points
The file depends on cached ref/out/synth state from `core.h`, frequency factorization from `ref.c`, firmware-node/property APIs, and Linux DPLL property structures. `dpll.c` consumes these properties during pin registration.

## Risks and tests
Invalid firmware frequency lists must not prevent registration except for allocation failures. Output frequency validation divides by requested frequency, so zero frequencies from firmware are risky and should be validated by tests. Tests should cover missing nodes, labels, connection type mapping, unknown types, esync flag, frequency filtering, differential labels, and channel type defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.h

## Purpose
This header declares the ZL3073x property helper model used to register DPLL devices and pins with meaningful metadata.

## Important APIs and types
`struct zl3073x_pin_props` contains an optional firmware node, `struct dpll_pin_properties`, generated package label storage, and the `esync_control` flag. It declares pin property get/put and DPLL type lookup.

## Integration, state, risks, and tests
`dpll.c` allocates these objects during pin registration and releases them after DPLL core registration. The header owns no persistent state. Tests should catch lifetime errors around fwnode references and supported frequency arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.c

## Purpose
This file manages ZL3073x input reference state: frequency encoding, monitor status, reference configuration, reference-sync/esync/N-div settings, and phase compensation.

## Important APIs
`zl3073x_ref_freq_factorize()` maps a requested frequency into base and multiplier values supported by the device. `zl3073x_ref_state_fetch()` reads one reference’s state from hardware. `zl3073x_ref_state_update()` refreshes monitor status. `zl3073x_ref_state_get()` returns cached state. `zl3073x_ref_state_set()` validates and commits mutable reference configuration.

## Control flow
Fetch handles differential N pins by copying the P pin’s shared config and invariants. For normal refs it reads monitor status, locks `multiop_lock`, loads the reference mailbox, reads config, frequency base/mult/ratio, esync divider, sync control, and phase compensation. Set rejects invariant changes, skips unchanged mutable config, loads the mailbox, writes changed fields, chooses 32-bit or 48-bit phase-comp register based on chip flag, commits through the reference mailbox, and updates the cache.

## State and persistence
`zldev->ref[index]` stores mutable config, invariant config bits, dynamic FFO/measured-frequency fields, and monitor status. Hardware configuration persists in device firmware/register state; dynamic measurements are refreshed by `core.c` periodic work.

## Dependencies and integration
The file depends on `core.c` mailbox/register helpers and `regs.h`. `dpll.c` uses it for input pin frequency, phase adjust, ref-sync, esync, status, and notification comparisons.

## Risks and tests
Frequency factorization accepts only frequencies divisible by known bases with 16-bit multipliers. Differential N pins assume P pin state was fetched first. Invariant rejection prevents accidental enable/differential changes through DPLL ops. Tests should cover factorization boundaries, 32-bit vs 48-bit phase compensation, differential copy behavior, mailbox failures, and monitor status transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.h

## Purpose
This header defines the ZL3073x input-reference cache and inline helpers for frequency, sync mode, paired sync reference, differential/enabled status, and monitor health.

## Important APIs and types
`struct zl3073x_ref` groups mutable config (`phase_comp`, `esync_n_div`, frequency base/mult/ratio, `sync_ctrl`), invariant `config`, and dynamic status (`ffo`, `meas_freq`, `mon_status`). Inline helpers expose FFO, measured frequency, computed reference frequency, frequency set/factorization, sync mode/pair get/set, differential/enabled flags, and status OK.

## Control flow and integration
The header’s helpers are used by property validation, DPLL pin callbacks, periodic notification checks, and state commit logic. `zl3073x_ref_freq_set()` mutates the cache candidate and leaves hardware commit to `zl3073x_ref_state_set()`.

## Risks and tests
Computed frequency multiplies base, multiplier, and ratio with integer math; test high and low frequencies. Sync bitfield helpers affect ref-sync and esync behavior, so connect/disconnect tests should validate the exact register encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/regs.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/regs.h

## Purpose
This header is the ZL3073x register map contract. It encodes logical register descriptors, hardware limits, bit masks, mode constants, mailbox registers, HWREG access registers, and flash utility registers.

## Important APIs and constants
Hardware limits include maximum channels, references, outputs, synths, and pin counts. `ZL_REG()` and `ZL_REG_IDX()` encode page, offset, byte size, and maximum indexed offset into one integer consumed by `core.c`. Macros decode offset, page, size, max offset, and physical register address. The header defines page 0 identity/status registers, page 2 monitor/status registers, page 4 measurement controls, page 5 DPLL controls, page 9 synth/output controls, pages 10/12/13/14 mailboxes, page 255 HWREG access, and flash-mode registers.

## Control flow and state
There is no executable control flow, but every register access helper validates descriptor size and index range against these encodings. Mailbox constants define which multi-register operations need `multiop_lock`.

## Dependencies and integration points
All ZL3073x source files consume this header either directly or through state headers. It depends on Linux bitfield and bit macros.

## Risks and tests
Wrong register sizes, page numbers, masks, or indexed strides would corrupt hardware access. The encoded `max_offset` field is a key safety check. Tests should include compile-time mask use, runtime invalid-index detection, register size mismatch fault paths, and hardware smoke tests for each mailbox page and flash-mode register group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/spi.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/spi.c

## Purpose
This file is the SPI transport binding for ZL3073x devices. It mirrors the I2C transport but initializes regmap over SPI.

## Important APIs and data
`zl3073x_spi_probe()` allocates core state and initializes `devm_regmap_init_spi()`. SPI ID and OF tables cover `zl30731` through `zl30735`. `module_spi_driver()` registers the transport.

## Control flow, state, and integration
Probe allocates `zl3073x_dev`, stores the SPI regmap, then calls `zl3073x_dev_probe()`. State is owned by the common core and devres. The module imports the `ZL3073X` namespace.

## Risks and tests
Transport-specific risks are SPI regmap setup and compatible matching. Test module builds, OF/SPI ID matching, probe failure cleanup, and basic register access over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.c -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.c

## Purpose
This file fetches and exposes ZL3073x synthesizer state. Synthesizers drive outputs and are associated with DPLL channels.

## Important APIs
`zl3073x_synth_state_fetch()` reads one synthesizer’s control and frequency parameters from hardware. `zl3073x_synth_state_get()` returns the cached state.

## Control flow
Fetch reads the direct synth control register, then under `multiop_lock` loads the synth mailbox and reads base, multiplier, numerator, and denominator. It rejects zero denominator to protect later frequency calculations and logs the computed frequency.

## State and persistence
`zldev->synth[index]` caches invariant synthesizer state. This driver does not provide a synth state setter; synth configuration is treated as hardware/firmware-defined and re-fetched on full start.

## Dependencies and integration
It depends on core mailbox/register helpers and `synth.h`. Output frequency calculations, output pin registration, phase granularity, and DPLL-output association use this cached state.

## Risks and tests
Incorrect frequency components affect every output frequency and pin property. Tests should cover zero denominator rejection, disabled synth handling, DPLL selection decoding, and output registration for synths tied to different channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.h -->
# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.h

## Purpose
This header defines cached synthesizer state and inline helpers for synthesizer DPLL ownership, frequency, and enablement.

## Important APIs and types
`struct zl3073x_synth` stores frequency multiplier/base/numerator/denominator and control as invariants. Inline helpers decode the driving DPLL channel, compute frequency, and test enablement. It declares fetch/get APIs.

## Integration, risks, and tests
The core fetches all synths during full start; output and property helpers consume the cache. Frequency computation is central to output pin frequency and phase granularity, so denominator validation in `synth.c` plus output-frequency tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/synth.h -->
