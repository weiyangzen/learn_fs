# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/alc861vd.c

## Purpose
`alc861vd.c` supports Realtek ALC660-VD and ALC861-VD codecs, which are related to ALC882 and add an independent DAC. It supplies VD-specific ignored pins, SSID ports, shutdown behavior, beep routing, and board quirks.

## APIs, Types, and Functions
Important functions are `alc861vd_parse_auto_config()`, `alc861vd_fixup_dallas()`, `alc660vd_fixup_asus_gpio1()`, and `alc861vd_probe()`. `alc861vd_fixups[]` contains Dallas pin-cap overrides and ASUS GPIO1 reset behavior. `alc861vd_fixup_tbl[]` maps HP TX1000, ASUS A7-K, and Toshiba L30-149. `snd_hda_id_alc861vd[]` matches ALC660-VD and ALC861-VD.

## Control Flow
Probe allocates `alc_spec` with mixer node `0x0b`, enables cdefine beep NID `0x23`, sets `spec->shutup = alc_eapd_shutup`, runs `alc_pre_init()`, selects and applies `PRE_PROBE` fixups, parses auto config with ignored NID `0x1d` and SSID ports `{0x15,0x1b,0x14}`, configures beep through input index `0x05` on node `0x0b`, and applies `PROBE` fixups. Dallas fixups override caps for pins `0x18` and `0x19` to exclude VREF80 before parsing.

## State and Persistence Behavior
State lives in `struct alc_spec`: shutup callback, beep NID, GPIO masks, parsed routes, and fixup modifications. GPIO setup happens at pre-probe and is later written by shared init. EAPD shutup persists as the suspend/remove policy.

## Dependencies and Integration Points
The file depends on the shared Realtek helper API, generic HDA parser/control/PCM lifecycle, HDA fixup framework, jack event handling, and PCI subsystem quirk matching.

## Risks
Pin capability overrides must match hardware exactly; removing VREF80 changes microphone bias options. ASUS GPIO1 handling mutates both `gpio_mask` and GPIO data via common helpers. A wrong beep amp index or mixer node can create silent or invalid beep controls.

## Test Signals
Check codec binding for both IDs, BIOS pin parsing with the VD SSID order, EAPD shutup on suspend, beep controls when analog is present, HP/Toshiba Dallas mic bias behavior, ASUS GPIO1 reset behavior, and normal jack unsolicited events.
