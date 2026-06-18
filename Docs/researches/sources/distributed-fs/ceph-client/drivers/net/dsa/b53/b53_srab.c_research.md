# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_srab.c

Purpose: SRAB MMIO transport for B53 switches, with register bridge access, optional port link IRQs, mux/SerDes discovery, and phylink capability hooks.

Important APIs/types/functions: SRAB command/data/control/interrupt/mux macros, `struct b53_srab_priv`, `struct b53_srab_port_priv`, grant/op helpers, width-specific read/write ops, IRQ enable/disable, mux init, and platform probe/remove/shutdown.

Control flow: probe maps SRAB registers, allocates B53 with SRAB ops, prepares optional named link IRQs, reads mux resource for port 5/4 modes, initializes SerDes for SGMII, and registers the switch. Each register operation requests grant, issues command, accesses data registers, and releases grant. SGMII IRQ thread calls `b53_port_event()`.

State and persistence behavior: runtime state includes MMIO bases, per-port IRQ enabled flags, detected interface modes, and common B53 state. Hardware grants/interrupts are transient.

Dependencies and integration points: platform/OF/MMIO/IRQ APIs, optional B53 SerDes helpers, phylink interface modes, common B53 core.

Risks: grant loop checks `i == 5` despite 20 iterations; optional IRQ absence may reduce link-change notification; port 6 is skipped; SerDes map only supports port 5 lane 0 and port 4 lane 1; missing mux resource silently limits capability discovery.

Test signals: compatible probe matrix, grant/command timeout injection, IRQ link events, mux modes, SerDes enabled/disabled builds, and remove/shutdown interrupt cleanup.
