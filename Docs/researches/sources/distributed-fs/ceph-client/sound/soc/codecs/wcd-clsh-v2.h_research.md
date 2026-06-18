# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.h

## Purpose

`wcd-clsh-v2.h` is the public interface for the WCD Class-H controller. It defines the logical Class-H events, output states, amplifier modes, supported codec version identifiers, and exported controller functions used by codec drivers. The source was read as a complete 66-line file.

## Important APIs, Types, and Functions

`enum wcd_clsh_event` exposes `WCD_CLSH_EVENT_PRE_DAC` and `WCD_CLSH_EVENT_POST_PA`, matching the enable/disable event sequence used by DAPM event handlers. State macros define `WCD_CLSH_STATE_IDLE`, `WCD_CLSH_STATE_EAR`, `WCD_CLSH_STATE_HPHL`, `WCD_CLSH_STATE_HPHR`, `WCD_CLSH_STATE_LO`, and `WCD_CLSH_STATE_AUX`. `enum wcd_clsh_mode` covers Class-H normal, HiFi, low-power, low-HiFi, ultra-low-power, Class-AB variants, and `CLS_NONE`. `enum wcd_codec_version` selects WCD9335/WCD934x versus WCD937x+ programming.

The header forward-declares `struct wcd_clsh_ctrl` and declares `wcd_clsh_ctrl_alloc()`, `wcd_clsh_ctrl_free()`, `wcd_clsh_ctrl_get_state()`, `wcd_clsh_ctrl_set_state()`, and `wcd_clsh_set_hph_mode()`.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by `wcd-clsh-v2.c`; codec drivers include this file and call the public functions during DAPM state transitions.

## State and Persistence Behavior

The header does not allocate or store data. It describes state values and an opaque controller pointer whose storage is owned by the implementation. State persists only inside the allocated controller and codec registers programmed through it.

## Dependencies and Integration Points

The header includes `<sound/soc.h>` because public APIs use `struct snd_soc_component`. It is consumed by codec implementations such as `wcd9335.c` and by the implementation file itself.

## Risks and Edge Cases

State values are bitmasks, but the implementation currently validates only individual state values. New codec versions must be reflected in both the enum and implementation dispatch. Mode names include overlapping Class-H and Class-AB variants, so caller-side mode selection must match the output path and codec generation.

## Test Signals

Compile coverage should include this header from both the controller implementation and at least one codec driver. API compatibility tests are mostly build-time: enum users, opaque pointer usage, and exported symbol prototypes should remain synchronized with `wcd-clsh-v2.c`.
