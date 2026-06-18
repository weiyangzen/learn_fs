# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/types.h

Purpose: Provides small portability definitions for the SMT/hardware code on Linux, mainly legacy memory qualifiers and I/O accessor aliases.

Important APIs/types/functions: Includes `<linux/types.h>`, defines `_packed`, `far`, and `_far` as compatibility no-ops, and maps `inp/inpw/inpd/outp/outpw/outpd` to `ioread8/16/32` and `iowrite8/16/32`.

Control flow: No direct control flow. Calls through the accessor macros perform MMIO or I/O memory reads and writes wherever the legacy code uses DOS/NDIS-style function names.

State and persistence behavior: No owned state. The I/O macros mutate hardware registers and read clear-on-read status registers through call sites in the rest of the driver.

Dependencies and integration points: Included by nearly every `skfp` C file before hardware headers. It lets older portable code compile in the Linux kernel without rewriting all register access calls.

Risks: Accessor argument order differs between read and write wrappers and must match the Linux APIs. These wrappers do not add locking or barriers beyond what `ioread/iowrite` provide. The no-op packing/near/far definitions may hide assumptions from non-Linux source origins.

Test signals: Compile coverage for all files using `inp/outp` aliases; hardware smoke tests that read/write timer, FORMAC, and PLC registers; static review for any call sites expecting old `outp(value, port)` order rather than the defined `outp(port, value)`.
