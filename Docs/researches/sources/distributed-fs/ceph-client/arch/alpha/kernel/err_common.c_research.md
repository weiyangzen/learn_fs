# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_common.c

**Purpose:** Supplies shared Alpha machine-check and console data-log utilities: raw logout-frame dumping, timestamp printing, subpacket parsing, annotation, handler registration, and previous-boot console data-log draining from HWRPB per-CPU structures.

**Important APIs/types/functions:** Exposes `err_print_prefix`, `mchk_dump_mem()`, `mchk_dump_logout_frame()`, `el_print_timestamp()`, `el_process_subpackets()`, `el_process_subpacket()`, `el_annotate_subpacket()`, `cdl_check_console_data_log()`, `cdl_register_subpacket_annotation()`, and `cdl_register_subpacket_handler()`. Internal state is `subpacket_handler_list` and `subpacket_annotation_list`, both singly linked lists registered by EV7/TITAN/Marvel handlers.

**Control flow:** Machine-check handlers or boot-time console-log checks pass an `el_subpacket` to `el_process_subpacket()`. Header subpackets are decoded by class/type to determine event name, frame length, packet count, and timestamp, then child subpackets are iterated. Non-header packets are routed through the registered class handler list. Annotation lookup matches class/type/revision and prints per-word labels while dumping memory. `cdl_check_console_data_log()` walks HWRPB processor slots, processes any `console_data_log_pa` pointer through identity mapping, then clears the pointer so firmware can discard it on restart.

**State and persistence behavior:** The only durable-ish behavior is clearing `pcpu->console_data_log_pa` in HWRPB after logging previous-boot errors. Handler/annotation lists are initialized during boot and then read during error handling. `err_print_prefix` is temporarily changed by platform handlers to alter severity.

**Dependencies and integration points:** Uses `<asm/hwrpb.h>`, `<asm/err_common.h>`, machine-check frame structures, and registration declarations in `err_impl.h`. `err_ev7.c`, `err_titan.c`, and `err_marvel.c` plug into this registry.

**Risks:** Subpacket parsing trusts firmware-provided lengths and packet counts; corrupt logs can lead to confusing output or early aborts. Registration duplicate detection does not check the final existing list element before appending, so duplicate last entries are a subtle risk. Global `err_print_prefix` is not concurrency-safe across simultaneous machine checks.

**Test signals:** Validate by booting with synthetic or firmware-supplied console data logs, registering EV7/TITAN handlers, and checking that known header/subpacket classes are printed and unknown classes abort cleanly. Static review should verify every handler returns the next subpacket pointer correctly and annotations terminate with NULL.
