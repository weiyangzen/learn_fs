# sources/distributed-fs/ceph-client/include/soc/tegra/bpmp-abi.h

## Purpose

`bpmp-abi.h` is the packed wire-format contract for NVIDIA Tegra BPMP firmware IPC. It defines MRQ request/response headers, MRQ numeric IDs, command enums, request/response payload structures, buffer lengths, ABI compatibility constants, and BPMP-local error numbers. It is a protocol definition rather than executable code, with many families documented conditionally for T186, T194, T234/T238, TH500/TB500, and T264 platforms.

## Important APIs, Types, and Functions

The central types are `struct mrq_request` and `struct mrq_response`. `mrq_request.mrq` selects the service, and `flags` carries `BPMP_MAIL_DO_ACK`, `BPMP_MAIL_RING_DB`, and optionally `BPMP_MAIL_CRC_PRESENT`. With CRC enabled the flags word encodes options, transaction ID, payload length, and CRC16; `mrq_response` mirrors the same transaction metadata while returning `err`.

The file defines services including ping, query tag, debug/debugfs, reset, I2C, clock, query ABI, power gating, thermal, ABI ratchet, EMC latency, shutdown, ring-buffer console, CPU limits, straps, UPHY, FMON, EC, bandwidth manager, ISO clients, telemetry, power limits, gears, overcurrent status, C2C, throttle, power model, PCIe, power control, CR7, SLC, telemetry-ex, HWPM, DVFS, and PPP profile. Each complex service uses a command selector plus a packed anonymous union of command-specific payloads. Examples include `mrq_clk_request/response`, `mrq_pg_request/response`, `mrq_thermal_host_to_bpmp_request`, `mrq_bwmgr_int_request/response`, `mrq_uphy_request/response`, and `mrq_hwpm_request/response`.

## Control Flow

Callers serialize `struct mrq_request` followed by an MRQ-specific payload into an IPC frame, send it through a BPMP transport, and receive `struct mrq_response` plus an optional response payload. Discovery is explicit through `MRQ_QUERY_ABI` and per-family `*_QUERY_ABI` commands. Several flows are stateful or bidirectional: thermal trip setup can later generate BPMP-to-host `MRQ_THERMAL`, debug open/read/write/close carries file handles, and ring-buffer console calls expose firmware FIFO state.

## State and Persistence

The header stores no runtime state. It describes operations that mutate BPMP-owned hardware or firmware state: clocks, resets, power domains, thermal trips, memory bandwidth floors/caps, power limits, SLC and power-controller bypass, UPHY/PCIe controller state, C2C training, HWPM streaming, DVFS manager/controller state, and debug handles. Firmware owns persistence and lifetime.

## Dependencies and Integration Points

The header depends on integer/size types and packing macros when compiled outside normal kernel context. `soc/tegra/bpmp.h` and BPMP client drivers use `MSG_MIN_SZ`, `MSG_DATA_MIN_SZ`, MRQ IDs, and payload layouts to marshal messages. Consumers include clock, reset, power-domain, thermal, memory-controller/interconnect, PCIe/UPHY, debugfs, telemetry, and platform monitoring code.

## Risks

The biggest risks are ABI drift and layout mismatch. Structures are packed, many payloads must fit inside `MSG_DATA_MIN_SZ`, and optional CRC metadata can be mandatory on functional-safety platforms. Variable-length I2C and debug payloads require strict bounds handling. Platform-specific commands must be probed before use; callers need to handle `-BPMP_ENODEV`, `-BPMP_ENOTSUP`, `-BPMP_EBADCMD`, and `-BPMP_EBADMSG`. Some requests program hardware with caller-provided IDs or class codes, so validation responsibility is split between caller and firmware.

## Test Signals

Strong signals are compile/layout checks for size and offsets, CRC16 test vectors, marshalling tests for command selectors and payload lengths, query-ABI negative tests, and hardware/simulator smoke tests using ping, threaded ping, query tag, clock info, reset max ID, thermal zone count, and other read-only commands before state-changing requests.
