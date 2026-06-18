<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-prodikeys.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-prodikeys.c

## Purpose
This driver supports the Creative Prodikeys PC-MIDI keyboard. It combines HID keyboard handling, extra multimedia/function keys, a vendor output report for mode/LED state, and an ALSA raw MIDI input device that converts the musical keyboard reports into MIDI note events. It also exposes sysfs controls for MIDI channel, octave shift, and sustain duration.

## Important APIs, types, and functions
`struct pcmidi_snd` is the per-interface state object: HID device, USB interface number, output report 6, extra-key input device pointer, MIDI mode/sustain/channel/octave state, sustain timers, function state, last-key cache, rawmidi lock/substream/trigger state, and ALSA card/rawmidi pointers. `struct pcmidi_sustain` stores delayed note-off events.

Sysfs handlers are `show/store_channel`, `show/store_sustain`, and `show/store_octave`. MIDI/event handling is split across `pcmidi_handle_report1`, `pcmidi_handle_report3`, `pcmidi_handle_report4`, `pcmidi_handle_report`, `pcmidi_send_note`, and `pcmidi_sustained_note_release`. ALSA setup/teardown is in `pcmidi_snd_initialise` and `pcmidi_snd_terminate`. HID callbacks are `pk_report_fixup`, `pk_input_mapping`, `pk_raw_event`, `pk_probe`, and `pk_remove`.

## Control flow
Probe requires USB, determines the interface number, allocates state, parses HID, restores `HID_QUIRK_NOGET` when requested, starts HID, and initializes ALSA only for interface 1. Report fixup corrects report 4 count in a known 178-byte descriptor. Input mapping for Microsoft vendor page on interface 1 records the input device and adds extra key capabilities.

Raw reports on interface 1 are intercepted for report IDs 1, 3, and 4. Report 1 handles qwerty MIDI-mode special keys such as octave down and sustain toggle. Report 3 converts note pairs into MIDI note-on/note-off bytes using middle C, current channel, and octave; sustain mode delays note-off by arming one of 32 timers. Report 4 handles extra office/media keys, Fn lock, MIDI launcher/mode toggle, octave up in MIDI mode, and emits key press/release events through the captured input device. Output report 6 is used to set device mode/state bytes such as 0xc1, 0xc5, and 0xc6.

ALSA initialization creates an `snd_card`, low-level device, one-input rawmidi device, sysfs attributes, spinlock, sustain timers, output-report operational state, and then registers the card. The rawmidi trigger path gates whether `pcmidi_send_note` delivers bytes to the current input substream.

## State and persistence behavior
MIDI channel, octave, sustain duration, MIDI mode, Fn state, last pressed extra keys, and in-flight sustain timers are runtime state only. Sysfs writes update in-memory controls. Sustain timers persist delayed note-off events until they fire or `stop_sustain_timers` deletes them during teardown. ALSA card lifetime can extend until userspace closes it because removal uses `snd_card_disconnect` and `snd_card_free_when_closed`.

## Dependencies and integration points
The driver depends on HID core, USB interface metadata, Linux input, timers, spinlocks, ALSA core/rawmidi, module parameters (`index`, `id`, `enable`), sysfs, and `hid-ids.h`. It integrates one physical HID device with both input and sound subsystems.

## Risks and test signals
Risks include interface-number assumptions, rawmidi lock/substream races, timer-delayed note-off after removal, failure unwind across ALSA/sysfs/timers, and note arithmetic outside valid MIDI ranges when octave shifts combine with device note values. Tests should verify descriptor fixup, interface 1-only ALSA creation, channel/octave/sustain sysfs validation, note-on/off conversion, sustain timer release and teardown, extra key press/release state, MIDI mode toggles, rawmidi open/trigger gating, and removal while ALSA clients are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-prodikeys.c -->
