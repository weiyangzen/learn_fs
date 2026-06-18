# Research Group subset-b-006784

This grouped report covers the requested memblock, nvdimm, and radix-tree test sources. Each file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.c

## Purpose
`basic_api.c` is the core memblock basic API test suite. It validates initialization defaults and region-array semantics for `memblock_add*()`, `memblock_reserve()`, `memblock_remove()`, `memblock_free()`, bottom-up allocation mode, `memblock_trim_memory()`, `memblock_overlaps_region()`, and, under `CONFIG_NUMA`, `memblock_set_node()`. The tests are narrow unit-style checks that directly inspect the global `memblock` object rather than exercising a boot path.

## Important APIs, Types, And Functions
The exported entry point is `memblock_basic_checks()`, which runs all local check groups. Important helper-facing state comes from `common.h`: `struct region`, `PREFIX_PUSH()`, assertion macros, `reset_memblock_regions()`, `reset_memblock_attributes()`, and dummy physical-memory helpers. Check groups are organized as `memblock_add_checks()`, `memblock_reserve_checks()`, `memblock_remove_checks()`, `memblock_free_checks()`, `memblock_bottom_up_checks()`, `memblock_trim_memory_checks()`, `memblock_overlaps_region_checks()`, and `memblock_set_node_checks()`.

## Control Flow
Each individual check resets memblock region state, creates a few synthetic address ranges, invokes one memblock API, and asserts the expected region base, size, count, and `total_size`. The add/reserve suites cover disjoint ranges, top and bottom overlap merging, containment, duplicate insertion, gap-filling merge, `PHYS_ADDR_MAX` truncation, and array growth past the initial 128 entries. Remove/free suites mirror those cases but verify erasure, trimming, split-region behavior, absent-range no-ops, and full removal of the only region. `memblock_basic_checks()` is a fixed sequential runner, so later tests depend on previous tests restoring global memblock state.

## State And Persistence
The file mutates the global `memblock.memory`, `memblock.reserved`, `memblock.bottom_up`, and `memblock.current_limit` fields. Array-growth tests call `memblock_allow_resize()` and allocate dummy memory so `memblock_double_array()` can relocate region arrays; they then restore `memblock.memory.regions` or `memblock.reserved.regions` to avoid dangling pointers after freeing dummy memory. There is no durable persistence, but process-global state must be reset rigorously between checks.

## Dependencies And Integration Points
The suite depends on kernel memblock internals exposed to the user-space memblock test harness, Linux size constants, NUMA conditionals, and `common.c` setup helpers. It integrates with the broader memblock selftest runner through `memblock_basic_checks()` declared in `basic_api.h`.

## Risks
Several assertions are exact structural expectations, so legitimate kernel-side memblock representation changes can break tests even if external behavior remains valid. The near-`PHYS_ADDR_MAX` tests are sensitive to address arithmetic overflow behavior. Array-growth tests are fragile because they intentionally point memblock region arrays into temporary dummy memory and must restore the original arrays before cleanup. One notable test, `memblock_remove_overlap_top_check()`, asserts `rgn->base == r1.base + r2.base`; this is unusual for an overlap trim expectation and should be reviewed if failures appear around that case.

## Test Signals
Success is signaled by completing all assertions and optional verbose `ksft_test_result_pass()` output. Failures call `test_fail()` before `assert()` aborts. High-value signals include the double-array tests, all-location reserve tests, the regression case for overlapping allocation while doubling the reserved array, and the NUMA repeated `memblock_set_node()` loop that catches nid loss after array resize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.h

## Purpose
`basic_api.h` is the public header for the memblock basic API test suite. It provides a guarded declaration of the suite entry point and includes the shared memblock test harness header.

## Important APIs, Types, And Functions
The only declared API is `int memblock_basic_checks(void);`. The file includes `common.h`, so any translation unit including this header also receives the common assertion macros, memblock setup helpers, and shared test constants.

## Control Flow
There is no runtime control flow in this header. Its compile-time role is to connect the test runner or other test translation units to the implementation in `basic_api.c`.

## State And Persistence
The header defines no state. It exposes a function whose implementation mutates the global memblock state and depends on reset helpers.

## Dependencies And Integration Points
The include guard `_MEMBLOCK_BASIC_H` prevents duplicate declarations. The dependency on `common.h` ties this API to the local test harness rather than to a standalone memblock interface.

## Risks
The header is intentionally minimal. Its main risk is unnecessary coupling: including it pulls in all of `common.h`, including Linux and kselftest headers. That is acceptable for the local test tree but would be too broad for a production interface.

