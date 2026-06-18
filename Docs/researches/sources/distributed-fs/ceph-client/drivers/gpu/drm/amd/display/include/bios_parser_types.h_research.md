# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_types.h

Purpose: defines AMD display BIOS parser command/result enums and parameter structures for encoder, transmitter, CRTC timing, pixel clock, spread spectrum, connector capability, and bandwidth/latency data.

Important APIs and control flow: enums cover ATOM-style signal types, BIOS parser results, encoder/transmitter/external encoder actions, pipe and LVTMA actions, and DCE clock type. Structures include `bp_encoder_control`, `bp_external_encoder_control`, `bp_crtc_source_select`, `bp_transmitter_control`, load detection, hardware CRTC timing with polarity/interlace flags, pixel clock adjustment/programming parameters, DCE clock programming, spread-spectrum parameters, connector caps, encoder caps, SOC bounding-box latencies, and connector speed caps.

State and persistence behavior: no runtime state. These types are ABI-like contracts passed between display manager and BIOS parser/ATOM execution code; fields often carry firmware-specific units such as kHz, 100 Hz, 10 kHz, 100 ns, lane settings, and packed bit capability flags.

Dependencies and integration points: depends on `dm_services.h`, signal/object/GPIO/link service types, and display enums such as engine, transmitter, lane count, color depth, HPD, clock source, and graphics object IDs. BIOS parser implementations fill or consume these structures to drive VBIOS tables.

Risks and test signals: risks include typos preserved in enum names for compatibility, bitfield packing assumptions, direct VBIOS translation values that must not be renumbered, unit mismatches, missing fields for newer PHY/HPO/USB-C capabilities, and unsupported BIOS table versions. Test signals include BIOS table execution for encoder enable/setup, transmitter power and lane settings, pixel clock programming including YUV420/deep color/PHY-only flags, spread-spectrum values, and parsed DP/HDMI/UHBR capability bits matching hardware.
