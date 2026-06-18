<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_protocol.h

Purpose: This header is the client-facing contract for the Texas Instruments System Control Interface firmware protocol. It does not implement mailbox transport itself; it defines version data, the opaque `ti_sci_handle`, operation tables, request parameter structs, resource descriptors, and build-time stubs used by TI SoC drivers.

Important APIs/types/functions: `struct ti_sci_handle` aggregates `ti_sci_ops`, including core reboot, device lifecycle, clock, low-power, resource-management, IRQ routing, ring accelerator, PSI-L, UDMAP, and processor-control operations. UDMAP/ring config structs use `valid_params` bitmasks such as `TI_SCI_MSG_VALUE_RM_RING_*_VALID` and `TI_SCI_MSG_VALUE_RM_UDMAP_*_VALID` to describe partial firmware updates. Public helpers include `ti_sci_get_handle()`, phandle lookup variants, devm-managed lookup, resource allocation/release, and OF resource acquisition.

Control flow: Consumers first acquire a handle, then call function pointers under `handle->ops`. The header encodes protocol sequencing obligations rather than logic: device and clock `get_*` calls must be balanced with `put_*`, resources are allocated from `ti_sci_resource` bitmaps, and processor ownership flows through request/release/handover before configuration/control.

State and persistence: Runtime state is external to the header: firmware owns SoC resource state; client drivers own usage balancing; `ti_sci_resource` persists local allocation bitmaps guarded by a raw spinlock. Context-loss counters and requested/current state calls are exposed for recovery after power transitions.

Dependencies/integration: Integrates with the device model, OF phandles, TI firmware, clock/reset/device drivers, IRQ domains, DMA/ring accelerator users, and remote processor/boot code. When `CONFIG_TI_SCI_PROTOCOL` is disabled, inline stubs return `-EINVAL`, `ERR_PTR(-EINVAL)`, zero, or `TI_SCI_RESOURCE_NULL`.

Risks and test signals: Main risks are unbalanced get/put calls, incorrect `valid_params` masks, stale firmware ABI assumptions, invalid resource subtype IDs, and using the stub path as if it were functional. Test signals include TI SCI probe logs, resource exhaustion behavior, handle acquisition error paths, reset/clock state readbacks, UDMAP/ring programming validation, and suspend/resume context-loss recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_protocol.h -->
