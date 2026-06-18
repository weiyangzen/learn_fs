# sources/distributed-fs/ceph-client/include/sound/ac97/regs.h

## Purpose
`regs.h` is the canonical AC97 register and bit definition catalog. It covers standard audio registers, modem registers, vendor/page registers, slot numbers, volume mute masks, powerdown bits, extended audio/modem capabilities, S/PDIF fields, paging, interrupts, and GPIO status bits.

## Important APIs, Types, and Functions
There are no functions or types. Important macros include register offsets such as `AC97_RESET`, `AC97_MASTER`, `AC97_EXTENDED_ID`, `AC97_POWERDOWN`, `AC97_SPDIF`, and `AC97_VENDOR_ID1/2`; slot aliases such as `AC97_SLOT_PCM_LEFT`, `AC97_SLOT_MIC`, and `AC97_SLOT_SPDIF_LEFT`; capability masks such as `AC97_BC_*`, `AC97_EI_*`, `AC97_EA_*`; and modem GPIO flags such as `AC97_GPIO_LINE1_OH`.

## Control Flow
No executable flow exists. Drivers use these constants while probing codecs, configuring mixer paths, programming sample rates, assigning PCM slots, managing power states, and interpreting interrupt or GPIO status registers.

## State and Persistence Behavior
The file owns no state. Its macros define the binary contract for values stored in AC97 codec hardware registers and in software register caches maintained elsewhere.

## Dependencies and Integration Points
It is included by `ac97_codec.h` and by AC97 controller, codec, and board-specific drivers. It aligns Linux definitions with the AC97 2.x specification and modem extensions.

## Risks and Test Signals
Risks are incorrect masks or register offsets causing silent hardware misprogramming, especially for power, S/PDIF, GPIO, and page selection fields. Test signals include codec probe on representative devices, register-cache validation, suspend/resume power tests, and static checks for no duplicate or shifted bit misuse.
