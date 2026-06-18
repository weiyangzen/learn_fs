# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.h

## Purpose
Assigns numeric board IDs for AU0828-supported devices.

## Important APIs, types, and functions
Defines IDs for unknown board, Hauppauge HVR950Q, HVR850, DViCO FusionHDTV7, HVR950Q MXL, Woodbury, Impact VCB-e, and HVR1265.

## Control flow and state
No executable flow. These constants index `au0828_boards[]` and populate `driver_info` in the USB ID table. The selected ID controls board state copied into `struct au0828_dev` at probe.

## Dependencies and integration points
Included by `au0828.h`, `au0828-cards.c`, and core code. Integrates USB device matching, card profiles, DVB frontend attachment, GPIO setup, and RC support decisions.

## Risks and test signals
Risks are index reorder without matching board array and USB ID table updates. Test signals are each USB ID resolving to the intended board profile and no out-of-bounds board access in probe.
