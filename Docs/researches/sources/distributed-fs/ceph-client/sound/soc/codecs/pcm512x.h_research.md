# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.h

Purpose: shared PCM512x register and API header for bus wrappers and the core codec driver. It defines the paged virtual register address space, bit fields for power/PLL/I2S/GPIO/volume/clocking, and shared lifecycle exports.

Important APIs and types: exports `pcm512x_pm_ops`, `pcm512x_regmap`, `pcm512x_probe()`, and `pcm512x_remove()`. `PCM512x_PAGE_BASE()` maps hardware pages into virtual regmap space starting at `PCM512x_VIRT_BASE`. Bit macros cover reset, power, mute, PLL lock/enable, clock references, dividers, error detection, I2S word length/format, GPIO functions, analog gain, and boost.

Control flow contribution: `pcm512x.c` uses these macros throughout DAI setup, PLL coefficient programming, divider writes, mute handling, bias transitions, runtime PM, and regmap range configuration.

State and persistence: no state is stored in the header; however, `PCM512x_MAX_REGISTER` and the page/register macros define the cacheable virtual address range. Volatile status/PLL/GPIO registers are selected in the C file from these constants.

Dependencies and integration points: Linux PM and regmap declarations. Included by I2C/SPI shims and the shared core.

Risks: virtual register numbers intentionally differ from raw 8-bit page-window addresses; future code must use these macros rather than raw offsets for paged registers. Several bit fields use compact datasheet abbreviations that can be misapplied without the C-file context.

Test signals: compile all users, verify regmap range page switching, and validate representative bit fields for I2S format, clock references, GPIO output selection, and mute/power controls against hardware traces.
