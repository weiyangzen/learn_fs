# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Makefile

Purpose: kbuild rules for ChromeOS EC IIO common and client drivers.

Important entries: `cros-ec-sensors-core-objs` links `cros_ec_sensors_core.o` and `cros_ec_sensors_trace.o` into the core module. The feature objects are gated by `CONFIG_IIO_CROS_EC_SENSORS_CORE`, `CONFIG_IIO_CROS_EC_SENSORS`, `CONFIG_IIO_CROS_EC_SENSORS_LID_ANGLE`, and `CONFIG_IIO_CROS_EC_ACTIVITY`.

Control flow: selecting the core builds a composite object that includes both implementation and tracepoint definition; selecting client drivers builds standalone platform drivers that import the core exports.

State and persistence: no runtime state. It determines module composition and linkage boundaries.

Dependencies and integration: must align with local Kconfig symbols and source exports from `cros_ec_sensors_core.c`. Including tracepoint C in the core object ensures `CREATE_TRACE_POINTS` is compiled exactly once.

Risks and test signals: missing trace object causes unresolved trace symbols; mismatched object names break module builds. Test signals are module build, modpost symbol resolution, and tracepoint availability when the core is loaded.
