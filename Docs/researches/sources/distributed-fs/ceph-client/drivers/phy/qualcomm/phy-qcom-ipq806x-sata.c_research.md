# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-sata.c

This Qualcomm IPQ806x SATA PHY driver programs one MMIO register block and keeps a config clock enabled while the provider is registered. `struct qcom_ipq806x_sata_phy` holds MMIO, `cfg_clk`, and device.

Probe maps the resource, creates a generic PHY, gets and enables `cfg`, registers `of_phy_simple_xlate`, and disables the clock on remove. Init enables spread-spectrum clocking, programs Gen1/2/3 TX pre-emphasis and amplitude fields, sets RX equalization, asserts PHY reset and reference SSP enable, waits for writes to complete and 20-70 us for settling, then clears reset. Exit asserts PHY reset again.

State is the MMIO parameter registers and enabled config clock. Dependencies are clk, generic PHY, platform MMIO, and OF. Integration is with IPQ806x SATA controllers using a single PHY phandle. Risks include hard-coded tuning values, no polling for lock or ready status, no runtime PM, and no cleanup path if provider registration fails beyond disabling the clock. Test signals are SATA link stability rather than explicit status checks.
