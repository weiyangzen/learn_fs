# subset-b-004993 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/overlay.c -->
# sources/distributed-fs/ceph-client/drivers/of/overlay.c

## Purpose
Implements Linux Open Firmware device-tree overlay application and removal. It accepts an overlay FDT, unflattens it into a detached overlay tree, resolves phandles, converts fragments into an `of_changeset`, applies the changeset to the live tree, and later reverts overlays in topmost order.

## Important APIs, types, and functions
- Public API: `of_overlay_fdt_apply()`, `of_overlay_remove()`, `of_overlay_remove_all()`, `of_overlay_notifier_register()`, `of_overlay_notifier_unregister()`, `of_overlay_mutex_lock()`, and `of_overlay_mutex_unlock()`.
- Core state type: `struct overlay_changeset`, carrying the overlay id, IDR/list membership, backing FDT memory, unflattened overlay root, notifier state, fragment table, symbols flag, and embedded `struct of_changeset`.
- Overlay model helpers: `struct fragment` maps a fragment `__overlay__` node to a live target; `struct target` tracks whether recursion is operating in the live tree or in newly attached overlay nodes.
- Build path: `init_overlay_changeset()` discovers fragments and optional `/__symbols__`; `find_target()` resolves `target` phandles or `target-path`; `build_changeset()` calls recursive `build_changeset_next_level()`, `add_changeset_node()`, and `add_changeset_property()`.
- Removal path: `overlay_removal_is_ok()` and `node_overlaps_later_cs()` enforce stack-like removal; `find_node()` checks ancestor/descendant overlap.

## Control flow
`of_overlay_fdt_apply()` validates FDT header and size, allocates `overlay_changeset`, assigns an ID from `ovcs_idr`, links it on `ovcs_list`, copies and aligns the FDT, unflattens it, then calls `of_overlay_apply()` while holding `of_overlay_phandle_mutex` and `of_mutex`. `of_overlay_apply()` calls `of_resolve_phandles()`, initializes fragments, sends `OF_OVERLAY_PRE_APPLY`, builds the changeset, applies entries, sends entry notifications, then sends `OF_OVERLAY_POST_APPLY`.

Node application descends each fragment. Existing target children are matched by basename; new nodes are duplicated with `__of_node_dup()`, flagged `OF_OVERLAY`, attached via `of_changeset_attach_node()`, and then populated recursively. Properties are duplicated unless they are pseudo properties in live-tree targets. Existing `#address-cells` and `#size-cells` must match and are not updated. Symbol properties are fixed up by `dup_and_fixup_symbol_prop()` so overlay-local paths become live-tree paths.

Removal looks up the ID, refuses corrupt trees, verifies the overlay is topmost relative to later changesets, sends `OF_OVERLAY_PRE_REMOVE`, reverts entries, sends entry revert notifications, clears the caller's ID, sends `OF_OVERLAY_POST_REMOVE`, and frees overlay memory when notifier state permits it.

## State and persistence behavior
State is in kernel memory only: `ovcs_idr`, `ovcs_list`, `devicetree_state_flags`, the copied FDT, the unflattened overlay memory, and the embedded changeset. `DTSF_APPLY_FAIL` and `DTSF_REVERT_FAIL` are sticky; once set by failed rollback/reapply paths, future apply/remove calls return `-EBUSY`. Successful overlay IDs persist until explicitly removed. Overlay FDT memory is retained while an overlay is live and freed only after post-remove or before successful apply.

## Dependencies and integration points
Depends on OF core locking and data structures from `of_private.h`, libfdt validation, `of_fdt_unflatten_tree()`, `of_resolve_phandles()` from `resolver.c`, dynamic changeset internals, notifier chains, `idr`, and global `of_mutex`. It integrates with platform-device creation through OF reconfiguration notifications in `platform.c`; applying/removing overlays emits changeset notifications that other OF subsystems consume.

