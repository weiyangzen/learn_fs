# sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.c

Purpose: DECstation/DECsystem MS02-NV battery-backed NVRAM support. It probes fixed MIPS physical slot addresses, hides firmware diagnostic SRAM, and registers the page-aligned user NVRAM region as an `MTD_RAM` device.

Important APIs/types/functions: `ms02nv_read()` and `ms02nv_write()` are direct memcpy MTD callbacks over `ms02nv_private.uaddr`; `ms02nv_probe_one()` checks firmware magic/diagnostic words with `get_dbe()`; `ms02nv_init_one()` allocates resources, `mtd_info`, and private state; `ms02nv_remove_one()` unregisters and releases all resources. The module lifecycle is `ms02nv_init()`/`ms02nv_cleanup()`.

Control flow: init checks supported MIPS machine types, derives an address stride from memory-controller CSR bits, and walks `ms02nv_addrs`. Each candidate reserves an 8 MiB module resource, probes magic/size, creates diagnostic/user/CSR child resources, computes a page-aligned user mapping, registers the MTD, and pushes it on `root_ms02nv_mtd`. Cleanup pops that list.

State and persistence: persistent bytes live in battery-backed NVRAM. Runtime state is the global MTD linked list plus resource ownership. The driver intentionally avoids the first firmware-owned page and does not erase or validate user payloads.

Dependencies/integration: tightly coupled to MIPS DEC platform headers, CKSEG1 uncached access, Linux resource management, and MTD core registration. It uses `phys_to_virt()` rather than ioremap because this is platform memory.

Risks: no range checks in callbacks because MTD core is expected to bound requests; incorrect firmware diagnostic size or unsupported slot placement can hide usable memory; module removal assumes `root_ms02nv_mtd` is non-null per call. Probe reserves resources before validating hardware and must unwind precisely.

Test signals: boot on supported DECstation variants should log detected modules and expose `mtdN`; read/write through `mtdchar` should preserve data across reboot/power if battery is good; negative tests include unsupported `mips_machtype`, bad magic, and resource-conflict paths.
