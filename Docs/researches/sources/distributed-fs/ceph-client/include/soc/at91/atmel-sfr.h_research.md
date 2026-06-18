# sources/distributed-fs/ceph-client/include/soc/at91/atmel-sfr.h

Purpose: lists Atmel Special Function Register offsets and bit fields used for EBI/DDR, USB, UTMI, light sleep, I2S clock selection, and write protection.

Important APIs and types: offsets include DDR/EBI configuration, OHCI interrupt config/status, UTMI clock trim and DP/DM swap, light sleep, I2S clock selection, and write-protection mode. Macros encode chip select assignment, EBI pull-up/pull-down/drive, NAND-on-D16, DDR multi-port enable, OHCI resume/suspend bits, UTMI trim/swap fields, memory power gating, and write-protect enable/key mask.

Control flow: AT91 platform drivers update SFR syscon registers during pin/memory/USB/suspend initialization, typically through regmap read-modify-write operations and write-protect unlock sequences.

State and persistence: hardware SFR state persists until reset or power-domain loss and affects multiple peripherals. No software state is owned.

Dependencies and integration points: depends on `BIT()`/`GENMASK()` from includers and integrates syscon/regmap clients for AT91 SoC glue.

Risks and test signals: risks include shared register contention, incorrect write-protect key handling, enabling DDR/EBI bits on the wrong SoC, and USB suspend/resume polarity mistakes. Test board boot, NAND/EBI mux, USB host/device operation, suspend light-sleep entry, and regmap write-protect paths.