## Risks and edge cases
- Partial apply failure can leave live-tree state uncertain; this is explicitly guarded by sticky corruption flags.
- Notifier callbacks must not retain overlay pointers past post-remove; otherwise `free_overlay_changeset()` can free memory still referenced by clients.
- Duplicate changeset entries are rejected, but only after building the full changeset.
- Overlay removal must be LIFO for overlapping nodes; non-topmost removal returns `-EBUSY`.
- Updating existing properties outside overlay-created nodes warns about memory leaks on removal.
- Target discovery depends on valid phandles, paths, and `/__symbols__` availability for symbols fragments.

## Test signals
Covered heavily by `drivers/of/unittest.c` overlays, including apply/remove, non-topmost removal, duplicate node/property rejection, bad phandle/symbol/unresolved overlays, notifier injected errors, GPIO/I2C/platform interaction, high-level overlay use, and PCI overlay attachment. `overlay_test.c` adds KUnit coverage for test-managed overlay apply, platform device creation, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/overlay_test.c -->
# sources/distributed-fs/ceph-client/drivers/of/overlay_test.c

## Purpose
Provides KUnit tests for test-managed device-tree overlays. It verifies that `of_overlay_apply_kunit()` can add a node, cause platform-device creation, and cleanly remove both node and device during KUnit cleanup.

## Important APIs, types, and functions
- Test cases: `of_overlay_apply_kunit_apply()`, `of_overlay_apply_kunit_platform_device()`, and `of_overlay_apply_kunit_cleanup()`.
- Helper: `of_overlay_bus_match_compatible()` matches platform bus devices by `of_device_is_compatible()`.
- Uses KUnit helpers `of_node_put_kunit()`, `of_root_kunit_skip()`, `kunit_cleanup()`, and standard `KUNIT_ASSERT_*` / `KUNIT_EXPECT_*` checks.

## Control flow
Each test applies `kunit_overlay_test` through `of_overlay_apply_kunit()`. The apply test looks up the added `kunit-test` node by name. The platform-device test looks up the node and then calls `of_find_device_by_node()` to verify a platform device was instantiated. The cleanup test creates a fake KUnit test, applies the overlay against that fake owner, verifies node and platform device existence, calls `kunit_cleanup(&fake)`, then confirms the node and any compatible platform device are gone.

## State and persistence behavior
The file intentionally relies on KUnit-managed resource cleanup. Overlay state persists for the fake test only until `kunit_cleanup()` runs. Device and node references are explicitly dropped with `of_node_put_kunit()`, `of_node_put()`, `put_device()`, or `platform_device` reference helpers.

## Dependencies and integration points
Depends on `CONFIG_OF_OVERLAY`, `CONFIG_OF_EARLY_FLATTREE`, platform bus lookup, `of_private.h`, and generated KUnit overlay fixture `kunit_overlay_test`. It exercises the integration between OF overlays, dynamic OF reconfiguration, and platform-device population.

## Risks and edge cases
The cleanup test skips when no usable OF root or overlay support exists. It deliberately uses a fake KUnit context to verify owner-scoped cleanup; failures here usually indicate stale overlay nodes or leaked platform devices after tests.

## Test signals
The file is itself a test signal: it checks node creation, device creation, and cleanup. It complements the larger boot-time `unittest.c` overlay coverage with KUnit-scoped lifetime assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/overlay_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/pdt.c -->
# sources/distributed-fs/ceph-client/drivers/of/pdt.c

## Purpose
Builds the initial Linux `struct device_node` tree from a platform firmware PROM device tree, primarily for Open Firmware style systems such as SPARC and PowerPC.

## Important APIs, types, and functions
- Public entry: `of_pdt_build_devicetree(phandle root_node, struct of_pdt_ops *ops)`.
- Firmware operation table: `struct of_pdt_ops` supplies `pkg2path`, `nextprop`, `getproplen`, `getproperty`, `getchild`, and `getsibling`.
- Node creation path: `of_pdt_create_node()`, `of_pdt_build_tree()`, `of_pdt_build_prop_list()`, and `of_pdt_build_one_prop()`.
- Naming: `of_pdt_build_full_name()` uses SPARC path-component behavior or generic `pkg2path()` fallback plus property `name`.

