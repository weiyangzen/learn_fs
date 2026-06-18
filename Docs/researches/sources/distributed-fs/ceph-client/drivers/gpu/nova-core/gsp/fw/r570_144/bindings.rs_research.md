# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/r570_144/bindings.rs

Purpose: bindgen-generated Rust representation of the NVIDIA R570.144 GSP firmware ABI. It provides constants and C-layout types for vGPU/GSP RPC functions, events, WPR metadata, message queues, registry data, static GPU info, system info, and CPU sequencer command payloads.

Important APIs and types: `NV_VGPU_MSG_FUNCTION_*` and `NV_VGPU_MSG_EVENT_*` enumerate firmware RPC functions and events. Key structs include `GspSystemInfo`, `GspStaticConfigInfo_t`, `GspFwWprMeta`, `GSP_ARGUMENTS_CACHED`, `rpc_message_header_v`, `GSP_MSG_QUEUE_ELEMENT`, `PACKED_REGISTRY_TABLE`, `PACKED_REGISTRY_ENTRY`, `rpc_run_cpu_sequencer_v17_00`, and `GSP_SEQUENCER_BUFFER_CMD`. `__IncompleteArrayField<T>` models C flexible arrays.

Control flow: no driver logic is implemented here. Runtime behavior arises when higher-level wrappers read or write these layouts into firmware queues and shared buffers.

State and persistence: these definitions describe persistent shared-memory formats exchanged with GSP firmware. WPR metadata and queue headers carry boot and RPC state; static config carries discovered GPU capabilities.

Dependencies and integration: generated from C ABI headers and consumed by `r570_144.rs`, GSP command code, command queue code, sequencer parsing, and firmware boot metadata setup.

Risks: this file is layout-critical. Manual edits, bindgen option changes, endian assumptions, default zeroing of unions, and flexible-array sizing can break firmware communication. The surface is intentionally low-level and should remain wrapped by safer modules.

Test signals: compile-time layout compatibility is partial. Real validation requires GSP boot, command queue traffic, CPU sequencer execution, and static-info retrieval on supported hardware.
