# sources/distributed-fs/ceph-client/drivers/of/unittest.c

## Purpose
Boot-time OF self-test harness that injects testcase data, tests OF APIs, applies overlays, validates dynamic device behavior, and reports pass/fail counts.

## Important APIs, types, and functions
Harness pieces are `of_unittest()`, `unittest()`, `EXPECT_*`, and `struct unittest_results`. Data setup uses `unittest_data_add()`, `attach_node_and_children()`, and `unittest_unflatten_overlay_base()`. Tests cover lookup, dynamic properties, changesets, phandle args, strings, address/IRQ parsing, platform population, overlays, GPIO, I2C, PCI, lifecycle, and high-level overlay use.

## Control flow
`of_unittest()` taints the kernel, attaches generated testcase DTBO data to the live tree, ensures aliases, checks testcase availability, runs feature tests in a fixed order, rechecks tree linkage, runs high-level overlay tests, and logs totals. Overlay tests map linker-provided DTBO symbols through `overlays[]`, call `of_overlay_fdt_apply()`, track selected overlay IDs, and clean up in LIFO order.

## State and persistence behavior
State includes pass/fail counters, injected testcase nodes, overlay tracking arrays, GPIO/I2C/PCI counters, and static overlay metadata. Some tests intentionally alter live-tree internals, especially lifecycle refcount tests.

## Dependencies and integration points
Depends on OF core, dynamic changesets, property APIs, phandle parsing, address and IRQ translation, overlays/resolver, platform bus, GPIO, I2C/mux, PCI dynamic OF nodes, memblock/libfdt, sysfs attach, and DTBO objects from `unittest-data/Makefile`.

## Risks and edge cases
Coverage is config-dependent. Expected log text is part of validation. Intentional failing overlays and direct live-tree manipulation can expose brittle assumptions. Fixture names and expected results are tightly coupled to generated DTBO objects.

## Test signals
This is the main test signal for the OF files in this work item, producing kernel-log pass/fail counts and exercising successful, failing, cleanup, reference-count, and dynamic-device paths.