## Test Signals
The file itself has no executable checks. A build failure here would indicate declaration/header dependency drift; runtime signals come from `memblock_basic_checks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.c

## Purpose
`common.c` implements shared support for the memblock test binaries: resetting memblock state, allocating fake physical memory, setting up NUMA layouts, parsing command-line options, and emitting verbose kselftest-style pass/fail labels.

## Important APIs, Types, And Functions
Key exported helpers are `reset_memblock_regions()`, `reset_memblock_attributes()`, `setup_memblock()`, `setup_numa_memblock()`, `dummy_physical_memory_init()`, `dummy_physical_memory_cleanup()`, `dummy_physical_memory_base()`, `parse_args()`, `test_fail()`, `test_pass()`, `test_print()`, and the prefix stack operations. Global test state includes `static struct test_memory memory_block`, `static const char *prefixes[PREFIXES_MAX]`, `static int nr_prefixes`, `static int verbose`, and `bool movable_node_enabled`.

## Control Flow
`parse_args()` handles `--help`, `--movable-node`, and `--verbose`; help exits immediately. `setup_memblock()` resets region arrays, registers a `MEM_SIZE` range at the allocated dummy base, and fills dummy memory with byte value `1`. `setup_numa_memblock()` splits the dummy memory into eight node fractions expressed in basis points and sets hotplug flags unless `movable_node_enabled` simulates the `movable_node` kernel parameter. Prefix helpers build nested test names consumed by verbose pass/fail output.

## State And Persistence
All state is process-local. `dummy_physical_memory_init()` allocates `PHYS_MEM_SIZE` bytes with `malloc()` and `dummy_physical_memory_cleanup()` frees it. `reset_memblock_regions()` zeroes only the active portions of `memblock.memory.regions` and `memblock.reserved.regions`, then restores counts, max values, and totals. `reset_memblock_attributes()` restores names, allocation direction, and current limit.

## Dependencies And Integration Points
The file depends on Linux memblock and memory-hotplug headers, `getopt_long_only()`, `assert()`, `malloc/free`, kselftest output helpers, and the `movable_node_is_enabled()` stub behavior in the broader test harness. Tests in `basic_api.c` and allocation suites rely on this file to keep global memblock state deterministic.

## Risks
Because the helpers operate on the real global `memblock` object, missed cleanup can cascade into later tests. `reset_memblock_regions()` clears only `cnt` entries, so corruption outside the active count would persist. `setup_numa_memblock()` trusts the caller-provided fractions to add up sensibly; it asserts each fraction is at most 10000 but does not assert the sum equals 10000. Verbose output preserves `errno` around `vprintf()`, which avoids one class of test interference.

## Test Signals
Failures in shared setup usually surface as downstream assertion failures. Verbose mode adds kselftest pass/fail lines with nested prefixes, improving localization of a failed memblock API scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.h

## Purpose
`common.h` defines the shared memblock test harness contract: constants for fake memory sizing, assertion macros, basic data carriers, setup function declarations, and small inline utilities for pass reporting, top-down/bottom-up execution, and memory-content validation.

## Important APIs, Types, And Functions
Important constants are `MEM_SIZE`, `PHYS_MEM_SIZE`, `NUMA_NODES`, `INIT_MEMBLOCK_REGIONS`, and `INIT_MEMBLOCK_RESERVED_REGIONS`. `enum test_flags` controls raw allocation/content checks. `struct test_memory` wraps dummy allocated memory and `struct region` models base/size pairs. Assertion macros include equality, inequality, ordering, and byte-wise memory equality/inequality checks. Inline helpers include `region_end()`, `test_pass_pop()`, `run_top_down()`, `run_bottom_up()`, and `assert_mem_content()`.

## Control Flow
Macros call `test_fail()` before `assert()` when conditions are violated. `run_top_down()` and `run_bottom_up()` set the global memblock allocation direction, push a prefix, execute a caller-provided check function, and pop the prefix. `assert_mem_content()` chooses zeroed versus nonzero content expectations from `TEST_F_RAW`.

## State And Persistence
The header itself owns no storage, but its inline helpers mutate global memblock allocation direction through `memblock_set_bottom_up()` and mutate the prefix stack through `prefix_push()`/`prefix_pop()`.

## Dependencies And Integration Points
The header depends on Linux memblock, size, type, printk, and kselftest headers, plus libc `stdlib` and `assert`. It is the central integration point for all memblock test C files.

## Risks
Assertion macros evaluate arguments more than once only in a limited way, but callers should still avoid side effects in expected/seen expressions. `ASSERT_MEM_NE()` means every byte must differ from the expected byte; it is not a general "buffers differ" helper. Inline control-flow helpers assume the called test restores anything beyond allocation direction.

## Test Signals
The macros generate immediate abort-on-failure behavior, with optional verbose failure naming supplied by `common.c`. Build signals include whether kernel headers and kselftest headers remain compatible with this user-space harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/Kbuild -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/Kbuild

## Purpose
This `Kbuild` file builds the nvdimm test module stack by combining real driver sources with local test overrides. It enables link-time wrapping of kernel APIs so nvdimm, pmem, dax, and ACPI NFIT drivers can run against synthetic resources instead of real platform firmware or physical persistent memory.

## Important APIs, Types, And Functions
The file is build metadata rather than C code. Important declarations are the `ldflags-y += --wrap=...` lines for ioremap, memremap, resource request/release, ACPI evaluate calls, and `devm_memremap_pages`; source roots `DRIVERS`, `NVDIMM_SRC`, `ACPI_SRC`, and `DAX_SRC`; and module object lists such as `nfit-y`, `nd_pmem-y`, `device_dax-y`, `dax_pmem-y`, and `libnvdimm-y`.

## Control Flow
At build time, kbuild conditionally assembles modules based on configuration symbols. For example, `nfit-y` includes real ACPI NFIT core/intel code plus `acpi_nfit_test.o` and `config_check.o`, while `libnvdimm-y` includes real libnvdimm core objects plus `libnvdimm_test.o`. `obj-m += test/` delegates to the nested test module directory.

## State And Persistence
No runtime state is defined here. The persistent effect is the module composition and linker wrapping strategy encoded in build artifacts.

## Dependencies And Integration Points
This file integrates directly with in-tree kernel driver sources under `drivers/nvdimm`, `drivers/acpi/nfit`, and `drivers/dax`. It depends on the wrapper implementations in `test/iomap.c` and local watermark files to prove test-linked modules are loaded.

## Risks
The build is highly sensitive to internal driver object names and symbol signatures. New driver files, renamed functions, or changed wrapped API prototypes can silently omit behavior or fail module linking. The `KBUILD_CFLAGS` filtering removes missing-prototype/declaration warnings, which is practical for wrapping but can hide drift.

## Test Signals
Successful module build verifies that target config symbols are module-compatible and that wrapped symbols resolve. Runtime watermark calls and `config_check.o` provide additional signals that test modules, not base-tree modules, are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/Makefile

## Purpose
This Makefile provides a simple external-module entry point for building and installing the nvdimm test modules against a kernel tree.

## Important APIs, Types, And Functions
Build targets are `default` and `install`. `KDIR ?= ../../../` defaults the kernel source/build directory to the repository root relative to this tool directory.

## Control Flow
`default` invokes `$(MAKE) -C $(KDIR) M=$$PWD`, asking kbuild to build the current directory as an external module. `install` first builds, then invokes `modules_install` for the same module directory.

## State And Persistence
The Makefile itself holds no runtime state. The `install` target persists built modules into the kernel module install tree selected by kbuild.

## Dependencies And Integration Points
It depends on a kernel build tree that can process the local `Kbuild` file. It is a developer convenience wrapper around kbuild rather than part of the in-kernel module dependency graph.

## Risks
The default `KDIR` assumes the current repository layout. Invoking from unusual working directories is safe because `M=$$PWD` expands in the shell, but a wrong `KDIR` will build against the wrong tree or fail.

## Test Signals
A successful `make` proves kbuild can compile the module set. A successful `make install` additionally proves module installation permissions and paths are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/acpi_nfit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/acpi_nfit_test.c

## Purpose
`acpi_nfit_test.c` supplies a test watermark for the ACPI NFIT module and overrides `nfit_intel_shutdown_status()` so tests receive deterministic dirty-shutdown data.

## Important APIs, Types, And Functions
The `nfit_test_watermark(acpi_nfit)` macro emits and exports `acpi_nfit_test()`. The strong definition `nfit_intel_shutdown_status(struct nfit_mem *nfit_mem)` sets `NFIT_MEM_DIRTY_COUNT` and assigns `dirty_shutdown = 42`.

## Control Flow
The watermark function returns success when called by the test harness. The shutdown-status override is called by ACPI NFIT code in place of the production implementation and unconditionally marks the DIMM as having a dirty shutdown count.

## State And Persistence
The file mutates only the passed `struct nfit_mem`: its flag bitmap and `dirty_shutdown` field. There is no independent persistent state.

## Dependencies And Integration Points
It includes `watermark.h` and `<nfit.h>`, and relies on kbuild linking this object into the test `nfit` module after real ACPI NFIT sources. It integrates with sysfs/user tests expecting a stable dirty shutdown count.

## Risks
The override assumes the target symbol remains replaceable and that `NFIT_MEM_DIRTY_COUNT`/`dirty_shutdown` semantics remain stable. If production code changes to require additional shutdown-status fields, this deterministic stub could become incomplete.

## Test Signals
Calling `acpi_nfit_test()` confirms the test-linked module is active. Observing a dirty shutdown value of `42` confirms the override path was used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/acpi_nfit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/config_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/config_check.c

## Purpose
`config_check.c` enforces the module configuration assumptions required by the nvdimm test stack.

## Important APIs, Types, And Functions
The single function `check()` uses `BUILD_BUG_ON()` with `IS_MODULE()` and `IS_ENABLED()` predicates for `CONFIG_LIBNVDIMM`, `CONFIG_BLK_DEV_PMEM`, `CONFIG_ND_BTT`, `CONFIG_ND_PFN`, `CONFIG_ACPI_NFIT`, `CONFIG_DEV_DAX`, and `CONFIG_DEV_DAX_PMEM`.

## Control Flow
There is no runtime branching beyond compile-time constant evaluation. If a required config is not built as a module, compilation fails. `CONFIG_ACPI_NFIT` is only required as a module when enabled.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
Every major test module object list includes `config_check.o`, so incompatible kernel configurations fail early at build time rather than during module insertion.

## Risks
The checks intentionally reject built-in configurations for symbols that the tests need as loadable modules. Kernel config symbol renames or dependency changes require updating this file.

## Test Signals
The primary signal is a build-time failure. A successful build means the required driver components can be replaced or supplemented by the test modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/config_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax-dev.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax-dev.c

## Purpose
`dax-dev.c` overrides `dax_pgoff_to_phys()` for the nvdimm test environment. It maps DAX page offsets through synthetic nfit resources and converts vmalloc-backed test memory to real page frame numbers when needed.

## Important APIs, Types, And Functions
The key function is `phys_addr_t dax_pgoff_to_phys(struct dev_dax *dev_dax, pgoff_t pgoff, unsigned long size)`. It uses `struct dev_dax_range`, `struct range`, `range_len()`, `PHYS_PFN()`, `PFN_PHYS()`, `get_nfit_res()`, `vmalloc_to_page()`, and `page_to_pfn()`.

## Control Flow
The function walks `dev_dax->ranges`, finds the range containing the requested `pgoff`, computes the physical address, and verifies `addr + size - 1` fits in the range. If the address belongs to a synthetic nfit resource, it refuses huge alignment greater than `PAGE_SIZE`, maps the vmalloc address to a page, and returns that PFN as a physical address. Otherwise it returns the computed address. Failure returns `-1` in a `phys_addr_t`.

## State And Persistence
No local state is persisted. The function reads live `dev_dax` range data and synthetic resource registrations managed by the nfit/ndtest modules.

## Dependencies And Integration Points
This file includes the private DAX header from `drivers/dax` and the nfit test lookup interface. It is linked into the test `device_dax` module to adapt production DAX behavior to vmalloc-backed fake persistent memory.

## Risks
Returning `-1` as `phys_addr_t` relies on callers treating it as an invalid physical address. The `addr + size - 1` check can be sensitive to overflow if callers pass extreme sizes. The synthetic-resource path only supports page-sized alignment, limiting coverage for larger-aligned DAX configurations.

## Test Signals
Successful device-dax tests over nfit resources demonstrate correct pgoff-to-vmalloc PFN translation. Failures often appear as invalid PFNs, alignment rejection, or inability to map synthetic DAX ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax_pmem_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax_pmem_test.c

## Purpose
`dax_pmem_test.c` provides a watermark function for the test-linked `dax_pmem` module.

## Important APIs, Types, And Functions
`nfit_test_watermark(dax_pmem)` defines and exports `dax_pmem_test()`.

## Control Flow
The generated function logs a debug message containing `KBUILD_MODNAME` and returns `0`.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
The file depends on `watermark.h` and is linked into the `dax_pmem` test module. `nfit.c` and `ndtest.c` call `dax_pmem_test()` at module init to validate the module composition.

## Risks
The file only proves linkage; it does not validate dax-pmem behavior. If omitted from the module object list, callers would fail to link or runtime watermark validation would be absent.

## Test Signals
The signal is the exported `dax_pmem_test()` returning success and optionally emitting a debug log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax_pmem_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/device_dax_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/device_dax_test.c

## Purpose
`device_dax_test.c` provides a watermark function for the test-linked `device_dax` module.

## Important APIs, Types, And Functions
`nfit_test_watermark(device_dax)` defines and exports `device_dax_test()`.

## Control Flow
The generated function logs a debug message and returns `0`.

## State And Persistence
No persistent state is introduced.

## Dependencies And Integration Points
The file integrates with the nvdimm test module init paths, which call `device_dax_test()` to confirm that the device-dax module being exercised is the test-composed one.

## Risks
This is a linkage sentinel only. It cannot catch behavioral regressions in DAX mapping or resource handling by itself.

## Test Signals
The exported function returning `0` is the positive signal; missing symbol or wrong module composition is the failure signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/device_dax_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/libnvdimm_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/libnvdimm_test.c

## Purpose
`libnvdimm_test.c` provides a watermark function for the test-linked `libnvdimm` module.

## Important APIs, Types, And Functions
`nfit_test_watermark(libnvdimm)` defines and exports `libnvdimm_test()`.

## Control Flow
The generated watermark logs the current module name at debug level and returns success.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
The file depends on `watermark.h` and is linked into the test `libnvdimm` module. Both ACPI NFIT and non-NFIT test modules call this watermark at init.

## Risks
It does not verify libnvdimm runtime behavior; it only confirms test linkage.

## Test Signals
Success is the presence and successful call of `libnvdimm_test()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/libnvdimm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem-dax.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem-dax.c

