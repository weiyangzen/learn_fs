# sources/distributed-fs/ceph-client/include/linux/ipmi_smi.h

## Purpose
`ipmi_smi.h` defines the low-level System Management Interface side of the IPMI stack: how KCS/SMIC/BT/platform SMI drivers register, exchange messages with the IPMI message handler, report asynchronous data, and expose device identity.

## Important APIs, types, and functions
Important definitions include `struct ipmi_smi`, watch-mask bits, `enum ipmi_smi_msg_type`, `struct ipmi_smi_msg`, `struct ipmi_smi_handlers`, `struct ipmi_device_id`, `ipmi_demangle_device_id`, `ipmi_add_smi`, `ipmi_register_smi`, `ipmi_unregister_smi`, `ipmi_smi_msg_received`, `ipmi_smi_watchdog_pretimeout`, `ipmi_alloc_smi_msg`, and `ipmi_free_smi_msg`.

## Control flow
Low-level drivers register handlers and private `send_info`, wait for `start_processing`, then accept serialized outbound messages via `sender`. They return completions or async data with `ipmi_smi_msg_received`, optionally poll, flush, enter run-to-completion mode, and toggle maintenance/watch behavior.

## State and persistence
State lives in SMI interface registration, queued `ipmi_smi_msg` objects, response buffers, watch mode, run-to-completion mode, and parsed BMC device IDs. It is runtime-only.

## Dependencies and integration points
It integrates with `ipmi.h`, IPMI message definitions, platform devices, procfs, device model, and interrupt/polling SMI drivers.

## Risks and test signals
Risks include non-failing sender contract violations, malformed Get Device ID parsing, shutdown while messages are inflight, panic polling deadlocks, and async message size errors. Tests should cover add/remove with users present, `ipmi_demangle_device_id` boundary lengths, IPMB-direct support, watchdog pretimeout delivery, and run-to-completion crash paths.
