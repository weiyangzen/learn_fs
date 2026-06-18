# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utinit.c

Purpose: `utinit.c` initializes and shuts down ACPICA global state, including caches, mutex tracking, owner IDs, events/GPEs, handlers, global lock fields, namespace root, and subsystem termination.

Important APIs/types/functions: `acpi_ut_init_globals()` creates caches and resets global subsystem state for cold or warm restart. Static `acpi_ut_free_gpe_lists()` frees GPE interrupt/block lists when hardware support is enabled. Static `acpi_ut_terminate()` frees GPE lists and address ranges. `acpi_ut_subsystem_shutdown()` performs high-level shutdown of events, dynamic interfaces, namespace, tables, globals, and caches.

Control flow: Initialization first creates caches, then clears address range lists, mutex info, owner ID masks, event counters, GPE/event handler state, global notify/exception/init/table/interface handlers, global lock fields, DSDT/debug/shutdown flags, hardware state, and root namespace node fields. Shutdown checks `acpi_gbl_shutdown`, marks shutdown and clears startup flags, then calls event termination, interface termination, namespace termination, table termination, utility termination, and cache deletion.

State and persistence behavior: This file resets most ACPICA globals that define runtime subsystem state. Shutdown frees memory and marks the subsystem terminated; repeated shutdown logs an error and returns.

Dependencies and integration points: It depends on allocation/cache code, event/GPE code, namespace termination, table termination, interface management, address list cleanup, debug memory tracking, and compile-time reduced-hardware/compiler/disassembler options. It is called by subsystem initialization and termination entry points.

Risks and test signals: Risks include partial initialization failure after cache creation, forgotten globals across warm restart, double shutdown, freeing GPE lists while live handlers remain, and debugger mutex lifetime constraints. Tests should cover init-shutdown-init cycles, reduced hardware builds, GPE list cleanup, address range cleanup, root node initialization, double shutdown behavior, and cache deletion after namespace/table teardown.
