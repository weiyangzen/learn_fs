# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.h

## Purpose
`loader.h` defines the ISHTP firmware-loader fixed-client protocol and manifest structures used by `loader.c` and HBM fixed-client dispatch. It gives the loader command IDs, packed request/response layouts, DMA fragment descriptor shape, retry/timeout constants, loader capability bit, loader fixed-client address, and firmware manifest version layout.

## Important APIs, types, and functions
Important definitions are `LOADER_MSG_SIZE`, `LOADER_CMD_XFER_QUERY`, `LOADER_CMD_XFER_FRAGMENT`, `LOADER_CMD_START`, `LOADER_XFER_MODE_DMA`, `union loader_msg_header`, query/ack structures, `struct loader_capability`, `struct loader_xfer_dma_fragment`, `struct fragment_dscrpt`, `union loader_recv_message`, `ISHTP_LOADER_TIMEOUT`, `ISHTP_LOADER_RETRY_TIMES`, `ISHTP_SUPPORT_CAP_LOADER`, `ISHTP_LOADER_CLIENT_ADDR`, `ISH_MANIFEST_ALIGNMENT`, `ISH_GLOBAL_SIG`, `struct version_in_manifest`, and `struct ish_global_manifest`. It declares `ishtp_loader_work()`.

## Control flow and integration points
The header has no executable control flow. HBM checks `ISHTP_SUPPORT_CAP_LOADER` in the host-start response and schedules `ishtp_loader_work()`. Fixed-client RX dispatch routes messages from address `ISHTP_LOADER_CLIENT_ADDR` into the loader wait buffer. Loader code uses the flexible DMA-fragment table and manifest layouts to transfer and parse firmware.

## State and persistence behavior
No state is stored in this header. It defines volatile protocol messages and the firmware manifest fields copied into `struct ishtp_device` after load.

## Dependencies
It includes Linux bit, jiffies, sizes, and type helpers plus `ishtp-dev.h` for IPC payload sizing. The ABI structures use little-endian integer annotations and flexible arrays.

## Risks and edge cases
`FRAGMENT_MAX_NUM` depends on the loader message size and the flexible descriptor layout; changes to either can alter maximum DMA batching. Packed bitfield header semantics must match firmware. Timeout and retry constants directly influence loader robustness. Manifest parsing assumes 4 KiB alignment and the `ISHG` signature.

## Test signals
Structure size/offset checks, loader-capability probe, fixed-client response routing, fragment-count boundary tests, firmware larger than one fragment, retry timeout behavior, and manifest signature/version parsing are the main validation points.
