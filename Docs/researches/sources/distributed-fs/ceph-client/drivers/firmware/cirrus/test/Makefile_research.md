# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/Makefile

## Purpose
This Makefile assembles the Cirrus DSP KUnit utility module and KUnit test module from multiple object files.

## Important Targets
`cs_dsp_test_utils-objs` groups helper objects: mock memory maps, bin builder, mock regmap, utility module metadata, and wmfw builder. `cs_dsp_test-objs` groups the actual KUnit suites covering bin loading, bin errors, callbacks, control parsing/cache/read-write, wmfw loading, wmfw errors, and suite registration. `obj-$(CONFIG_FW_CS_DSP_KUNIT_TEST_UTILS)` and `obj-$(CONFIG_FW_CS_DSP_KUNIT_TEST)` gate final object inclusion.

## Control Flow, State, And Persistence
There is no runtime control flow in this file. It persists the test composition contract: utility helpers can be built separately and the full test module links all listed suites.

## Dependencies And Integration Points
The file integrates with `drivers/firmware/cirrus/Kconfig`, KUnit, and exported namespaces from `cs_dsp.c` plus `FW_CS_DSP_KUNIT_TEST_UTILS`.

## Risks And Test Signals
Object ordering and completeness matter because tests reference helper symbols. Build tests should ensure both utility-only and full-test configurations link, and that adding a test source updates this object list.
