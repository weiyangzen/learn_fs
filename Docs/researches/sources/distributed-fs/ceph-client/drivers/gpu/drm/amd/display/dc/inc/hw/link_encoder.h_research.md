# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/link_encoder.h

## Purpose

`link_encoder.h` defines the hardware abstraction for physical display link encoders. It covers legacy DIO/DIG, analog/LVDS/TMDS/DP encoders, USB-C/DPIA cases, and HPO DP2 link encoders used for 128b/132b DisplayPort paths.

## Important APIs, Types, And Functions

`encoder_init_data` carries connector, HPD, encoder object, analog encoder, channel, transmitter, and context data used during construction. `encoder_feature_support` is a bitfield-backed capability set for HBR2/HBR3/TPS3/TPS4, HDMI 6G, DP2/UHBR rates, USB-C, deep color, YCbCr 4:2:0, and FEC. `struct link_encoder` stores the vtable, AUX offset, IDs, output-signal mask, preferred engine, features, transmitter, HPD GPIO/source, and USB-C combo PHY flag.

`link_encoder_funcs` covers state readout, output validation, hardware init/setup, enabling TMDS/DP/MST/LVDS/analog/DPIA, disabling outputs, DP lane settings and PHY patterns, MST allocation updates, PSR secondary packets, DIG frontend routing, HPD enable/disable/state/filtering, FEC control, maximum link capability, DIG mode, DIO PHY mux selection, and destruction. `link_enc_assignment` tracks dynamic endpoint-to-engine ownership. HPO DP support is represented by `hpo_dp_link_encoder`, `hpo_dp_link_encoder_funcs`, `hpo_dp_link_enc_state`, and DP2 training/test-pattern enums.

## Control Flow

Modeset/link training code selects or dynamically assigns a link encoder, initializes it, sets signal mode, enables the appropriate physical output, then programs DP lane settings or HDMI/TMDS clocking. MST and DP2 paths update allocation tables and VCP throttling after the link is active. Disable paths call signal-specific shutdown and may release dynamic assignments.

## State And Persistence Behavior

Persistent state is split between the software object fields and hardware registers. Capability flags persist for the lifetime of the link encoder object. Dynamic assignment entries persist in `resource_context` across current and transient states. FEC-ready/active state and training completion are read from hardware into `link_enc_state` or `hpo_dp_link_enc_state`.

## Dependencies And Integration Points

The header depends on graphics-object, signal, and DC type definitions. It integrates with `link_enc_cfg.h` for dynamic DIG assignment, `link_hwss.h` for signal-specific link sequencing, DP link-training code, MST payload management, HPD handling, and resource-pool construction.

## Risks And Test Signals

Risks include stale capability flags, incorrect encoder-to-endpoint assignment during transient commits, mismatched DP2/HPO versus DIO paths, FEC readiness races, and HPD filter differences. Test signals include DP/HDMI/eDP link training, MST payload changes, USB4 DPIA links, FEC enablement, DP2 UHBR modes, hotplug storms, suspend/resume, and link-status readback after modesets.
