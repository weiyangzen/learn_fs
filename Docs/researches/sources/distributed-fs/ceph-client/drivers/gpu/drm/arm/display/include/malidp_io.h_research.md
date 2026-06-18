# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_io.h

Purpose: provides small MMIO helpers for Mali/Komeda display register access using byte offsets over a `u32 __iomem *` base.

Important APIs/types/functions: `malidp_read32()`, `malidp_write32()`, `malidp_write64()`, `malidp_write32_mask()`, and `malidp_write_group()`. The helpers shift register byte offsets by two to address 32-bit words and wrap Linux `readl()`/`writel()`.

Control flow: register users compute byte offsets from hardware headers, then call these helpers for scalar, masked, 64-bit split, or contiguous table writes. `malidp_write32_mask()` reads the current register, clears mask bits, and ORs the supplied value.

State and persistence: all state is hardware MMIO state. There is no software cache, locking, or barrier beyond the semantics of `readl()`/`writel()`.

Dependencies/integration: depends on `<linux/io.h>`. Used broadly by D71 component/device code for GCU, LPU, CU, DOU, layer, scaler, and timing registers.

Risks: callers must pass byte offsets and already-mask `v` for masked writes; `v | tmp` can set bits outside `m` if not pre-masked. `malidp_write64()` assumes low then high register order. No endianness or posted-write verification is provided. Test signals: register trace/dump comparisons, sparse `__iomem` checks, hardware readback after masked writes, and table-programming tests for gamma/scaler coefficients.
