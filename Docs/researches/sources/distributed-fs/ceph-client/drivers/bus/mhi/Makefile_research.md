# sources/distributed-fs/ceph-client/drivers/bus/mhi/Makefile

Purpose: top-level build file for MHI bus host and endpoint subdirectories.

Important declarations: `obj-$(CONFIG_MHI_BUS) += host/` builds the host stack when enabled; `obj-$(CONFIG_MHI_BUS_EP) += ep/` builds the endpoint stack when enabled.

Control flow and state: build-time only; no runtime state. It delegates actual object composition to the subdirectory Makefiles.

Dependencies and integration: links Kconfig symbols to host/endpoint build directories. It assumes subdirectory Makefiles define `mhi.o`, `mhi_ep.o`, and optional controller objects.

Risks and tests: risk is limited to symbol/path drift. Test signals are incremental kernel builds for `CONFIG_MHI_BUS=m/y`, `CONFIG_MHI_BUS_EP=m/y`, and combined host+endpoint configurations.