## Control flow
`of_pdt_build_devicetree()` stores the PROM ops table, creates `of_root`, forces its full name to `/`, recursively builds child and sibling links with `of_pdt_build_tree()`, then calls `of_alias_scan()` using `kernel_tree_alloc()`. Each node gets initialized with `of_node_init()`, parent link, phandle, `name` property, property list headed by a synthetic `.node` property, and a firmware-derived full name.

## State and persistence behavior
All allocations use `prom_early_alloc()` and are intended to become permanent early-boot device-tree memory. `of_pdt_prom_ops` is `__initdata`. SPARC builds assign increasing `unique_id` values. The property builder has a static reusable temporary `struct property *tmp` for the failed `nextprop()` end-of-list case.

## Dependencies and integration points
Depends on architecture-provided PROM callbacks, early allocator behavior, OF core node/property structures, optional SPARC `irq_trans_init()`, and global `of_root`. The produced tree is later consumed by common OF APIs, alias handling, IRQ translation, and device population.

## Risks and edge cases
Generic naming falls back to `"name@unknownN"` when `pkg2path()` fails. Property lengths less than or equal to zero are normalized to empty properties. Since allocation is early and permanent, malformed firmware data can produce lasting tree shape or property errors rather than recoverable allocations.

## Test signals
No direct tests in this file. Indirect validation comes from all OF lookup, alias, phandle, IRQ, and platform-population tests that operate after a PROM-derived tree is built on relevant architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/pdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/platform.c -->
# sources/distributed-fs/ceph-client/drivers/of/platform.c

## Purpose
Creates and destroys Linux devices from device-tree nodes. It provides platform-device and AMBA-device population, default boot-time population, managed populate/depopulate helpers, and dynamic OF reconfiguration handling.

## Important APIs, types, and functions
- Lookup/registration: `of_find_device_by_node()`, `of_device_add()`, `of_device_register()`, `of_device_unregister()`, `of_device_alloc()`, and `of_platform_device_create()`.
- Population: `of_platform_bus_probe()`, `of_platform_populate()`, and `of_platform_default_populate()`.
- Cleanup: `of_platform_device_destroy()`, `of_platform_depopulate()`, `devm_of_platform_populate()`, and `devm_of_platform_depopulate()`.
- Boot hooks: `of_platform_default_populate_init()` at `arch_initcall_sync`, and `of_platform_sync_state_init()` at `late_initcall_sync`.
- Dynamic integration: `of_platform_notify()` and `of_platform_register_reconfig_notifier()` under `CONFIG_OF_DYNAMIC`.

## Control flow
Population starts from a root node, then `of_platform_bus_create()` optionally enforces a `compatible` property, skips special nodes such as `operating-points-v2`, checks `OF_POPULATED_BUS`, applies auxdata overrides, creates AMBA devices for `"arm,primecell"`, otherwise creates platform devices. If the new node matches a bus table, children are recursively populated and `OF_POPULATED_BUS` is set.

`of_platform_default_populate_init()` handles special boot-time cases: PPC BootX display nodes, selected `/reserved-memory` compatible nodes, `/firmware`, `simple-framebuffer` with `sysfb_disable()`, then default population for the rest of the tree. Dynamic reconfiguration creates a platform device for added nodes whose parent is root or an already populated bus, and destroys matching devices on removal.

## State and persistence behavior
Node flags `OF_POPULATED` and `OF_POPULATED_BUS` are the key persistent in-memory state that prevents duplicate devices and drives depopulation. Created devices hold OF node references through `device_set_node()` and device model lifetime. Managed populate stores the requesting device in devres so cleanup occurs on unbind.

## Dependencies and integration points
Depends on OF address translation, IRQ/MSI configuration, DMA masks, platform bus, optional AMBA, `sysfb`, device links supplier sync-state pause/resume, and OF dynamic notifier infrastructure. It is the main consumer of overlay reconfiguration notifications emitted after overlay changesets modify the tree.

