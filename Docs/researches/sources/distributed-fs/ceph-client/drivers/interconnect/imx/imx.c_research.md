# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.c

Purpose: shared i.MX provider implementation. It turns SoC node tables into interconnect providers, optionally programs NoC priority registers, and maps bandwidth votes into PM QoS minimum-frequency requests.

Important APIs/types/functions: exports `imx_icc_register()` and `imx_icc_unregister()`. Private flow uses `imx_icc_node_set()`, `imx_icc_set()`, `imx_icc_node_init_qos()`, `imx_icc_node_add()`, and `imx_icc_register_nodes()`.

Control flow: registration allocates onecell data, initializes provider callbacks, maps NoC MMIO if settings exist, creates nodes, initializes PM QoS for adjustable nodes, links nodes, and registers the provider. Votes program fixed NoC priority/mode for configured nodes and update frequency constraints from `(avg + peak) * bw_mul / bw_div`.

State and persistence: per-node data stores descriptors, settings, QoS device/request, and provider pointer. PM QoS requests and hardware registers persist until vote changes or unregister.

Dependencies/integration: OF phandles, platform devices, MMIO, PM QoS, core interconnect APIs.

Risks and test signals: test deferred probe, disabled phandles, NoC mapping failure, duplicate IDs, frequency overflow, unsupported modes, partial cleanup, and `put_device()` lifetime assumptions.
