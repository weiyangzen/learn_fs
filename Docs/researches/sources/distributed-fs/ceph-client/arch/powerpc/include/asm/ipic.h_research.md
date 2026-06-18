# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ipic.h

Purpose: Declares the Freescale IPIC interrupt controller register offsets, initialization flags, priority groups, MCP IRQ IDs, and setup/status APIs.

Important APIs, types, and functions: Defines spread-mode and MCP flags, IPIC register offsets, `enum ipic_prio_grp`, `enum ipic_mcp_irq`, `ipic_set_default_priority()`, `ipic_get_mcp_status()`, `ipic_clear_mcp_status()`, `ipic_init()`, and `ipic_get_irq()`.

Control flow: Platform code initializes IPIC from a device-tree node with flags, sets default priority, uses `ipic_get_irq()` as the interrupt dispatch source, and reads/clears MCP status for critical events.

State and persistence: Controller state is in IPIC hardware registers and implementation-owned `struct ipic`.

Dependencies and integration points: Depends on Linux IRQ core and OF node discovery. It integrates embedded Freescale interrupt routing with generic IRQ handling.

Risks: Priority/register offsets are hardware ABI. Incorrect spread-mode flags or MCP routing can starve or misclassify interrupts. Status clear masks must be precise.

Test signals: IRQ dispatch from all groups, default priority setup, MCP status read/clear, device-tree init failures, and mixed internal/external interrupt load.
