# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw/commands.rs

Purpose: Rust wrapper layer for a small set of NVIDIA GSP firmware command payloads. It turns generated bindgen ABI structs into typed Nova-Core command objects that can be initialized safely enough for command queue submission.

Important APIs and types: `GspSetSystemInfo::init()` builds `bindings::GspSystemInfo` from PCI BAR resources, PCI IDs, and fixed configuration mirror values. `PackedRegistryEntry::new()` creates DWORD registry entries. `PackedRegistryTable::init()` creates a variable-length table header. `GspStaticConfigInfo::gpu_name_str()` exposes the firmware-provided GPU name bytes.

Control flow: callers construct command payloads through in-place initializers, then serialize them through `AsBytes` for GSP RPC paths. `GspSetSystemInfo` depends on `pci::Device<Bound>` resource reads, so initialization can fail before any command is sent.

State and persistence: no persistent state is owned here; all data is transient command payload state. The ABI values are persisted only when copied into command buffers.

Dependencies and integration: depends on generated `r570_144` bindings, kernel PCI/device APIs, `GSP_PAGE_SIZE`, and kernel transmute traits. It integrates with higher GSP firmware command modules by providing byte-compatible payload wrappers.

Risks: unsafe `AsBytes`/`FromBytes` implementations intentionally accept padding because the data stays inside the kernel; ABI layout drift or uninitialized padding assumptions would be high risk. `maxUserVa` is hard-coded and noted as questionable relative to upstream RM behavior.

Test signals: no direct tests. Confidence should come from GSP boot/RPC integration tests, command-size assertions, and failures in firmware initialization if system info or registry payloads are malformed.
