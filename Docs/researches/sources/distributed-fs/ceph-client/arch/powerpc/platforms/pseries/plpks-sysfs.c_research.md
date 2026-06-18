# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-sysfs.c

Purpose: Exposes PLPKS configuration values under `/sys/firmware/plpks/config`.

Important APIs/types/functions: Uses `PLPKS_CONFIG_ATTR` to create read-only attributes for version, object limits, total/used space, supported policies, signed update algorithms, and wrapping features. Exports `plpks_config_create_softlink()`.

Control flow: Init checks PLPKS availability, creates `plpks` and `config` kobjects below `firmware_kobj`, and attaches the attribute group. Each sysfs read calls the corresponding `plpks_get_*` accessor. `used_space` refreshes configuration in the core before returning.

State and persistence: Keeps global kobject pointers for the PLPKS root and config directory. All displayed data comes from cached or refreshed PLPKS core configuration.

Dependencies and integration points: Depends on `plpks.c` availability/config accessors, firmware sysfs, pseries subsystem initcall ordering, and consumers that may create symlinks to the config directory.

Risks: Initialization cleanup must release both kobjects on partial failures. Attribute values are only as fresh as the core accessor semantics, so most fields are initialization snapshots except used space.

Test signals: Sysfs presence only when PLPKS is available, read formatting for all attributes, symlink creation success/failure, kobject allocation failure paths, and config value refresh after object writes/removes.

Source read size: 96 lines, 2787 bytes.
