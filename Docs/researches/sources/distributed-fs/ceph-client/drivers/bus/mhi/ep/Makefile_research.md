# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Makefile

Purpose: builds the endpoint MHI bus stack.

Important declarations: `obj-$(CONFIG_MHI_BUS_EP) += mhi_ep.o`; `mhi_ep-y := main.o mmio.o ring.o sm.o`.

Control flow and state: build-time aggregation only. It links controller registration, MMIO helpers, ring cache/interrupt support, and state-machine helpers into one endpoint object.

Dependencies and integration: driven by `CONFIG_MHI_BUS_EP`; exports symbols consumed by endpoint controller and client drivers.

Risks and tests: path/object drift would drop part of the endpoint stack. Test signals are module and built-in builds, symbol export availability, and link coverage for functions referenced across `main.c`, `mmio.c`, `ring.c`, and `sm.c`.
