# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/Kconfig

## Purpose
`vcap/Kconfig` defines build configuration for the shared Microchip VCAP library and its KUnit tests. It makes the VCAP rule API available under Microchip Ethernet drivers and provides an optional test target for the library.

## Important APIs, Types, and Functions
- `config VCAP` is a bool option under `NET_VENDOR_MICROCHIP` with help text explaining VCAP as a TCAM rule/action/counter engine.
- `config VCAP_KUNIT_TEST` is a bool KUnit test option depending on `KUNIT` and `VCAP`, selecting `DEBUG_FS` and defaulting to `KUNIT_ALL_TESTS`.

## Control Flow
Kconfig control flow is declarative. When `NET_VENDOR_MICROCHIP` is enabled, users can select `VCAP`; when KUnit and VCAP are built in, `VCAP_KUNIT_TEST` can build the VCAP model unit tests. The selected symbols drive object inclusion in the adjacent Makefile.

## State and Persistence Behavior
The file does not manage runtime state. Its selections affect kernel build artifacts and whether the VCAP library and tests are present. `select DEBUG_FS` for tests changes build-time diagnostic availability.

## Dependencies and Integration Points
It integrates with the kernel Kconfig tree, Microchip network driver menu, KUnit, DEBUG_FS, and `drivers/net/ethernet/microchip/vcap/Makefile`. Sparx5 and other Microchip switch drivers depend on the VCAP library for rule offload.

## Risks and Edge Cases
- `VCAP` is a bool, not a tristate, so module composition must account for built-in behavior.
- The test dependency line includes `depends on KUNIT=y && VCAP=y && y`, which enforces built-in KUnit/VCAP and contains a redundant `&& y`.
- Selecting `DEBUG_FS` for KUnit tests may alter debugfs build coverage when all tests are enabled.

## Test Signals
- Build matrix should include `VCAP=y`, `VCAP=n`, and `VCAP_KUNIT_TEST=y`.
- Kconfig lint or `olddefconfig` runs should verify dependencies do not create impossible configs.
- KUnit runs should confirm the selected test object links and executes only in valid configurations.
