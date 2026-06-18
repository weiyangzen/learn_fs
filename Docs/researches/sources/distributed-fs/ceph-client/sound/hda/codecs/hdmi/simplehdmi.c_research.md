# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/simplehdmi.c

## Purpose

This file provides a compact non-generic HDMI helper path for codecs with one fixed converter and one fixed pin, and registers VIA VX900 HDMI/DP codecs through that path.

## Important APIs, types, and functions

Exported helpers include `snd_hda_hdmi_simple_probe`, `snd_hda_hdmi_simple_build_pcms`, `snd_hda_hdmi_simple_build_controls`, `snd_hda_hdmi_simple_init`, `snd_hda_hdmi_simple_remove`, `snd_hda_hdmi_simple_pcm_open`, and `snd_hda_hdmi_simple_unsol_event`. Internal helpers build one jack and provide simple playback open/close/prepare callbacks.

## Control flow

Probe allocates `hdmi_spec`, initializes one pin and one converter array entry, sets `multiout.dig_out_nid`, and stores a default 2-channel playback template. Build PCMs creates one HDMI PCM and copies the playback template, adjusting maximum channels from converter capabilities. Build controls creates digital output controls and an AV jack. Init enables pin output, unmutes pin output amp if present, and enables jack detection. PCM open applies channel constraints and delegates to HDA multi-out digital open.

## State and persistence behavior

State is minimal and in-memory: one converter, one pin, one `multiout`, one PCM record, optional channel constraint list, and jack pointer. Remove frees arrays and `spec`.

## Dependencies and integration points

It depends on `hdmi_local.h`, HDA jack helpers, HDA multi-out digital helpers, and the HDA codec driver table. Legacy NVIDIA MCP reuses these helpers and overrides selected pieces.

## Risks and test signals

Risks include assuming exactly one converter/pin, missing ELD/control sophistication from the generic path, and channel capability mismatch on reused simple helpers. Test VIA VX900 probe/init, jack reporting, PCM open/prepare/close, SPDIF control creation, and simple helper reuse by `nvhdmi-mcp.c`.
