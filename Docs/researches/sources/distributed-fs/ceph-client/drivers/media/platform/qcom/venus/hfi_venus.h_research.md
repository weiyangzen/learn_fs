# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.h

This header is the public lifecycle interface for the Venus HFI transport backend. It intentionally hides the queue, register, and power-management internals defined in `hfi_venus.c`.

The exported APIs are `venus_hfi_create(struct venus_core *core)`, `venus_hfi_destroy(struct venus_core *core)`, and `venus_hfi_queues_reinit(struct venus_core *core)`. `venus_hfi_create()` allocates transport state and installs HFI ops on the core, `venus_hfi_destroy()` tears it down, and `venus_hfi_queues_reinit()` resets shared queue headers after hardware reset or recovery.

Control flow is driven by the core probe/remove and recovery paths outside this header. Callers only need a `venus_core`; the private `venus_hfi_device` remains opaque through `core->priv`.

The header stores no state. Its dependency is the forward declaration of `struct venus_core`; implementation dependencies are kept private to reduce coupling.

Risks are lifecycle ordering. Destroy must only run after users are quiesced, and queue reinitialization assumes DMA queue memory is still allocated. Test signals include successful core probe, clean module/remove path, recovery/reset path that reinitializes queues, and absence of use-after-free around `core->ops` and `core->priv`.
