# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/spapr.c

## Purpose
`spapr.c` implements the XIVE backend for pseries/sPAPR guests. It translates the generic XIVE core operations into PAPR `H_INT_*` hypercalls, manages guest-available logical interrupt source number ranges, shares queue pages for secure guests, and initializes XIVE from the pseries device tree and option-vector state.

## Important APIs, Types, And Functions
`struct xive_irq_bitmap` tracks allocatable LISN ranges from `ibm,xive-lisn-ranges`; helpers add, allocate, free, and remove these bitmaps. PAPR wrappers include `plpar_int_reset`, source info/config get/set, queue info/config get/set, `plpar_int_sync`, and `plpar_int_esb`. Backend callbacks in `xive_spapr_ops` include IRQ data population, IRQ configuration, queue setup/cleanup, IPI get/put, update pending, ESB read/write via hcall, shutdown, source sync, and debug display.

## Control Flow
Initialization checks architecture vector 5 and `xive=off` policy, finds `ibm,power-ivpe`, maps the OS TIMA window, computes an allowed priority from `ibm,plat-res-int-priorities`, builds LISN allocator bitmaps, selects a queue size, then calls `xive_core_init`. Interrupt source population calls `H_INT_GET_SOURCE_INFO`, records StoreEOI/LSI/H_INT_ESB flags, and either relies on hypercall ESB access or maps EOI/trigger pages. Queue setup allocates a queue page, asks for queue notification info, programs `H_INT_SET_QUEUE_CONFIG`, and shares the page with the ultravisor for secure guests. Interrupt acknowledgement reads `TM_SPC_ACK_OS_REG`, updates pending priority bits, and lets common code drain queues.

## State And Persistence
The backend keeps runtime queue shift and a list of LISN allocation bitmaps. Allocated IPI LISNs are marked in these bitmaps until CPU teardown. Queue pages are normal kernel pages but become shared/unshared with the ultravisor for secure guests. Hypervisor-side interrupt source and queue configuration is mutable runtime state reset by `H_INT_RESET`.

## Dependencies And Integration Points
Dependencies include PAPR hcalls, RTAS-like busy delay semantics, flattened and live device tree data, PowerPC TIMA registers, secure guest helpers `is_secure_guest`, `uv_share_page`, and `uv_unshare_page`, and the shared XIVE core. It integrates with pseries machine init and uses `machine_arch_initcall(pseries, xive_core_debug_init)`.

## Risks
Hypercalls may return busy and require delay/retry; missing retries would cause transient boot or interrupt setup failures. LISN bitmap locking must protect concurrent IPI allocation. H_INT_ESB sources deliberately skip MMIO mapping, so common ESB access depends on the `esb_rw` callback. Secure guest page share/unshare balance is required for memory isolation. Priority selection must avoid hypervisor-reserved priorities.

## Test Signals
Signals include pseries guest boot with XIVE enabled, fallback behavior when option vector or `xive=off` disables XIVE, CPU hotplug with IPI LISN allocation/free, secure guest queue sharing, interrupt delivery through H_INT_ESB and MMIO ESB paths, and debugfs bitmap dumps.
