# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_impl.h

**Purpose:** Private implementation header for Alpha machine-check/error handlers. It defines subpacket annotation and handler registry types, bitfield helper macros, and cross-file prototypes connecting common, EV6, EV7, Marvel, TITAN, and Privateer error handling code.

**Important APIs/types/functions:** Defines `struct el_subpacket_annotation`, `SUBPACKET_ANNOTATION()`, `struct el_subpacket_handler`, `SUBPACKET_HANDLER_INIT()`, `EXTRACT()`, and `GEN_MASK()`. Declares shared functions such as `mchk_dump_mem()`, `mchk_dump_logout_frame()`, `el_process_subpacket()`, `cdl_register_subpacket_annotation()`, EV7 collector/handlers, EV6 processing, Marvel handlers, and TITAN/Privateer handlers.

**Control flow:** This header has no runtime control flow, but its types determine the registry flow in `err_common.c`: class handlers return the next `el_subpacket`, annotations provide per-word labels, and platform files register arrays during init. `EXTRACT()` and `GEN_MASK()` are used throughout platform decoders to convert raw CSR fields to display and validity masks.

**State and persistence behavior:** No storage is allocated here. It exposes the global `err_print_prefix` and registration interfaces that mutate state in `err_common.c`.

**Dependencies and integration points:** Includes `<asm/mce.h>` for machine-check structures and disposition constants. It is included by all researched `err_*.c` files and is intentionally private to `arch/alpha/kernel`.

**Risks:** Macro naming conventions require each field to provide `__S` and `__M` symbols; mismatches fail at compile time or decode the wrong bits if constants are wrong. Registry struct layouts are shared across files, so changes must be coordinated. Because prototypes are conditional only by compile selection elsewhere, stale declarations can hide missing object coverage until link.

**Test signals:** Compile all Alpha machine-check configurations using EV6, EV7/Marvel, TITAN, and Privateer paths. Static checks should confirm every registered handler matches the expected `struct el_subpacket *(*)(struct el_subpacket *)` signature and every annotation array is NULL-terminated.
