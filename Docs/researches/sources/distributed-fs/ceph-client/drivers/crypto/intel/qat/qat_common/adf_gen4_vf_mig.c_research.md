## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.c

Purpose: Implements Gen4 VF live-migration device operations, including migration buffer setup, VF bank quiesce/resume, compatibility checks, state serialization, and state restore.

Important APIs/functions: `adf_gen4_init_vf_mig_ops()` fills `qat_migdev_ops`. Device lifecycle functions allocate/free a 4096-byte state buffer, open/close per-VF `adf_gen4_vfmig` with an `adf_mstate_mgr`, and reset setup sizes. `adf_gen4_vfmig_suspend_device()` drains each VF bank, records stopped banks, and quiesces coalescing timers; resume clears drain status for stopped banks. Save/load setup handles config sections for capabilities, ring-to-service map, and extended DC capabilities. Save/load state handles generic VF state, misc PF2VM/VM2PF/VINT registers, and ETR bank state.

Control flow and state: Migration state is organized with `adf_mstate_mgr` sections: config/setup, generic VF fields, misc BAR registers, and per-bank ETR registers. `mdev->setup_size` and `remote_setup_size` split static setup from dynamic state. Rate-limiting SLAs are serialized as `mig_user_sla` records and checked on load to ensure destination CIR/PIR and service/ring-pair coverage are sufficient. PFVF misc save takes `pfvf_mig_lock` with a timeout to avoid racing PF/VF messages.

Dependencies/integration: Depends on bank state save/restore callbacks, Gen4 bank drain/quiesce helpers, PFVF compatibility helpers, rate limiting, migration state manager APIs, VF info fields, and Gen4 mailbox/VINT offsets.

Risks and test signals: Risks include insufficient 4096-byte state space, partial setup loads returning `-EAGAIN`, PFVF lock timeout, SLA mismatch, incompatible VF protocol version, capability mask mismatch, and failure to resume drained banks after errors. Tests should cover save/load round trips, partial remote setup lengths, incompatible/newer VF compat versions, destination capability superset/equality rules, SLA capacity checks, bank save/restore failures, and suspend/resume cleanup after a mid-bank drain failure.
