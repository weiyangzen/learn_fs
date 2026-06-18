# sources/distributed-fs/ceph-client/drivers/nvmem/mxs-ocotp.c

Purpose: Freescale MXS/i.MX23/i.MX28 OCOTP read-only NVMEM provider.

Important APIs/types/functions: `struct mxs_ocotp` holds clock, MMIO base, and NVMEM device. `mxs_ocotp_wait()` polls busy/error bits. `mxs_ocotp_read()` opens OCOTP banks for read, returns zeros for non-data or unaligned register offsets, and copies data words. Match data supplies SoC-specific size.

Control flow: probe maps the controller, obtains and prepares the clock, registers cleanup action to unprepare it, and exposes 16-byte stride/4-byte word reads. Each read enables the clock, clears stale error, waits idle, opens banks, delays, waits again, reads requested words, closes banks, and disables the clock.

State/persistence: OTP state is persistent in hardware and read-only. Runtime state is limited to clock preparation and MMIO mapping.

Dependencies/integration: compatibles `fsl,imx23-ocotp` and `fsl,imx28-ocotp`; uses STMP set/clear register offsets, clock framework, and NVMEM provider.

Risks: polling is CPU-relax busy-wait with a fixed iteration count. The driver intentionally masks non-data regions with zeros, which can hide incorrect cell offsets. Author module string has a missing closing parenthesis but no runtime effect.

Test signals: clock enable failure, busy/error timeout, reads from data and non-data offsets, and SoC size selection.
