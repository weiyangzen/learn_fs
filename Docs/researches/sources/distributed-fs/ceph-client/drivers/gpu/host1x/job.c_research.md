<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.c

## Purpose

`job.c` implements host1x job allocation, reference counting, command descriptor construction, buffer pinning, relocation patching, optional command firewall validation/copying, unpin cleanup, and debug dumping.

## Important APIs, Types, And Functions

- `host1x_job_alloc()` lays out one allocation containing the job, relocs, unpin records, command descriptors, and DMA address arrays, with overflow checks.
- `host1x_job_get()` / `host1x_job_put()` manage references and release fences, syncpoints, and caller resources.
- `host1x_job_add_gather()` and `host1x_job_add_wait()` append command descriptors.
- `pin_job()` pins relocation targets and, when firewall is disabled, gather BOs; it creates IOMMU mappings for discontiguous gather SG tables where needed.
- `copy_gathers()` copies command buffers into trusted WC memory and validates opcodes/relocations when the firewall is enabled.
- `do_relocs()` patches relocation target addresses into gather command buffers or the firewall copy.
- `host1x_job_pin()` and `host1x_job_unpin()` are the public pin/unpin pair.

## Control Flow

Job allocation reserves enough trailing memory for the requested relocs/gathers/unpins. Pinning first pins relocation targets and validates access direction. If command firewall is enabled, gather buffers are copied into a host-owned DMA buffer, validated opcode by opcode, then relocated in the copy. Without firewall, gather BOs are pinned directly, mapped into contiguous IOVA if required, and relocated in place. On any pin error, previously pinned resources are unwound.

The firewall validator decodes host1x opcodes, tracks remaining words, class/register/count/mask state, and requires relocations for address registers reported by the client callback. Only supported opcodes are accepted; unknown or malformed streams return `-EINVAL`.

## State And Persistence Behavior

Jobs persist by kref while queued in CDMA and while users hold references. Pinning persists BO references, DMA mappings, IOVA allocations, copied gather buffers, relocated command words, `num_unpins`, and address arrays. Unpin releases mappings/BO refs and frees firewall gather copies.

## Dependencies And Integration Points

Depends on public host1x job structures, BO pin/mmap APIs, DMA/IOMMU/IOVA, channel/CDMA submit, syncpoints, fences, and client callbacks such as `is_addr_reg` and `is_valid_class`. DRM Tegra submit code populates these jobs.

## Risks And Edge Cases

Firewall validation accepts only a subset of opcodes and requires relocation ordering to match address-register writes. `copy_gathers()` must free its DMA copy on later unpin even after validation failure. IOMMU map failures and multi-chunk relocation targets are rejected. Relocation shifts are currently unsupported by validation. Tests should cover overflow allocation rejection, pin failure unwinds, firewall valid/invalid streams, duplicate gather BO handling, IOMMU gather mapping, and fence cleanup in `job_free()`.

## Test Signals

Submit tests with reloc read/write/bidirectional flags, firewall on/off, invalid class/register opcodes, address registers without relocations, gathers above 4 GiB, command-buffer copy allocation fallback, and timeout unpin paths provide strong coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.c -->
