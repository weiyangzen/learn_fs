# sources/distributed-fs/ceph-client/drivers/media/platform/arm/Kconfig

Purpose: Provides the top-level ARM media platform Kconfig menu and includes the Mali-C55 ISP driver Kconfig.

Important APIs/types/functions: No C API; it defines menu structure through a comment and `source "drivers/media/platform/arm/mali-c55/Kconfig"`.

Control flow and state: Kernel configuration flow enters this file from the media platform Kconfig hierarchy and delegates all actual options to the Mali-C55 subdirectory. No runtime state exists.

Dependencies and integration: Integrated by the kernel Kconfig tree under media platform drivers. It is paired with the ARM platform `Makefile`.

Risks: Any new ARM media driver under this directory must be sourced here or it will not be configurable. Path mismatch would break menuconfig.

Test signals: `make menuconfig` visibility and `scripts/kconfig/conf` coverage for `VIDEO_MALI_C55`.
