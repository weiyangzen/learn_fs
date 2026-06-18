# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8192-pm-domains.h

Purpose: MT8192 SCPSYS direct-control domain table.

Important data: domains include `audio`, `conn`, GPU `mfg0` through `mfg6`, `disp`, `ipe`, `isp`, `isp2`, `mdp`, `venc`, `vdec`, `vdec2`, `cam`, `cam_rawa`, `cam_rawb`, and `cam_rawc`. GPU `mfg0`/`mfg1` are supply-backed; `conn` is keep-default-off; major media domains carry bus-protection sequences using infra/SMI blocks.

Control flow: selected by `mediatek,mt8192-power-controller`. The generic direct-control driver registers domains by DT child `reg`, powers non-default-off domains on during init, and later idles unused domains through genpd.

State and persistence behavior: table only; runtime state uses SPM status offsets `0x016c`/`0x0170`, domain supplies, SRAM ack bits, and access-controller state.

Dependencies and integration points: depends on MT8192 power binding IDs and access-controller phandles. Display, camera, image, video, GPU, audio, and connectivity consumers attach through genpd.

Risks: MFG chain and camera raw domains require correct parent relationships in DT. Bus-protect sequences are lengthy enough that wrong block ordering or missing SMI regmap causes transition failures.

Test signals: test display/MDP, ISP/IPE/camera raw, video encode/decode, GPU OPP/regulator behavior, and connectivity default-off handling.
