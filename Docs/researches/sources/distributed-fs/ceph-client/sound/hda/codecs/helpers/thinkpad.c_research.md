# sources/distributed-fs/ceph-client/sound/hda/codecs/helpers/thinkpad.c

## Purpose

This include-style helper connects ThinkPad mute and mic-mute LEDs to generic HDA LED controls when ThinkPad ACPI support is available.

## Important APIs, types, and functions

With `CONFIG_THINKPAD_ACPI`, `is_thinkpad` checks Lenovo subsystem vendor `0x17aa` plus ACPI IDs `LEN0068`, `LEN0268`, or `IBM0068`. `hda_fixup_thinkpad_acpi` registers mute and micmute LED cdevs during pre-probe. Without the config, it compiles to a no-op.

## Control flow

The helper is invoked from a codec fixup. It only acts during `HDA_FIXUP_ACT_PRE_PROBE`, validates the platform, then adds LED devices to the generic HDA codec state.

## State and persistence behavior

It creates runtime LED class device integration and does not persist data. LED state follows generic HDA mixer/micmute state.

## Dependencies and integration points

It depends on ThinkPad ACPI, ACPI discovery, LED class APIs, and generic HDA LED helpers. It is included by Realtek codec sources rather than built as a standalone module.

## Risks and test signals

Risks include ACPI ID coverage gaps, false positives on Lenovo non-ThinkPad machines, and config-dependent build regressions. Test ThinkPad mute/micmute LEDs, hotkey interaction, mixer state sync, and no-op builds without `CONFIG_THINKPAD_ACPI`.
