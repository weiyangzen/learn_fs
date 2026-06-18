# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.h

## Purpose

`hpidspcd.h` declares the DSP firmware-file format and reader API used by ASI HPI backend bootload code.

## Important APIs, types, and functions

`struct code_header` describes firmware files with size, type tag, adapter ID, version, and checksum, and is compile-time asserted to 20 bytes. `struct dsp_code` contains a copied header, total block length in words, current word count, and private reader state. Function declarations cover open, close, rewind, single-word read, and block read.

## Control flow

There is no executable flow in the header. It defines the contract that implementation and backends follow: open a firmware image for an adapter, read sequential words/blocks, rewind for verification, and close when done.

## State and persistence behavior

`struct dsp_code` is transient bootload state owned by backend stack/local variables. The firmware header fields are persistent file metadata and are used to validate adapter/driver compatibility. The checksum field is part of the format even though the current implementation does not verify it.

## Dependencies and integration points

It includes `hpi_internal.h` for types and compile-time assertion support. It integrates with Linux firmware files named by `hpidspcd.c`, and with `hpi6000.c`/`hpi6205.c` bootload loops that consume the record stream.

## Risks and test signals

Risks include file-format ABI drift, unchecked checksum semantics, word-size/endian assumptions, and callers misusing the block pointer after close. Test signals are compile-time header size assertion, firmware open/close, sequential read boundary checks, rewind verification loops, and bootload failure propagation to adapter create responses.
