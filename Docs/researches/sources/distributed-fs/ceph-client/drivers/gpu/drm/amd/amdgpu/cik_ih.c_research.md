# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.c

Purpose: implements the CIK interrupt handler (IH) IP block. CIK writes interrupt vectors into a GPU-accessible ring buffer; this file initializes that ring, enables/disables hardware interrupt delivery, decodes 128-bit interrupt vectors, handles ring pointer management and overflow, and exposes IH lifecycle callbacks to the AMDGPU IP framework.

Important APIs and functions: `cik_ih_irq_init()` programs IH registers, ring base, ring size, writeback pointer address, MSI-dependent control bits, and enables interrupts. `cik_ih_get_wptr()` reads the write pointer from writeback memory and handles overflow. `cik_ih_decode_iv()` decodes source id, source data, ring id, VMID, and PASID from the current ring entry and advances rptr by 16 bytes. `cik_ih_set_rptr()` writes the hardware read pointer. IP callbacks include early/sw/hw init/fini, suspend/resume, idle wait, soft reset, and no-op gating hooks. `cik_ih_ip_block` exports this as an IH block version 2.0.

Control flow: early init adds the IRQ domain and installs IH function pointers. SW init allocates the hardware IH ring and software IH ring, then initializes AMDGPU IRQ infrastructure. HW init disables interrupts, programs ring and interrupt control registers, sets writeback, clears pointers, enables PCI bus mastering, enables interrupts, and marks the software IH ring enabled if allocated. Interrupt processing elsewhere calls the function table to get wptr, decode entries until rptr catches wptr, and commit rptr.

State and persistence: mutates `adev->irq.ih` and `adev->irq.ih_soft` ring fields (`enabled`, `rptr`, writeback pointers), hardware IH registers, and IRQ domain/core state. Overflow handling intentionally advances `ih->rptr` to a recent vector boundary and clears the hardware overflow flag.

Dependencies and integration points: depends on AMDGPU IRQ and IH core helpers, Linux PCI bus mastering, BIF/OSS register definitions, writeback memory, and the AMDGPU IP block framework. SDMA/GFX/display interrupt sources are decoded through this common vector path and dispatched by AMDGPU IRQ code.

Risks: IH pointer units are bytes while ring array indexing is dwords, so off-by-unit errors are dangerous. Overflow recovery drops old vectors by moving rptr, which can lose fence/hotplug/error events. Writeback pointer memory must be coherent and correctly addressed. Soft reset only toggles IH if SRBM reports busy. MSI-dependent `RPTR_REARM` behavior must match interrupt mode.

Test signals: IRQ domain initialization, module load without IH timeout, interrupt storm/overflow logging, fence completion from SDMA/GFX interrupts, hotplug interrupt delivery, suspend/resume IRQ recovery, and successful soft reset under fault injection.
