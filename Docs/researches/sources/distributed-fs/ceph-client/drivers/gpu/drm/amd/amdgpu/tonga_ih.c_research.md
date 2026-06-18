# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c

## Purpose

`tonga_ih.c` implements the AMDGPU interrupt handler IP block for Tonga/VI-generation hardware using an IH ring buffer. It allocates and initializes interrupt rings, programs IH registers, decodes interrupt vectors, manages read/write pointers, supports suspend/resume, and participates in soft reset handling.

## Important APIs, Types, And Functions

The exported object is `tonga_ih_ip_block`. `tonga_ih_irq_init()` programs `INTERRUPT_CNTL`, IH ring base, ring size, writeback, VMID, MSI rearm behavior, writeback address, RPTR/WPTR reset, optional doorbell RPTR, bus mastering, and enables interrupts. `tonga_ih_get_wptr()` reads writeback memory, detects overflow, repositions `rptr`, and clears overflow in `IH_RB_CNTL`. `tonga_ih_decode_iv()` converts four dwords into `amdgpu_iv_entry` fields and advances `rptr` by 16 bytes. `tonga_ih_set_rptr()` writes RPTR through doorbell or register. IP lifecycle functions wrap ring allocation, IRQ domain setup, hardware init/fini, idle waits, and soft reset.

## Control Flow

Early init creates the IRQ domain and installs IH function pointers. Software init allocates the hardware IH ring and software IH ring, enables doorbell mode, and initializes AMDGPU IRQ core. Hardware init disables interrupts, programs the ring, enables PCI bus mastering, and enables interrupts. IRQ processing outside this file calls the installed `get_wptr`, `decode_iv`, and `set_rptr` callbacks. Soft reset checks `SRBM_STATUS.IH_BUSY`, stores an SRBM reset mask, disables IH, toggles `SRBM_SOFT_RESET`, and reinitializes IH afterward.

## State And Persistence Behavior

Driver state lives in `adev->irq.ih`, `adev->irq.ih_soft`, `adev->irq.ih_funcs`, and `adev->irq.srbm_soft_reset`. Hardware state includes IH control registers, ring base, writeback address, doorbell RPTR, RPTR/WPTR, interrupt enable bits, and SRBM soft-reset bits. Overflow recovery deliberately skips to the last not-overwritten vector estimate, so some interrupt events may be lost but processing can resume.

## Dependencies And Integration Points

The file depends on OSS 3.0 and BIF 5.1 register headers, AMDGPU IRQ core, IH ring helpers, PCI bus mastering, doorbell writes, MSI behavior, and generic IP block lifecycle management. It feeds decoded IVs into the broader AMDGPU interrupt dispatch path.

## Risks And Test Signals

Risks include ring-size/order mismatches, writeback endianness, overflow handling that drops events, incorrect doorbell index programming, MSI rearm differences, and soft reset races with live interrupt writes. Tests should cover IRQ domain creation, ring allocation/free, MSI and non-MSI operation, doorbell and register RPTR modes, interrupt storm/overflow recovery, suspend/resume, soft reset while IH busy, idle timeout behavior, and decoded IV dispatch.
