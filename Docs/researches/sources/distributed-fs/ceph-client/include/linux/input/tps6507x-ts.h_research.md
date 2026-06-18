<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/tps6507x-ts.h -->
# sources/distributed-fs/ceph-client/include/linux/input/tps6507x-ts.h

Purpose: Defines board initialization data for TPS65070/TPS6507x touchscreen support.

Important APIs/types/functions: `struct touchscreen_init_data` supplies polling period in milliseconds, minimum pressure threshold, and input id vendor/product/version.

Control flow: Driver probe uses the struct to configure polling cadence, touch qualification, and input device identity.

State/persistence: Board data persists for device lifetime; polling and pressure thresholds guide runtime event reporting.

Dependencies/integration: Integrates TPS6507x MFD/I2C touchscreen code and input device registration.

Risks: Too-low pressure thresholds create false touches; too-slow polling harms responsiveness.

Test signals: Poll interval behavior, min-pressure boundary, input id values, and no-touch versus touch transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/tps6507x-ts.h -->
