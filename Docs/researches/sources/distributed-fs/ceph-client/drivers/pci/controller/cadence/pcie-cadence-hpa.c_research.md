<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa.c

Purpose: HPA common helper implementation for Cadence PCIe. It supplies HPA link-up detection, detect-quiet tuning, and outbound region programming for memory/IO and normal-message TLPs.

Important APIs/types/functions: `cdns_pcie_hpa_link_up()`, `cdns_pcie_hpa_detect_quiet_min_delay_set()`, `cdns_pcie_hpa_set_outbound_region()`, and `cdns_pcie_hpa_set_outbound_region_for_normal_msg()`.

Control flow: link-up reads the HPA PHY debug-status register. Detect-quiet updates the HPA PHY-layer config delay field. Outbound region setup rounds requested size up to a power of two, enforces at least 256-byte addressing granularity, writes PCI target address, descriptor type, optional supplied bus/devfn values for RC mode, CPU base, and control bits. Normal-message setup is a specialized outbound region with fixed 128 KiB aperture and message descriptor type.

State/persistence: no private state. Hardware state is the HPA AXI slave outbound region table and IP register detect-quiet field. Values persist until controller reset or later region reprogramming.

Dependencies/integration: HPA register macros and HPA inline read/write accessors. Called by HPA host setup and could be reused by HPA endpoint support.

Risks: `fls64(size - 1)` assumes nonzero size. HPA RC descriptor semantics require bus/devfn supply bits in `CTRL0`; missing them breaks RC-originated TLP IDs. Unlike classic helper, no `cpu_addr_fixup` callback is applied, so platform address aliasing must be handled elsewhere.

Test signals: HPA link-up bit polling, detect-quiet register update, outbound IO and MEM windows of small and large sizes, RC-mode bus/devfn injection, EP-mode captured bus/device use, normal message delivery, and register trace validation for all programmed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa.c -->
