# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-private.c

## Purpose
`k3-udma-private.c` exposes a narrow private ABI from the main K3 UDMA DMAengine provider to the glue layer and other closely related K3 DMA code. The file is included at the end of `k3-udma.c`, so it has access to internal static helpers and structures while still exporting symbols with stable `xudma_*` names. It avoids duplicating resource management, PSI-L pairing, ringacc lookup, and register access in glue clients.

## Important APIs, Types, And Functions
The exported PSI-L wrappers are `xudma_navss_psil_pair()` and `xudma_navss_psil_unpair()`, delegating to `navss_psil_pair()` and `navss_psil_unpair()`. Device lookup and property access helpers include `of_xudma_dev_get()`, `xudma_get_device()`, `xudma_get_ringacc()`, `xudma_dev_get_psil_base()`, and `xudma_dev_get_tisci_rm()`. Resource helpers include `xudma_alloc_gp_rflow_range()`, `xudma_free_gp_rflow_range()`, `xudma_rflow_is_gp()`, generated `xudma_tchan_get()/put()`, `xudma_rchan_get()/put()`, `xudma_rflow_get()/put()`, and generated id accessors. Runtime register access is exported through generated `xudma_tchanrt_read()/write()` and `xudma_rchanrt_read()/write()`. PKTDMA helpers are `xudma_is_pktdma()`, `xudma_pktdma_tflow_get_irq()`, and `xudma_pktdma_rflow_get_irq()`.

## Control Flow
`of_xudma_dev_get()` optionally follows a phandle property, finds the platform device by node, drops references appropriately, and returns the probed `struct udma_dev` or `-EPROBE_DEFER` if the DMA provider is not ready. Resource get functions reserve bits in the owning `udma_dev` bitmaps through internal helpers, and put functions clear those bits. RX flow get/put uses the dedicated flow in-use map and enforces GP-flow allocation rules through `__udma_get_rflow()`. Runtime register read/write helpers guard null resource pointers, then access the mapped channel runtime region.

## State And Persistence
This file does not create independent persistent state. It mutates the parent `struct udma_dev` resource bitmaps and accesses its TISCI, ringacc, MSI, and MMIO state. The resource put macros clear bitmap bits directly, so callers must pair get/put calls carefully and avoid double puts. Device-node and platform-device references are transient and released before returning.

## Dependencies And Integration Points
The implementation depends on static symbols and struct definitions from `k3-udma.c` because it is textually included there. Its public declarations live in `k3-udma.h`, and its consumers include `k3-udma-glue.c`. It integrates with device tree, platform device probing, K3 ringacc, TI SCI RM/PSI-L, MSI event offsets in `udma_soc_data`, and the UDMA resource bitmaps initialized by the main provider.

## Risks And Edge Cases
Because this is a private exported shim, ABI drift between `k3-udma.h`, this file, and `k3-udma.c` can break glue users at build or runtime. `xudma_tchan_put()` and `xudma_rchan_put()` clear allocation bits without validating that the pointer belongs to the device or is currently allocated, unlike `__udma_put_rflow()` which logs an unused-flow put. `of_xudma_dev_get()` returns a raw `udma_dev` pointer after dropping the platform-device reference, so normal device lifetime assumptions depend on provider-driver binding and probe ordering. Register helpers silently ignore null resources, which is convenient for cleanup but can mask invalid call paths.

## Test Signals
Useful tests include provider-probe deferral via `of_xudma_dev_get()`, resource get/put bitmap accounting, explicit-id reservation conflicts, RX flow GP allocation enforcement, PSI-L pair/unpair calls receiving the correct NAVSS device id and destination thread encoding, PKTDMA flow IRQ offsets, and null-resource runtime-register access returning or doing nothing without crashing.
