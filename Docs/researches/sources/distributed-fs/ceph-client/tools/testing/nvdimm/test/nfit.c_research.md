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
