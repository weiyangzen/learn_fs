# sources/distributed-fs/ceph-client/drivers/nvmem/qoriq-efuse.c

Purpose: Read-only, root-only NVMEM provider for NXP QorIQ Security Fuse Processor data.

Important APIs/types/functions: `struct qoriq_efuse_priv` holds MMIO base. `qoriq_efuse_read()` uses `__ioread32_copy()` for aligned 32-bit reads. Probe maps the resource and registers a 4-byte stride NVMEM device named `qoriq_efuse_read`.

Control flow: probe allocates state, maps resource 0, sizes config from the resource, and registers NVMEM. Runtime reads copy `bytes / 4` words from base plus offset.

State/persistence: eFuse data persists in hardware and is read-only through this driver. No runtime cache.

Dependencies/integration: platform driver for `fsl,t1023-sfp`; uses MMIO and NVMEM provider APIs.

Risks: trailing non-word bytes are intentionally ignored, relying on `.stride = 4` to prevent such requests. Root-only is set because SFP contents may include security-sensitive data.

Test signals: aligned 32-bit reads, root-only permissions, resource-size config, and attempted unaligned access through NVMEM core.
