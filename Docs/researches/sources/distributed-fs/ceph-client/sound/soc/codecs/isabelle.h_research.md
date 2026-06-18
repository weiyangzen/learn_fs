# sources/distributed-fs/ceph-client/sound/soc/codecs/isabelle.h

## Purpose
This header defines the register offsets and bit-field values used by the TI Isabelle codec driver. It is the shared hardware contract for power, interrupt, PLL, sample-rate, interface, TX/RX routing, gains, DPGAs, DACs, output drivers, PDM, and supported DAI format/rate constants.

## Important APIs, types, and functions
There are no functions or C types. Important definitions include register offsets from `ISABELLE_PWR_CFG_REG` through `ISABELLE_HF_NG_CFG2_REG`, `ISABELLE_CHIP_EN`, interface format fields `ISABELLE_AIF_FMT_MASK`, `ISABELLE_I2S_MODE`, `ISABELLE_LEFT_J_MODE`, `ISABELLE_PDM_MODE`, width fields `ISABELLE_AIF_LENGTH_*`, master/slave bit `ISABELLE_AIF_MS`, sample-rate values `ISABELLE_FS_RATE_*`, and `ISABELLE_MAX_REGISTER` for regmap bounds.

## Control flow
The header has no executable control flow. The implementation uses these constants during component bias transitions, `hw_params`, DAI format setup, mixer/control declarations, DAPM widgets, and route definitions.

## State and persistence behavior
The header stores no runtime state. It describes hardware register state that is persisted in the codec until changed or reset. Regmap caching in `isabelle.c` relies on the offsets and `ISABELLE_MAX_REGISTER` being correct.

## Dependencies and integration points
It depends only on Linux bit operations. It is included by `isabelle.c` and is tightly coupled to the regmap defaults, controls, widgets, and callback writes in that driver.

## Risks and edge cases
Incorrect offsets or masks will misprogram broad parts of the codec because the implementation is heavily table-driven. The header includes many registers not actively used by `isabelle.c`, such as interrupt/accessory/button and PLL fields, so future additions must verify reset values and cache behavior rather than assuming unused fields are safe.

## Test signals
Direct test coverage is compilation of `isabelle.c`. Runtime signals are correct chip enable toggling, sample-rate and width writes, DAI format writes, and successful operation of controls and DAPM routes that reference the defined registers.
