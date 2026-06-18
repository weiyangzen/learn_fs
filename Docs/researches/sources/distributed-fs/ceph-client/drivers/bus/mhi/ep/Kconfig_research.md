# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Kconfig

Purpose: declares the endpoint-side MHI bus implementation configuration symbol.

Important declarations: `CONFIG_MHI_BUS_EP` is a tristate named "Modem Host Interface (MHI) bus Endpoint implementation". Help text describes endpoint devices such as SDX55 modem over PCIe.

Control flow and state: configuration-time only. Enabling it selects compilation of the endpoint bus stack through the endpoint Makefile.

Dependencies and integration: no explicit dependency is declared here; controller drivers are expected to provide endpoint transport operations and register with `mhi_ep_register_controller()`.

Risks and tests: risk is that missing dependencies may allow build configurations without required lower-level transport symbols, though the stack itself depends mostly on core kernel facilities. Test signals are `mhi_ep.o` module/builtin builds and endpoint controller driver builds against exported endpoint APIs.
