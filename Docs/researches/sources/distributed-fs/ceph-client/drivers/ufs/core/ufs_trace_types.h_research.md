# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace_types.h

## Purpose

This header defines small enums used by UFS tracepoints to classify command trace phases and transaction-specific field payloads.

## Important APIs, Types, and Functions

`enum ufs_trace_str_t` includes send/complete/error variants for SCSI commands, query requests, and task management. `enum ufs_trace_tsf_t` classifies UPIU TSF payloads as CDB, OSF, TM input, or TM output.

## Control Flow

No runtime control flow exists. The enums are consumed by `ufs_trace.h` and trace callers.

## State and Persistence Behavior

The header owns no state. Enum numeric values become part of trace event interpretation.

## Dependencies and Integration Points

It is included by `ufs_trace.h` and indirectly by UFS core trace call sites.

## Risks and Test Signals

Risks include reordering enum values without considering trace consumers and mismatches with string tables in `ufs_trace.h`. Test signals include trace decoding of every enum value.
