# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/commands.rs

## Purpose

`gsp/commands.rs` defines high-level typed GSP RPC commands and message readers used during early GSP initialization and information retrieval.

## Important APIs, Types, And Functions

Commands include `SetSystemInfo`, `SetRegistry`, and internal `GetGspStaticInfo`. Message/read types include `GspInitDone`, `GetGspStaticInfoReply`, and `GpuNameError`. Public helpers are `wait_gsp_init_done()` and `get_gsp_info()`.

## Control Flow

`SetSystemInfo` initializes a generated `GspSetSystemInfo` from the PCI device. `SetRegistry` builds a packed registry table with three hardcoded keys and a variable payload containing entry records plus NUL-terminated strings. `wait_gsp_init_done()` loops receiving messages until `GspInitDone` arrives, skipping unrelated recognized messages. `get_gsp_info()` sends `GetGspStaticInfo` and parses the reply GPU name.

## State And Persistence Behavior

Commands are temporary typed builders; their serialized bytes persist only in the command queue until consumed by GSP. Registry entries are hardcoded in the command object. The static-info reply stores a copied 64-byte GPU name.

## Dependencies And Integration Points

It depends on generated GSP command bindings, `Cmdq`, `CommandToGsp`, `MessageFromGsp`, `SBufferIter`, PCI device abstractions, and C string/UTF-8 parsing. GSP boot queues system/registry setup before final initialization and reads GPU info after init done.

## Risks And Test Signals

Risks include hardcoded registry policy, payload offset calculations including table size, string termination, ignored extra reply payload, GPU name not NUL-terminated or invalid UTF-8, and skipped unrelated messages hiding important events. Test command serialization sizes, registry payload bytes, init-done wait with interleaved events, static-info reply parsing, and hardware logs showing accepted registry/system info.
