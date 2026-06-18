# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c

Purpose: Implements the DCN10 link encoder: the DIG backend/PHY control surface for DVI, HDMI, DP SST, DP MST, eDP, HPD, AUX, PSR, DP training, and MST allocation.

Important APIs/types/functions: The `dcn10_lnk_enc_funcs` table exposes validation, init, setup, TMDS/DP/MST enable, output disable, lane settings, PHY pattern programming, MST SAT updates, PSR helpers, DIG FE/BE connection, HPD/AUX, capability queries, and destroy. Construction reads VBIOS encoder capability info and maps transmitters to preferred DIG engines.

Control flow: Validation dispatches by stream signal and checks DVI/HDMI/DP limits, color depth, pixel encoding, EDID max TMDS clock, HDMI 2.0 debug disable, and YCbCr420 support. Hardware init calls VBIOS transmitter init, handles LVDS brightness, initializes AUX, and associates HPD. Output enable routes through VBIOS transmitter-control tables after programming lanes/modes. DP PHY pattern paths set training patterns, PRBS, D102, 80-bit custom, CP2520 compliance, or video passthrough. MST allocation writes up to four stream rows, triggers SAT update, and polls completion/keepout.

State/persistence: Persistent object state includes base capabilities, transmitter, connector, HPD GPIO/source, preferred engine, and register metadata. Hardware state includes DIG mode/source, DP lane count, training complete, PHY bypass/PRBS/symbols, MST SAT, HPD enable/filter, and AUX settings.

Dependencies/integration: Depends on DC BIOS transmitter/encoder-control tables, GPIO/IRQ services, stream encoders, link settings, DPCD training fields, and register helpers.

Risks: Many paths rely on VBIOS return status; failures log and break to debugger but often do not propagate to higher layers. Some validation mutates `max_hdmi_pixel_clock` when SCDC overwrite is skipped. Fixed polling for MST update may time out silently. Custom pattern programming assumes a 10-byte pattern.

Test signals: Cover stream validation matrix, VBIOS command parameters for TMDS/DP/MST, DP lane settings per lane, every PHY test pattern, MST allocation rows and timeout path, HPD filter programming, AUX initialization, and DIG mode/source readback.
