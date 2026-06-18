# sources/distributed-fs/ceph-client/drivers/platform/chrome/Makefile

Purpose: kbuild mapping for ChromeOS platform support drivers.

Important APIs, types, and functions: maps Kconfig symbols to single objects and composite modules. Composite objects include `cros_ec_lpcs-objs := cros_ec_lpc.o cros_ec_lpc_mec.o`, `cros-ec-typec-objs`, `cros-ec-proto-objs`, `cros-ec-sensorhub-objs`, and `cros_kunit_proto_test-objs`. It sets include flags for trace-generated objects.

Control flow: kbuild includes objects according to `obj-$(CONFIG_...)`. Optional Type-C altmode object inclusion is guarded by `ifneq ($(CONFIG_CROS_EC_TYPEC_ALTMODES),)`.

State and persistence: build-only; no runtime state.

Dependencies and integration points: must match Chrome Kconfig symbols and source filenames. The LPC object layout is important because MEC helper functions are linked into the same module. Trace objects need `-I$(src)` so generated trace headers resolve.

Risks and edge cases: composite module names differ from some source filenames (`cros_ec_lpcs`, `cros-ec-proto`, `cros-ec-typec`). Missing objects in composites can create unresolved symbols. Test object naming must align with KUnit module expectations.

Test signals: module builds for each Chrome symbol, especially composites and optional Type-C altmode inclusion. `modinfo` can confirm module descriptions and dependency graph.
