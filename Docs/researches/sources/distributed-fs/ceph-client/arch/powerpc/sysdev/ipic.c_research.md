<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.c

Purpose: Implements the Freescale Integrated Programmable Interrupt Controller driver, including irqdomain mapping, level/edge mask/ack/type operations, machine-check status helpers, and suspend/resume restore.

Important APIs/types/functions: Public APIs are `ipic_init()`, `ipic_set_default_priority()`, `ipic_get_mcp_status()`, `ipic_clear_mcp_status()`, and `ipic_get_irq()`. Important data are `primary_ipic`, `ipic_info[]`, `struct ipic`, `ipic_level_irq_chip`, `ipic_edge_irq_chip`, and saved suspend state.

Control flow: `ipic_init()` maps registers from OF, creates a 128-entry linear domain, configures spread/mix priority modes, MCP routing, IRQ0-to-MCP behavior, sets default domain, and masks internal interrupt groups. Domain mapping starts each IRQ as level-low and then `ipic_set_irq_type()` can switch external interrupt sources to falling-edge handling by programming `IPIC_SECNR`. Mask/unmask/ack operations use per-source register metadata from `ipic_info[]`. `ipic_get_irq()` reads `SIVCR`, returns zero for no pending vector, otherwise maps the hardware vector.

State and persistence: State is global and primary-only: mapped IPIC registers, irqdomain, source metadata table, raw spinlock, hardware mask/priority/sense/error registers, and optional suspend snapshot of all relevant controller registers.

Dependencies and integration points: Depends on OF address mapping, irqdomain one/two-cell translation, Freescale IPIC register constants from `asm/ipic.h`, PowerPC platform `ppc_md.get_irq`, syscore suspend/resume, and `fsl_deep_sleep()` behavior.

Risks: `ipic_info[]` is sparse; invalid hardware IRQs would index entries with zero masks unless guarded by valid DT/domain use. Only low-level and falling-edge senses are supported, with edge mode limited to external interrupts. `ipic_from_irq()` always returns `primary_ipic`, so multiple IPIC instances are not supported.

Test signals: Freescale IPIC board boot, level and external falling-edge interrupts, MCP status read/clear, priority register initialization, deep-sleep suspend/resume, malformed IRQ type requests, and irqdomain xlate/map coverage.

Source read size: 893 lines, 18942 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.c -->
