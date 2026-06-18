# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2.h

## Purpose
`iris_hfi_gen2.h` declares the Gen2 HFI setup interface and defines the Gen2-specific instance wrapper that extends `struct iris_inst`.

## Important APIs, Types, And Functions
`struct iris_inst_hfi_gen2` embeds `struct iris_inst`, owns a reusable 4 KiB HFI packet buffer, tracks whether input/output port-settings-change subscriptions were set, stores transient `struct iris_hfi_frame_info`, and holds source/destination `struct hfi_subscription_params`. `to_iris_inst_hfi_gen2()` converts from base instance to wrapper. The exported functions are command/response ops init and Gen2 instance allocation.

## Control Flow
Gen2 session open allocates the reusable packet buffer in the wrapper. Command builders reuse it for one header plus one sub-packet at a time. Response parsing uses wrapper fields to aggregate per-frame info across multi-packet responses and to store subscription values for source-change handling.

## State And Persistence Behavior
The wrapper persists for the session lifetime. `packet` is allocated on open and freed on close or open failure. Subscription params persist across stream setup and source-change responses; `hfi_frame_info` is reset for each response header.

## Dependencies And Integration Points
It includes `iris_instance.h` and relies on `iris_hfi_gen2_packet.h` types through included instance/common headers. Platform generation selection uses these exported init/allocation functions.

## Risks And Test Signals
The embedded-base allocation pattern means Gen2 instances must always be allocated by `iris_hfi_gen2_get_instance()`. Tests should verify close frees the packet buffer, failed open frees it, and no generic free path assumes the allocation is exactly `sizeof(struct iris_inst)`.
