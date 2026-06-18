<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus.h

Purpose: This is the umbrella kernel Greybus API header. It includes the Greybus manifest, protocol, host-device, SVC, control, module, interface, bundle, connection, and operation headers and defines the bus-driver interface.

Important APIs/types/functions: `struct greybus_driver` contains name, bundle `probe`, `disconnect`, id table, and embedded `device_driver`. Matching helpers include `GREYBUS_DEVICE()`, `GREYBUS_DEVICE_CLASS()`, and `GREYBUS_ID_MATCH_DEVICE`. Driver registration uses `greybus_register_driver()`, `greybus_deregister_driver()`, `greybus_register()`, `greybus_deregister()`, and `module_greybus_driver()`. Runtime helpers set/get bundle driver data. Constants define Greybus version and CPort limits. `cport_id_valid()` checks CPort IDs against the host device.

Control flow, state, and persistence: Greybus drivers bind to `gb_bundle` devices via the Linux driver core. Probe typically creates protocol connections and stores driver state in bundle drvdata; disconnect tears those resources down. Core objects persist as Linux devices linked by host, module, interface, bundle, connection, and operation lifetimes.

Dependencies/integration: This header is kernel-only and integrates with Linux modules, driver core, PM runtime, IDR/IDA, debugfs, and all Greybus subheaders.

Risks and test signals: Bundle matching must use correct class/vendor/product flags. CPort validation relies on host `num_cports`. Tests should cover module registration/unregistration, driver probe/disconnect paths, disabled Greybus handling, debugfs init/cleanup, and invalid CPort IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus.h -->
