# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8195-pm-domains.h

Purpose: MT8195 SCPSYS table for a high-end SoC with PCIe/USB PHY, Ethernet, ADSP/audio, GPU, display/video, imaging, and camera domains.

Important data: domains are `pcie_mac_p0`, `pcie_mac_p1`, `pcie_phy`, `ssusb_pcie_phy`, `csi_rx_top`, `ether`, `adsp`, `audio`, GPU `mfg0`-`mfg6`, `vppsys0`, `vdosys0`, `vppsys1`, `vdosys1`, `dp_tx`, `epd_tx`, `hdmi_tx`, `wpesys`, `vdec0`, `vdec1`, `vdec2`, `venc`, `venc_core1`, `img`, `dip`, `ipe`, `cam`, `cam_rawa`, `cam_rawb`, and `cam_mraw`. It uses active-wakeup, always-on, keep-default-off, domain-supply, and SRAM-isolation flags.

Control flow: `mt8195_scpsys_data` is consumed by the generic direct-control driver. Some domains use status offsets `0x174/0x178` while others use `0x16c/0x170`; ordered `bp_cfg` entries protect buses across infra/SMI blocks.

State and persistence behavior: no local state. Runtime state is hardware register state plus regulator/clocks owned by domain nodes.

Dependencies and integration points: requires MT8195 binding IDs, access-controller list, domain supplies for GPU roots, and correct consumer DT references for display/video/camera/PCIe/USB/Ethernet/ADSP.

Risks: mixed status registers and many default-off media domains raise DT validation importance. `ssusb_pcie_phy` is always-on, so power measurements and suspend expectations must account for it. HDMI/DP/EPD TX domains have active/default-off policy differences.

Test signals: full multimedia pipeline tests, PCIe/USB/Ethernet wake tests, GPU power/regulator tests, and suspend/resume validation should be used with bus-protect timeout logging enabled.
