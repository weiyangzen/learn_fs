# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/Makefile

## Purpose

This Makefile wires the MT2701 audio platform and machine drivers into Kbuild.

## Important APIs, Types, and Functions

It defines `snd-soc-mt2701-afe-y := mt2701-afe-pcm.o mt2701-afe-clock-ctrl.o`, builds that composite object under `CONFIG_SND_SOC_MT2701`, and adds machine drivers for `CONFIG_SND_SOC_MT2701_CS42448` and `CONFIG_SND_SOC_MT2701_WM8960`.

## Control Flow

There is no runtime flow. At build time, Kbuild links the PCM platform code and clock-control code into one MT2701 AFE module/object, while codec-specific machine drivers are independently selected by Kconfig.

## State and Persistence Behavior

No state is stored. The file controls which compiled objects are present in the kernel or modules.

## Dependencies and Integration Points

The platform object depends on `mt2701-afe-pcm.c` and `mt2701-afe-clock-ctrl.c`. Machine entries depend on codec drivers for CS42448/BT SCO or WM8960 being available through ASoC.

## Risks and Edge Cases

Missing one of the platform objects would break link-time references between PCM and clock helpers. Enabling a machine driver without the platform driver or matching DT nodes would build but not produce a usable sound card.

## Test Signals

Kbuild coverage with each listed Kconfig symbol verifies object names and symbol resolution. Runtime card enumeration validates the selected machine object binds.
