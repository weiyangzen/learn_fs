# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.h

Purpose: private header for BMan self-test code.

Important APIs: includes `bman_priv.h`, sets `pr_fmt`, and declares `void bman_test_api(void)`.

Control flow and integration: shared by the test module entry and API test implementation so `bman_test.c` can call the optional API test.

State and persistence: no state.

Risks and test signals: risk is test code depending on private implementation details through `bman_priv.h`. Test signals are successful test module build with and without API test object.
