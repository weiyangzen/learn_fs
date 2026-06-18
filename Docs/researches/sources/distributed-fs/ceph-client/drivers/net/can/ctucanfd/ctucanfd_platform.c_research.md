# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/ctucanfd_platform.c

Purpose: OF platform wrapper for CTU CAN FD IP cores in FPGA/SoC systems.

Important APIs and functions: `ctucan_platform_probe()` devm-maps the first memory resource, obtains the IRQ, assumes four TX buffers, and delegates to `ctucan_probe_common()` with runtime PM enablement and a callback that stores the netdev in platform driver data. `ctucan_platform_remove()` unregisters the candev, disables runtime PM, deletes NAPI, and frees the CAN netdev. PM operations reuse `ctucan_suspend()` and `ctucan_resume()`.

Control flow and state: probe is short and relies on devm resource ownership for MMIO mapping. All runtime controller behavior is delegated to the base driver. Persistent state is the platform drvdata netdev and `struct ctucan_priv` initialized by the common probe. Dependencies include OF matching for `ctu,ctucanfd-2` and `ctu,ctucanfd`, platform IRQ/resource helpers, runtime PM, and SocketCAN common registration. Risks include hard-coded TX buffer count pending future DT property support, remove assuming drvdata is non-NULL, and clock acquisition being deferred to common probe when `can_clk_rate` is zero. Test signals include OF probe, clock lookup in common code, PM enable/disable symmetry, and successful NAPI cleanup on remove.
