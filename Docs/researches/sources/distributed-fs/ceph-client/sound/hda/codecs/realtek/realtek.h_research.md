# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/realtek.h

## Purpose
`realtek.h` defines the shared interface and private state contract for Realtek HD-audio codec modules. It is the bridge between per-codec files, ALSA HDA generic parser infrastructure, Realtek coefficient/GPIO/headset helpers, and side-codec component support.

## APIs, Types, and Functions
Important types are `struct alc_customize_define`, `struct alc_coef_led`, `struct alc_spec`, and `struct coef_fw`. `struct alc_spec` embeds `struct hda_gen_spec` as its first field and stores Realtek SKU fields, parse flags, GPIO and LED state, coefficient mutex, headset pin/mode/type state, init/power/shutup hooks, PLL fix data, optional keyboard input state, and HDA component parent state. The header declares coefficient helpers, GPIO helpers, common init/power/parser/build APIs, beep helpers under `CONFIG_SND_HDA_INPUT_BEEP`, common fixups, and device-specific cross-codec fixups.

## Control Flow
Per-codec modules include this header, allocate `alc_spec` with `alc_alloc_spec()`, manipulate fields before parser execution, and then call shared lifecycle functions. Inline `alc_pre_init()` maps to `alc_fill_eapd_coef()`. Inline coefficient locking helpers power up the codec, lock `spec->coef_mutex`, and power down after unlock.

## State and Persistence Behavior
The header defines all persistent in-memory Realtek state. `coef0` is cached after first read. GPIO data and LED masks persist across init callbacks. Headset mode/type fields prevent redundant coefficient changes and are reset by fixups on resume. Hook function pointers allow codec modules to persist custom init, suspend, or power actions.

## Dependencies and Integration Points
Includes cover Linux ACPI/PCI/DMI/I2C/SPI/input/LED infrastructure, ALSA core/jack/HDA APIs, local HDA parser headers, generic codec code, and side-codec component headers. Export declarations in `realtek.c` use the `SND_HDA_CODEC_REALTEK` namespace consumed by codec modules.

## Risks
Because `hda_gen_spec` must remain first in `alc_spec`, layout changes are risky. Missing initialization of new fields in `alc_alloc_spec()` can affect every Realtek codec. The header exposes many low-level helpers, so misuse of NIDs, coefficient masks, or fixup phases by codec modules can cause hardware regressions.

## Test Signals
Compile coverage across all Realtek modules, namespace import/export consistency, `CONFIG_SND_HDA_INPUT_BEEP` on/off builds, lockdep around coefficient access, and successful generic parser use through embedded `hda_gen_spec` are the primary signals.
