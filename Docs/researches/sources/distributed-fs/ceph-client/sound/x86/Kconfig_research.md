# sources/distributed-fs/ceph-client/sound/x86/Kconfig

## Purpose
Defines the x86-specific sound driver menu and the Intel HDMI LPE audio config option.

## Important APIs, Types, And Functions
- `menuconfig SND_X86` gates x86 sound devices that are not SoC or PCI class drivers.
- `config HDMI_LPE_AUDIO` builds the Intel Atom HDMI audio without HDAudio support as a tristate.

## Control Flow
Kconfig selection enables compilation only on `X86`. `HDMI_LPE_AUDIO` depends on `DRM_I915` and selects `SND_PCM`, linking the audio driver to i915-provided platform device support.

## State And Persistence
The selected Kconfig symbols persist in kernel build configuration and determine whether the module or built-in object is produced.

## Dependencies And Integration Points
Integrates with `sound/x86/Makefile`, ALSA PCM, and i915's HDMI LPE platform-data bridge.

## Risks
Because `HDMI_LPE_AUDIO` depends directly on `DRM_I915`, build coverage must include i915 configurations. Missing `SND_PCM` would break ALSA symbols, hence the explicit select.

## Test Signals
Check `oldconfig` visibility on x86, module build for `CONFIG_HDMI_LPE_AUDIO=m`, and built-in build for `=y`.
