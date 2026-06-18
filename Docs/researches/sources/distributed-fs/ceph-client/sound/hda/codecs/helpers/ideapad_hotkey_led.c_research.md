# sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/ideapad_hotkey_led.c

## Purpose

This include-style helper wires Lenovo Ideapad mute and mic-mute LEDs into generic HDA LED class device support when the platform ACPI driver is enabled.

## Important APIs, types, and functions

With `CONFIG_IDEAPAD_LAPTOP`, `is_ideapad` checks Lenovo subsystem vendor `0x17aa` and ACPI IDs `LHK2019` or `VPC2004`. `hda_fixup_ideapad_acpi` adds mute and micmute LED cdevs during `HDA_FIXUP_ACT_PRE_PROBE`. Without the config, the fixup is an empty stub.

## Control flow

The codec fixup table calls `hda_fixup_ideapad_acpi`. During pre-probe the helper validates platform identity, then registers both LED class devices through `snd_hda_gen_add_mute_led_cdev` and `snd_hda_gen_add_micmute_led_cdev`.

## State and persistence behavior

It adds runtime LED class device integration to the codec generic spec. No file or firmware persistence is used.

## Dependencies and integration points

It depends on ACPI device discovery, `CONFIG_IDEAPAD_LAPTOP`, Linux LED class support, and generic HDA LED helpers.

## Risks and test signals

Risks include false-positive Lenovo matching, missing LEDs when ACPI IDs change, and build coverage for both config branches. Test Ideapad mute/micmute hotkeys, LED state changes from mixer controls, and no-op behavior when `CONFIG_IDEAPAD_LAPTOP` is disabled.
