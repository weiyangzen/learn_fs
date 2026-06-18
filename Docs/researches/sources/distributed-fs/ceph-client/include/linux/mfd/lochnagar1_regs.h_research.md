# sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar1_regs.h

Purpose: This header defines Lochnagar1 board register addresses and bitfields for audio interface routing, MCLK selection, DSP/codec clocks, general-purpose audio interfaces, GPIO/LED, reset, and I2C codec interface mode.

Important APIs, types, and constants: Register macros include codec AIF selections, codec MCLK selections, AIF control registers, external AIF control, DSP AIF and clock selection, GF/PSIA/SPDIF routing, GPIO/LED registers, reset, and I2C control. Bitfields define common source selection, LRCLK/BCLK direction, AIF enable bits, MCLK enable bits, GF clock output enable, DSP and codec reset bits, and codec CIF mode.

Control flow, state, and persistence: There is no code. Consumers write source-select fields and enable/direction bits to route clocks and serial audio between codecs, DSP, PSIA, SPDIF, and general-function headers. Reset bits control attached codec/DSP devices. State is board routing and reset configuration persisted in Lochnagar1 registers while powered.

Dependencies and integration points: It integrates with the Lochnagar core regmap, ALSA SoC machine/card support, clock framework consumers, GPIO/LED children, and board reset control.

Risks and test signals: Risks include source-route mismatches, wrong LRCLK/BCLK master direction, forgetting to enable an AIF/MCLK after selecting a source, and reset polarity misuse. Test signals include audio loopback on each routed AIF, MCLK frequency/enable checks, DSP/codec reset tests, LED/GPIO register tests, and I2C CIF mode readback.
