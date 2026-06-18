# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.c

## Purpose

This file validates and extracts IPU7 CPD firmware package contents. CPD packages contain manifest, metadata, and binary entries for ISYS and PSYS firmware.

## Important APIs, Types, and Functions

Public APIs are `ipu7_cpd_validate_cpd_file()` and `ipu7_cpd_copy_binary()`. Internal packed types model CPD header, entries, metadata attribute, IPL metadata, and combined metadata. Helpers locate entries, manifest, and per-binary metadata.

## Control Flow

Validation checks CPD marker, entry count, header/entry bounds, each entry bounds, manifest maximum size, and metadata type/length for both binaries. It then parses the last 128 bytes of each binary into six newline-delimited metadata lines and logs name/version/timestamp/commit. Copying searches binary entries by 12-byte name, copies the binary into the code region at the IPL load offset, and returns the entry point from IPL metadata.

## State and Persistence Behavior

No persistent driver state is owned. It reads firmware package memory and writes caller-provided code region memory.

## Dependencies and Integration Points

It integrates with the main IPU7 firmware request/load path and buttress authentication/boot code. It uses `struct ipu7_device` for logging.

## Risks and Edge Cases

Validation does not verify CRC or cryptographic signature; secure-mode authentication is separate. Version metadata parsing is best-effort and continues on malformed online metadata. Copying trusts validated offsets and metadata load offsets.

## Test Signals

Test malformed marker, entry count, entry bounds, oversized manifest, bad metadata type/length, missing binary name, valid copy offset/entry, and malformed trailing online metadata.
