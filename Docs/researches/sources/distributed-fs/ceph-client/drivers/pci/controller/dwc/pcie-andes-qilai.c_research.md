# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-andes-qilai.c

Purpose: Implements the Andes QiLai DWC PCIe root-complex glue. It enables LTSSM through APB registers, reports link state from APB status bits, enables MSI at the APB interrupt-control level, and programs IO coherence-port cache attributes after host initialization.

Important APIs and types: `struct qilai_pcie` embeds `struct dw_pcie` and stores `apb_base`. Key functions are `qilai_pcie_link_up()`, `qilai_pcie_start_link()`, `qilai_pcie_enable_msi()`, `qilai_pcie_iocp_cache_setup()`, `qilai_pcie_host_init()`, `qilai_pcie_host_post_init()`, and `qilai_pcie_probe()`.

Control flow: Probe allocates the embedded DWC object, enables use of parent DT ranges and required generic resources with `dw_pcie_cap_set(..., REQ_RES)`, maps the `apb` resource, enables runtime PM without callbacks, and calls `dw_pcie_host_init()`. Host init sets the APB MSI enable bit. After the PCI host is probed, post-init enables write-back/read-write-allocate ARCACHE/AWCACHE modes in `PCIE_LOGIC_COHERENCY_CONTROL3`.

State and persistence: Hardware state includes APB LTSSM enable, MSI interrupt enable, APB link status, and DWC coherency-control cache attributes. Driver state is the mapped APB base and embedded DWC core; runtime PM is marked active but has no callbacks.

Dependencies and integration points: Integrates with the generic DWC host core, runtime PM helpers, OF resource mapping, and DWC clock/reset resource management through `REQ_RES`. Cache attribute programming depends on DBI read-only write enable/disable.

Risks: Coherency mode affects DMA visibility and system-cache snooping; wrong ARCACHE/AWCACHE values can cause data coherency or performance problems. MSI requires both APB and generic DWC MSI setup. The link-up helper uses `FIELD_GET()` on single-bit masks, which is correct but easy to misread. Parent DT ranges must describe address translation correctly.

Test signals: Probe `andestech,qilai-pcie`, verify required clocks/resets are obtained, link-up via SMLH/RDLH bits, MSI interrupt delivery, coherency-control register values after post-init, PCI DMA correctness under cache pressure, and runtime PM active state during boot.