## Purpose
`pmem-dax.c` overrides pmem direct-access behavior for the test environment. It adapts `__pmem_direct_access()` so vmalloc-backed fake nvdimm resources can be exposed through DAX paths.

## Important APIs, Types, And Functions
The key function is `long __pmem_direct_access(struct pmem_device *pmem, pgoff_t pgoff, long nr_pages, enum dax_access_mode mode, void **kaddr, unsigned long *pfn)`. It uses `is_bad_pmem()`, `get_nfit_res()`, `vmalloc_to_page()`, `page_to_pfn()`, `PHYS_PFN()`, and pmem fields such as `data_offset`, `phys_addr`, `virt_addr`, `size`, `pfn_pad`, and `bb`.

## Control Flow
The function computes a byte offset from `pgoff` plus pmem data offset, rejects bad blocks with `-EIO`, and then branches on whether the target physical address belongs to an nfit test resource. Synthetic resources return a direct kernel address and a vmalloc-derived PFN, capped to one page. Non-test resources return production-style address/PFN data and either the requested page count when badblocks exist or the remaining good PFN span.

## State And Persistence
No local state persists. The function reads badblock state from the pmem device and resource membership from the nfit test registry.

## Dependencies And Integration Points
It depends on pmem internals, libnvdimm headers, Linux DAX interfaces, and the nfit test lookup API. It is linked into the test `nd_pmem` module alongside real `drivers/nvdimm/pmem.o`.

