# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_benchmark.h

Purpose: declares the Loongson debugfs copy benchmark entry point.

Important APIs/types/functions: `lsdc_show_benchmark_copy(struct lsdc_device *, struct drm_printer *)`.

Control flow: debugfs code calls the function to print benchmark results.

State and persistence: no state in the header.

Dependencies and integration points: includes `lsdc_drv.h` for `struct lsdc_device`.

Risks and test signals: declaration must match implementation and debugfs use. Test compile and `benchmark` debugfs file.
