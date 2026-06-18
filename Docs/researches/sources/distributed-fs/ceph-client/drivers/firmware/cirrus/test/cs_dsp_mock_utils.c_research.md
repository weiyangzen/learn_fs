# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_utils.c

## Purpose
This tiny file supplies module metadata for the Cirrus DSP KUnit utility module. Its existence lets multiple helper objects link into a named module with the right license and namespace import.

## Important APIs, Types, And Functions
There are no functions or data definitions. The file declares `MODULE_DESCRIPTION`, `MODULE_AUTHOR`, `MODULE_LICENSE`, and `MODULE_IMPORT_NS("FW_CS_DSP")`.

## Control Flow, State, And Persistence
There is no runtime state or control flow. Its build-time effect is module metadata and namespace import for the aggregate `cs_dsp_test_utils` object.

## Dependencies And Integration Points
It depends only on `linux/module.h`. The namespace import integrates the utility module with production `FW_CS_DSP` exports used by helper and test objects.

## Risks And Test Signals
Risk is low but namespace imports are required for modpost correctness. Test signals are successful builds of `CONFIG_FW_CS_DSP_KUNIT_TEST_UTILS=m/y` without missing namespace warnings.
