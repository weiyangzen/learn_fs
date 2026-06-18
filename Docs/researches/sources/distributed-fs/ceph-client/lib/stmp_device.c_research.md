# sources/distributed-fs/ceph-client/lib/stmp_device.c

## Purpose
Provides a reset helper for STMP-style hardware blocks, primarily used by ARM/Freescale i.MX/SoC drivers that expose soft-reset and clock-gate control bits at a register base.

## APIs, Control Flow, and State
The exported API is `stmp_reset_block(void __iomem *reset_addr)`. It manipulates `STMP_MODULE_SFTRST` and `STMP_MODULE_CLKGATE` through STMP set/clear register offsets. Control flow clears and polls soft reset, clears clock gate, sets soft reset, polls for clock gate to assert, clears and polls soft reset again, then clears and polls clock gate. `stmp_clear_poll_bit()` writes to the clear register, delays one microsecond, and spins up to a fixed timeout for the bit to clear. Failures log an error and return `-ETIMEDOUT`.

State is entirely device register state. The helper stores no kernel-global data.

## Dependencies, Integration, Risks, and Tests
Depends on MMIO `readl()`/`writel()`, `udelay()`, errno, and `linux/stmp_device.h` register offsets. Integration points are platform device drivers resetting STMP-compatible modules during probe, resume, or error recovery. Risks include passing the wrong register base, insufficient timeout for slow hardware, busy-wait latency, reset ordering assumptions that differ by SoC revision, and racing concurrent driver access to the same block. Test signals include platform boot/probe logs, driver reset recovery tests, suspend/resume coverage, timeout fault injection with mocked MMIO, and hardware register trace validation.
