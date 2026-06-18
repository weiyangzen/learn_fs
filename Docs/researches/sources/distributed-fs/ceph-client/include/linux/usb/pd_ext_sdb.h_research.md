# `sources/distributed-fs/ceph-client/include/linux/usb/pd_ext_sdb.h`

## Purpose

`pd_ext_sdb.h` defines USB PD extended Status Data Block fields. It supports decoding status extended messages that report internal temperature, power state, battery state, and event flags.

## Important APIs, Types, and Constants

- The header provides packed/status field definitions and masks for extended status payload interpretation.
- Constants describe event and status bit positions used by TCPM and Type-C partner status logic.

## Control Flow and Lifetimes

After receiving a PD extended Status message, TCPM validates the extended-message length, decodes the status data block through these definitions, and updates policy or user-visible partner status.

## State and Persistence Behavior

The status data block is transient wire data. Cached partner status lives in TCPM/Type-C runtime objects.

## Dependencies and Integration Points

It integrates with `pd.h` extended message framing, TCPM receive paths, and Type-C partner status reporting.

## Risks and Edge Cases

Extended messages may be chunked or shorter than expected. Temperature/power fields must be interpreted using PD-defined units and sentinel values. Reserved bits should be preserved only where required and ignored otherwise.

## Test Signals

Inject status extended messages with normal, warning, and reserved values; test short/chunked payload handling; verify partner status updates; and fuzz event bits.
