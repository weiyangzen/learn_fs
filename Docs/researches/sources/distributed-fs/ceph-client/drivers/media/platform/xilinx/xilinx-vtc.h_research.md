# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.h

Purpose: public provider interface for Xilinx VTC consumers. It defines maximum horizontal/vertical sizes, the `struct xvtc_config` timing payload, an opaque `struct xvtc_device`, and get/put/start/stop prototypes.

Important API: `xvtc_of_get(struct device_node *np)` resolves a consumer's `xlnx,vtc` phandle; `xvtc_generator_start()` programs blanking/sync/frame sizes from `xvtc_config`; `xvtc_generator_stop()` disables generation; `xvtc_put()` is a placeholder release hook.

Control flow/state is implemented in `xilinx-vtc.c`. Dependencies are minimal forward declarations, allowing consumers such as TPG to avoid internal register knowledge.

Risks: consumers must populate timing fields consistently and handle `NULL` for no VTC versus `ERR_PTR()` for deferral/error. Test signals are compile coverage for consumers and runtime phandle/provider tests.
