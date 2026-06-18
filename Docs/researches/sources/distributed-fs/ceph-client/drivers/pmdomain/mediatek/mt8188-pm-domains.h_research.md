# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8188-pm-domains.h

Purpose: MT8188 SCPSYS data for a large multimedia/GPU/peripheral power topology.

Important data: domains include GPU `mfg0`-`mfg4`, PCIe/CSI PHY/MAC entries, `ether`, `hdmi_tx`, ADSP always-on/infra/main domains, `audio`, `audio_asrc`, VPP/VDO systems, DP/eDP TX, `wpe`, `vdec0`, `vdec1`, `venc`, `vcore`, `img_main`, `dip`, `ipe`, and camera vcore/main/sub domains. Notable caps include `DOMAIN_SUPPLY`, `KEEP_DEFAULT_OFF`, `ACTIVE_WAKEUP`, `ALWAYS_ON`, `EXT_BUCK_ISO`, and `SRAM_ISO`.

Control flow: selected through `mt8188_scpsys_data`. The generic driver interprets table entries as direct MTCMOS domains, with multiple status register regions (`0x174/0x178` and `0x16c/0x170`) and ordered access-controller bus-protection sequences.

State and persistence behavior: no mutable table state. Runtime state includes SPM control/status, buck isolation for ADSP AO, SRAM isolation for ADSP infra/main, and regulator state for GPU roots.

Dependencies and integration points: requires DT binding IDs, a matching access-controller phandle list, clocks grouped by domain node, and consumer references for display/video/camera/PCIe/GPU/audio/ADSP.

Risks: large domain count and mixed status offsets increase the chance of ID or register mismatch. Always-on domains conflict with keep-default-off semantics if flags are changed. External buck isolation and SRAM isolation bits have strict order requirements.

Test signals: boot should register all domains without access-controller count errors. Exercise ADSP, HDMI/DP/eDP, PCIe, Ethernet wake, video pipelines, camera, and GPU separately while checking default-off and always-on policies.
