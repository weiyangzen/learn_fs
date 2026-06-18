# sources/distributed-fs/ceph-client/include/sound/madera-pdata.h

Source read summary: 59 lines, Cirrus Logic Madera codec platform data.

Purpose: defines board/platform configuration fields for Madera-family codecs, including input modes, DMIC references, mono outputs, PDM speaker format, auxiliary power pins, and max clocked AIF channels.

Important APIs, types, and functions: constants define maximum inputs, muxed channels, outputs, AIFs, PDM speakers, and DSPs. `struct madera_codec_pdata` carries `max_channels_clocked`, `dmic_ref`, per-input `inmode`, `out_mono`, `pdm_fmt`, and `out_mono`/speaker related arrays referenced by the codec driver.

Control flow: board code or firmware translation fills the pdata before codec probe; the codec driver reads the arrays during initialization to program routing, bias, PDM, and clocking defaults.

State and persistence behavior: pdata is static board configuration copied or referenced at device probe. It does not store runtime state; hardware registers reflect the configuration until reset or reprogramming.

Dependencies and integration points: depends on Linux integer types and Madera codec driver definitions/datasheet values. Integrates platform data systems with ASoC codec setup.

Risks and edge cases: array dimensions must match maximum constants; wrong DMIC reference or input mode can damage capture routing; platform-data and device-tree/ACPI defaults must not conflict.

Test signals: probe each supported Madera variant with populated and default pdata, verify DMIC/input/output/PDM register programming, and check bounds for all max arrays.
