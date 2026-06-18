# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/rpc-if.c

Purpose: Renesas RPC-IF HyperFlash adapter. It maps HyperBus operations onto the Renesas RPC-IF framework and registers the resulting HyperFlash through the HyperBus core.

Important APIs/types/functions: `struct rpcif_hyperbus` embeds `struct rpcif`, `hyperbus_ctlr`, and `hyperbus_device`. `rpcif_op_tmpl` encodes 8-bit DDR command/address/data defaults. Operation helpers are `rpcif_hb_prepare_read()`, `rpcif_hb_prepare_write()`, `rpcif_hb_read16()`, `rpcif_hb_write16()`, and `rpcif_hb_copy_from()`. Lifecycle is `rpcif_hb_probe()`/`rpcif_hb_remove()`.

Control flow: probe allocates state, initializes RPC-IF software state from the parent device, enables runtime PM, initializes hardware in HyperBus mode, fills HyperBus map size/virt from RPC-IF direct map, installs read/write/copy ops, grabs the first parent child node, and registers with HyperBus core. 16-bit accesses prepare a manual RPC-IF transfer and call `rpcif_manual_xfer()`. Bulk reads prepare a read op then use `rpcif_dirmap_read()`.

State and persistence: persistent state is HyperFlash contents. Runtime state is RPC-IF device configuration, runtime PM enablement, direct-map pointer/size, child OF node, and HyperBus MTD registration.

Dependencies/integration: Renesas RPC-IF API (`memory/renesas-rpc-if.h`), HyperBus core, platform device id `rpc-if-hyperflash`, parent OF layout, runtime PM, and MTD.

Risks: probe obtains a child OF node but remove does not release it with `of_node_put()`, unlike the AM654 driver. Write bulk `copy_to` is not provided, so map users only get 16-bit writes plus bulk reads. Runtime PM is enabled/disabled but individual operations rely on RPC-IF internals for active state.

Test signals: RPC-IF init/hw-init failure paths, manual 16-bit read/write correctness, dirmap reads across ranges, HyperBus registration failure cleanup, runtime PM enable/disable, and OF node reference accounting.