## Risks
The synthetic path intentionally limits DAX to one page at a time because backing memory is vmalloc-based. Tests that expect multi-page direct mappings over fake resources must account for this. Badblock checks operate before synthetic-resource handling, so injected badblocks still prevent direct access.

## Test Signals
Correct signals are successful namespace/DAX accesses over fake nfit resources, valid `kaddr` values, and PFNs corresponding to vmalloc pages. Error signals include `-EIO` for bad pmem and unexpectedly short direct-access spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem-dax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem_test.c

## Purpose
`pmem_test.c` provides a watermark function for the test-linked pmem module.

## Important APIs, Types, And Functions
`nfit_test_watermark(pmem)` defines and exports `pmem_test()`.

## Control Flow
The generated function logs a debug message and returns `0`.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
The watermark is linked into the `nd_pmem` test module and called by the nfit/ndtest module init paths to validate module composition.

## Risks
It is a sentinel only and does not validate pmem read/write, badblock, or DAX behavior.

## Test Signals
Presence and successful return of `pmem_test()` confirm the test module is linked as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/Kbuild -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/Kbuild

## Purpose
The nested nvdimm test `Kbuild` builds the synthetic platform modules: the NFIT/ND test module and the iomap wrapper module.

## Important APIs, Types, And Functions
It sets include paths for `drivers/nvdimm` and `drivers/acpi/nfit`, declares `obj-m += nfit_test.o` and `obj-m += nfit_test_iomap.o`, conditionally chooses `nfit.o` or `ndtest.o` as the body of `nfit_test-y`, and maps `nfit_test_iomap-y := iomap.o`.

## Control Flow
At build time, if `CONFIG_ACPI_NFIT=m`, `nfit_test` is built from `nfit.c` and `ndtest.o` is also built as its own module. Otherwise, `nfit_test` is backed by `ndtest.c`. The iomap wrapper module is always built from `iomap.c`.

## State And Persistence
No runtime state is stored. The build output persists the chosen module composition.

## Dependencies And Integration Points
This file integrates the wrapper layer in `iomap.c` with either the ACPI NFIT emulator or the non-NFIT test bus. It relies on config state already checked by the parent nvdimm build.

## Risks
The conditional means module names and behavior differ depending on `CONFIG_ACPI_NFIT`. Test scripts must know whether to load `nfit_test` as NFIT or non-NFIT and whether `ndtest` exists separately.

## Test Signals
Build output showing `nfit_test`, `nfit_test_iomap`, and optionally `ndtest` is the main signal. Runtime module insertion validates the selected branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/iomap.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/iomap.c

