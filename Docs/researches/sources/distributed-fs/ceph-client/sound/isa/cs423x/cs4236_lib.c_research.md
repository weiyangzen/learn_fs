# sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236_lib.c

## Purpose

`cs4236_lib.c` provides the low-level extensions for CS4235, CS4236B, CS4237B, CS4238B, and CS4239 chips on top of the generic WSS layer. It validates the CS4236 control port, initializes extended/control registers, installs custom PCM rate/format callbacks, implements PM register image save/restore, and creates enhanced mixer, IEC958, and 3D controls.

## Important APIs, Types, and Functions

- `snd_cs4236_ext_map[]` is the default image for 18 extended indirect registers.
- `snd_cs4236_ctrl_out()` and `snd_cs4236_ctrl_in()` access control registers through `cport + 3/4` while updating `chip->cimage`.
- `snd_cs4236_xrate()` applies an eight-entry ratnum rate constraint and `divisor_to_rate_register()` converts ALSA selected divisors into DAC/ADC rate register values.
- `snd_cs4236_playback_format()` and `snd_cs4236_capture_format()` set WSS format registers and CS4236 DAC/ADC rate registers.
- `snd_cs4236_create()` wraps `snd_wss_create()`, validates enhanced hardware and cport, initializes control and extended registers, and overrides WSS callbacks.
- `snd_cs4236_pcm()` creates WSS PCM and clears joint-duplex info.
- Mixer helper families implement single/double controls over extended registers, control registers, and mixed WSS/extended registers.
- `snd_cs4236_mixer()` selects CS4235/CS4239 or CS4236-family control sets, then adds hardware-specific 3D and IEC958 controls.

## Control Flow

Creation first creates a WSS chip, then returns it unchanged if enhanced CS4236 bits are absent. Enhanced chips require a non-auto control port; the library reads control register 1 and extended version and requires them to match. It then initializes control registers for reset/digital-output defaults, installs custom rate and format callbacks, installs PM callbacks, writes the default extended image, and initializes compatible WSS registers. PCM creation delegates to `snd_wss_pcm()` and adjusts flags. Mixer creation adds a base control table based on hardware type, then appends 3D controls for CS4235/CS4237B/CS4238B variants and IEC958 controls for CS4237B/CS4238B.

## State and Persistence Behavior

State is stored in the generic `struct snd_wss`: `image[]` for base WSS registers, `eimage[]` for CS4236 extended registers, `cimage[]` for control registers, callback pointers for rate/format/PM behavior, and the control port. Suspend snapshots base registers 0-31, all 18 extended registers, and control registers 2-8. Resume enters MCE, restores base registers except special/version registers, restores extended/control registers except selected reserved control register 7, and exits MCE.

## Dependencies and Integration Points

The file depends on generic WSS helper functions, CS4236 register macros from `<sound/wss.h>`, ALSA PCM constraint APIs, ALSA control/TLV APIs, IEC958 constants from `<sound/asoundef.h>`, and ISA I/O. It is linked into `snd-cs4236.o` and used by `cs4236.c`.

## Risks and Edge Cases

The cport validation is critical; a wrong control port may otherwise write arbitrary ISA I/O locations. Rate selection depends on `params->rate_den` matching the ratnum constraint; unexpected divisors trigger `snd_BUG()`. IEC958 enable toggles MCE and resets channel-status state with timing delays, which is sensitive to locking and hardware timing. The mixer put helper for different left/right extended registers writes both values; correctness depends on the cached image matching hardware. Hardware-specific control tables differ substantially, so wrong hardware ID produces incorrect mixer semantics.

## Test Signals

Tests should cover enhanced and fallback creation, cport mismatch failure, rate-constraint negotiation, playback/capture format changes, suspend/resume image restore, mixer get/put change reporting, CS4235/CS4239 versus CS4236B/CS4237B/CS4238B control sets, IEC958 enable and channel status controls, and 3D controls on the appropriate chip IDs.
