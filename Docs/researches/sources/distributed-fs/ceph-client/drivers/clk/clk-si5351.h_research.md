# sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.h

Purpose: private register and limit header for `clk-si5351.c`. It centralizes Si5351 address constants, frequency/divider bounds, bit masks, parameter block offsets, output controls, and chip-variant identifiers.

Important APIs/types/functions: the file exports no functions. It defines frequency constraints such as PLL VCO range, multisynth and clkout minimum/maximum rates, divider parameter bounds (`SI5351_PLL_A_MIN`, `SI5351_MULTISYNTH_P*_MAX`), register addresses for status, output enable, PLL input source, clkout control, parameter blocks, phase offsets, PLL reset, crystal load, and fanout enable. `enum si5351_variant` identifies A, A3, B, and C variants used by probe matching and DT validation.

Control flow: no executable control flow. The C driver uses these constants to validate requested rates, choose parameter registers, mask/update bitfields, and expose variant-specific behavior.

State and persistence: no runtime state. The definitions describe persistent hardware register layout and encoded values that the C driver writes through regmap.

Dependencies and integration: included only by the Si5351 driver. It depends on the external platform-data enums for some semantic values in the C file, but this header itself is self-contained. Constants must match the Skyworks/Silicon Labs datasheet and AN619 equations used by the implementation.

Risks: incorrect bounds or bit masks directly corrupt rate calculations and register writes. The naming typo "MULTISYNTH" versus comments saying "multisync" is harmless but can complicate review. Variant enum values are ABI-like inside the driver because I2C/OF match data casts them through integer pointer fields.

Test signals: build coverage plus driver-level rate/variant tests are the only meaningful validation. Golden register-map tests would catch mistakes in offsets, masks, and parameter limits.
