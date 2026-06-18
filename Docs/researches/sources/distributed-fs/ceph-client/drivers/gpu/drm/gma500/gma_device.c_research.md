<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.c

## Purpose

This file provides a shared helper to determine and store the GMA core frequency from chipset/root PCI configuration.

## Important APIs, Types, And Functions

The exported function is `gma_get_core_freq(struct drm_device *dev)`. It writes a message/control value to root PCI config offset `0xD0`, reads offset `0xD4`, decodes the low three bits, and stores `dev_priv->core_freq` as 100, 133, 150, 178, 200, 266, or zero.

## Control Flow

The helper obtains the root PCI device for the domain/bus, performs the config write/read transaction, releases the root device, and switches on `clock & 0x07` to update the private frequency field. Cedarview chip setup calls it before display initialization uses timing/watermark data.

## State And Persistence

The only software state mutation is `drm_psb_private.core_freq`. The helper also briefly changes chipset PCI config message registers as part of the read protocol.

## Dependencies And Integration Points

It depends on PCI, `psb_drv.h`, and `gma_device.h`. It is integrated by `cdv_chip_setup()` and potentially other chip setup paths.

## Risks And Test Signals

Risks include assuming root PCI device lookup succeeds, hardcoded config offsets/protocol, and frequency table validity across chip variants. Test signals are Cedarview/Poulsbo probe, root PCI config access failure handling under fault injection, and comparing stored core frequency against platform documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.c -->