## Purpose
`iomap.c` is the interception layer that lets real nvdimm, DAX, and ACPI code operate on synthetic in-memory resources. It supplies `--wrap` implementations for memory mapping, I/O resource allocation, and ACPI evaluation.

## Important APIs, Types, And Functions
The public test setup API is `nfit_test_setup(lookup, evaluate)`, `nfit_test_teardown()`, and `get_nfit_res()`. Wrapped functions include `__wrap_devm_ioremap()`, `__wrap_devm_memremap()`, `__wrap_devm_memremap_pages()`, `__wrap_memremap()`, `__wrap_devm_memunmap()`, `__wrap_ioremap()`, `__wrap_ioremap_wc()`, `__wrap_iounmap()`, `__wrap_memunmap()`, request/release-region wrappers, insert/remove-resource wrappers, `__wrap_acpi_evaluate_object()`, and `__wrap_acpi_evaluate_dsm()`.

## Control Flow
`nfit_test_setup()` stores lookup/evaluate callbacks in a global RCU-protected list. Mapping wrappers first ask `get_nfit_res()` whether the requested offset or address belongs to a synthetic resource; if so they return an address inside `nfit_res->buf`, otherwise they delegate to the real kernel function. Region request wrappers record synthetic subrequests in `nfit_res->requests` under a spinlock, optionally registering devres cleanup. ACPI `_FIT` evaluation returns the prebuilt fake NFIT object, while DSM evaluation delegates to the registered test callback before falling back to real ACPI.

## State And Persistence
State lives in the global `iomap_head` list and a single `iomap_ops` record. Each `nfit_test_resource` also owns a request list protected by its lock. Devres actions make requested regions and dev_pagemap references device-lifetime scoped.

## Dependencies And Integration Points
This module depends on linker `--wrap` flags from the parent `Kbuild`, RCU, devres, ACPI APIs, resource APIs, and `nfit_test.h`. It is the central integration point between synthetic resources allocated in `nfit.c`/`ndtest.c` and production driver code.

## Risks
The file assumes only one active `iomap_ops` provider and uses the first RCU list entry. Wrapper signature drift is a major compatibility risk. Address matching accepts both resource starts and vmalloc buffer addresses, which is necessary for unmap paths but can mask bugs if arbitrary addresses overlap synthetic buffers. Some devres allocation failure paths can leave request records allocated after a resource was created.

## Test Signals
Successful tests prove real drivers requested, mapped, and unmapped fake resources through the wrapper layer. Useful signals include absence of duplicate-resource warnings, correct ACPI `_FIT` data delivery, and fallback to real APIs for non-test resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.c

## Purpose
`ndtest.c` implements a synthetic non-ACPI nvdimm platform for exercising libnvdimm, pmem, DAX, labels, region registration, and PAPR-style sysfs attributes without real NFIT firmware.

## Important APIs, Types, And Functions
Important static data defines two bus instances, DIMM groups, and region mappings. Core functions include `ndtest_ctl()`, `ndtest_resource_lookup()`, `ndtest_alloc_resource()`, `ndtest_create_region()`, `ndtest_init_regions()`, `ndtest_dimm_register()`, `ndtest_nvdimm_init()`, `ndtest_bus_register()`, `ndtest_probe()`, `ndtest_init()`, and `ndtest_exit()`. Sysfs attributes expose DIMM handles, failure injection fields, PAPR metadata, region range indexes, and health flags.

## Control Flow
Module init calls watermark functions, registers the nfit test lookup provider, creates a class and a 4 GiB aligned gen_pool, registers two platform devices, and then registers the platform driver. Probe registers an nvdimm bus, allocates DMA arrays, creates label/DIMM/DCR synthetic resources, registers nvdimms, creates pmem or IO regions, and installs devres cleanup. Control commands support label config size/get/set and optional failure injection through per-DIMM `fail_cmd` and `fail_cmd_code`.

## State And Persistence
Global state includes `instances[NUM_INSTANCES]`, `ndtest_pool`, and static bus/dimm/region descriptors. Runtime state is stored in each `struct ndtest_priv`: platform device, resource list, bus descriptor, nvdimm bus, DMA arrays, and selected config. DIMM state includes label buffers, flags, command failure masks, and registered device pointers. No state persists beyond module lifetime.

## Dependencies And Integration Points
The file integrates with libnvdimm through `nvdimm_bus_register()`, `nvdimm_create()`, `nvdimm_pmem_region_create()`, and command masks. It integrates with the mapping wrapper through `nfit_test_setup(ndtest_resource_lookup, NULL)` and resource records compatible with `iomap.c`. It also exposes PAPR SCM-like attributes and flags for userspace nvdimm tests.

## Risks
The global static configs are mutated in-place when DIMMs are registered, so repeated load/unload depends on cleanup resetting all observable state. `NUM_DCR` is four while the second bus pushes IDs using `dimm_start`; the code sizes DMA arrays to `NUM_DCR`, so additions to the configured DIMM count need careful bounds review. Failure injection uses bit shifts of command numbers; large command IDs would overflow the mask.

## Test Signals
Signals include successful module insertion, creation of two nvdimm buses, DIMM and region sysfs attributes, functioning label get/set commands, and ability to inject command failures through sysfs. Runtime resource lookup warnings indicate missing synthetic-resource registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.h -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.h

## Purpose
`ndtest.h` defines the private data model for the non-NFIT nvdimm test platform.

## Important APIs, Types, And Functions
Important structures are `ndtest_priv`, `ndtest_blk_mmio`, `ndtest_dimm`, `ndtest_mapping`, `ndtest_region`, and `ndtest_config`. These types describe synthetic platform devices, DIMM metadata, label and MMIO resources, region mappings, and per-bus configuration.

## Control Flow
The header contains declarations only. Runtime behavior is implemented in `ndtest.c`, which allocates and populates these structures during platform probe.

## State And Persistence
The structures hold module-lifetime state: registered device pointers, resource lists, nvdimm bus descriptors, DMA addresses, labels, command failure settings, region definitions, and mappings. None is persisted outside the module.

