# sources/distributed-fs/ceph-client/include/uapi/linux/module_signature.h

## Purpose
Defines the appended kernel module signature marker, signature type enum, and trailing metadata block layout used to locate and verify signed modules.

## Important APIs, Types, And Functions
Exports `MODULE_SIGNATURE_MARKER`, `MODULE_SIGNATURE_TYPE_PKCS7`, and packed metadata `module_signature` fields: algorithm, hash, id type, signer/key lengths, padding, and big-endian signature length.

## Control Flow
Module loading scans for the marker, parses the appended signature data sequence, reads the metadata block, and verifies a PKCS#7 signature according to kernel key policy.

## State, Persistence, And Dependencies
Signature data persists appended to module files. Depends on `linux/types.h` for fixed-width and big-endian types.

## Integration Points
Used by module signing tools, kernel module loader, and secure boot/module signature enforcement.

## Risks
The length field is big-endian and the structure is at the end of appended data. Incorrect signer/key lengths or marker scanning can make valid modules unverifiable.

## Test Signals
Validate signed module parsing, marker detection, PKCS#7 type handling, big-endian `sig_len`, rejection of truncated trailers, and unsigned-module behavior under enforcement.
