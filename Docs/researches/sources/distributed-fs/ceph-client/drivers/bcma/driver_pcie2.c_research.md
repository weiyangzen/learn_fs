# sources/distributed-fs/ceph-client/drivers/bcma/driver_pcie2.c

Purpose: initializes and services the BCMA PCIe Gen2 core. It applies chip/revision-specific workarounds, sets latency tolerance reporting values, configures power-management timing, records the preferred PCIe read request size, and applies that size when the PCI host is brought up.

Important APIs and functions: `bcma_core_pcie2_cfg_write()` writes indirect PCIe Gen2 config registers. `bcma_core_pcie2_war_delay_perst_enab()` toggles delayed PERST and SPROM-load clock-control bits for BCM4360 revisions. `bcma_core_pcie2_set_ltr_vals()` writes hard-coded LTR0-LTR2 values. `bcma_core_pcie2_hw_ltr_war()` applies the LTR workaround for core revisions 2-9 and 11-13, excluding 10. `pciedev_reg_pm_clk_period()` derives PM clock period from the chipcommon ALP clock. `bcma_core_pcie2_init()` is the main init entry; `bcma_core_pcie2_up()` calls `pcie_set_readrq()` on the host PCI device.

Control flow: init first checks a SPROM field and may write config offset `0x4e0`. It chooses `pcie2->reqsize` as 1024 for BCM4360/4352 and 128 otherwise. For BCM4360 rev > 3 it enables the delayed-PERST workaround, then runs LTR, low-power clock-generation placeholders, PM clock period, and mailbox/reference update workarounds in sequence.

State and persistence: software state is mainly `pcie2->reqsize` and `pcie2->core`. Hardware-visible state is stored in PCIe Gen2 config-indirect registers, clock control, LTR state, PM clock period, and mailbox registers. No memory ownership is created.

Dependencies and integration points: depends on BCMA core accessors `pcie2_read32/write32/set32`, chip IDs, chipcommon PMU clock calculation, and the Linux PCI `pcie_set_readrq()` helper. `main.c` initializes this core when `BCMA_CORE_PCIE2` unit 0 exists, and `host_pci.c` invokes runtime `up()` for PCI-host devices that scanned a PCIe2 core.

Risks: many values are magic hardware constants with partial TODO blocks, so behavior is fragile across new revisions. `pcie_set_readrq()` errors are logged but not recovered. Tests should cover BCM4360/4352 and default chips, read request size after probe/resume, LTR-enabled cores, and regression logs around PM clock period calculation.
