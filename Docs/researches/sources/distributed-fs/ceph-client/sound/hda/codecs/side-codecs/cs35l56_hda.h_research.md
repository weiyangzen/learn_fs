# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.h

## Purpose
This header defines the shared state and public interface for the CS35L56-family HDA smart-amp driver. It is included by the common implementation and by I2C/SPI bus bindings.

## Important APIs, types, and functions
`struct cs35l56_hda` embeds `struct cs35l56_base`, an HDA codec pointer, a DSP work item, amp index/count/name fields, `struct cs_dsp`, playback/suspend flags, ASP TX mask, ALSA control pointers, and optional debugfs root. `cs35l56_hda_from_base()` converts shared base pointers back to the HDA wrapper. The exported declarations are `cs35l56_hda_common_probe()`, `cs35l56_hda_remove()`, and `cs35l56_hda_pm_ops`.

## Control flow
The header has no executable flow, but it defines the object passed from bus probe to common probe. Bus wrappers allocate and initialize `base.dev` and `base.regmap`, then call `cs35l56_hda_common_probe()`. Removal and PM callbacks flow back through the declarations in this header.

## State and persistence
The struct fields represent the lifetime state of one amplifier instance. Some fields are stable identity (`index`, `system_name`, `amp_name`), some are runtime state (`playing`, `suspended`, `asp_tx_mask`), and some link to external framework resources (`codec`, controls, debugfs, `cs_dsp`, base regmap/GPIO/IRQ data).

## Dependencies and integration points
It depends on Linux device/GPIO/regulator/workqueue headers, Cirrus `cs_dsp`, WMFW, and `sound/cs35l56.h`. The `extern` PM ops allow I2C and SPI drivers to share the same suspend/resume implementation.

## Risks and edge cases
Because the bus wrappers and common code share this struct directly, initialization ordering matters: `base.dev` and `base.regmap` must be valid before common probe. Lifetime ownership of `system_name`, controls, debugfs, and DSP resources must remain consistent with remove/unbind paths.

## Test signals
Build tests should cover all configurations using I2C, SPI, debugfs, and PM. Runtime tests should verify `container_of` conversion through calibration/debugfs paths and that bus wrappers call remove/PM functions against a fully initialized object.
