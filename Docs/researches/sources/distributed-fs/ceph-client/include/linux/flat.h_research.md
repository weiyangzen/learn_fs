# sources/distributed-fs/ceph-client/include/linux/flat.h

## Purpose
This header defines the uClinux flat executable file format used by binary loaders on no-MMU systems.

## APIs, types, and control flow
`FLAT_VERSION` identifies the current format. `struct flat_hdr` stores network-byte-order fields for magic, revision, entry offset, data range, bss end, stack size, relocation table offset/count, flags, build date, and reserved filler. Flags describe load mode, GOT/PIC usage, gzip compression, compressed data/relocs, and kernel tracing. Legacy v2 support defines relocation type constants and `flat_v2_reloc_t`, a union exposing the raw 32-bit relocation value or endian-dependent bitfields for offset and type.

## State and dependencies
There is no runtime state. The header encodes on-disk ABI and depends on endian bitfield configuration and fixed-width big-endian integer types.

## Integration, risks, and tests
The binary-format loader and no-MMU exec path consume this format. Risks include endian conversion bugs, accepting unsupported old-format enhancements, relocation bitfield layout mismatch, malformed offsets/counts, and compressed payload bounds errors in loader code. Tests should parse known flat binaries, reject bad magic/version, verify big-endian field decoding on both endian builds, exercise v2 relocation interpretation, and validate flags combinations for XIP and compressed data.
