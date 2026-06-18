# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw_hdmi.c

Purpose: HDMI helper implementation for the generic Intel SOF SoundWire machine driver.

Important APIs, types, and functions: `sof_sdw_hdmi_init()` obtains the SoundWire machine private context, casts its Intel-private payload, and stores the HDMI codec component from the runtime codec DAI. `sof_sdw_hdmi_card_late_probe()` checks `idisp_codec` and the stored component, then calls `hda_dsp_hdmi_build_controls()`.

Control flow and integration: `sof_sdw.c` installs `sof_sdw_hdmi_init()` on the first iDisp HDMI BE link and invokes `sof_sdw_hdmi_card_late_probe()` from its card late-probe path after generic SoundWire late probe succeeds.

State and persistence: It mutates only `intel_ctx->hdmi.hdmi_comp`; no allocation or persistence exists.

Dependencies: ASoC runtime helpers, `asoc_sdw_mc_private`, shared SoundWire context definitions, and HDA DSP HDMI control helper.

Risks: If the first HDMI BE does not initialize or iDisp is absent, HDMI control creation must be skipped or return `-EINVAL` as appropriate. Test signals include HDMI controls on SoundWire+iDisp systems and successful registration without HDMI codec.
