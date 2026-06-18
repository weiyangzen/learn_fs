# sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_otp.c

Purpose: Read-only NVMEM provider for LPC18xx/43xx OTP banks.

Important APIs/types/functions: `struct lpc18xx_otp` holds the MMIO base. `lpc18xx_otp_read()` copies 32-bit OTP words. `lpc18xx_otp_nvmem_config` declares read-only, 4-byte stride/word access and fixed 64-byte size.

Control flow: probe allocates state, maps resource 0, fills config size/device/private fields, and registers the NVMEM device. Reads convert byte offset and length to word index/count and perform `readl()` across the requested words.

State/persistence: OTP data is hardware-programmed and read-only through this driver. No runtime persistence beyond the devm-managed mapping and registered NVMEM device.

Dependencies/integration: platform driver matched by `nxp,lpc1850-otp`; integrates with NVMEM fixed cells and consumers for part IDs, keys, USB IDs, or general-purpose OTP words.

Risks: the boundary check compares word count against a byte-sized constant after `index` conversion, so it is permissive rather than a precise byte bound; NVMEM core size normally limits callers. The TODO notes write support through boot ROM is absent.

Test signals: read all four banks, check 4-byte alignment behavior, and verify invalid/out-of-range requests are contained by NVMEM core sizing.
