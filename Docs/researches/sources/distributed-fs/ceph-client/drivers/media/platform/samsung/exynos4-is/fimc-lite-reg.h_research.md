# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.h

## Purpose
Defines FIMC-LITE register offsets, bit fields, and the MMIO helper API implemented by `fimc-lite-reg.c`.

## Important APIs, Types, and Functions
Key definitions cover `CISRCSIZE`, `CIGCTRL`, `CIIMGCPT`, crop offsets, DMA format/address registers, interrupt status bits, and `CIFCNTSEQ`. The helper prototypes expose reset, IRQ, bus, format, window, DMA, test-pattern, dump, and buffer-mask operations.

## Control Flow
The main driver uses these constants to program source geometry, interrupt enables, capture enable, output DMA mode, and per-buffer sequence masks. The inline `flite_hw_set_dma_buf_mask()` writes the active DMA-buffer mask directly.

## State and Persistence
The header has no software state. It documents volatile register layout and bit semantics used to reconstruct hardware state after each reset or resume.

## Dependencies and Integration Points
Includes `linux/bitops.h` and `fimc-lite.h`, binding the register API to `struct fimc_lite`, `struct flite_frame`, `struct flite_buffer`, and `struct fimc_source_info`.

## Risks and Edge Cases
Several masks assume 13- or 14-bit geometry fields; callers must clamp dimensions before register writes. `FLITE_REG_CIGCTRL_IRQ_*` bits are disable-mask bits, so inverted semantics can easily enable the wrong interrupt set.

## Test Signals
Compile-test all helper declarations against `fimc-lite.c`, confirm register constants match hardware manuals for Exynos4/5 variants, and inspect IRQ-mask programming for DMA versus ISP output modes.
