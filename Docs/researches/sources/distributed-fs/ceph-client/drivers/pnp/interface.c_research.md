<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/interface.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/interface.c

Purpose: Sysfs user interface for PnP devices. It exposes possible options, current resources, IDs, and allows privileged resource commands via the writable `resources` attribute.

Important APIs/types/functions: `pnp_info_buffer` and `pnp_printf()` implement PAGE_SIZE bounded formatting. `pnp_print_*()` functions render option types. Sysfs methods are `options_show()`, `resources_show()`, `resources_store()`, and `id_show()`. `pnp_dev_groups` attaches attributes to all PnP devices.

Control flow: show paths iterate device options/resources and render text. Store rejects attached devices, then parses commands: `disable`, `activate`, `fill`, `auto`, `clear`, `get`, and `set ...`. `set` clears current resources and parses repeated `io`, `mem`, `irq`, `dma`, and `bus` tokens into new resource entries under `pnp_res_mutex`.

State/persistence: sysfs writes mutate `dev->resources`, `dev->active`, and firmware/device state through manager and protocol callbacks. No separate persistence; firmware may persist through backend implementation.

Dependencies/integration: PnP manager APIs, protocol get/set/disable, resource helpers, mutexes, sysfs attribute groups, and user access via driver core.

Risks: parser uses `simple_strtoull()` on the kernel buffer and has minimal validation for trailing garbage or unsupported flags. `pnp_printf()` truncates silently by stopping output. User-written resource sets bypass conflict checks until activation and can configure dangerous legacy resources.

Test signals: sysfs reads for large option lists, command parsing for all resource types, busy-device rejection, protocol get/set integration, and invalid input fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/interface.c -->
