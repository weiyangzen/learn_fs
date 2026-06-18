# sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_metadata.h

## Purpose

`kexec_metadata.h` defines a small optional KHO metadata ABI that records the previous kernel release and kexec count across a kexec chain. The source was read as a complete 46-line file.

## Important APIs, Types, and Functions

The header defines `KHO_KEXEC_METADATA_VERSION`, `KHO_METADATA_NODE_NAME`, and packed `struct kho_kexec_metadata` with `version`, `previous_release[__NEW_UTS_LEN + 1]`, and `kexec_count`.

## Control Flow

There is no executable flow. The previous kernel registers a `kexec-metadata` subtree through KHO and stores this struct in preserved memory; the next kernel reads it to identify its predecessor and update the count.

## State and Persistence Behavior

The struct is preserved across kexec as plain C data. `version` must remain first so future readers can safely decide how to interpret the remaining bytes.

## Dependencies and Integration Points

It includes `linux/types.h` and `linux/utsname.h`. It integrates with KHO subtree registration and kernel release identification.

## Risks and Edge Cases

Because the data is not an FDT payload, layout and packing are the ABI. `previous_release` uses the UAPI-sized `__NEW_UTS_LEN`, so changes must maintain the version contract. Readers should reject unsupported versions and validate string termination.

## Test Signals

Kexec metadata preservation tests, version mismatch tests, string length/termination checks, and repeated-kexec count increment tests are useful.
