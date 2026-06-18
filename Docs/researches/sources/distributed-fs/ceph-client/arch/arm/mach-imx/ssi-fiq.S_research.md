# sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq.S

Purpose: Fast interrupt handler for i.MX SSI audio FIFO service, designed to be copied into the FIQ vector.

Important APIs/types/functions: Defines global labels/data `imx_ssi_fiq_start`, `imx_ssi_fiq_end`, `imx_ssi_fiq_base`, `imx_ssi_fiq_rx_buffer`, and `imx_ssi_fiq_tx_buffer`; uses FIQ banked registers r8/r9 for ring offsets and sizes.

Control flow: On FIQ entry, the handler reads SSI base, checks TX FIFO-empty interrupt enable/status, writes four 16-bit samples from the TX buffer, advances/wraps r8, then checks RX FIFO-full interrupt enable/status, reads four 16-bit samples into the RX buffer, optionally skips AC97 slot 12 dummy words, advances/wraps r9, and returns with `subs pc, lr, #4`.

State and persistence: Persistent state is encoded in FIQ banked registers r8/r9 and the three patched word variables for SSI base/RX/TX buffers. Hardware state is SSI SIER/SISR/SACNT and FIFO reads/writes.

Dependencies and integration points: Depends on ARM FIQ mode, SSI register layout, ASoC SSI setup that patches exported symbols and initializes banked registers, and `ssi-fiq-ksym.c` for modular access.

Risks: Calling the label as a normal function is invalid. The handler assumes buffer size/offset packing in 16-bit halves and fixed FIFO transfer width. It has no locking, bounds checks beyond wrap logic, or cache management; setup must provide coherent buffers.

Test signals: Audio playback/capture stress with FIQ enabled, AC97 and non-AC97 modes, ring wrap tests, and underrun/overrun monitoring.
