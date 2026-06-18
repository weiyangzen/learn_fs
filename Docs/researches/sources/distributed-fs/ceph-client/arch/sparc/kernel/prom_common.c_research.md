# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_common.c

Purpose: provides shared SPARC Open Firmware device-tree support: console globals, integer property lookup, runtime OF property mutation, string-list search, PROM property iteration quirks, and boot-time PDT-to-OF tree construction.

Important APIs/functions: exports `of_console_device`, `of_console_path`, `of_console_options`, `of_getintprop_default()`, `of_set_property_mutex`, `of_set_property()`, and `of_find_in_proplist()`. Internal helpers are `handle_nextprop_quirks()` and `prom_common_nextprop()`. `prom_build_devicetree()` builds the device tree and initializes the console.

Control flow: property reads return a default unless an exactly 4-byte property exists. `of_set_property()` duplicates the new value, locks a mutex plus `devtree_lock`, calls `prom_setprop()`, updates the in-memory property value/length on success, frees old dynamic values, and marks the property dynamic. Device-tree building uses `of_pdt_build_devicetree()` with SPARC PROM operations, then calls architecture-specific `of_console_init()`.

State and persistence: maintains in-memory OF property lists and console globals. `prom_early_allocated` counts init-time allocations for boot logging. `of_set_property()` also attempts to update firmware property state via PROM, but no filesystem persistence is involved.

Dependencies and integration points: depends on Linux OF/PDT infrastructure, SPARC PROM callbacks (`prom_nextprop`, `prom_getproperty`, `prom_setprop`, child/sibling traversal), `devtree_lock`, and 32/64-bit PROM implementations.

Risks: SPARC32 and SPARC64 `prom_nextprop()` differ, requiring explicit quirk handling. Runtime property mutation must keep firmware and in-memory OF state coherent. The code currently notes procfs update gaps after property changes.

Test signals: early tree build, correct console globals, drivers reading integer properties with defaults, runtime `of_set_property()` success/failure paths, dynamic property replacement without leaks, and property iteration on both SPARC32 and SPARC64 PROMs.
