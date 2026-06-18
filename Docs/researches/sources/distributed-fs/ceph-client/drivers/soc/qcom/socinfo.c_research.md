# sources/distributed-fs/ceph-client/drivers/soc/qcom/socinfo.c

## Purpose

`socinfo.c` registers Qualcomm SoC identity from the SMEM hardware/software build-id record. It maps Qualcomm numeric IDs to marketing names, publishes a `soc_device`, feeds SMEM identity bytes into the randomness pool, and optionally creates debugfs files for raw socinfo fields, PMIC metadata, and image-version strings.

## Important APIs, Types, and Functions

`struct qcom_socinfo` stores the registered `soc_device`, attributes, and optional debugfs root. `struct soc_id` and the large `soc_id[]` table map `QCOM_ID_*` values to names. `socinfo_machine()` performs lookup. `qcom_socinfo_probe()` reads `SMEM_HW_SW_BUILD_ID`, fills `soc_device_attribute`, registers it, initializes debugfs, and calls `add_device_randomness()`. Debugfs helpers include `qcom_show_build_id()`, PMIC model/die revision readers, image-version file operations, and `socinfo_debugfs_init()/exit()`.

## Control Flow

Probe obtains the SMEM record and its size. It builds `family = "Snapdragon"`, `machine` from the ID table, decimal `soc_id`, major/minor `revision`, and optional serial number when the SMEM item is large enough. After `soc_device_register()`, debugfs initialization decodes fields by `fmt` version using fallthrough cases. Image-version directories are backed by SMEM version tables 469 and 667.

## State and Persistence Behavior

The driver has no file persistence. It snapshots pointers and formatted strings for soc-bus registration while the authoritative data remains in SMEM. Debugfs exposes raw or decoded SMEM fields read through the original SMEM buffer and cached converted values. Remove unregisters the `soc_device` and removes debugfs recursively.

## Dependencies and Integration Points

It integrates with Qualcomm SMEM, `linux/soc/qcom/socinfo.h`, dt-binding Qualcomm IDs, the generic soc bus, debugfs, seq_file, and the kernel entropy pool. User space observes results through `/sys/devices/soc*` and optional `/sys/kernel/debug/qcom_socinfo`.

## Risks and Edge Cases

The ID table must be kept synchronized with `dt-bindings/arm/qcom,ids.h`; missing entries produce a numeric `soc_id` but no machine string. Debugfs field decoding is heavily version-dependent and relies on SMEM item sizes for only selected variable-offset fields. The image-version loop creates entries if SMEM table pointers exist but does not validate every indexed block against the returned table size. `qcom_show_build_id()` prints firmware-provided bytes as a C string, relying on SMEM layout correctness.

## Test Signals

Test with old and new socinfo formats, unknown IDs, absent serial fields, malformed PMIC array offsets, and both image-version SMEM tables. Verify soc-bus attributes, debugfs fields by format version, PMIC model fallback for unknown IDs, remove cleanup, and entropy feed path under KASAN/KMSAN for bounds issues.
