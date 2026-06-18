<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.c

Purpose: platform child-driver for individual encoder/decoder firmware cores. It maps reserved memory and registers, initializes iface shared memory, handles firmware loading/boot/reset/shutdown, manages runtime PM and mailbox lifetime, allocates instance IDs, and owns core-level DMA helpers.

Important APIs/functions: exported `csr_writel()`, `csr_readl()`, `vpu_alloc_dma()`, `vpu_free_dma()`, `vpu_core_set_state()`, `vpu_request_core()`, `vpu_release_core()`, `vpu_inst_register()`, `vpu_inst_unregister()`, `vpu_core_find_instance()`, `vpu_get_resource()`, `vpu_core_driver_init()`, and `vpu_core_driver_exit()`. Probe/remove are `vpu_core_probe()` and `vpu_core_remove()`.

Control flow: probe reads reserved boot/RPC regions, remaps them, validates uncached RPC placement, derives log/activity subregions, maps CSR registers, initializes mailbox and iface private data, configures system/log buffers, enables runtime PM, registers the core with the parent VPU, and creates debugfs. `vpu_request_core()` selects a deinitialized or least-used active core, resumes it, boots/restores if needed, and increments `request_count`. Instance registration acquires an instance bit and optional activity slice. Suspend snapshots active firmware, cancels work, and releases parent references; resume reboots or resets active cores and resumes queued message work.

State and persistence: `struct vpu_core` persists firmware/RPC/log/activity memory descriptors, instance list/mask, request count, supported instance count, firmware version, state, hang mask, mailbox handles, FIFOs, workqueues, and iface pointer. State is memory-only and rebuilt at probe/boot.

Dependencies and integration: depends on reserved-memory DT bindings, platform driver matching (`nxp,imx8q-vpu-encoder`/decoder), request_firmware, dma coherent allocations, pm_runtime, mailbox setup, iface ops from `vpu_rpc.c`, and parent `vpu_dev` from `vpu_drv.c`.

Risks: `vpu_core_parse_dt()` can leak memremap mappings on later validation failure. Pointer arithmetic on `void *` is GCC-extension style. Runtime PM calls sometimes ignore negative resume return values. Hang recovery is tied to unregister when no instances remain. Correct reserved-memory layout and uncached attributes are mandatory.

Test signals: probe/remove with valid and invalid DT reserved-memory regions, firmware too large, boot timeout, runtime suspend/resume with active sessions, core hang/reset after command timeout, multi-instance allocation bounds, mailbox request failure, and debugfs core status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.c -->
