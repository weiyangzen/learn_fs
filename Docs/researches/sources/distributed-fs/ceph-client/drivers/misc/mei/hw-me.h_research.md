<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.h

Purpose: declares ME hardware configuration structures, the ME hardware private state, platform configuration indexes, and public entry points for the classic ME/GSC hardware backend.

Important APIs and types: `struct mei_cfg` describes generation-specific FW status registers, optional firmware-exclusion quirk, kind string, DMA descriptor sizes, FW-version support, and TRC support. `struct mei_me_hw` stores config, MMIO address, IRQ, PG state, D0i3 support, host-buffer depth, FW status reader callback, and optional polling-thread state. `enum mei_cfg_idx` indexes the platform config table and must match `mei_cfg_list[]` in `hw-me.c`. Public functions include `mei_me_get_cfg()`, `mei_me_dev_init()`, PG enter/exit, IRQ handlers, and polling thread.

Control flow: PCI probe code selects a `mei_cfg` index, obtains it with `mei_me_get_cfg()`, calls `mei_me_dev_init()`, wires MMIO/IRQ fields, and registers/start the common MEI device. Interrupt and PM code use the declared handlers.

State and persistence: no storage in the header. It defines the layout embedded after `struct mei_device` allocation and accessed with `to_me_hw(dev)`.

Dependencies and integration: includes PCI, IRQ, MEI public headers, `mei_dev.h`, and `client.h`. The enum and config table are a strict cross-file ABI inside the driver.

Risks: enum/table desynchronization selects wrong platform behavior. The `to_me_hw` cast assumes `struct mei_me_hw` is allocated immediately after `struct mei_device`; allocation changes must preserve that layout. Polling mode is inferred from negative IRQ and must be initialized consistently by probe.

Test signals: build coverage for all config enum users, probe using every config index present in PCI ID tables, D0i3/runtime PM tests, and polling-mode tests when no IRQ is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.h -->
