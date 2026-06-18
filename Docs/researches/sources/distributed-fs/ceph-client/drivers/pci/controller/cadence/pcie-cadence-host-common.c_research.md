<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.c

Purpose: common host-side library shared by classic Cadence and HPA Cadence host drivers. It handles link wait/retrain policy and maps host bridge DMA ranges into Cadence root-port inbound BAR resources.

Important APIs/types/functions: `bar_max_size`, `cdns_pcie_host_training_complete()`, `cdns_pcie_host_wait_for_link()`, `cdns_pcie_retrain()`, `cdns_pcie_host_start_link()`, BAR selectors `cdns_pcie_host_find_min_bar()` and `cdns_pcie_host_find_max_bar()`, `cdns_pcie_host_dma_ranges_cmp()`, `cdns_pcie_host_bar_config()`, and `cdns_pcie_host_map_dma_ranges()`.

Control flow: link start waits for platform-specific link-up, then optionally retrains if a quirk is set and the link came up at Gen1 despite higher capability. DMA mapping either programs an RP_NO_BAR catch-all when no `dma-ranges` exist, or sorts bridge DMA ranges largest-first and splits each range across the smallest fitting available BAR or the largest BAR chunk that can fit part of the range. The actual hardware write is delegated through a callback so classic and HPA layouts can share the algorithm.

State/persistence: BAR availability lives in `rc->avail_ib_bar[]`; this library marks entries used indirectly through the callback. Hardware state persists in inbound address-translation and root BAR registers written by the caller-specific callback. No durable state survives controller reset; resume paths reset `avail_ib_bar` and replay mapping.

Dependencies/integration: PCI host bridge private data, bridge `dma_ranges`, OF helper for `cdns,no-bar-match-nbits`, list sorting, Cadence RC structures, and caller callbacks from `pcie-cadence-host.c` or `pcie-cadence-host-hpa.c`.

Risks: all sizes are assumed power-of-two compatible when passed to callbacks. Splitting consumes a limited three-entry BAR namespace; unusual or many DMA ranges can fail. `bar_max_size[RP_BAR0]` is very large while BAR aperture masks differ by architecture, so callback correctness matters. Link retraining only triggers under a narrow speed condition and may not help other training failures.

Test signals: no-`dma-ranges` fallback, multiple sorted DMA ranges, large range splitting, BAR exhaustion, Gen2 retrain on affected hardware, training timeout, and replay after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.c -->
