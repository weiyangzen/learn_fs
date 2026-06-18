# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.c

Purpose: Shared Realtek speaker amplifier helpers for Intel SOF machine drivers, covering RT1011, RT1015P, RT1015, RT1308, and RT1019P.

Important APIs, types, and functions: Common two-speaker and four-speaker widgets/controls are reused across amps. `get_num_codecs()` counts ACPI devices by HID. RT1011 support programs PLL/sysclk from BCLK, sets four-slot TDM masks, and uses different prefix/widget behavior for CML compatibility. RT1015 support obtains BCLK, sets PLL/sysclk, and applies four-slot TDM RX masks. RT1308 support derives MCLK from topology, sets PLL/sysclk to rate*512, and exposes one stereo speaker widget. RT1015P and RT1019P are simpler auto-mode helpers with one component and two speaker routes.

Control flow and integration: Machine drivers choose helper functions to patch generated amp links and, where needed, call codec_conf helpers to install name prefixes. Runtime hw_params configures clocks/TDM slots per codec family.

State and persistence: Static component, route, ops, and codec_conf arrays. Runtime state is limited to codec clock/TDM programming.

Dependencies: Realtek codec headers, SOF topology BCLK/MCLK helpers, ASoC DAPM/DAI, ACPI enumeration, and Intel CML detection.

Risks: Multi-amp layouts depend on ACPI instance counts and fixed component order. TDM masks must match topology and amplifier wiring. CML compatibility prefixes are special cases. Test signals include each amp family, two/four RT1011 counts, TDM slot validation, IV/feedback capture where applicable, and DAPM route/control creation.
