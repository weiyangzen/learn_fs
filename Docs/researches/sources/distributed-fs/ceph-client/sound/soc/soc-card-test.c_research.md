# sources/distributed-fs/ceph-client/sound/soc/soc-card-test.c

Purpose: KUnit coverage for `snd_soc_card_get_kcontrol()` lookup behavior.

Important APIs and data: `test_card_controls[]` defines twelve dummy mixer controls with distinct shift values and left/right-prefixed names. `test_snd_soc_card_get_kcontrol()` adds controls to a test card, looks each up by exact name, checks the returned `soc_mixer_control->shift`, and verifies misses for unrelated, partial, and NULL names. Fixture setup allocates `soc_card_test_priv`, registers a KUnit device, creates an ASoC card, and calls `snd_soc_register_card()`.

Control flow and state: per-test init builds and registers a card; the test adds controls and performs lookups; exit unregisters the card and drops the device reference. State is isolated through KUnit allocations.

Dependencies and integration: depends on KUnit, `kunit/device.h`, ASoC card registration, and control helper macros. It directly exercises `soc-card.c`.

Risks: because the fixture registers a minimal card, future ASoC registration prerequisites could break the test before the lookup logic runs. The test validates exact control name lookup but not component-prefixed lookup from `soc-component.c`.

Test signals: the KUnit suite name is `soc-card`; expected pass means every added control is found with matching private shift and invalid names return NULL.
