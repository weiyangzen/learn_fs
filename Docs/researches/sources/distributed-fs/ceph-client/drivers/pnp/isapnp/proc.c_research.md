<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/proc.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/proc.c

Purpose: Optional `/proc/bus/isapnp` interface exposing raw 256-byte ISA PnP logical-device configuration space.

Important APIs/types/functions: `isapnp_proc_bus_lseek()`, `isapnp_proc_bus_read()`, `isapnp_proc_attach_device()`, and `isapnp_proc_init()`.

Control flow: proc init creates `bus/isapnp` and iterates ISA PnP devices. Per-device read begins ISA config for the card/logical device, reads byte indexes from the file offset up to 256, copies to user, and ends config.

State/persistence: no persistent state beyond proc dentries in card/device structures. Reads access live ISA PnP registers.

Dependencies/integration: procfs, ISA PnP exported config APIs, card/device numbering.

Risks: raw config exposure can race with configuration changes despite `isapnp_cfg_mutex` inside begin/end. `__put_user()` return is ignored after `access_ok`.

Test signals: proc directory creation for each card/device, bounded seek/read, concurrent reads, and behavior when proc entry allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/proc.c -->
