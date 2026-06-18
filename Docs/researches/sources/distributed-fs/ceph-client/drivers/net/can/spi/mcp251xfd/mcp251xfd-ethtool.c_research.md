# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ethtool.c

Purpose: Exposes MCP251xFD ring sizing, IRQ coalescing, and hardware timestamp capability through ethtool.

Important APIs, types, and functions: `mcp251xfd_ethtool_init()` installs ethtool ops and initializes defaults. Ring get/set functions report and set RX/TX pending objects. Coalesce get/set functions expose IRQ delay and max-frame thresholds. Layout decisions are delegated to `can_ram_get_layout()`.

Control flow: Getters compute current-mode layout maxima and return current `priv` fields. Setters normalize requested values, reject live changes with `-EBUSY` when the device is running, and store settings for the next ring allocation.

State and persistence behavior: Mutates in-memory RX/TX object count and coalescing fields only. Settings do not persist across driver unload or reboot.

Dependencies and integration points: Uses Linux ethtool ops, SocketCAN timestamp reporting, and the CAN RAM layout helper. Ring allocation later consumes these settings.

Risks: Bad normalization can overcommit RAM or violate FIFO depth/coalescing constraints. The ethtool disable convention `usecs=0,max_frames=1` must remain intact.

Test signals: `ethtool -g/-G` and `-c/-C` in CAN and CAN-FD modes, clamping tests, live-change `-EBUSY`, and RX/TX coalescing interrupt behavior.
