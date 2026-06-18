
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dma.h

Purpose: legacy ISA 8237 DMA controller constants and inline programming helpers.

Important APIs and control flow: defines DMA zones, controller I/O ports, page/address/count registers, and mode bits. Optional `claim_dma_lock()`/`release_dma_lock()` guard programming. Helpers enable/disable channels, clear the flip-flop, set mode/page/address/count, and read residue. Channel 0-3 byte mode and 5-7 word mode differ in address/count shifting and page-register masking.

State, dependencies, and risks: state is hardware DMA controller registers, page registers, flip-flop position, and optional `dma_spin_lock`. Dependencies include port I/O, ISA DMA API, and physical address constraints below 16 MiB. Risks include crossing 64K/128K boundaries, programming without the DMA lock, odd byte counts on 16-bit channels, and legacy hardware assumptions. Test signals are ISA DMA users, floppy/sound legacy drivers, DMA API debug, and emulator hardware tests.
