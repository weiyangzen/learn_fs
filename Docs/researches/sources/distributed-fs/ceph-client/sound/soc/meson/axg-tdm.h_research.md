# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm.h

Purpose: Defines shared AXG TDM constants, stream/interface state structures, format masks, clock polarity helpers, stream lifecycle prototypes, and the TDM slot programming API.

Important APIs and types: `AXG_TDM_NUM_LANES`, `AXG_TDM_CHANNEL_MAX`, and `AXG_TDM_FORMATS` describe generic hardware capabilities. `struct axg_tdm_iface` stores sclk/lrclk/mclk and shared format/slot/rate state. `struct axg_tdm_stream` stores formatter list, lock, stream width/channel/mask data, ready flag, and continuous-clock state. Inline helpers `axg_tdm_lrclk_invert()` and `axg_tdm_sclk_invert()` centralize polarity interpretation. Prototypes expose stream allocation/start/stop/reset/continuous-clock and `axg_tdm_set_tdm_slots()`.

Control flow: No standalone executable flow beyond inline polarity helpers and stream reset, which stops then starts a stream. Runtime behavior is implemented in formatter and interface modules.

State and persistence: Declares state allocated by `axg-tdm-interface.c` and manipulated by formatter modules. The mask pointer is owned by card/link data and referenced by streams.

Dependencies and integration points: Included by AXG card, TDM interface, TDM formatter, TDMIN, and TDMOUT code. It is the shared ABI across separately built Meson TDM modules.

Risks: The polarity helpers encode subtle ASoC format/inversion semantics; changing them affects both interface clock phase and formatter compensation. Stream mask lifetime must outlive streams because only pointers are stored. `AXG_TDM_CHANNEL_MAX` allows large topologies but actual masks still cap active channels.

Test signals: Build/link coverage, TDM format inversion tests, stream reset behavior, and card-slot mask lifetime through probe/remove.
