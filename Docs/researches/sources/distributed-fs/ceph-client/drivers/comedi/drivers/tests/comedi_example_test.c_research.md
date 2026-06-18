## sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/comedi_example_test.c

Purpose: Minimal example Comedi unit-test kernel module demonstrating the local `unittest.h` harness.

Important APIs, types, and functions: A tiny fake `struct comedi_device` contains `board_name` and `item`. Static global `dev` starts with board name `fake_device`. `init_fake()` initializes `dev.item` to 10. `test0()` runs two assertions through `unittest()`. `unittest_enter()` builds a NULL-terminated `unittest_fptr` array and calls `exec_unittests("example", unit_tests)`. `unittest_exit()` is empty.

Control flow and state: Loading the module runs `unittest_enter()`, which invokes `test0()`. `test0()` resets the fake device state and verifies both a negative and positive assertion case. State is only the module-global fake device; it is reinitialized before the assertions and no state persists beyond module lifetime.

Dependencies and integration: The module includes `linux/module.h` and local `unittest.h`, and uses normal `module_init()`/`module_exit()` declarations. It is built when the tests Makefile sees `CONFIG_COMEDI_TESTS_EXAMPLE`.

Risks and test signals: This is an example rather than a substantive driver test. It does not exercise real Comedi core or hardware paths and shadows a tiny local `struct comedi_device`. Useful signals are that the test module compiles, loads, executes the two assertions, emits the expected harness results, and unloads cleanly.
