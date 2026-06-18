# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Makefile

Purpose: Defines the composite Mali-C55 driver object.

Important APIs/types/functions: No C API. `mali-c55-y` aggregates capture, core, ISP, params, resizer, stats, and TPG objects; `obj-$(CONFIG_VIDEO_MALI_C55) += mali-c55.o` ties the composite object to Kconfig.

Control flow and state: Kbuild compiles each implementation unit and links them into one module or built-in object.

Dependencies and integration: The object list must match exported functions declared in `mali-c55-common.h`; omissions become unresolved symbols.

Risks: Adding a new implementation file without updating this list leaves code unbuilt. Removing a listed file breaks build.

Test signals: `make M=drivers/media/platform/arm/mali-c55`, module load, and link-time symbol checks.
