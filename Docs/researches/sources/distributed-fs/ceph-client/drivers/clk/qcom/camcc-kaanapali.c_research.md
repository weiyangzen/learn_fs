# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-kaanapali.c

## Purpose
`camcc-kaanapali.c` registers the main Kaanapali camera clock controller. It provides PLLs, postdividers, RCGs, branch clocks, resets, and GDSC power domains for camera front-end, image processing, JPEG, CSIPHY/CSID, CAMNOC, debug, and top-level camera infrastructure.

## Important APIs, Types, And Functions
Major objects include eight Taycan EKO-T alpha PLLs (`cam_cc_pll0` through `cam_cc_pll7`), postdiv outputs for selected even/odd PLL paths, many `clk_rcg2` sources for CAMNOC, CCI, CPHY RX, CRE, CSIPHY timers, CSID, AHB, ICP, IFE lite, IPE, JPEG, OFE, QDSS, TFE, and XO, and many `clk_branch` gates consuming those sources. Power domains are `cam_cc_titan_top_gdsc`, `cam_cc_ipe_0_gdsc`, `cam_cc_ofe_gdsc`, and `cam_cc_tfe_0/1/2_gdsc`. The descriptor also exports reset maps and critical CBCRs. Probe is `cam_cc_kaanapali_probe()` calling `qcom_cc_probe()`.

## Control Flow, State, And Persistence
The file is generated-style static data. PLL configs establish root camera frequencies from TCXO, postdividers expose even/odd outputs, parent maps connect RCGs to PLL outputs, frequency tables constrain supported functional rates, branch clocks gate each hardware leaf, GDSCs describe power-domain topology under Titan top, resets map BCR offsets, and the `qcom_cc_desc` ties everything to a fast regmap up to `0x2601c` with `use_rpm = true`. Runtime state is persisted in camera CC MMIO registers and Linux clock/reset/genpd registrations.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include Kaanapali camera DT bindings, qcom alpha PLL/RCG/branch/reset/GDSC helpers, RPM-aware common clock probing, TCXO/sleep/AHB parents, camera subsystem consumers, reset-controller clients, and generic PM domains. Risks include table-size or binding-ID drift, incorrect PLL calibration values destabilizing camera rates, critical CBCR mistakes gating driver/GDSC/sleep clocks, GDSC parent/flag mistakes breaking power sequencing, and rate-table gaps causing camera pipeline failures. Test signals include provider probe on `qcom,kaanapali-camcc`, camera pipeline streaming through CSIPHY/CSID/TFE/OFE/IPE/JPEG paths, reset control assertions, GDSC on/off transitions, `clk_summary` rate/parent checks for major sources, and unused-clock cleanup preserving critical CBCRs.
