# sources/distributed-fs/ceph-client/sound/pci/ice1712/se.h

## Purpose
`se.h` declares the ONKYO SE board descriptors, supported subdevice IDs, and the exported card-info table for `se.c`.

## Important APIs, Types, and Functions
- `SE_DEVICE_DESC` lists SE-90PCI and SE-200PCI names for the enclosing card registry.
- `VT1724_SUBDEVICE_SE90PCI` and `VT1724_SUBDEVICE_SE200PCI` are the subvendor match IDs.
- `extern struct snd_ice1712_card_info snd_vt1724_se_cards[]` exposes the table implemented by `se.c`.

## Control Flow
No executable control flow is present. The ICE1724 registry includes this header to discover the board table; `se.c` uses the IDs to branch during initialization.

## State and Persistence
The header stores no state. Its constants define the stable hardware identity contract for the ONKYO board driver.

## Dependencies and Integration Points
It depends on the ICE1712 card-info type being visible to consumers and integrates with the generic Envy24HT card registry.

## Risks and Test Signals
Incorrect IDs or descriptions would prevent automatic board matching or expose the wrong model string. Test signals are module alias matching and correct `card->shortname`/model after probe.
