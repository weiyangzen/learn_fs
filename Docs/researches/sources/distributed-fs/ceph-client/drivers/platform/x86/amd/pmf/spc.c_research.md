# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/spc.c

Purpose: `spc.c` implements Smart PC input collection for the PMF TEE policy engine. It gathers system, power, thermal, battery, sensor-fusion, platform-profile, lid, and custom BIOS input data into `struct ta_pmf_enact_table`.

Important APIs, types, and functions: public `amd_pmf_populate_ta_inputs()` fills TA enact inputs. Debug builds provide string converters and `amd_pmf_dump_ta_inputs()`. Helpers include `amd_pmf_get_smu_info()`, `amd_pmf_get_battery_info()`, `amd_pmf_get_slider_info()`, `amd_pmf_get_sensor_info()`, `amd_pmf_get_custom_bios_inputs()`, and custom BIOS mapping helpers that split inputs across `bios_input_1` and `bios_input_2`.

Control flow: when the TEE policy engine invokes enactment, PMF calls `amd_pmf_populate_ta_inputs()`. It sets lid state from ACPI, power source from PMF core, transfers fresh SMU metrics into the selected v1/v2 metrics table, reads battery properties, maps current platform profile to TA slider enum, asks AMD SFH for ALS/HPD/SRA data, and consumes at most one queued custom BIOS input snapshot while preserving previous values for unchanged inputs.

State and persistence: SPC reads and updates `amd_pmf_dev` metrics tables, custom BIOS previous-value storage, and circular-buffer tail. It does not persist data outside runtime memory. TA inputs are a snapshot of current system state plus preserved custom BIOS input state.

Dependencies and integration points: depends on ACPI lid helpers, power_supply APIs, AMD SFH HID information (`amd_get_sfh_info()`), PMF metrics transfer and platform profile state, and ACPI custom BIOS input queueing from `acpi.c`.

Risks: `amd_pmf_get_battery_prop()` loops possible battery names but returns `value.intval` even if no supply was found, leaving an uninitialized return path. It also does not break after a successful read, so later missing supplies do not stop prior value use clearly. Several input-gathering helpers ignore failures in the top-level populate path, meaning TA may receive default or stale values. SMU metric transfer send-command failures are not checked before copying from `dev->buf`.

Test signals: TA input snapshots under AC/DC, battery present/absent cases, platform-profile mapping for performance/balanced/low-power profiles, SFH ALS/HPD/SRA availability and absence, lid open/closed mapping, custom BIOS input queue consumption and previous-value preservation, and debug dumps when `AMD_PMF_DEBUG` is enabled.
