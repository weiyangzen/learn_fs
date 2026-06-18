<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-card.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-card.h

## Purpose
`soc-card.h` declares ASoC card-level helper APIs for locking, controls, jacks, power management, probing/removal, DAI link management, PCI SSID storage, driver data, and codec DAI lookup.

## Important APIs, types, and functions
It defines card mutex lock subclasses and inline lock/unlock helpers. APIs include `snd_soc_card_get_kcontrol()`, `snd_soc_card_jack_new()`, `snd_soc_card_jack_new_pins()`, suspend/resume pre/post hooks, `snd_soc_card_probe()`, `late_probe()`, `fixup_controls()`, `remove()`, bias-level setters, `snd_soc_card_add_dai_link()`, and `snd_soc_card_remove_dai_link()`. Inline helpers set/get PCI subsystem IDs when `CONFIG_PCI` is enabled, set/get card driver data, and find a codec DAI by name.

## Control flow
The ASoC core or machine drivers lock the card, create controls/jacks, run card probe and late probe, manage PM ordering, adjust bias, and add/remove DAI links dynamically. PCI SSID helpers store machine-identification metadata for topology or quirk use.

## State and persistence behavior
State is stored in `struct snd_soc_card`: mutexes, controls, jacks, DAI links, PCI SSID fields, and driver data. It persists while the card is registered only.

## Dependencies and integration points
It depends on `struct snd_soc_card`, DAPM contexts, jacks, DAI links, PCI configuration, and runtime DAI iteration macros from `soc.h`.

## Risks and test signals
Risks include lock subclass misuse, looking up only codec index 0 in multi-codec links, PCI helper stubs returning `-ENOENT`, DAI link add/remove during active streams, and jack/control name collisions. Test signals include card probe/remove ordering, PM hook ordering, PCI and non-PCI builds, multi-link codec lookup, dynamic link add/remove, and jack creation with pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-card.h -->
