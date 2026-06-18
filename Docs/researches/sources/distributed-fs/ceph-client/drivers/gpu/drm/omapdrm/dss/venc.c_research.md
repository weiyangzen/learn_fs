# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/venc.c

Purpose: Implements the OMAP VENC analog TV encoder platform driver and DRM bridge for PAL/NTSC composite or S-Video output.

Important APIs/functions: Static `venc_config_pal_trm` and `venc_config_ntsc_trm` hold TRM-derived register tables. `venc_probe()` maps registers, gets VDDA DAC regulator, optionally gets `tv_dac_clk` for matching OMAP3/AM35 SoCs, parses endpoint channel/polarity, enables runtime PM, registers output, and adds a component. `venc_bind()` reads revision and creates debugfs. Bridge callbacks expose PAL/NTSC modes, validate/fixup to canonical interlaced modes, set the active config and TV pixel clock, and power on/off. Runtime PM callbacks control optional TV DAC clock.

Control flow: Bridge mode_set chooses PAL or NTSC table and sets DISPC TV pclk to 13.5 MHz. Enable runtime-resumes VENC, resets it, writes the selected table, selects VENC output and DAC power in DSS, programs output control for composite/S-Video and polarity, enables VDDA DAC, and enables the DSS manager. Disable clears output control/DAC power, disables manager, regulator, and runtime PM.

State and persistence: `struct venc_device` stores base, regulator, optional clock, DSS pointer, selected config, type, polarity, output, bridge, and debugfs handle. Register state is reprogrammed on enable.

Dependencies/integration: Uses component framework, runtime PM, regulators/clocks, SoC matching, OF graph properties `ti,channels` and `ti,invert-polarity`, DRM bridge modes, and DSS manager/output helpers.

Risks and test signals: Only PAL and NTSC exact mode families are accepted. Probe requires valid `ti,channels` when endpoint exists. Power-off disables manager after clearing output/DAC, which may have analog artifact implications. Test PAL/NTSC mode enumeration, composite and S-Video DTs, OMAP3 TV DAC clock PM, regulator failures, debugfs register dump, and repeated enable/disable.
