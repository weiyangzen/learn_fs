# sources/distributed-fs/ceph-client/arch/sh/mm/ioremap.h

Purpose: declares fixed ioremap helpers shared between memory initialization and the main ioremap implementation.

Important APIs: `ioremap_fixed` and `ioremap_fixed_init` when fixed ioremap is configured; fallback stubs otherwise.

Control flow: header-only declarations/stubs let `init.c` and `ioremap.c` call early mapping helpers conditionally.

State and persistence: no state directly; declared functions manage fixed mappings in `ioremap_fixed.c`.

Dependencies and integration: included by `init.c`, `ioremap.c`, and `ioremap_fixed.c`.

Risks: stub behavior must match configuration expectations so callers do not assume early fixed mappings exist when disabled.

Test signals: build coverage with and without `CONFIG_IOREMAP_FIXED` and early ioremap users during boot.
