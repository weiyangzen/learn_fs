# sources/control-plane/mayastor/libnvme-rs/src/nvme_uri.rs

Purpose: higher-level NVMe-oF target wrapper for parsing target URIs, connecting/disconnecting through libnvme, discovering block devices, and monitoring udev events.

Important APIs/types/functions: `NvmeStringWrapper` frees libnvme-allocated C strings. `NvmeTransportType` supports TCP and RDMA. `NvmeTarget` stores target address, port, subsystem NQN, transport, and hostnqn autogen flag. Methods include `TryFrom<&str/String>`, `with_rand_hostnqn`, `connect`, `block_devices`, `disconnect`, `list`, `start_poll`, `poll`, `handle_event`, and `Drop`.

Control flow: URI parsing accepts `nvmf`/`nvmf+tcp` as TCP and `nvmf+rdma+tcp` as RDMA, defaulting port to 4420. `connect` scans/creates a libnvme root, reads or generates host identity, creates a controller, and calls `nvmf_add_ctrl`. `block_devices` repeatedly scans until namespaces for the target NQN are found or retries expire. `disconnect` scans matching subsystems and disconnects each controller. `list` collects namespace metadata from subsystem and controller namespace iterators.

State/persistence: modifies kernel NVMe controller state on connect/disconnect. `Drop` attempts disconnect on target destruction. Host identity may come from `/etc/nvme` or generated UUID/NQN.

Dependencies/integration: uses generated libnvme bindings, libc free, mio/udev polling, URL parsing, UUID generation, and internal tree iterators/device model.

Risks: many `unsafe` C calls and `unwrap()` conversions can panic on unexpected null/non-UTF8 metadata. Drop-side disconnect may surprise callers if multiple users share a controller. Udev polling currently has only a FIXME callback. RDMA scheme spelling looks unusual and should be validated against callers.

Test signals: `nvme_parse_uri` validates TCP URI parsing. Runtime tests should cover connect/list/disconnect, hostnqn autogen, retry behavior, and nonmatching NQN filtering.
