# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs.c

Purpose: creates the main `qat` sysfs attribute group for device state control, service configuration, PM idle support, auto-reset, ring-pair service lookup, and ring-pair count.

Important API: `adf_sysfs_init`. Attributes include `state`, `cfg_services`, `pm_idle_enabled`, `auto_reset`, `rp2srv`, and `num_rps`.

Control flow and state: `state_store` starts/stops the device after checking reset/busy state. `cfg_services_store` parses service strings, requires device down, updates config, and refreshes capabilities. `pm_idle_enabled_store` requires device down and stores config. `auto_reset_store` directly toggles `accel_dev->autoreset_on_error`. `rp2srv_store/show` stores a selected ring number under `accel_dev->sysfs.lock` and returns its service mapping. Init adds the group and sets ring number to unset.

Dependencies and integration: depends on QAT device manager, config parser/storage, service mapping macros, and lifecycle APIs.

Risks and test signals: sysfs state changes can trigger full device lifecycle; service changes while up are rejected. Test invalid service strings, down/up transitions, busy device rejection, ring bounds, unset `rp2srv`, and config persistence.
