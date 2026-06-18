# sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.h

## Purpose

This header declares identifiers and register constants for the VT1724 AMP AUDIO2000 and Chaintech AV-710 board support implemented in `amp.c`.

## Important APIs, Types, and Functions

`AMP_AUDIO2000_DEVICE_DESC` contributes textual device descriptors for the parent driver. `VT1724_SUBDEVICE_AUDIO2000` and `VT1724_SUBDEVICE_AV710` define subvendor IDs, with AUDIO2000 currently using a dummy ID while AV-710 uses `0x12142417`. `WM_DEV`, `WM_ATTEN_L`, `WM_ATTEN_R`, `WM_DAC_CTRL`, and `WM_INT_CTRL` describe the AV-710 WM8728 I2C address and registers. The header declares `snd_vt1724_amp_cards[]`.

## Control Flow, State, Dependencies, Risks, and Tests

There is no runtime control flow or state. Constants drive matching and external codec programming in `amp.c`. The header depends on `struct snd_ice1712_card_info` being visible through including C files. The key risk is the duplicate real subdevice ID for AV-710 and AUDIO2000, handled by a dummy AUDIO2000 ID. Test by compiling the ICE1724 module, verifying descriptor strings include both boards, and confirming card-info symbol linkage.
