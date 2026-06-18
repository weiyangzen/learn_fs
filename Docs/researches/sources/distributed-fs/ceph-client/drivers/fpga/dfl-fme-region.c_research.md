## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-region.c

Purpose: this platform driver registers FPGA regions for DFL FME ports. Each region connects the FME FPGA manager with the port bridge used for PR isolation.

Important APIs and functions: `fme_region_get_bridges()` converts platform data bridge device into a bridge list entry with `fpga_bridge_get_to_list()`. `fme_region_probe()` gets the manager from platform data, fills `fpga_region_info` with manager, compatibility ID, bridge callback, and private platform data, then registers a full FPGA region. Remove unregisters the region and puts the manager reference.

Control flow: PR management creates one region platform device per implemented port. Region probe may defer until the manager is available. During programming, the FPGA region framework calls `get_bridges`, disables bridge(s), invokes the manager, and then handles bridge release/re-enable according to region flow.

State and persistence: `struct fpga_region` registered by the framework persists for the platform device lifetime. It holds a reference to the manager and uses manager compatibility ID for bitstream compatibility checks.

Dependencies and integration: it depends on FPGA manager and region frameworks, bridge framework indirectly, and platform data from `dfl-fme-pr.c`. It is one of the child drivers selected by `FPGA_DFL_FME_REGION`.

Risks: if the manager is absent, probe returns `-EPROBE_DEFER`; missing bridge devices cause programming-time bridge acquisition failures. Region private data points to platform data copied into the platform device, so creator and consumer layouts must remain synchronized. Only one bridge device is added per region.

Test signals: test probe deferral until manager driver loads, successful region registration with compatibility ID, bridge acquisition failure, remove ordering relative to manager, and PR programming through the region.
