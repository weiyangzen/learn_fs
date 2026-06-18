# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-io.h

## Purpose
This header defines cx18 MMIO access wrappers for reliable CX23418 register and encoder-memory operations. It centralizes readback/retry behavior for writes.

## Important APIs, Types, and Functions
Inline APIs include raw and normal `readl/writel`, `writew`, `writeb`, retrying variants, `_noretry` variants, `cx18_writel_expect()`, `cx18_memcpy_fromio()`, register accessors `cx18_write_reg*()` and `cx18_read_reg()`, and encoder-memory accessors `cx18_write_enc()` and `cx18_read_enc()`. It also declares interrupt mask and page helpers implemented in `cx18-io.c`.

## Control Flow
Write helpers loop up to `CX18_MAX_MMIO_WR_RETRIES`, checking readback after each write. `cx18_writel_expect()` waits for a masked expected value rather than raw equality and ignores all-ones reads when that cannot be a valid expected value. Register helpers apply offsets to `cx->reg_mem`; encoder helpers apply offsets to `cx->enc_mem`.

## State and Persistence
The helpers do not hold state but mutate hardware registers and memory. Their retry behavior is a driver-wide reliability policy for suspect MMIO writes.

## Dependencies and Integration Points
The header depends on `cx18-driver.h` for `struct cx18` and retry limits. It is used by nearly every cx18 implementation file, especially firmware, mailbox, GPIO, I2C, IRQ, and A/V code.

## Risks and Edge Cases
Readback after writes can be expensive but is required for reliability on this hardware. `_noretry` variants bypass protection and should be limited to sequences where readback is not valid or upload protocol needs exact timing. Paged encoder memory access still requires callers to manage `cx18_setup_page()`.

## Test Signals
Stress firmware load, repeated register programming, and capture start/stop under high interrupt load. MMIO debug traces or hardware failures after replacing retrying helpers with raw writes would be high-risk signals.
