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
