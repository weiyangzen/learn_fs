# sources/distributed-fs/ceph-client/sound/hda/controllers/acpi.c

## Purpose
`acpi.c` is a platform-driver wrapper for Azalia-compatible HD-audio controllers described by ACPI objects rather than PCI. It creates an ALSA card, maps controller registers from platform resources, initializes the shared `azx` controller core, probes codecs, configures them, and registers the card.

## Important APIs, Types, and Functions
`struct hda_acpi` embeds `struct azx` and stores the ALSA card, platform device, MMIO base, async probe work, and optional `struct hda_data`. `struct hda_data` supplies ACPI-match-specific card naming and `azx->driver_caps`.

Key functions are `hda_acpi_probe()`, `hda_acpi_create()`, `hda_acpi_probe_work()`, `hda_acpi_init()`, `hda_acpi_dev_free()`, `hda_acpi_remove()`, `hda_acpi_shutdown()`, and system sleep callbacks. The match table currently includes NVIDIA ACPI IDs with `AZX_DCAPS_CORBRP_SELF_CLEAR`.

## Control Flow
Probe allocates `hda_acpi`, gets match data or defaults, creates an ALSA card, initializes work, creates the `azx` bus/device, stores the card in drvdata, and schedules `probe_work`. The work item initializes IRQ/MMIO/streams/chip, probes up to 8 codecs, configures codecs, registers the card, and marks `chip->running`.

## State and Persistence Behavior
Runtime state is held by the device-managed `hda_acpi`, the ALSA card, `azx` bus fields, stream DMA pages, and `chip->running`. Work cancellation and `snd_card_free()` drive teardown. System suspend/resume delegates to runtime PM force helpers and updates ALSA power state.

## Dependencies and Integration Points
The driver depends on platform resources from ACPI `_CRS`, ALSA core card/device lifecycle, shared `hda_controller.h` helpers, `azx_interrupt`, stream allocation, codec probing/configuration, and platform PM.

## Risks
Probe is asynchronous; failures inside `probe_work` return without directly surfacing to platform probe after the card object was installed. Resource parsing must expose one IRQ and one MMIO range. The `hda->data` fallback allocates zeroed data, so defaults must remain valid. Device free must cancel pending work before freeing streams and bus state.

## Test Signals
Test ACPI matching, IRQ/MMIO acquisition, nonzero codec mask after chip init, card names from `hda_data`, codec configuration, card registration, shutdown stopping a running chip, and suspend/resume power-state transitions.