## Dependencies And Integration Points
The header depends on Linux platform-device and libnvdimm types. It is included by `ndtest.c` and complements `nfit_test.h` resource definitions used by the shared iomap wrapper.

## Risks
The structures expose raw pointers and fixed-size counters without helper APIs, so consistency is maintained by convention in `ndtest.c`. Expanding mappings beyond `NDTEST_MAX_MAPPING` in implementation would require coordinated changes.

## Test Signals
There are no direct test signals. Compile success verifies structural compatibility with current libnvdimm headers; runtime signals come from the module using these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit.c -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit.c

## Purpose
`nfit.c` is a full synthetic ACPI NFIT platform emulator. It builds fake NFIT tables, allocates vmalloc-backed persistent-memory resources, registers platform devices, and implements command handlers for labels, ARS, bad-range injection, Intel SMART, firmware update/activation, security, and hotplug notification behavior.

## Important APIs, Types, And Functions
Important state types include `struct nfit_test`, `struct nfit_test_dcr`, `struct nfit_test_sec`, and `struct nfit_test_fw`. Major functions include `nfit_test_ctl()`, `nfit_test0_alloc()`, `nfit_test1_alloc()`, `nfit_test0_setup()`, `nfit_test1_setup()`, `nfit_ctl_test()`, `nfit_test_probe()`, `nfit_test_init()`, `nfit_test_exit()`, `nfit_test_lookup()`, `test_alloc()`, and many command helpers for ARS, SMART, firmware, and security flows.

## Control Flow
Module init validates watermark modules, registers the shared iomap callbacks, creates a workqueue, class, and aligned gen_pool, allocates two platform-device instances, and registers the platform driver. Probe optionally runs `nfit_ctl_test()` for ACPI control parsing, allocates per-instance arrays, invokes the instance-specific allocator/setup pair, initializes the ACPI NFIT descriptor, and calls `acpi_nfit_init()`. Instance 0 is then rebuilt with hotplug enabled, exported through fake `_FIT`, and an ACPI notify is sent.

## State And Persistence
Global state includes `instances[NUM_NFITS]`, `nfit_pool`, `nfit_wq`, `dimm_fail_cmd_flags`, `dimm_fail_cmd_code`, `dimm_sec_info`, `last_activate`, and DSM `result`. Per-instance state includes the NFIT table buffer, resource list, vmalloc/DMA arrays for DIMMs, labels, flush hints, DCRs, SPA sets, ARS status, badrange list, SMART thresholds, firmware state, and test DIMM devices. All state is module-lifetime and cleaned via devres, platform unregister, workqueue destruction, and gen_pool destruction.

## Dependencies And Integration Points
The file is tightly coupled to ACPI NFIT, libnvdimm, nfit Intel DSM definitions, badrange helpers, platform devices, genalloc, vmalloc, and the `iomap.c` wrapper layer. It integrates with real production code by linking real ACPI NFIT driver sources into the test module and supplying fake ACPI tables/resources underneath.

## Risks
The file encodes detailed ACPI NFIT structure layouts, command IDs, status codes, and topology assumptions, so upstream structure or semantic changes can break tests. Many command paths trust buffer lengths but use packed, variable-length command layouts that require careful size accounting. Global security and firmware state is indexed by DIMM handle and can be affected by load/unload or multi-instance assumptions. Workqueue-based ARS error notification and timed firmware/security transitions rely on jiffies, making timing-sensitive tests possible.

## Test Signals
Signals include module insertion, successful `nfit_ctl_test()` checks for ACPI command parsing, creation of NFIT regions/nvdimms, hotplug notify behavior, label read/write success, ARS start/status/clear and injection behavior, SMART threshold notifications, command failure injection through sysfs, security state transitions, and firmware update/activation state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit_test.h

## Purpose
`nfit_test.h` defines shared contracts for the nvdimm test wrapper layer and synthetic NFIT/ND command payloads.

## Important APIs, Types, And Functions
Important resource types are `struct nfit_test_request` and `struct nfit_test_resource`. Command structures cover NFIT translate-SPA and ARS error injection plus Intel SMART, SMART thresholds, SMART injection, firmware update, firmware query, and latch-shutdown-status payloads. Callback typedefs `nfit_test_lookup_fn` and `nfit_test_evaluate_dsm_fn` connect resource providers to `iomap.c`. The header declares all wrapper functions and setup/teardown/resource lookup APIs.

## Control Flow
There is no implementation control flow. The declarations enable `nfit.c`, `ndtest.c`, and `iomap.c` to share resource lookup and command structure definitions.

## State And Persistence
The defined structures model module-lifetime resource state: resource ranges, vmalloc buffers, request subregions, locks, device owners, and command payloads. Actual storage is allocated by `nfit.c` or `ndtest.c`.

## Dependencies And Integration Points
The header depends on ACPI, list, UUID, resource, and spinlock kernel headers. It is the central ABI between the synthetic platform modules and the link-time wrappers.

## Risks
The packed command structures must match driver/user ABI expectations exactly. Comments note variable input data layouts, making offset and status placement easy to break. Adding wrapper declarations requires matching linker flags in `Kbuild`.

## Test Signals
Compile success verifies that wrapper prototypes and command payloads match the current kernel headers. Runtime signals are produced by the modules that allocate `nfit_test_resource` instances and service these command payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/watermark.h -->
# sources/distributed-fs/ceph-client/tools/testing/nvdimm/watermark.h

## Purpose
`watermark.h` defines tiny exported test functions used to verify that test-composed nvdimm modules are linked and loaded instead of standard base-tree modules.

## Important APIs, Types, And Functions
It declares watermark functions for pmem, libnvdimm, acpi_nfit, device_dax, dax_pmem, and dax_pmem variants. The `nfit_test_watermark(x)` macro defines `int x##_test(void)` and exports it.

