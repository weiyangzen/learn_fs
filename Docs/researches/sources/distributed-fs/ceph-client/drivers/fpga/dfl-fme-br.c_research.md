## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-br.c

Purpose: this platform driver adapts a DFL AFU port into an FPGA bridge used by FME partial reconfiguration regions.

Important APIs and functions: `struct fme_br_priv` stores platform data, cached port ops, and cached port feature data. `fme_bridge_enable_set()` lazily finds the target port by ID in the DFL container, obtains `dfl_fpga_port_ops`, and calls its `enable_set()` callback. Probe registers an FPGA bridge named `DFL FPGA FME Bridge`.

Control flow: the PR management feature creates one bridge platform device per implemented port. When the FPGA region disables or enables bridges, this driver resolves the DFL port and delegates to the AFU driver's reset-based enable implementation. Remove unregisters the bridge and releases the port ops reference if acquired.

State and persistence: cached `port_fdata` and `port_ops` persist after first bridge use. The actual bridge state is the AFU port reset state managed by the port driver.

Dependencies and integration: it depends on DFL container port lookup, AFU `dfl_fpga_port_ops`, FPGA bridge framework, and platform data from `dfl-fme-pr.c`.

Risks: lazy lookup means probe can succeed even if the target port is not yet available; first enable may return `-ENODEV` or `-ENOENT`. Cached `port_fdata` lifetime depends on DFL container lifetime. `enable_show` is not implemented, so users cannot read state through bridge ops.

Test signals: test bridge enable before/after AFU port driver registration, missing port ID, missing `enable_set`, PR flows disabling and re-enabling ports, and remove after lazy ops acquisition.
