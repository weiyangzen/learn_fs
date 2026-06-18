# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.h

Purpose: Declares generic data structures for laying out CAN controller RAM between RX and TX objects in CAN 2.0 and CAN-FD modes.

Important APIs, types, and functions: Defines `CAN_RAM_NUM_MAX`, `enum can_ram_mode`, `struct can_ram_obj_config`, `struct can_ram_config`, `struct can_ram_layout`, and `can_ram_get_layout()`.

Control flow: No executable flow. The structs describe object sizes, defaults, min/max counts, FIFO counts, FIFO depth constraints, total RAM size, and computed default/max/current layouts.

State and persistence behavior: Defines transient configuration/calculation containers only; no hardware or persistent state.

Dependencies and integration points: Includes ethtool types because calculation accepts ethtool ring and coalesce structs. MCP251xFD publishes a concrete config and uses it from ethtool/ring code.

Risks: Future users must confirm power-of-two and coalescing assumptions match their hardware. Narrow integer fields limit representable object/RAM counts.

Test signals: Compile coverage, static initialization checks, and layout tests for both modes and maximum sentinel handling.
