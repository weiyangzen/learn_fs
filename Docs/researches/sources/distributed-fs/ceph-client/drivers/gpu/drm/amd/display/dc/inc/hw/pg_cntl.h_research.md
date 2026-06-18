# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/pg_cntl.h

## Purpose

`pg_cntl.h` defines a power-gating controller abstraction for display hardware blocks. It gives DC a vtable for enabling, disabling, and querying power-gated domains without baking register details into common resource code.

## Important APIs, Types, And Functions

The file defines `struct pg_cntl` with context, instance, and a `pg_cntl_funcs` table. The function table provides block power-on/off and state-related callbacks implemented by ASIC-specific code.

## Control Flow

Resource or hardware-sequencing code calls the power-gating callbacks before programming a block that may be gated and after disabling unused resources. The abstraction lets ASIC implementations handle register handshakes and polling internally.

## State And Persistence Behavior

Software state is minimal. Persistent behavior is hardware power state: gated blocks lose or ignore register programming until powered, and ungated blocks consume power until the controller gates them again.

## Dependencies And Integration Points

This interface integrates with display resource construction, block initialization, low-power modes, and memory/LUT power controls such as MPC memory power.

## Risks And Test Signals

Risks include programming blocks while gated, failing to gate unused blocks, and missing wait/ack sequences. Test signals include runtime power-management counters, suspend/resume, modeset after idle, display underflow after ungating, and register access warnings.
