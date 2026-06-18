# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_ih.c

Purpose: Southern Islands interrupt handler ring IP block. It programs the IH ring, decodes 16-byte legacy interrupt vectors, tracks read/write pointers, handles overflow, and exposes the IH lifecycle to amdgpu core.

Important APIs, types, and functions: exports `si_ih_ip_block` and installs `si_ih_funcs` with `get_wptr`, `decode_iv`, and `set_rptr`. Main functions include `si_ih_irq_init()`, `si_ih_enable_interrupts()`, `si_ih_disable_interrupts()`, `si_ih_get_wptr()`, `si_ih_decode_iv()`, `si_ih_soft_reset()`, and IP callbacks for early/sw/hw init and suspend/resume.

Control flow: software init allocates the hardware IH ring and soft IH ring, then initializes amdgpu IRQ support. Hardware init disables interrupts, programs dummy page, IH base, writeback address, ring size, read/write pointers, MSI rearm behavior, enables bus mastering, and enables interrupts. During interrupt processing, `get_wptr` reads writeback memory and recovers from overflow by advancing `rptr`; `decode_iv` maps four dwords into legacy client/source/ring/vmid fields and advances by 16 bytes.

State and persistence: state is in `adev->irq.ih`, `adev->irq.ih_soft`, IH ring BO memory, writeback memory, and IH/MMIO registers. No disk state exists.

Dependencies and integration points: depends on PCI bus mastering, amdgpu IRQ core, `amdgpu_ih_ring_init`, generated OSS register definitions, and SDMA/GFX clients that emit legacy IRQ source IDs.

Risks and test signals: overflow handling drops entries by moving `rptr` near `wptr`; repeated overflow means interrupt consumers are too slow. `set_rptr` always writes hardware `IH_RB_RPTR`, so callers must avoid using it for soft ring semantics unless core guards that path. Test signals include MSI/non-MSI interrupt delivery, SDMA trap IRQs, ring overflow warning behavior, suspend/resume interrupt recovery, and idle/soft-reset paths.
