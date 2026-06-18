# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c

## Purpose
`cz_ih.c` implements the Carrizo/VI interrupt handler IP block for AMDGPU. It configures the hardware interrupt ring buffer, provides IH ring callbacks for write-pointer retrieval, interrupt-vector decoding, and read-pointer updates, and exposes the `cz_ih_ip_block` lifecycle hooks used by VI ASIC initialization.

## Important APIs, Types, and Functions
The exported object is `const struct amdgpu_ip_block_version cz_ih_ip_block`, with type `AMD_IP_BLOCK_TYPE_IH`, version `3.0.0`, and `cz_ih_ip_funcs`. The internal `amd_ip_funcs` implementation covers early init, software init/fini, hardware init/fini, suspend/resume, idle wait, soft reset, and clock/power gating stubs.

Core functions are `cz_ih_irq_init()`, `cz_ih_irq_disable()`, `cz_ih_get_wptr()`, `cz_ih_decode_iv()`, and `cz_ih_set_rptr()`. `cz_ih_funcs` installs these as `amdgpu_ih_funcs`. `cz_ih_sw_init()` allocates the main IH ring at 64 KiB and the software IH ring at `IH_SW_RING_SIZE`, then calls `amdgpu_irq_init()`. `cz_ih_early_init()` adds the IRQ domain and installs `adev->irq.ih_funcs`.

## Control Flow
Hardware init disables interrupts, programs dummy-page and interrupt-control registers, writes the IH ring GPU base address, computes ring size with `order_base_2(ring_size / 4)`, enables overflow handling and write-pointer writeback, sets writeback addresses, clears RPTR/WPTR, optionally arms MSI rearm behavior, calls `pci_set_master()`, and enables interrupts. Hardware fini disables interrupts and waits briefly.

`cz_ih_get_wptr()` reads the little-endian write pointer from writeback memory. For the software ring it returns directly. For hardware, it checks the overflow bit, re-reads `mmIH_RB_WPTR` to avoid stale writeback state, warns on real overflow, advances `ih->rptr` to `(wptr + 16) & ptr_mask`, toggles `WPTR_OVERFLOW_CLEAR`, and returns `wptr & ptr_mask`. `cz_ih_decode_iv()` reads four dwords at `ih->rptr >> 2`, decodes legacy client, source id, source data, ring id, VMID, and PASID, then advances RPTR by 16 bytes. `cz_ih_set_rptr()` writes `mmIH_RB_RPTR`.

## State and Persistence Behavior
The file mutates in-memory AMDGPU interrupt state (`adev->irq.ih.enabled`, `adev->irq.ih.rptr`, `adev->irq.ih_soft.enabled`, and `adev->irq.ih_funcs`) and IH hardware registers. Ring memory and writeback memory are allocated by common IH helpers; this code only programs their addresses into the device. No state is persisted beyond the device lifecycle. Suspend disables the block and resume reinitializes it.

## Dependencies and Integration Points
Dependencies include `amdgpu_ih.h`, `amdgpu_irq` core helpers, PCI bus mastering, VI OSS/BIF register headers, MMIO helpers `RREG32`/`WREG32`, and field macros from generated mask headers. `vi.c` adds `cz_ih_ip_block` for Carrizo/Stoney-style VI APUs. The IRQ processing core later calls through `adev->irq.ih_funcs` to fetch WPTR, decode IVs, and commit RPTR.

## Risks
Incorrect ring size/address programming can make interrupts disappear or overwrite memory. Overflow handling deliberately skips to the last non-overwritten vector; that preserves forward progress but can drop interrupts. Decode layout assumes 16-byte legacy IV entries; incompatible hardware formats need different IH implementations. `cz_ih_set_clockgating_state()` and `cz_ih_set_powergating_state()` are TODO stubs, so power-management expectations are minimal. Timeout/reset paths depend on `SRBM_STATUS.IH_BUSY` being reliable.

## Test Signals
Signals include successful IRQ domain creation, ring allocation, MSI/non-MSI interrupt delivery, correct handling of IH writeback, no spurious overflow warnings under normal load, valid decoded VMID/PASID/source IDs, suspend/resume interrupt recovery, and `cz_ih_wait_for_idle()` returning without timeout. Fault-injection or stress tests should cover overflow behavior, soft reset when IH busy, and both hardware and software IH rings.
