<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/proc.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/proc.c

Purpose: Optional `/proc/bus/pnp` interface exposing PnP BIOS nodes, ESCD data, ISA config, and raw resource streams, with write access to dynamic/boot node resource data.

Important APIs/types/functions: show functions for configuration, ESCD info/data, legacy resources, device list, and per-node data. `pnpbios_proc_write()` writes raw node data back via `pnp_bios_set_dev_node()`. `pnpbios_interface_attach_device()` creates per-node files under current and boot directories. `pnpbios_proc_init/exit()` manage proc tree.

Control flow: proc init creates `bus/pnp`, `boot`, and summary files. Device attachment creates hex-named node files; current config files are omitted when `pnpbios_dont_use_current_config` is set. Reads allocate node/info buffers, call BIOS wrappers, and stream data. Writes validate byte count equals node data length, copy from user, and set node.

State/persistence: reads live BIOS state; writes can mutate volatile current or nonvolatile boot configuration depending on file path. Proc dentries persist until exit.

Dependencies/integration: procfs, seq_file, PnP BIOS wrappers, node_info sizing, user copy APIs.

Risks: help text correctly warns writes can desynchronize the PnP driver because direct proc writes do not notify resource state. ESCD size is capped at 32 KiB, but other BIOS calls use large buffers. Per-node data pointer encodes boot flag in high byte via cast.

Test signals: proc tree creation/removal, ESCD sanity cap, node sequence handling, write length validation, current-config disabled behavior, and user copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/proc.c -->
