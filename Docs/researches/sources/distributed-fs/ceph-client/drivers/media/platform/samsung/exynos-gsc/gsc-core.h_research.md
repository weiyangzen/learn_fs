# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.h

Purpose: primary internal header for the Exynos G-Scaler driver. It defines constants, flags, color/datapath enums, core structures, inline register helpers, and cross-file function prototypes.

Important APIs and types: key types include `gsc_fmt`, `gsc_frame`, `gsc_addr`, `gsc_ctrls`, `gsc_scaler`, `gsc_m2m_device`, `gsc_pix_max`, `gsc_pix_min`, `gsc_pix_align`, `gsc_variant`, `gsc_driverdata`, `gsc_dev`, and `gsc_ctx`. It declares format/scaler/control/address helpers, mem2mem registration functions, job finish, and low-level `gsc_hw_*` register functions.

Control flow: `gsc-core.c`, `gsc-m2m.c`, and `gsc-regs.c` share this contract. File handles map to contexts via `file_to_ctx`; V4L2 controls map via `ctrl_to_ctx`; queue and hardware programming paths use `ctx_get_frame`, state helpers, and register inlines.

State and persistence: the header defines but does not allocate device/context state. Device state persists for the platform instance; context state persists per V4L2 file handle; frame/address/scaler fields are updated during format, selection, and job setup.

Dependencies and integration points: includes Linux delay/sched/spinlock/types/io/PM runtime, V4L2 controls/device/mem2mem/mediabus, vb2 DMA-contig, and `gsc-regs.h`. It is the shared ABI among all exynos-gsc compilation units.

Risks: broad shared structs increase coupling. Inline MMIO helpers directly read/modify/write IRQ and enable registers; callers must hold appropriate state and hardware power. Some comments contain typos and legacy terminology, so code should be treated as authoritative. `GSC_MAX_CLOCKS` and `GSC_MAX_DEVS` bound OF match data.

Test signals: full exynos-gsc build, sparse/compiler warning coverage after struct changes, V4L2 mem2mem runtime tests, and register-programming tests through `gsc-regs.c`.
