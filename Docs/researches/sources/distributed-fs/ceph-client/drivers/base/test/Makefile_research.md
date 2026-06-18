# sources/distributed-fs/ceph-client/drivers/base/test/Makefile

Purpose: this Makefile maps the device-model test Kconfig symbols to concrete test objects.

Important APIs, types, and functions: `obj-$(CONFIG_TEST_ASYNC_DRIVER_PROBE)` adds `test_async_driver_probe.o`; `obj-$(CONFIG_DM_KUNIT_TEST)` adds `root-device-test.o` and `platform-device-test.o`; `obj-$(CONFIG_DRIVER_PE_KUNIT_TEST)` adds `property-entry-test.o`. It also applies `$(DISABLE_STRUCTLEAK_PLUGIN)` to `property-entry-test.o`.

Control flow: the kernel build system expands the conditional `obj-*` lines according to configuration. The file has no runtime control flow.

State and persistence: generated object inclusion is persistent only for the build. No runtime state is introduced.

Dependencies and integration points: it depends on the Kconfig symbols declared in the adjacent Kconfig file and on the kernel Kbuild infrastructure. The `DISABLE_STRUCTLEAK_PLUGIN` flag is an integration signal that property-entry tests use initializers or patterns incompatible with structleak instrumentation assumptions.

Risks: a mismatch between Kconfig symbol names and object names would silently omit tests. Removing the structleak flag could create false-positive build failures or altered test behavior.

Test signals: `make` with the relevant configs should compile exactly these objects. `modinfo` or KUnit run output can confirm module descriptions and suites are present.
