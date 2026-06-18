# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-mbox.c

## Purpose
`isst-core-mbox.c` implements the `struct isst_platform_ops` backend for API version 1 platforms that expose Intel Speed Select controls through mailbox, MSR, and selected MMIO operations. It translates the generic operations used by `isst-core.c` into `ISST_IF_MBOX_COMMAND`, `ISST_IF_IO_CMD`, and MSR ioctl calls, decodes mailbox response bitfields into common SST data structures, and writes uncore frequency sysfs settings when applying performance levels.

## Important APIs, Types, And Functions
The exported entry point is `mbox_get_platform_ops()`, returning a static `mbox_ops` table. The low-level command paths are `_send_mbox_command()` and `_send_mmio_command()`. Backend parameter state is controlled by `mbox_update_platform_param()` for `ISST_PARAM_MBOX_DELAY` and `ISST_PARAM_MBOX_RETRIES`. Feature readers include `mbox_read_pm_config()`, `mbox_get_config_levels()`, `mbox_get_ctdp_control()`, `mbox_get_tdp_info()`, `mbox_get_pwr_info()`, `mbox_get_coremask_info()`, `mbox_get_get_trl()`, `mbox_get_get_trls()`, `mbox_get_trl_bucket_info()`, `mbox_get_pbf_info()`, and `mbox_get_fact_info()`. Mutators include `mbox_set_tdp_level()`, `mbox_set_pbf_fact_status()`, `mbox_pm_qos_config()`, `mbox_set_clos()`, and `mbox_clos_associate()`.

## Control Flow
Generic calls from `isst-core.c` enter through the ops table. Most mailbox operations build a command, subcommand, parameter, and request-data value, call `_send_mbox_command()`, then unpack the response into `isst_pkg_ctdp`, `isst_pkg_ctdp_level_info`, `isst_pbf_info`, `isst_fact_info`, or `isst_clos_config`. `_send_mbox_command()` handles optional delay, opens `/dev/isst_interface`, retries ioctl failures, and returns response data. For non-SKX CLOS reads/writes other than PM QoS config, `_send_mbox_command()` routes to `_send_mmio_command()` using PM QoS/CLOS/PQR offsets instead of mailbox commands.

## State And Persistence Behavior
Backend process state is limited to `mbox_delay` and `mbox_retries`. Hardware state can be changed by CONFIG_TDP set-level and set-control commands, CLOS PM QoS configuration, CLOS parameter writes, PQR association writes, PM config writes, and TRL MSR changes initiated through shared core helpers. `_set_uncore_min_max()` persists uncore min/max frequency choices to `/sys/devices/system/cpu/intel_uncore_frequency/package_%02d_die_%02d/*_freq_khz`.

## Dependencies And Integration Points
The file depends on `linux/isst_if.h`, `/dev/isst_interface`, mailbox and IO kernel modules, `isst-core.c` wrappers for MSR access, display error helpers, topology helpers such as `set_cpu_mask_from_punit_coremask()` and `find_phy_core_num()`, and platform predicates from `isst-config.c`. It supplies frequency-display semantics: mailbox values normally use `DISP_FREQ_MULTIPLIER` of 100, while EMR expands TRL level names to `level-N`.

## Risks And Edge Cases
Mailbox bitfield decoding is platform-specific. Several failure paths return zeroed data to keep legacy platforms usable, notably config-level fallback where dynamic SST is absent. `_send_mbox_command()` exits on `ENOTTY`, so missing kernel modules are fatal. CLOS routing differs between SKX and newer platforms, which risks mismatched logical core ids if topology mapping is wrong. Uncore sysfs path names are assumed to match package/die formatting. `mbox_pm_qos_config()` refuses to disable core-power while turbo-freq remains enabled. EMR has five TRL levels; other mailbox platforms expose three named levels.

## Test Signals
Backend tests should validate mailbox command packing, retry/delay behavior, CLOS MMIO fallback selection, bitfield decoding for config levels, TDP info, PBF masks, FACT buckets, and PM QoS enable/disable transitions. Hardware or ioctl mocks should cover ENOTTY handling, failed mailbox reads, locked TDP set-level, invalid FACT bucket handling, and uncore sysfs write failures.
