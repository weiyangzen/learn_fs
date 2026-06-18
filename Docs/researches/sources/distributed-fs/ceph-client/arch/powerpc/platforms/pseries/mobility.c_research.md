# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/mobility.c

## Purpose
Implements pSeries partition mobility and migration support. It updates the live device tree after migration, drives VASI/H_JOIN/ibm,suspend-me handshakes, coordinates all CPUs through stop-machine, and exposes a sysfs migration trigger.

## Important APIs, Types, And Functions
Device-tree update helpers include `mobility_rtas_call`, `pseries_devicetree_update`, `delete_dt_node`, `update_dt_node`, `update_dt_property`, `add_dt_node`, and `post_mobility_fixup`. Migration flow helpers are `poll_vasi_state`, `wait_for_vasi_session_suspending`, `do_suspend`, `do_join`, `pseries_suspend`, `pseries_cancel_migration`, `pseries_migrate_partition`, and `rtas_syscall_dispatch_ibm_suspend_me`. Sysfs setup uses `migration_store` and `mobility_sysfs_init`.

## Control Flow
Migration first suspends VAS and HVPIPE, waits for the VASI session to enter suspending state, optionally relaxes hardlockup watchdog timeout, and calls `stop_machine` so all online CPUs enter `H_JOIN`. The CPU that receives `H_CONTINUE` performs `ibm,suspend-me`; on completion one CPU marks the shared state done and prods the rest. Successful migration runs `post_mobility_fixup`: activate firmware, lock CPU hotplug readers, tear down cacheinfo, process RTAS update-nodes/update-properties directives, rebuild cacheinfo, refresh mitigations, and reread hv-24x7 system info. Failed suspend attempts can retry while VASI remains suspending; final failure signals cancellation.

## State And Persistence
Persistent kernel state includes the `/sys/kernel/mobility` kobject, watchdog LPM factor sysctl when enabled, temporary update buffers, and live device-tree changes. Migration changes firmware/hypervisor session state and may alter runtime topology, cache nodes, mitigation choices, VAS, and HVPIPE availability.

## Dependencies And Integration Points
Depends on RTAS `ibm,update-nodes`, `ibm,update-properties`, and `ibm,suspend-me`; PAPR hcalls `H_VASI_STATE`, `H_JOIN`, `H_PROD`, and `H_VASI_SIGNAL`; DLPAR attach/detach/configure helpers; cacheinfo; CPU hotplug; stop_machine; watchdog code; VAS and HVPIPE migration handlers; hv-24x7; and sysfs.

## Risks And Edge Cases
Firmware can split property updates across calls, remove/add platform-facilities nodes that drivers cannot handle, or omit VASI state support. The code intentionally ignores platform-facilities add/remove operations. H_JOIN can return prematurely due to unrelated prods and must retry until shared done state is visible. Destination systems can have fewer SLB entries, so the code clamps SLB size before suspend. Device tree update failures leave partially refreshed topology.

## Test Signals
Run migration through sysfs and RTAS syscall dispatch, including successful, retry, and cancellation paths. Validate device-tree changes, cacheinfo rebuild, CPU hotplug exclusion, VAS/HVPIPE disable and resume, watchdog timeout restoration, VASI completion wait, platform-facilities handling, and PRRN/migration-scope update processing.
