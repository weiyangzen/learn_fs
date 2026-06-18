# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-mach.c

## Purpose
This is the AMD Yellow Carp machine driver for systems using the ACP6x PDM digital microphone path. It registers a single capture-only ASoC card named `acp6x` that connects the CPU DAI `acp_yc_pdm_dma.0`, the generic `dmic-codec.0` codec DAI `dmic-hifi`, and the ACP PDM platform component.

## Important APIs, Types, And Functions
Key data is `acp6x_dai_pdm[]`, `acp6x_card`, and the large `yc_acp_quirk_table[]`. `acp6x_probe()` is the main entry point. It checks ACPI `AcpDmicConnected`, evaluates `_WOV`, applies DMI overrides via `dmi_first_match()`, attaches the card to the platform device, and calls `devm_snd_soc_register_card()`. The platform driver is registered with `module_platform_driver()` and has alias `platform:acp_yc_mach`.

## Control Flow
Probe first initializes local defaults, reads the parent ACPI companion property, then evaluates `_WOV`. `_WOV == 0` rejects the device with `-ENODEV`; ACPI read failure falls through to DMI matching. If ACPI explicitly enables a DMIC, probe stores `&acp6x_card` as driver data. A DMI match can also store the card. If neither path supplies a card, probe returns `-ENODEV`; otherwise it registers the card.

## State And Persistence
The driver has static card and DAI-link objects. Per-device state is minimal; `machine` is currently `NULL` and stored as card driver data. Long-lived activation state lives in ASoC core objects after card registration.

## Dependencies And Integration Points
It depends on the `acp_yc_pdm_dma.0` platform component from `acp6x-pdm-dma.c`, the `dmic-codec` platform device from `pci-acp6x.c`, ACPI firmware properties/methods, and DMI board identifiers. It also uses common ASoC PM ops.

## Risks And Test Signals
The DMI table is large and contains duplicate entries, so regression risk is mostly false positive or false negative enablement on laptops. Firmware behavior around `_WOV` and `AcpDmicConnected` is a compatibility risk. Test signals include card creation only on intended machines, `arecord -l` exposing DMIC capture, suspend/resume retaining capture, and no card registration on systems without a supported DMIC path.
