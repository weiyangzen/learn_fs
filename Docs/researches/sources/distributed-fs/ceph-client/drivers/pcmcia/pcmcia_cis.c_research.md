# sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_cis.c

Purpose: Provides higher-level CIS helper APIs used by PCMCIA client drivers and the bus layer. It reads and loops tuples, auto-selects configuration table entries, extracts tuple buffers, and optionally retrieves Ethernet MAC addresses from LAN function extension tuples.

Important APIs and functions: Public functions are `pccard_read_tuple()`, `pcmcia_loop_config()`, `pcmcia_loop_tuple()`, `pcmcia_get_tuple()`, and, under `CONFIG_NET`, `pcmcia_get_mac_from_cis()`. Internal helpers include `pccard_loop_tuple()`, `pcmcia_do_loop_config()`, `pcmcia_io_cfg_data_width()`, tuple-copy helpers, and LAN-node-id parsing.

Control flow: `pccard_read_tuple()` fetches the first matching tuple and parses it. `pccard_loop_tuple()` iterates tuples of a type, optionally parses each, and calls a callback until it returns success. `pcmcia_loop_config()` walks `CISTPL_CFTABLE_ENTRY` tuples, tracks defaults, applies automatic Vcc/Vpp/audio/I/O/IOMEM setup to `pcmcia_device`, and calls a driver-supplied `conf_check`. Tuple getters copy the first tuple payload into caller-owned memory.

State and persistence: The helpers mutate `struct pcmcia_device` configuration fields during auto-configuration: `config_index`, `vpp`, `config_flags`, resources, `io_lines`, and `card_addr`. They otherwise allocate transient buffers.

Dependencies and integration points: Sits on top of low-level tuple iteration and parsing in `cistpl.c`, and feeds resource setup in `pcmcia_resource.c` and PCMCIA client drivers. The MAC helper integrates with `struct net_device`.

Risks: Automatic configuration must interpret defaults correctly and avoid selecting unsupported Vcc, missing I/O windows, or undersized memory windows. Callback return convention is inverted from normal iteration: returning 0 stops with success. Tuple payload allocation makes callers responsible for freeing buffers.

Test signals: Client drivers using `pcmcia_loop_config()`, cards with default CFTABLE entries, multi-window I/O cards, memory-window cards, tuple-copy users, and network cards with `CISTPL_FUNCE_LAN_NODE_ID`.