## Control Flow
Each generated watermark function emits a debug message containing `KBUILD_MODNAME` and returns `0`.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
Watermark C files include this header to generate exported symbols. `nfit.c` and `ndtest.c` call the symbols during module initialization.

## Risks
The macro requires including files to have `pr_debug`, `KBUILD_MODNAME`, and `EXPORT_SYMBOL` available. It validates module composition only, not behavior.

## Test Signals
Successful symbol resolution and return value `0` are the intended signals. Debug output identifies which module supplied the watermark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/nvdimm/watermark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/Makefile

## Purpose
This Makefile builds user-space radix-tree, XArray, Maple tree, IDR, IDA, regression, iteration, and benchmark tests from kernel library sources plus local harness files.

## Important APIs, Types, And Functions
Important variables are `TARGETS`, `CORE_OFILES`, and `OFILES`. Targets include `main`, `idr-test`, `multiorder`, `xarray`, and `maple`. Special object dependencies map `xarray.o` to `../../../lib/test_xarray.c` and `idr-test.o` to `../../../lib/test_ida.c`.

## Control Flow
The `targets` target builds generated headers and all test binaries. `main` links the full object set. Focused binaries link subsets such as `idr-test.o $(CORE_OFILES)`. `clean` removes binaries, objects, generated headers, and generated source copies.

## State And Persistence
The Makefile persists generated headers under `generated/` and compiled objects/binaries. No runtime state is defined.

## Dependencies And Integration Points
It includes `../shared/shared.mk`, which supplies common user-space kernel-test build rules and generated headers. It integrates local test harness code with selected kernel library test sources.

## Risks
The object list must stay synchronized with test source files and upstream kernel library test locations. The `clean` target deletes generated local copies such as `radix-tree.c` and `idr.c`, so any manual edits to generated files would be lost.

## Test Signals
Successful builds of `main` and focused targets verify that user-space shims and generated headers are compatible with current kernel tree code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/benchmark.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/benchmark.c

## Purpose
`benchmark.c` measures insertion, tagging, iteration, and deletion costs for radix trees across multiple tree sizes and index steps.

## Important APIs, Types, And Functions
Important functions are `benchmark_iter()`, `benchmark_insert()`, `benchmark_tagging()`, `benchmark_delete()`, `benchmark_size()`, and public `benchmark()`. It uses radix-tree iteration macros, tag APIs, `item_insert()`, `item_delete()`, `item_kill_tree()`, `rcu_barrier()`, and `clock_gettime(CLOCK_MONOTONIC)`.

## Control Flow
`benchmark()` loops over sizes `1 << 10` and `1 << 20` and a range of sparse/dense step values. For each pair, `benchmark_size()` inserts items, tags them, measures tagged and untagged iteration, deletes items, and kills any remaining tree state. When compiled with `BENCHMARK`, `benchmark_iter()` repeats loops enough to get stable timing.

## State And Persistence
State is local to each `RADIX_TREE(tree, GFP_KERNEL)` instance. The volatile `sink` in `benchmark_iter()` prevents the compiler from discarding iteration work. No results are persisted outside printed output.

## Dependencies And Integration Points
This file depends on the local radix-tree user-space harness and is invoked at the end of `main.c` after functional tests. It uses `printv()` so output volume is controlled by verbosity.

## Risks
Timing is environment-sensitive and not a pass/fail signal. Without `BENCHMARK`, single-pass measurements for small trees can be noisy. The benchmark also depends on test item allocation behavior and RCU cleanup.

## Test Signals
The primary signal is performance output at verbosity level 2 and absence of leaks/assertion failures after cleanup. Functional regressions usually surface through allocation or deletion assertions in shared item helpers rather than timing values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/idr-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/idr-test.c

## Purpose
`idr-test.c` exercises the IDR and IDA APIs in the user-space radix-tree harness, including cyclic allocation, NULL entries, preload/no-wait behavior, 32-bit ID boundaries, iteration alignment, RCU lookup races, memory-allocation failure paths, and threaded IDA stress.

## Important APIs, Types, And Functions
Major IDR functions include `idr_alloc_test()`, `idr_alloc2_test()`, `idr_replace_test()`, `idr_null_test()`, `idr_nowait_test()`, `idr_get_next_test()`, `idr_u32_test()`, `idr_align_test()`, `idr_find_test()`, and `idr_checks()`. IDA functions include `ida_check_nomem()`, `ida_check_conv_user()`, `ida_check_random()`, `ida_alloc_free_test()`, `user_ida_checks()`, `ida_thread_tests()`, and `ida_tests()`. The file includes `../../../lib/test_ida.c` after defining module stubs.

## Control Flow
`idr_checks()` runs a broad deterministic sequence: fill/remove/destroy cycles, boundary allocations near `INT_MAX`, cyclic wraparound, base-offset tests, NULL replacement, preload tests, u32 handle tests, alignment iteration, and RCU find-race tests. IDA tests simulate no-memory paths with `GFP_NOWAIT`, conversion between exceptional entries and bitmaps, random allocate/free loops, and multithreaded random/leak tests. A weak `main()` runs this file standalone when not linked into the full harness.

## State And Persistence
Most state is local IDR/IDA instances. `DEFINE_IDR(find_idr)` is global for the concurrent find test. Threads register with the user-space RCU harness and clean up after time-bounded loops. No durable state is persisted.

## Dependencies And Integration Points
The file depends on Linux IDR/IDA APIs, XArray value encoding, local `struct item` helpers, pthreads, RCU user-space shims, and the kernel `test_ida.c` source. It is called from `main.c` as part of full radix-tree testing and can run as `idr-test`.

## Risks
Several tests are time-bound and randomized, so failures can be seed or scheduling sensitive. The `idr_u32_test()` path intentionally exercises IDs above `INT_MAX`, where `idr_get_next()` cannot represent them and warnings are expected. The included `test_ida.c` means upstream changes in that file directly affect this test.

