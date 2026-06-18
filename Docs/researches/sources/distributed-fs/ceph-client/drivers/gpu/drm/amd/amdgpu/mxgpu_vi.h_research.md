# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_vi.h

Purpose: this header defines the legacy VI MxGPU mailbox interface and exported entry points used by `mxgpu_vi.c` and `vi.c`. It captures the smaller pre-Navi PF/VF protocol for full-GPU access and FLR coordination and declares the VI virtualization operations table.

Important APIs and types: `VI_MAILBOX_TIMEDOUT` and `VI_MAILBOX_RESET_TIME` define polling and reset timing constants. `enum idh_request` contains the VI request IDs for GPU init access, release init access, fini access, release fini access, reset access, and VF error logging. `enum idh_event` contains mailbox receive values for clearing the message buffer, ready-to-access, FLR notification, FLR completion, and text messages. Externs include `xgpu_vi_virt_ops`, `xgpu_vi_init_golden_registers()`, `xgpu_vi_mailbox_set_irq_funcs()`, `xgpu_vi_mailbox_add_irq_id()`, `xgpu_vi_mailbox_get_irq()`, and `xgpu_vi_mailbox_put_irq()`.

Control flow: the header is declarative. VI ASIC setup code calls the golden-register initializer during virtualized device setup, installs IRQ source functions, registers mailbox IRQ IDs, then uses `xgpu_vi_virt_ops` callbacks for request/release/reset/wait-reset behavior. The corresponding C file writes these request values into mailbox DW0 and waits for the event values in receive DW0.

State and persistence: the header owns no state. Its constants parameterize runtime polling and protocol behavior in `mxgpu_vi.c`. The declared functions operate on `struct amdgpu_device` state, IRQ source tables, workqueue state, and mailbox MMIO registers, all of which are volatile runtime state.

Dependencies and integration: consumers require AMDGPU device and virtualization type declarations. Numeric values must match the PF/hypervisor protocol implemented for VI MxGPU. `vi.c` is the primary integration point, assigning the ops table and invoking the IRQ/golden-register helpers during VI ASIC initialization and teardown.

Risks: this protocol is intentionally much smaller than the NV mailbox protocol; generic callers cannot assume init-data or RAS callbacks exist. Changing enum values or timeout constants can break compatibility with older PF implementations. The header does not declare register offsets, so it relies on `mxgpu_vi.c` including the appropriate VI register headers for mailbox fields and masks.

Test signals: compile tests should verify `vi.c` and `mxgpu_vi.c` agree on the declarations. Runtime signals include successful VI SR-IOV VF init/fini/reset access, expected timeout behavior at `VI_MAILBOX_TIMEDOUT`, correct IRQ setup/teardown via the exported helpers, and absence of calls to unsupported newer virtualization callbacks.
