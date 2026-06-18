# sources/distributed-fs/ceph-client/sound/soc/soc-card.c

Purpose: wraps core ASoC card-level operations: mixer control lookup, jack creation, card lifecycle callbacks, bias callbacks, and dynamic DAI-link add/remove hooks.

Important APIs: `snd_soc_card_get_kcontrol()` returns a mixer kcontrol by exact name, guarding NULL. `jack_new()` initializes `snd_soc_jack` lists/mutex/notifier and calls `snd_jack_new()`. `snd_soc_card_jack_new()` and `_jack_new_pins()` export jack creation with optional pin attachment. Lifecycle wrappers include suspend/resume pre/post, probe, late_probe, remove, bias-level hooks, `snd_soc_card_add_dai_link()`, and `snd_soc_card_remove_dai_link()`.

Control flow and state: wrapper callbacks call optional function pointers on `struct snd_soc_card` and normalize return logging through `soc_card_ret()`. Probe/late_probe manage `card->probed`: if `probe` exists it sets probed after probe, and late_probe sets it after late probe; remove calls `card->remove` only when probed and then clears the flag. Jack creation initializes caller-owned jack structs.

Dependencies and integration: used broadly by ASoC core and machine drivers, including SoundWire helpers that create headset jacks. Depends on ALSA control and jack core plus card callback conventions.

Risks: lifecycle correctness hinges on `card->probed`; callback ordering changes can skip remove or call it too early. Jack helpers assume caller storage remains valid. `snd_soc_card_get_kcontrol()` performs exact lookup only, so callers must format names correctly.

Test signals: `soc-card-test.c` validates kcontrol lookup; runtime tests should cover jack creation with pins, probe/late_probe/remove ordering, and dynamic dai-link callbacks.