## Risks and edge cases
- `of_platform_device_create_pdata()` returns `NULL` for unavailable or already populated nodes, losing detailed failure codes.
- Resource allocation failures must clear `OF_POPULATED` or future population will skip the node.
- Dynamic add must clear `FWNODE_FLAG_NOT_DEVICE` before creation so fw_devlink can model consumers.
- Destroy only touches devices with populated OF nodes, leaving manually created children alone.
- Default population intentionally does not create devices for all `/reserved-memory` compatible children.

## Test signals
`unittest.c` validates `of_platform_default_populate()`, `of_platform_populate()`, device lookup, platform IRQ parsing behavior, depopulation, overlay-triggered platform-device creation/removal, and PCI child platform-device address translation. `overlay_test.c` has KUnit checks for overlay-driven platform-device creation and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/property.c -->
# sources/distributed-fs/ceph-client/drivers/of/property.c

## Purpose
Provides core OF property accessors, OF graph traversal helpers, firmware-node (`fwnode`) operations for device tree nodes, and supplier-link discovery for fw_devlink.

## Important APIs, types, and functions
- Property readers: `of_property_read_bool()`, `of_property_count_elems_of_size()`, typed index readers for u8/u16/u32/u64, variable array readers, `of_property_read_u64()`, `of_property_read_string()`, `of_property_match_string()`, `of_property_read_string_helper()`, `of_prop_next_u32()`, and `of_prop_next_string()`.
- Graph helpers: `of_graph_is_present()`, `of_graph_parse_endpoint()`, `of_graph_get_port_by_id()`, `of_graph_get_next_port()`, `of_graph_get_next_port_endpoint()`, `of_graph_get_next_endpoint()`, `of_graph_get_endpoint_by_regs()`, remote endpoint/port/parent helpers, and endpoint/port count helpers.
- Fwnode bridge: exported `of_fwnode_ops` implements get/put, property reads, child traversal, reference args, graph ops, I/O mapping, IRQ lookup, and link addition.
- Supplier linking: `struct supplier_bindings`, many `parse_*` helpers for clocks, interconnects, iommus, dmas, power domains, gpios, interrupts, regulators, remote endpoints, and `of_link_property()`.

## Control flow
Typed readers share `of_find_property_value_of_size()` to validate presence, non-empty values, minimum size, and optional maximum size, then convert big-endian cells into native values. String helpers iterate bounded NUL-terminated strings and return `-EILSEQ` for unterminated data. Graph helpers normalize either direct `port` children or a `ports` container, iterate endpoint nodes with refcount handoff semantics, and resolve `remote-endpoint` phandles.

The fwnode operations convert generic firmware-node requests back to OF APIs. Supplier linking walks each property on a consumer node, matches it against `of_supplier_bindings`, parses all supplier phandles for that property, optionally maps a graph endpoint back to its real consumer device, and calls `fwnode_link_add()`. Optional suppliers are skipped when fw_devlink is not strict.

## State and persistence behavior
Most APIs are stateless readers over immutable or dynamically updated in-memory OF properties. Fwnode `get`/`put` mirrors OF node refcounting. Supplier linking persists device dependency state by creating fwnode links. `of_is_fwnode_add_links_supported()` caches an x86 platform compatibility decision in a static integer.

## Dependencies and integration points
Depends on OF core property lookup, phandle parsing, OF graph conventions, OF address and IRQ helpers, DMA coherency helpers, device matching, and fw_devlink. `of_fwnode_ops` is the bridge used by generic driver core property APIs for OF-backed devices.

## Risks and edge cases
- Boolean property reads warn when a supposedly boolean property carries data.
- All property array readers rely on exact byte length validation; malformed lengths return `-EOVERFLOW`.
- String lists must be fully NUL-terminated inside property length or callers get `-EILSEQ`.
- Graph parent walking has special cases for `ports`, `in-ports`, and `out-ports`.
- Supplier parsing must avoid false positives such as `,nr-gpios` and GPIO hogs.
- Missing supplier nodes are tolerated by continuing through available suppliers; link creation does not abort on one failed supplier.

