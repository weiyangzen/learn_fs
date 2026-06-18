# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/aux_engine.h

## Purpose

`aux_engine.h` defines the AUX/I2C transaction engine abstraction used for DPCD and DDC communication. It models transaction payloads/status, engine types, AUX configuration, read/write command retry context, and engine callbacks.

## Important APIs, Types, And Functions

Important enums are transaction operation, address space, status, engine type, and default I2C speeds. `i2caux_transaction_payload/request`, `aux_config`, `aux_engine`, `read_command_context`, and `write_command_context` carry transaction state. `aux_engine_funcs` includes timeout configuration, acquire/release, configure, channel request/reply submission, reply readback, status query, availability check, high-level request submission, and destruction.

## Control Flow

Clients acquire an engine for a DDC object, configure AUX behavior, submit read/write requests to I2C or DPCD address spaces, process hardware replies, retry timeout/defer/invalid-reply cases through command contexts, then release the engine. Middle-of-transaction handling supports multi-part I2C-over-AUX sequences.

## State And Persistence Behavior

`aux_engine` persists as an AUX resource with instance, DDC binding, context, delay, retry limits, and acquire-reset behavior. Read/write contexts persist only for a transaction and record retry counters, request/reply packets, returned byte, completion, and success flags. Hardware state includes channel ownership and pending AUX transactions.

## Dependencies And Integration Points

It includes `dc_ddc_types.h`. It integrates with DDC services, link detection, EDID reads, DPCD reads/writes, link training, PSR/replay, firmware communication over AUX, and HPD-low policy.

## Risks And Edge Cases

AUX is retry-heavy and failure modes must be distinguished: busy, timeout, protocol error, NACK, incomplete, invalid operation, buffer overflow, and HPD disconnect. Incorrect `middle_of_transaction` or MOT handling can break I2C-over-AUX. Buffer length must stay within AUX limits. Acquiring without release can block link operations.

## Test Signals

Tests should cover EDID reads, DPCD reads/writes, HPD disconnect during AUX, defer storms, NACK, timeouts, channel busy, HPD-low AUX policy, and multi-part I2C transactions. Link training and hotplug reliability are practical integration signals.
