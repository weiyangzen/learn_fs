# sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Makefile

Purpose: kbuild rule for the SCMI-to-IIO sensor bridge.

Important entries: `obj-$(CONFIG_IIO_SCMI) += scmi_iio.o`.

Control flow: selecting `IIO_SCMI` builds one driver object.

State and persistence: no runtime state.

Dependencies and integration: aligns with the SCMI Kconfig symbol and `module_scmi_driver()` implementation in `scmi_iio.c`.

Risks and test signals: stale symbol/object names would prevent SCMI IIO support from building. Test signals are successful object build and module alias generation for the SCMI device id table.
