# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev7.c

**Purpose:** Implements EV7 PAL logout-frame subpacket collection, generic EV7 machine-check reporting, and registration of annotation/handler tables for EV7 processor, ZBOX, RBOX, and IO PAL subpackets.

**Important APIs/types/functions:** Exposes `ev7_collect_logout_frame_subpackets()`, `ev7_machine_check()`, `ev7_pal_subpacket_handler`, and `ev7_register_error_handlers()`. Local data includes annotation arrays for EV7 processor, ZBOX, RBOX, and IO subpacket fields. `ev7_process_pal_subpacket()` is the registered class handler for `EL_CLASS__PAL`.

**Control flow:** `ev7_collect_logout_frame_subpackets()` verifies the outer `EL_CLASS__HEADER/LOGOUT_FRAME`, steps to the PAL logout-frame subpacket, saves the logout data pointer, and iterates the declared PAL subpacket count. It stores typed pointers for processor, RBOX, ZBOX, IO, and environmental subpackets in `struct ev7_lf_subpackets`, returning NULL on unexpected class/type. `ev7_machine_check()` synchronizes, prints a CPU correctable/uncorrectable message, delegates packet printing to `el_process_subpacket()`, then releases the frame. `ev7_process_pal_subpacket()` handles nested PAL logout frames by printing LPID/RBOX/timestamp/exc address and recursively processing contained subpackets; other PAL packets are annotated generically.

**State and persistence behavior:** No persistent state beyond registering annotation and handler list entries in `err_common.c`. It reads PAL logout memory and clears PAL machine-check state with `wrmces`.

**Dependencies and integration points:** Provides the base EV7 parser used directly by `err_marvel.c` and by EV7-capable machine vectors. Depends on `<asm/err_ev7.h>` layout definitions, common subpacket registries, timestamp and annotation helpers, SMP CPU id, and PAL vector constants.

**Risks:** The collector assumes well-formed length fields and one expected PAL logout subpacket structure. Unknown PAL subpacket types cause collection failure even if some useful data was already found. Environmental array indexing depends on `ev7_lf_env_index()` matching the contiguous type range.

**Test signals:** Feed synthetic EV7 subpacket sequences with each recognized class/type, malformed outer headers, non-PAL nested packets, unknown PAL types, and all environmental subpacket types. Boot Marvel/EV7 configurations should show registered annotations and sane fallback annotation output for non-logout PAL subpackets.
