# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/amd_isp4.c

Purpose: `amd_isp4.c` is an AMD ISP4 platform helper that supplies missing firmware-node graph and I2C board information for a camera sensor, currently OV05C10. It binds ACPI sensor HID `OMNI5C10`, registers a software-node graph representing ISP, I2C, ports, endpoints, and remote endpoint links, then instantiates the sensor I2C client when the AMD ISP I2C adapter appears.

Important APIs, types, and functions: `struct amdisp_platform_info` holds an `i2c_board_info` template and node group; `struct amdisp_platform` holds copied board info, an I2C bus notifier, an instantiated `i2c_client`, and a mutex. Static `software_node` and `property_entry` objects describe `amd_camera`, `isp4`, `i2c1`, `OMNI5C10`, endpoint bus type, data lanes, link frequencies, and remote endpoint references. Runtime helpers are `prepare_amdisp_platform()`, `instantiate_isp_i2c_client()`, `isp_i2c_bus_notify()`, `try_to_instantiate_i2c_client()`, `amd_isp_probe()`, and `amd_isp_remove()`.

Control flow: probe gets the matched `amdisp_platform_info`, allocates platform state, initializes a mutex, copies board info, registers the software-node group, attaches the sensor software node to board info, registers an I2C bus notifier, stores the root software node in the ACPI companion `driver_data`, scans existing I2C devices, and stores drvdata. Bus notifications instantiate the I2C client when an adapter named `AMDISP_I2C_ADAP_NAME` is added, and clear the pointer if the client is removed. Remove unregisters the notifier, unregisters the I2C client, and unregisters the software-node group.

State and persistence: state is per platform device and devm-managed except the software-node group and I2C client, which are explicitly registered/unregistered. The mutex protects single-client creation and removal notification races. No persistent state is written.

Dependencies and integration points: dependencies include ACPI matching, I2C core, software nodes/property framework, V4L2-style fwnode graph conventions, and `linux/soc/amd/isp4_misc.h` for adapter naming. The driver integrates with sensor and V4L drivers by providing standard firmware properties and endpoint links that firmware omitted.

Risks: node index `src->swnodes[6]` is positional and fragile if the node list changes. `adev->driver_data` is assigned without an explicit null check after `ACPI_COMPANION()`. I2C adapter matching by name is simple but brittle. Remove calls `i2c_unregister_device()` on `i2c_dev` without checking whether a prior bus-remove notification already cleared it, but null is safe for the helper.

Test signals: ACPI match on `OMNI5C10`, successful software-node registration, creation of an `ov05c10` I2C client at address `0x10` when the ISP adapter exists or appears later, correct fwnode graph parsing by camera drivers, and clean notifier/client/node cleanup on unbind.
