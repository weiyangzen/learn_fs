# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu-bridge.c

Purpose: creates software-node firmware graphs for Intel IPU camera sensors on ACPI systems whose firmware lacks native fwnode graph data. It also handles IVSC/MEI CSI routing and optional VCM lens instantiation.

Important APIs/types/functions: exported namespace APIs are `ipu_bridge_parse_ssdb()`, `ipu_bridge_instantiate_vcm()`, and `ipu_bridge_init()`. Static data lists supported sensor ACPI HIDs and link frequencies, upside-down DMI quirks, property names, VCM types, and IVSC ACPI IDs. Key helpers discover IVSC devices, read SSDB buffers, parse rotation/orientation, create property entries and software nodes, register node groups, connect sensors, defer until IVSC is ready, and unregister on failure.

Control flow: consumer IPU drivers call `ipu_bridge_init()` with a sensor-fwnode parser. If the IPU already has a graph, bridge exits. Otherwise it waits for IVSC readiness, registers an IPU HID software node, iterates supported sensor HIDs, parses SSDB, creates sensor/IPU/IVSC/VCM graph nodes, attaches secondary fwnodes to ACPI devices, and sets the IPU secondary fwnode. Sensor drivers may call `ipu_bridge_instantiate_vcm()` to queue work that creates an I2C VCM client with runtime-PM linkage.

State and persistence: allocated `struct ipu_bridge` and software nodes intentionally survive like device-side firmware description during driver lifetime; VCM clients may persist across module reloads. ACPI and device references are held and released by unregister paths.

Dependencies/integration: integrates ACPI, DMI, I2C, platform bus, MEI client bus, PM runtime, software nodes, V4L2 fwnode parsing, and media IPU bridge headers.

Risks and test signals: risks include fwnode lifetime ownership, recursive graph checks, IVSC device readiness/defer logic, SSDB layout assumptions, DMI quirks, and asynchronous VCM creation races. Test on systems with/without existing graphs, with IVSC present/absent, with supported sensors and VCMs, across module reload, and by verifying media graph endpoints, lane counts, link frequencies, orientation, and runtime PM links.
