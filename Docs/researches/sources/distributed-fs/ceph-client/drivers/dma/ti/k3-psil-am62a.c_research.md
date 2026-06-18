# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62a.c

## Purpose
This file provides the AM62A PSI-L endpoint map for K3 UDMA. It is close to AM62 but uses AM62A-specific CSI2RX thread IDs and includes macros for both TR and packet PDMA endpoints.

## Important APIs, Types, and Functions
The main symbol is `struct psil_ep_map am62a_ep_map`. Endpoint entries are built through `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, `PSIL_SAUL()`, `PSIL_PDMA_MCASP()`, and `PSIL_CSI2RX()`. These macros configure PDMA XY packet or transfer mode, native packet endpoints with EPIB/PSD metadata, SAUL security accelerator flows, McASP burst/access flags, and native CSI2RX endpoints.

## Control Flow
No code executes in this file. `k3-psil.c` selects `am62a_ep_map` for SoC family `AM62AX`, then performs linear lookup through the source or destination arrays. Destination IDs keep the high destination-thread bit set; fallback symmetric lookup is available in the generic library if a destination-specific entry is absent.

## State and Persistence
The static source/destination arrays persist for the lifetime of the module/kernel image. Because the generic library returns mutable pointers, `psil_set_new_ep_config()` can alter a selected entry based on device-tree `dma-names` and `dmas`.

## Dependencies and Integration Points
The map integrates AM62A peripherals with K3 UDMA and is linked into `k3-psil-lib.o`. It depends on endpoint type constants and `struct psil_endpoint_config` from the public K3 PSI-L header.

## Risks
The AM62A CSI2RX range starts at `0x5000`, unlike AM62's `0x4700` range, so copy/paste between maps is a likely regression vector. SAUL and Ethernet flow assignments must stay coherent with firmware/resource manager allocation. Missing destination entries for PDMA devices would fall back only if symmetric lookup works for that ID.

## Test Signals
Probe UDMA on AM62AX hardware or DT tests and verify endpoint lookup for SAUL, PDMA SPI/UART/McASP, CPSW3G, and CSI2RX IDs. Negative lookup tests should confirm invalid AM62 or AM62A CSI ranges return `-ENOENT`.
