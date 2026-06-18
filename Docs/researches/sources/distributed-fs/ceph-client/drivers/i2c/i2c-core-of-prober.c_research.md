# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of-prober.c

Purpose: OF component prober for boards that describe multiple possible drop-in I2C components as disabled or `fail-needs-probe`. It powers shared resources, probes candidate addresses, and enables the responding device-tree node with a persistent changeset.

Important APIs: `i2c_of_probe_component()` is the main exported namespace API. Simple helper exports include `i2c_of_probe_simple_enable()`, `i2c_of_probe_simple_cleanup_early()`, `i2c_of_probe_simple_cleanup()`, and `i2c_of_probe_simple_ops`. Important data contracts come from `struct i2c_of_probe_cfg`, `struct i2c_of_probe_ops`, and `struct i2c_of_probe_simple_ctx`.

Control flow: the prober finds the named component type, validates that it is under an available I2C node, no-ops if a candidate is already enabled, obtains the adapter, runs optional enable callbacks, then SMBus-reads each candidate `reg` address. On the first responding device it releases exclusive GPIOs early if requested, updates the node status to `okay`, applies the changeset, runs cleanup, and drops the adapter reference.

State and persistence: successful node enablement is persistent for the running kernel because the `of_changeset` is intentionally leaked after apply. Simple helper state stores optional regulator and GPIO descriptors in the caller-provided context only during probing.

Dependencies and integration: depends on OF dynamic changesets, I2C adapter lookup, SMBus byte reads, regulators, GPIO descriptors, and driver-probe context. It deliberately does not support I2C mux paths yet.

Risks: global node-name assumptions can misidentify unrelated nodes of the same prefix. It assumes non-conflicting addresses and exactly one present component per type. GPIO cleanup ordering matters because the actual client driver may need the same descriptor. A failed or deferred adapter/resource lookup prevents selection.

Test signals: DT overlays with multiple candidates, regulator/GPIO delay options, successful status mutation, no-op reruns after one candidate is enabled, `-EPROBE_DEFER` when the bus is missing, and negative tests for muxed candidates.
