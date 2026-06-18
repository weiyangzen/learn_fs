# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/loopback.sh

Purpose: Tests hardware loopback behavior between two interfaces.

Important APIs/functions: `h1_create()`, `h1_destroy()`, `h2_create()`, `h2_destroy()`, `loopback_test()`, `setup_prepare()`, `cleanup()`, forwarding `simple_if_init/fini`, link setup, and ping checks.

Control flow: The script initializes two interfaces, configures loopback mode or relevant hardware state, sends traffic, and verifies packets loop as expected without requiring external forwarding beyond the test setup.

State and persistence: Mutates interface addresses and loopback/link settings, cleaned on exit.

Dependencies and integration points: Requires two test interfaces and driver support for the loopback operation being exercised, plus forwarding lib helpers.

Risks and test signals: Failures indicate loopback mode setup, traffic delivery, or cleanup regressions. Hardware support variability may cause skips or setup failures.
