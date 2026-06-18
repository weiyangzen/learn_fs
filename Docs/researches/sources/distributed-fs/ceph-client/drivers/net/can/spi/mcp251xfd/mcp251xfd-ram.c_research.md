# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.c

Purpose: Computes valid RX/TX object layouts for controller RAM shared by receive FIFOs, transmit FIFOs, and optional IRQ coalescing buffers.

Important APIs, types, and functions: `can_ram_get_layout()` is the exported helper. `can_ram_clamp()` and `can_ram_rounddown_pow_of_two()` enforce min/max limits, FIFO depth limits, power-of-two FIFO sizing, and reserved coalescing FIFO space.

Control flow: The helper derives defaults for selected CAN/CAN-FD object sizes, then derives maxima while preserving opposite-direction minimums. With user ring/coalesce parameters, it normalizes RX, computes optional RX coalescing, allocates remaining RAM to TX, computes optional TX coalescing, and fills current layout fields.

State and persistence behavior: Pure calculation; writes only to caller-provided `struct can_ram_layout`.

Dependencies and integration points: Used by MCP251xFD ethtool setup and ring allocation. Inputs come from `struct can_ram_config`, ethtool ring params, and ethtool coalesce params.

Risks: Packing bugs can create overlapping FIFOs, too-small FIFOs, or object counts that break ring masking assumptions. Coalescing boundary cases are especially sensitive.

Test signals: Unit-style layout vectors for CAN/CAN-FD, defaults, maxima, clamping, power-of-two rounding, coalescing disable convention, and no RAM overcommit.
