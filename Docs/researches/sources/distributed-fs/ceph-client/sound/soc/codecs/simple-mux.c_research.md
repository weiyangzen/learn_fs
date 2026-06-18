# sources/distributed-fs/ceph-client/sound/soc/codecs/simple-mux.c

Purpose: generic platform ASoC component for a two-input audio mux controlled by a GPIO. It creates a DAPM mux with configurable state labels and optional idle GPIO state.

Important APIs and data: `struct simple_mux` stores mux GPIO, current mux value, mutable label array, idle state, and per-instance copies of soc enum, kcontrol, widgets, routes, and component driver. The copies allow DT `state-labels` to customize control text and DAPM route names without modifying static templates.

Control flow: probe requests the required `mux` GPIO low, copies static templates into private storage, reads optional `state-labels`, validates optional `idle-state`, patches enum/kcontrol/widget/route pointers to private data, and registers a component with a custom `.read` callback. Mixer get/put reads/writes `priv->mux`; put defers GPIO changes while below PREPARE if an idle state is configured, otherwise sets GPIO immediately and calls `snd_soc_dapm_mux_update_power()`. DAPM event restores selected mux before power-up and switches to idle state after powerdown.

State and persistence: current mux selection and idle policy live in memory; GPIO output is the hardware state. No regmap or runtime PM exists. DAPM bias level determines whether a control change affects GPIO immediately.

Dependencies and integration points: depends on GPIO descriptors, OF properties, ASoC DAPM mux controls, and mux idle-state constants from the mux framework. Risks include only two states, required GPIO, label array length assumptions, and subtle behavior when controls change while powered down. Test signals are label override, invalid idle-state rejection, DAPM route switching, GPIO value at active/idle bias levels, and userspace mux control updates.
