## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-pseries.c

Purpose: provides the pSeries VIO backend for NX 842 compression. It submits 842 operations through `vio_h_cop_sync`, manages OF-derived constraints and live property updates, registers sysfs counters, exposes optional NX-GZIP capability data, and registers the `842` scomp algorithm through the shared `nx-842.c` layer.

Important types and functions: `struct nx842_devdata` stores the VIO device, counters, and OF limits. `struct nx842_workmem` contains pHyp scatterlists and `nx_csbcpb`. `nx842_pseries_compress` and `nx842_pseries_decompress` are backend function pointers. OF helpers include `nx842_OF_set_defaults`, `nx842_OF_upd_status`, `nx842_OF_upd_maxsglen`, `nx842_OF_upd_maxsyncop`, `nx842_OF_upd`, and `nx842_OF_notifier`. Probe/remove are `nx842_probe` and `nx842_remove`.

Control flow: init confirms an `ibm,compression` node, initializes RCU `devdata`, queries VAS/NX-GZIP capabilities, registers the VIO driver, and registers a pSeries VAS userspace API. Probe allocates devdata/counters, publishes them with RCU, registers the OF reconfig notifier, validates current OF properties, registers the scomp algorithm, and creates sysfs groups. Each compression operation checks alignment/length constraints, builds direct or indirect pHyp scatterlists, fills a `vio_pfo_op`, calls `vio_h_cop_sync`, validates CSB status, updates counters/histograms, and returns processed output length.

State and persistence: runtime state is global RCU-protected `devdata`, constraints maximum updated from OF, atomic counters and latency histograms, sysfs attributes, VAS capability globals, and the registered scomp algorithm. OF reconfiguration can replace devdata live; there is no on-disk state.

Dependencies: IBM VIO, hypervisor calls, OF reconfiguration notifier, VAS capability query APIs, sysfs, RCU, atomic counters, shared NX CSB/CPB structs, and `nx-842.c` exported context/operation functions.

Risks: `nx842_OF_upd` uses a property-name filter with ORed `strncmp` conditions that appears likely to treat most updates as uninteresting only if all names match, which warrants review. Probe error paths after crypto/sysfs registration must avoid leaked registration. Exit unregisters the scomp algorithm even though remove also does, so double-unregister ordering should be tested. RCU replacement must preserve counter ownership and not race with active operations. Hardware constraints are mutable and feed the shared compressor.

Test signals: VIO probe/remove, OF property update/reconfig tests for status/max-sg/max-sync, scomp vectors, sysfs counter and histogram reads, invalid alignment/length rejection, pHyp hcall error mapping, CSB error-code mapping, RCU race tests under concurrent compression, and init/exit with VAS capability present/absent.
