# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Kconfig

## Purpose
This Kconfig file defines the Cirrus DSP firmware support library and its KUnit test build switches. It separates the production DSP library from test utilities and the test suite.

## Important Symbols
`FW_CS_DSP` is a hidden tristate defaulting to `n`; client drivers select or depend on it to build `cs_dsp.o`. `FW_CS_DSP_KUNIT_TEST_UTILS` is a tristate for shared test helper objects. `FW_CS_DSP_KUNIT_TEST` is a visible KUnit option, depends on `KUNIT`, `REGMAP`, and `FW_CS_DSP`, defaults to `KUNIT_ALL_TESTS`, and selects the utility module.

## Control Flow, State, And Persistence
There is no runtime flow. The file persists build relationships: tests require the library and regmap, while helper utilities can be built independently for tests. Because `FW_CS_DSP` is hidden, production enablement is driven by users of the library rather than direct menu selection.

## Dependencies And Integration Points
The symbols map to the sibling Makefiles. Test utilities import the `FW_CS_DSP` namespace and are used by KUnit files under `drivers/firmware/cirrus/test`.

## Risks And Test Signals
The key risk is build skew: tests need helper symbols and the production namespace available. Validation should include `KUNIT_ALL_TESTS=y`, module/builtin combinations where possible, and compile testing with `REGMAP` disabled to ensure dependency exclusion works.