## Test signals
`unittest.c` validates string matching/counting/indexing, phandle parsing and mapped phandle args, graph-adjacent remote endpoint behavior through overlays and I2C/GPIO tests, address/IRQ helper integration, and fwnode/platform side effects indirectly. Many exported helpers are also covered by driver subsystems that consume OF properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/resolver.c -->
# sources/distributed-fs/ceph-client/drivers/of/resolver.c

## Purpose
Relocates and resolves phandles in a detached overlay tree before overlay application. It prevents overlay-local phandles from colliding with the live tree and resolves external symbol references through the live tree `/__symbols__` node.

## Important APIs, types, and functions
- Public API: `of_resolve_phandles(struct device_node *overlay)`.
- Helpers: `live_tree_max_phandle()`, `adjust_overlay_phandles()`, `adjust_local_phandle_references()`, `update_usages_of_a_phandle_reference()`, and `node_name_cmp()`.

## Control flow
`of_resolve_phandles()` validates that the overlay is non-NULL and detached. It computes `phandle_delta` as live max phandle plus one, adjusts each overlay node's phandle and `phandle`/`linux,phandle` properties, finds `__local_fixups__`, and applies the delta to local phandle references. It then finds `__fixups__`; for each fixup property, it looks up the named label in live `/__symbols__`, resolves that path to a live node, reads its phandle, and patches every listed `path:property:offset` usage in the overlay.

## State and persistence behavior
The function mutates the detached overlay in place: node phandle fields, phandle properties, local reference cells, and external reference cells are overwritten. It reads live tree state under `devtree_lock` while computing the max phandle. No durable external state is created, but callers must serialize resolve plus apply so two overlays cannot allocate overlapping phandle ranges.

## Dependencies and integration points
Depends on OF node traversal, raw `devtree_lock`, detached-node flags, `/__symbols__` convention, lib-style string parsing, and overlay locking from `overlay.c`. `of_overlay_apply()` calls this before building the changeset.

## Risks and edge cases
- Non-detached overlays return `-EINVAL`.
- Missing `/__symbols__`, unknown labels, malformed fixup tuples, bad offsets, or missing target properties abort resolution.
- `update_usages_of_a_phandle_reference()` duplicates the fixup value to allow in-place tokenization; allocation failure returns `-ENOMEM`.
- The resolver mutates property values in place, so the input overlay must be writable unflattened memory.

