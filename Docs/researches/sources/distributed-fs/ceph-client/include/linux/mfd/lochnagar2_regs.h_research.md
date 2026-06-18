# sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar2_regs.h

Purpose: This header defines the larger Lochnagar2 register map. It covers audio interface and clock routing, GPIO and GPIO-channel routing, reset controls, analogue path update controls, mic-bias and regulator fields, SPDIF, current monitor, power control, and codec core voltage settings.

Important APIs, types, and constants: Register macros cover many Lochnagar2 routing/control blocks. Key bitfields include AIF enable/LRCLK/BCLK/source masks, clock enable/source masks, GPIO source and channel source/status masks, DSP and codec reset bits, analogue path update and update status bits, input-bias and mic-bias source fields, codec CIF mode, SPDIF reset/hardware mode, IMON enable/channel/data-ready/data masks, power enable, MICVDD regulator enable/voltage select, and VDDCORE codec regulator enable/voltage select.

Control flow, state, and persistence: Consumers program routing and regulator fields through regmap. Analogue path changes require update sequencing coordinated with `lochnagar_update_config` and the core lock. IMON measurement flow configures channels, triggers measurement/data request, and polls done/data-ready bits. Hardware register state persists board routing, resets, regulator settings, and monitor configuration.

Dependencies and integration points: It integrates with the Lochnagar core, ALSA SoC audio routing/clocking, GPIO, regulator, SPDIF, and current-monitor consumers.

Risks and test signals: Risks include leaving one-shot analogue or IMON trigger bits asserted, mismatching GPIO channel status/source fields, wrong regulator voltage select masks, and missing reset sequencing for attached audio devices. Test signals include AIF routing tests, analogue path latch tests, IMON measurement readback, regulator enable/voltage tests, GPIO channel routing, and SPDIF reset/mode validation.
