# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721e.c

## Purpose
This file provides the J721E PSI-L endpoint map. It is a large declarative map for SA2UL, PRU_ICSSG, multiple PDMA groups, CSI2RX, CPSW9, CPSW0, MCU PDMA, MCU ADC, and MCU SA2UL endpoints.

## Important APIs, Types, and Functions
The exported symbol is `struct psil_ep_map j721e_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, `PSIL_SA2UL()`, and `PSIL_CSI2RX()`. These macros encode endpoint type, packet mode, EPIB/PSD requirements, PDMA burst/access flags, and SA2UL TX packet behavior.

## Control Flow
No functions execute locally. The generic library selects this map for `J721E` and performs linear thread-ID lookup. Source entries are used for RX, including many CSI2RX IDs from `0x4940` through `0x497f`; destination entries cover matching TX-capable groups where applicable.

## State and Persistence
The arrays are static persistent endpoint tables and can be mutated through the generic `psil_set_new_ep_config()` interface. Since lookup returns direct pointers, modifications are global to the selected map.

## Dependencies and Integration Points
The map depends on `k3-psil-priv.h`, the public K3 PSI-L endpoint definitions, and Makefile linkage into `k3-psil-lib.o`. It supplies endpoint metadata to K3 UDMA clients on J721E.

## Risks
This is a dense hardware table with many similar PDMA and CSI2RX IDs. Missing or transposed entries can break a peripheral without compiler signals. CSI2RX is source-only and native with minimal config, so consumers rely on correct thread IDs. Ethernet and SA2UL entries do not include explicit flow/channel mapping in this older style. Runtime mutation can hide table defects if used as a workaround.

## Test Signals
Run endpoint lookup tests for representative IDs in every group: SA2UL, ICSSG, McASP PDMA groups, SPI PDMA groups, UART PDMA groups, CSI2RX, CPSW9, CPSW0, MCU SPI/UART/ADC, and MCU SA2UL. Hardware tests should include camera capture and Ethernet paths because they touch the largest map regions.