## Test signals
`unittest.c` exercises successful overlay resolution, local fixups, bad phandles, bad symbols, unresolved labels, and the early test data attachment path that calls `of_resolve_phandles()` under `of_overlay_mutex_lock()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/resolver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/unittest-data/Makefile -->
# sources/distributed-fs/ceph-client/drivers/of/unittest-data/Makefile

## Purpose
Builds device-tree blob overlays and test case blobs used by OF boot-time unittests and overlay tests. It also defines static overlay application build tests through `fdtoverlay`.

## Important APIs, types, and functions
- Kbuild variables: `obj-y`, `obj-$(CONFIG_OF_OVERLAY)`, `DTC_FLAGS_*`, `dtb-$(CONFIG_OF_OVERLAY)`, and compound `*-dtbs` lists.
- Generated fixtures include `testcases.dtbo.o`, `overlay*.dtbo.o`, GPIO overlays, PCI overlay, and intentionally bad overlays.
- Static tests: `static_test_1-dtbs` and `static_test_2-dtbs` combine base DTBs and selected overlays.

## Control flow
Kbuild always builds `testcases.dtbo.o`. When `CONFIG_OF_OVERLAY` is enabled, it builds overlay objects used by `unittest.c`. `-@` is enabled for overlays and selected base/testcase blobs so `__symbols__` nodes exist. Warning suppressions are applied for intentional malformed test inputs. Static overlay lists exclude deliberately invalid overlays, then define composite DTBs that cause `fdtoverlay` failures to break the kernel build.

## State and persistence behavior
The file creates build artifacts only: DTBO object files and static composite DTBs. Runtime tests refer to linker symbols generated from these objects, such as `__dtbo_overlay_0_begin`.

## Dependencies and integration points
Depends on Kbuild DTB/DTBO rules, dtc symbol generation, `fdtoverlay`, and the fixture names hard-coded in `unittest.c`. It is the source of overlay data consumed by `OVERLAY_INFO_EXTERN()` and `overlay_data_apply()`.

## Risks and edge cases
The fixture list must stay in sync with declarations in `unittest.c`. Invalid overlays are intentionally built as objects but excluded from static fdtoverlay success tests. Removing `-@` would break symbol and fixup based overlay tests.

## Test signals
Build-time signal: `static_test_1.dtb` and `static_test_2.dtb` verify selected overlays apply with `fdtoverlay`. Runtime signal: generated objects back all OF unittest overlay scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/unittest-data/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/unittest.c -->
# sources/distributed-fs/ceph-client/drivers/of/unittest.c

## Purpose
Boot-time self-test harness for the OF core. It injects generated testcase data into the live tree, runs broad API and behavior checks, applies many overlays, validates dynamic device creation/removal, and reports aggregate pass/fail counts at late init.

## Important APIs, types, and functions
- Harness: `of_unittest()` registered with `late_initcall`, `unittest()` result macro, `EXPECT_*` log expectation markers, and `struct unittest_results`.
- Test data setup: `unittest_data_add()`, `attach_node_and_children()`, `update_node_properties()`, and `unittest_unflatten_overlay_base()`.
- Core tests: find-by-path/alias/options, dynamic property add/update/remove, tree linkage, phandle duplicate checks, `%pOF` printing, phandle args and mapped args, property strings, property duplication, changesets, DMA ranges, PCI ranges, bus ranges, `reg`, address translation, IRQ parsing, interrupt maps, IRQ refcounts, and match-node priority.
- Platform/overlay tests: `of_unittest_platform_populate()`, `of_unittest_overlay()`, overlay numbered cases 0-13 and 15, GPIO/I2C/mux helpers, notifier injection, lifecycle refcount tests, high-level overlay tests, and dynamic PCI node overlay tests.

## Control flow
`of_unittest()` taints the kernel with `TAINT_TEST`, calls `unittest_data_add()` to unflatten `testcases.dtbo.o`, resolves phandles, attaches testcase nodes to the live tree, ensures `/aliases`, checks testcase availability, then runs each test function in a fixed order. After ordinary OF tests and overlay/platform tests, it rechecks tree linkage, runs the high-level overlay test, and prints final counts.

`unittest_data_add()` copies linker-provided testcase DTBO data, unflattens it, serializes phandle resolution with the overlay mutex, and manually attaches children under `of_root`. Overlay tests use linker symbols declared by `OVERLAY_INFO_EXTERN()`, map names through `overlays[]`, and apply via `of_overlay_fdt_apply()`. Some overlays are tracked for later LIFO cleanup; others intentionally remain or trigger specific error paths.

## State and persistence behavior
Persistent in-memory state includes `unittest_results`, injected testcase nodes, overlay tracking arrays `track_ovcs_id*`, GPIO probe/request counters, PCI counters, and static `overlay_info` records. The lifecycle test intentionally manipulates refcounts and then removes a test node from its parent's child list to avoid later traversal warnings. Overlay fixture data is retained as linked binary data; overlay apply may leave successful overlays live until cleanup or until high-level tests intentionally exercise error cases.

## Dependencies and integration points
Depends on almost every OF subsystem: base lookup, dynamic changesets, property readers, phandle parsers, address and IRQ translators, platform population, overlays/resolver, GPIO, I2C, I2C mux, PCI dynamic OF nodes, memblock, libfdt, sysfs attach, and generated DTBO linker symbols from `unittest-data/Makefile`. It also depends on config guards to skip feature-specific tests when subsystems are absent.

## Risks and edge cases
- Test code intentionally mutates live-tree internals, including direct child-list manipulation in lifecycle tests.
- Expected log text is part of the validation contract; message changes can cause noisy regressions even if behavior remains equivalent.
- Many tests are config-dependent, so coverage varies significantly with kernel configuration.
- Overlay tests include intentionally failing overlays and partial-apply cleanup paths; changes to overlay error handling must preserve expected return/removal semantics.
- Fixture names and expected overlay IDs/messages are tightly coupled to the DTBO list and overlay core behavior.

## Test signals
This file is the primary test signal for the files in this work item. It produces pass/fail counts in the kernel log, exercises both successful and failing paths, validates reference counts, confirms dynamic platform/GPIO/I2C/PCI device behavior, and checks final tree linkage after destructive lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/of/unittest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/opp/Kconfig

## Purpose
Defines the `PM_OPP` Kconfig symbol for the Operating Performance Points framework.

## Important APIs, types, and functions
- Kconfig symbol: `config PM_OPP`, a boolean option without visible prompt in this file.
- Help text describes OPP tuples as frequency/voltage pairs per voltage domain and points readers to `Documentation/power/opp.rst`.

## Control flow
There is no runtime control flow. Kconfig evaluates the boolean symbol based on selections or dependencies elsewhere in the tree. When enabled, the OPP Makefile builds the core OPP implementation.

## State and persistence behavior
Persistent output is build configuration state: whether `CONFIG_PM_OPP` is set. That setting controls compilation of OPP framework objects and indirectly enables OPP users in SoC, CPU frequency, and power-management drivers.

## Dependencies and integration points
The symbol integrates with `drivers/opp/Makefile` and consumers that select or depend on `PM_OPP`. It belongs to the power-management/OPP subsystem, not the OF overlay subsystem, but OPP can consume OF data when `CONFIG_OF` builds `of.o`.

## Risks and edge cases
Because there is no prompt or explicit dependency here, correctness depends on other Kconfig entries selecting it only when the framework is needed. Documentation drift in the help text would be the main maintenance risk.

## Test signals
Build configuration and subsystem users are the test signal. Enabling `CONFIG_PM_OPP` should cause OPP core objects to compile via the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/opp/Makefile

## Purpose
Selects OPP subsystem object files for compilation based on kernel configuration.

## Important APIs, types, and functions
- `ccflags-$(CONFIG_DEBUG_DRIVER) := -DDEBUG` enables debug logging when driver debugging is configured.
- Always built in this directory: `core.o` and `cpu.o` through `obj-y`.
- Conditional objects: `of.o` for `CONFIG_OF`, `debugfs.o` for `CONFIG_DEBUG_FS`, and `ti-opp-supply.o` for `CONFIG_ARM_TI_CPUFREQ`.

## Control flow
No runtime control flow exists in the Makefile. Kbuild expands configuration-conditioned variables and links the selected objects into the kernel or built-in driver collection.

## State and persistence behavior
The file controls build artifacts only. The resulting object selection determines which OPP features exist at runtime: core/cpu support always, OF parsing when OF is enabled, debugfs inspection when debugfs is enabled, and TI supply handling for TI CPU frequency support.

## Dependencies and integration points
Integrates with `drivers/opp/Kconfig`, Kbuild, the OF subsystem through `of.o`, debugfs, and ARM TI cpufreq support.

## Risks and edge cases
Incorrect conditional object selection can silently remove subsystem functionality or compile unsupported code. The unconditional `core.o cpu.o` assumption means any build entering this directory expects OPP core and CPU support to be valid.

## Test signals
Build success across configurations is the main signal: `CONFIG_OF`, `CONFIG_DEBUG_FS`, `CONFIG_DEBUG_DRIVER`, and `CONFIG_ARM_TI_CPUFREQ` should include the expected objects and flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/Makefile -->
