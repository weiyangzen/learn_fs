# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_rx.c

## Purpose
`ipoib_rx.c` converts HFI1 accelerated IPoIB receive buffers into Linux `sk_buff`s and connects IPoIB RX initialization to the shared HFI1 netdev receive-context layer. It is intentionally small: packet demultiplexing and receive-context polling live elsewhere, while this file handles SKB preparation and IPoIB-specific RSM setup.

## Important APIs, types, and functions
- `copy_ipoib_buf()` copies the received IPoIB buffer into an SKB, sets checksum state, initializes protocol from the packet data, sets `mac_header`, and pulls the IPoIB encapsulation header.
- `prepare_frag_skb()` allocates large packets from NAPI fragment cache with `napi_alloc_frag()` and wraps them with `build_skb()`, falling back to `napi_alloc_skb()` only when fragment allocation fails.
- `hfi1_ipoib_prepare_skb()` chooses small SKB allocation versus fragment-backed allocation, then calls `copy_ipoib_buf()`.
- `hfi1_ipoib_rxq_init()` increments or creates HFI1 netdev RX queues through `hfi1_netdev_rx_init()` and programs AIP receive-side mapping through `hfi1_init_aip_rsm()`.
- `hfi1_ipoib_rxq_deinit()` reverses that order with `hfi1_deinit_aip_rsm()` and `hfi1_netdev_rx_destroy()`.

## Control flow
Receive polling code calls `hfi1_ipoib_prepare_skb()` with a receive queue, payload size, and source data pointer. The function accounts for `HFI1_IPOIB_ENCAP_LEN`, uses normal NAPI SKB allocation for packets that fit in a page-sized SKB, and uses a fragment-backed SKB for larger packets. After allocation, it copies data, marks the checksum as none, sets the packet protocol from the leading bytes, and strips the encapsulation header before handing the SKB to the network stack.

Initialization is tied to netdev creation in `ipoib_main.c`: RX queues are initialized before the HFI1 netdev ops are exposed, and deinitialized by the netdev destructor. Shared receive queues are reference-counted by `netdev_rx.c`; this file adds the IPoIB-specific RSM programming around that shared lifetime.

## State and persistence
This file does not own long-lived state beyond the NAPI allocation behavior. It relies on `struct hfi1_netdev_rxq` for the NAPI instance and on `struct hfi1_ipoib_dev_priv` for the device pointer. AIP RSM hardware state is programmed on init and cleared on deinit; there is no persistence outside device runtime.

## Dependencies and integration points
The code uses Linux SKB/NAPI allocation APIs, HFI1 IPoIB constants from `ipoib.h`, shared HFI1 netdev RX setup from `netdev.h`, and hardware RSM helpers `hfi1_init_aip_rsm()` and `hfi1_deinit_aip_rsm()`.

## Risks
- `copy_ipoib_buf()` reads the protocol from the beginning of `data`; callers must guarantee at least the encapsulation header is present and aligned enough for the cast.
- Large receive allocation uses fragment cache sizing that includes SKB shared info; off-by-one sizing would corrupt SKB metadata.
- RX init programs AIP RSM after netdev RX allocation. If RSM setup can fail in future, the function would need an unwind path because it currently returns the RX init status only.

## Test signals
- Exercise small and large IPoIB receives through NAPI and verify protocol, header offsets, packet length, and checksum state.
- Inject allocation failures for `napi_alloc_frag()`, `build_skb()`, and `napi_alloc_skb()` to confirm null handling.
- Open and destroy multiple IPoIB netdevs to verify shared RX queue reference counting and AIP RSM init/deinit balance.
