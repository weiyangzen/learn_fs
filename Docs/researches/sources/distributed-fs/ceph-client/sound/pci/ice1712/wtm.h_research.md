# sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.h

## Purpose
`wtm.h` declares the Waveterminal 192M board descriptor, subdevice ID, codec I2C addresses, and exported card-info table.

## Important APIs, Types, and Functions
- `WTM_DEVICE_DESC` contributes the user-visible Waveterminal description.
- `VT1724_SUBDEVICE_WTM` is the Waveterminal 192M subsystem ID.
- `AK4114_ADDR`, `STAC9460_I2C_ADDR`, and `STAC9460_2_I2C_ADDR` define external chip addresses.
- `extern struct snd_ice1712_card_info snd_vt1724_wtm_cards[]` exposes the table implemented by `wtm.c`.

## Control Flow
There is no executable flow. The constants are consumed by `wtm.c` and the generic ICE1724 registry.

## State and Persistence
No state is stored. The header is hardware-identity and bus-address metadata.

## Dependencies and Integration Points
It depends on the ICE1712 card-info type at the use site. The I2C addresses integrate directly with Envy24HT I2C helper calls in `wtm.c`.

## Risks and Test Signals
Wrong addresses or subdevice IDs would make codec access or card matching fail. Test signals are I2C ACKs from both STAC codec addresses and correct card registration as Waveterminal 192M.
