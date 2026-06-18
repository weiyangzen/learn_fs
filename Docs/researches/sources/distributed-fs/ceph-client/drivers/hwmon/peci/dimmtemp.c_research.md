# sources/distributed-fs/ceph-client/drivers/hwmon/peci/dimmtemp.c

Purpose: auxiliary-bus hwmon client exposing DIMM temperatures and threshold limits through PECI for multiple Intel server CPU generations. It discovers populated DIMMs dynamically and registers channels only after memory training data is usable.

Important APIs/types/functions: `struct peci_dimmtemp` stores the PECI device, generation info, delayed detection work, per-DIMM cached temperature/threshold data, labels, DIMM bitmap, and retry counter. `struct dimm_info` defines channel-rank count, DIMM index count, minimum PECI revision, and threshold-read callback. `get_dimm_temp()`, `update_thresholds()`, `get_dimm_thresholds()`, `check_populated_dimms()`, `create_dimm_temp_info()`, and generation-specific `read_thresholds_*()` functions implement detection and reads. `dimmtemp_read()`, `dimmtemp_read_string()`, and `dimmtemp_is_visible()` implement `hwmon_ops`.

Control flow: probe allocates private state, binds generation data from the auxiliary-device ID, warns on low PECI revision, initializes autocancel delayed work, and calls `create_dimm_temp_info()`. Detection reads `PECI_PCS_DDR_DIMM_TEMP` for each channel rank; `-EINVAL` marks empty ranks, empty or not-ready results cause delayed retry every five seconds, and repeated all-empty results eventually return no-device without failing probe. Once populated DIMMs are known, labels such as `DIMM A1` are allocated and hwmon is registered. Temperature reads use PCS DDR DIMM temperature; threshold reads use platform-specific PCI, endpoint PCI, or MMIO paths.

State and persistence: `dimm_mask` controls visible channels. Per-DIMM temperature and threshold values are cached for one second using `common.h` helpers. `no_dimm_retry_count` persists across delayed retries to distinguish early boot from truly empty memory. No persistent storage is written.

Dependencies and integration: depends on auxiliary bus, devm delayed work helpers, PECI CPU APIs, hwmon info API, bitmaps, bitfields, workqueues, and units. It imports namespace `PECI_CPU` and is instantiated by PECI CPU generation devices.

Risks: detection intentionally defers on ambiguous boot-time states, so hwmon registration may appear later than probe. The fixed maximum array is based on HSX maximums; a defensive `WARN_ONCE` protects unsupported larger layouts. Generation-specific threshold address formulas are brittle and must track CPU uncore documentation. `adm` style threshold reads may return `-ENODATA` when endpoint address discovery fails, affecting max/crit attributes while temperature reads still work.

Test signals: delayed retry behavior during early boot, no-DIMM handling after retry limit, label and visibility for populated DIMMs, per-generation threshold reads, cache refresh after HZ, and successful module unload canceling delayed work.
