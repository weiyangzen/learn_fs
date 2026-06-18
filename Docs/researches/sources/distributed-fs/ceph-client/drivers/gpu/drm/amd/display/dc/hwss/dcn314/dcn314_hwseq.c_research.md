# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.c

## Purpose
Implements DCN 3.1.4-specific sequencing for ODM/DSC programming, DSC/DPP/plane power gating, pixel-rate divider calculation, FIFO/DCCG/DIO resync, DPP root-clock control, and link-output disable handling with SYMCLK workaround.

## Important APIs, Types, and Functions
Exports `dcn314_update_odm`, `dcn314_dsc_pg_control`, `dcn314_enable_power_gating_plane`, `dcn314_calculate_dccg_k1_k2_values`, `dcn314_calculate_pix_rate_divider`, `dcn314_resync_fifo_dccg_dio`, `dcn314_dpp_root_clock_control`, `dcn314_disable_link_output`, and `dcn314_dpp_pg_control`. Internal helpers are `update_dsc_on_stream`, `get_odm_config`, `dcn314_is_pipe_dig_fifo_on`, and `apply_symclk_on_tx_off_wa`.

## Control Flow
ODM update derives ODM combine factor and OPP instances, programs OPTC combine/bypass, clears MPC out rate control, enables secondary OPP pipe clocks, and reprograms/disconnects DSC as topology changes. DSC programming divides slice width across ODM pipes, programs DSC blocks and OPTC DSC mode, and disables all ODM DSC blocks when off. Pixel divider calculation chooses K1/K2 based on 128b/132b DP, HDMI/DVI, YCbCr420, two-pixels-per-container, virtual signals, and ODM combine factor. FIFO resync temporarily disables eligible DPMS-off/virtual OTGs unless DIG FIFO is already on, triggers DIO FIFO resync through DCCG, and restores CRTC/ODM. Link disable delegates to link HWSS, handles eDP backlight or DMCU PHY locking, traces DPCD sequence, then reapplies SYMCLK-on/TX-off workaround when OTG still references the PHY clock. DPP PG handles debug-disabled power gating by force-disabling cursor when powering off.

## State and Persistence Behavior
Mutates OPTC ODM/DSC state, DSC block state, MPC rate control, OPP clocks, DCCG root clocks and FIFO resync state, pipe pixel-rate divider fields, link PHY `symclk_state` and ref-count-dependent behavior, DMCU PHY lock state, eDP backlight state, DPP cursor state, and PG registers. It reads current and target pipe contexts during staged programming.

## Dependencies and Integration Points
Depends on DCCG, TG/OPTC, DSC, OPP, MPC, link service/HWSS, DMCU, DCE I2C, VPG, DCN20 OPTC, and DCN30 color/common helpers. Integrated by `dcn314_init.c` through public/private hooks, while reusing DCN31 init/reset and DCN30/DCN20 base behavior.

## Risks and Test Signals
Risks include incorrect ODM slice/DSC slice arithmetic, failure to disconnect old DSC after ODM collapse, K1/K2 divider errors affecting stream clocks, FIFO resync disrupting live or seamless-boot streams, SYMCLK workaround failing for TMDS, root-clock gating races, and cursor stuck visible when DPP PG is disabled. Test DCN314 with ODM combine/split, DSC on/off, DP2 128b/132b, HDMI/DVI/YCbCr420, virtual/DPMS-off pipes, TMDS link disable, eDP backlight control, root clock optimization, DPP PG disabled, and multi-pipe mode sets.
