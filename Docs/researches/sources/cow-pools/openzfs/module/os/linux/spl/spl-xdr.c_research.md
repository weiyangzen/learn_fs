# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-xdr.c

## Purpose

Implements an in-memory XDR encoder/decoder used by libnvpair and ZFS metadata serialization. It serializes primitive values, opaque bytes, strings, and arrays into a portable big-endian representation.

## Main Entry Point

- `xdrmem_create(XDR *xdrs, caddr_t addr, uint_t size, enum xdr_op op)`: initializes an XDR stream over a caller-provided memory buffer for encode or decode and rejects invalid operations or pointer wraparound.

## Encoding/Decoding Behavior

- Uses 4-byte XDR alignment.
- Encodes integers in big-endian order.
- Pads opaque data with zero bytes.
- Rejects nonzero padding on decode.
- Rejects decoded strings containing embedded NUL bytes.
- Validates decoded char and ushort range.
- Bounds-checks buffer availability before advancing.
- Can allocate arrays or strings during decode when caller passes a null pointer.

## Important Functions

- `xdrmem_control()`: implements `XDR_GET_BYTES_AVAIL`.
- `xdrmem_enc_bytes()` / `xdrmem_dec_bytes()`: opaque byte operations with padding handling.
- `xdrmem_enc_uint32()` / `xdrmem_dec_uint32()`: endian primitive operations.
- `xdrmem_enc_char()` / `xdrmem_dec_char()`
- `xdrmem_enc_ushort()` / `xdrmem_dec_ushort()`
- `xdrmem_enc_uint()` / `xdrmem_dec_uint()`
- `xdrmem_enc_ulonglong()` / `xdrmem_dec_ulonglong()`
- `xdr_enc_array()` / `xdr_dec_array()`
- `xdr_enc_string()` / `xdr_dec_string()`

## Ops Tables

- `xdrmem_encode_ops`
- `xdrmem_decode_ops`

## Notes

The implementation documents strict ABI assumptions: 8-bit chars, 32-bit unsigned ints, 64-bit unsigned long longs, two’s-complement negative integers, suitable alignment, and kernel memory buffers only.
