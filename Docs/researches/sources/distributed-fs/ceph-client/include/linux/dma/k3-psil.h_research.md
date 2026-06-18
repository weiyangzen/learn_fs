<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-psil.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/k3-psil.h

## Purpose
Defines TI K3 PSI-L endpoint configuration metadata used to configure UDMA/PKTDMA threads.

## Important APIs, Types, And Functions
Defines `K3_PSIL_DST_THREAD_ID_OFFSET`, `enum udma_tp_level`, `enum psil_endpoint_type`, `struct psil_endpoint_config`, and `psil_set_new_ep_config()`. Config fields cover endpoint type, throughput level, packet vs TR mode, TDCM suppression, EPIB, PDMA ACC32/BURST, PS data size, mapped channel id, flow range, and default flow id.

## Control Flow
SoC/peripheral code registers or overrides endpoint configuration by device and name. UDMA setup consumes the endpoint config when pairing source/destination PSI-L threads and flows.

## State And Persistence
State is endpoint configuration associated with a device/name. It reflects runtime driver configuration of DMA thread behavior, not durable storage.

## Dependencies And Integration Points
Depends on devices and TI K3 UDMA/PKTDMA PSI-L topology. It integrates DMA controller setup with peripheral endpoint requirements.

## Risks And Edge Cases
Mapped channel and flow ranges must be internally consistent. Packet mode, EPIB, PS data size, and PDMA flags must match peripheral protocol. Destination thread IDs need the documented offset.

## Test Signals
Tests should cover native and PDMA endpoint types, throughput levels, packet/TR modes, mapped and unmapped channel flows, default flow validation, and invalid endpoint-name handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-psil.h -->