## Test Signals
Signals are assertion/BUG_ON absence, no leftover allocations after RCU barriers, and successful thread joins. Printed warnings around large u32 IDs are expected and bracketed by messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/idr-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check.c

## Purpose
`iteration_check.c` stress-tests XArray iteration while entries are concurrently inserted, removed, tagged, and retagged. It targets races involving retry entries, deleted nodes, paused iteration, RCU protection, and multi-order entries.

## Important APIs, Types, And Functions
Important constants are `NUM_THREADS`, `MAX_IDX`, `TAG`, and `NEW_TAG`. Functions include `my_item_insert()`, thread functions `add_entries_fn()`, `tagged_iteration_fn()`, `untagged_iteration_fn()`, `remove_entries_fn()`, `tag_entries_fn()`, and public `iteration_test(order, test_duration)`.

## Control Flow
`iteration_test()` seeds three per-thread random generators, sets `max_order`, starts five pthreads, sleeps for the requested duration, flips `test_complete`, joins all threads, and frees the XArray. Insertion attempts the largest conflict-free order down to zero under `xas_lock()`, handles allocation retry through `xas_nomem()`, and marks stored entries. Iterator threads repeatedly scan tagged or all entries under RCU, using `xas_retry()` and occasionally `xas_pause()` with an intervening `rcu_barrier()`. Other threads erase random entries and copy tags.

## State And Persistence
Global test state includes the thread array, random seeds, `DEFINE_XARRAY(array)`, `test_complete`, and `max_order`. State is reset at the start of each `iteration_test()` invocation and destroyed by `item_kill_tree()` at the end.

## Dependencies And Integration Points
This file depends on XArray advanced state APIs, local item allocation/free helpers, pthreads, sleep, and the user-space RCU harness. `main.c` calls it twice: once with order 0 and once with order 7.

## Risks
The test is inherently timing-sensitive. It catches concurrency bugs by running races for a duration rather than by deterministic interleavings, so weak machines or short durations may reduce coverage. The shared `rand_r()` seeds avoid global `rand()` races but still produce nondeterministic behavior from the main seed.

## Test Signals
The main signal is no crash, assertion, deadlock, or leak during the timed run. Failures often appear as invalid iteration, use-after-free under RCU, allocation accounting mismatches, or hangs during join.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check_2.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check_2.c

## Purpose
`iteration_check_2.c` is a targeted XArray regression test ensuring that deleting tagged entries below a stable tagged entry does not cause an RCU marked iterator to finish early.

## Important APIs, Types, And Functions
Key functions are thread functions `iterator()` and `throbber()`, plus public `iteration_test2(test_duration)`. It uses `XA_STATE`, `xas_for_each_marked()`, `xa_store()`, `xa_set_mark()`, `xa_erase()`, and `xa_destroy()`.

## Control Flow
`iteration_test2()` creates an XArray with a permanent tagged value at index 100, starts an iterator thread and a throbber thread, runs for the requested duration, then joins both threads and destroys the array. The throbber repeatedly stores and marks entries 0 through 99, then erases them. The iterator repeatedly scans marked entries under RCU and asserts that the final iterator index reaches at least 100.

## State And Persistence
`test_complete` is a static volatile flag shared by both threads. The XArray is local to the test invocation and destroyed at the end.

## Dependencies And Integration Points
The file depends on pthreads, XArray state iteration, RCU shims, and the local test harness. `main.c` runs it after the broader iteration tests.

## Risks
Like other race tests, coverage depends on timing and scheduler behavior. The volatile flag is sufficient for this simple test harness but is not a general synchronization pattern for production code.

## Test Signals
The decisive signal is the `assert(xas.xa_index >= 100)` in the iterator. Any early termination of marked iteration under concurrent lower-index deletion aborts the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/iteration_check_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/main.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/main.c

## Purpose
`main.c` is the primary orchestrator for the user-space radix-tree/XArray test binary. It combines deterministic checks, randomized stress, regression tests, IDR/IDA tests, iteration race tests, and benchmarks.

## Important APIs, Types, And Functions
Important functions include `__gang_check()`, `gang_check()`, `__big_gang_check()`, `big_gang_check()`, `add_and_check()`, `dynamic_height_check()`, `check_copied_tags()`, `copy_tag_check()`, `single_thread_tests()`, and `main()`. It calls external suites: `xarray_tests()`, `regression*_test()`, `multiorder_checks()`, `tag_check()`, `idr_checks()`, `ida_tests()`, `iteration_test()`, `iteration_test2()`, and `benchmark()`.

## Control Flow
`main()` parses `-l` for long runs, `-s` for random seed, and `-v` for verbosity; initializes random state, RCU, and radix-tree infrastructure; runs external regression/iteration suites; then runs single-thread tests and benchmarks. Gang checks insert contiguous ranges around large indexes and verify lookup/gang scan behavior. `dynamic_height_check()` verifies radix-tree height grows and shrinks as expected. `copy_tag_check()` creates randomized tagged entries near range boundaries and verifies `tag_tagged_items()` copies tags only inside the requested range.

## State And Persistence
State is mostly local radix-tree roots and stack arrays. Global harness state includes `test_verbose`, allocation counters, preempt count, and RCU registration. The random seed can be fixed for reproducibility. No durable state is written.

## Dependencies And Integration Points
The file depends on the local test harness, Linux radix-tree APIs, regression headers, XArray/radix-tree/IDR/IDA test functions, pthread-backed RCU shims, and benchmark support. It is the `main` target in the radix-tree Makefile.

## Risks
Randomized tests can expose rare failures but require preserving seeds for reproduction. Long-run mode expands stress durations and loop counts substantially. The code relies on `assert()` and abort-style failure, so partial results are not summarized after a failure.

## Test Signals
Positive signals are the printed seed, "running tests", no assertion failures, `tests completed`, and clean RCU/allocation accounting after `rcu_barrier()`. Failures are typically assertion aborts, explicit `abort()`, allocation leaks, or hangs in threaded tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/main.c -->
