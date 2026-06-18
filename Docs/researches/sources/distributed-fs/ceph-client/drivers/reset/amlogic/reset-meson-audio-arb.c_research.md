# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-audio-arb.c

Purpose: reset controller for Amlogic AXG/SM1 audio memory arbiter interfaces. It controls per-interface enable/reset bits and exposes them through the reset framework.

Important APIs/types/functions: `struct meson_audio_arb_data`, `struct meson_audio_arb_match_data`, reset bit tables, `meson_audio_arb_update()`, `meson_audio_arb_status()`, `meson_audio_arb_assert()`, `meson_audio_arb_deassert()`, `meson_audio_arb_probe()`, and `meson_audio_arb_remove()`.

Control flow: OF match selects AXG or SM1 bit mapping. Probe allocates state, enables the clock, maps registers, initializes a spinlock, writes the general enable bit, and registers a reset controller. Assert clears an interface bit; deassert sets it; status reports asserted when the bit is clear. Remove writes zero to disable access.

State and persistence: register contents are hardware state; no saved state survives driver unload. `spinlock_t lock` serializes read-modify-write cycles.

Dependencies and integration: depends on platform bus, OF match data, clock framework, MMIO, and dt-bindings reset IDs.

Risks and test signals: bit polarity is inverted, and remove disables all arbiter access. Test clock failure paths, register bit mappings for AXG/SM1, reset status polarity, and client audio DMA behavior after assert/deassert.
