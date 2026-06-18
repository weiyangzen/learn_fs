# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8189-pm-domains.h

Purpose: MT8189 SCPSYS table spanning connectivity, audio/ADSP, imaging, video, display, USB, GPU, eDP, and PCIe.

Important data: domains are `conn`, `audio`, `adsp-top-dormant`, `adsp-infra`, `adsp-ao`, `isp-img1`, `isp-img2`, `isp-ipe`, `vde0`, `ven0`, `cam-main`, `cam-suba`, `cam-subb`, `mdp0`, `disp`, `mm-infra`, `dp-tx`, `csi-rx`, `ssusb`, `mfg0`-`mfg3`, `edp-tx-dormant`, `pcie`, and `pcie-phy`. It uses separate low/MSB/XPU power status offsets, domain supplies for MFG roots, SRAM isolation plus inverted SRAM PDN for eDP dormant, and active-wakeup for USB/PCIe.

Control flow: consumed by `mtk-pm-domains.c` as direct-control data. Bus protection is split into entries that may run before and after subsystem clocks, matching the generic driver's `BUS_PROT_IGNORE_SUBCLK` logic.

State and persistence behavior: static table only. Runtime state is spread across several SPM status banks and bus-protect registers.

Dependencies and integration points: requires MT8189 binding IDs, access-controller block order, regulator supplies, and correct DT nesting for GPU/media domains. PCIe and eDP consumers rely on special dormant/PHY domains.

Risks: multiple status banks make copy/paste errors hard to detect until a domain times out. Dormant domains with inverted SRAM PDN need targeted suspend/resume validation. MFG supply domains must not be powered without regulators.

Test signals: run USB/PCIe wake tests, eDP/DP display modes, camera/video pipelines, ADSP workloads, and GPU power cycling with SPM status tracing.
