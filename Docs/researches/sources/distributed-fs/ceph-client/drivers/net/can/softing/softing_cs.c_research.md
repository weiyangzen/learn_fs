# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_cs.c

Purpose: PCMCIA bridge driver for Softing/Vector/EDIC CAN cards. It identifies supported card IDs, configures PCMCIA resources, and creates a `softing` platform device with platform data consumed by the generic DPRAM driver.

Important APIs/types/functions: `softingcs_platform_data[]` lists card names, manufacturer/product IDs, generation, bus count, clock/BRP/SJW limits, DPRAM size, boot/load/app firmware paths, and reset/IRQ callbacks. `softingcs_find_platform_data()` matches IDs. `softingcs_reset()` and `softingcs_enable_irq()` write PCMCIA config bytes. `softingcs_probe_config()` requests memory window parameters. `softingcs_probe()` creates a custom platform device with MEM and IRQ resources.

Control flow: PCMCIA probe matches IDs, selects platform data, configures IRQ/IOMEM/VPP/VCC, requests and enables the PCMCIA device, allocates an embedded platform_device plus resources, fills memory and IRQ resources, assigns a unique id, names it `softingcs.N`, and registers it. Remove unregisters the platform device and disables PCMCIA.

State and persistence: static platform data is immutable. `softingcs_index` assigns increasing IDs under spinlock. `pcmcia->priv` stores the platform device. Runtime firmware/card state lives in the generic Softing platform driver.

Dependencies/integration: PCMCIA core, platform bus, Softing platform data ABI, firmware files under `softing-4.6/`, and generic `softing` platform driver.

Risks: memory window size and generation-specific width/wait settings must match cards. `kzalloc_obj()` usage assumes local macro/support in this source tree. Platform device lifetime uses custom release to free the enclosing allocation. Generation 2 cards do not use `enable_irq` callback.

Test signals: insert each supported card ID; verify platform device creation and resource ranges; firmware request should match platform data; removal should unregister platform child and disable PCMCIA; unsupported IDs should return `-ENOTTY`.
