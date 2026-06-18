# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.h

## Purpose
Defines the SafeXcel EIP97/EIP197 register map, descriptor formats, context record layout, token encoding, hardware capability flags, driver state structures, helper prototypes, and algorithm template declarations.

## Important APIs, Types, and Functions
The header contains version constants for HIA/EIP blocks, register base macros for EIP197 and EIP97, CDR/RDR register offsets, DFE/DSE/AIC/PE/TRC/ICE bitfields, context-control encodings, token opcodes/instructions, firmware constants, and algorithm capability flags.

Important hardware-facing structures are `struct safexcel_context_record`, `struct result_data_desc`, `struct safexcel_result_desc`, `struct safexcel_token`, `struct safexcel_control_data_desc`, and `struct safexcel_command_desc`. Driver structures include `struct safexcel_desc_ring`, `struct safexcel_config`, `struct safexcel_ring`, `struct safexcel_priv_data`, `struct safexcel_register_offsets`, `struct safexcel_hwconfig`, `struct safexcel_crypto_priv`, `struct safexcel_context`, `struct safexcel_ahash_export_state`, and `struct safexcel_alg_template`.

Prototypes include queue/completion helpers, ring pointer helpers, descriptor allocation helpers, request mapping helpers, and `safexcel_hmac_setkey()`.

## Control Flow
`safexcel.c` uses register macros and structures to probe hardware, configure rings, process interrupts, and register algorithms. Algorithm-specific C files use `struct safexcel_context` callbacks and descriptor helper prototypes to build command/result descriptors, attach requests to result descriptors, and process completion.

## State and Persistence
The header defines all in-memory state containers for the SafeXcel core. `struct safexcel_crypto_priv` is per device, `struct safexcel_ring` is per hardware ring, and `struct safexcel_context` is per crypto transform. `struct safexcel_ahash_export_state` is an in-memory crypto API export/import format. No filesystem persistence is defined.

## Dependencies and Integration Points
Includes Linux crypto AEAD/hash/skcipher headers and SHA sizing constants. It is the central contract between `safexcel.c`, ring helpers, cipher/hash/AEAD algorithm files, and hardware firmware/register programming.

## Risks
Many bitfields and packed descriptors are hardware ABI and sensitive to layout, endian, and bus-width alignment. `struct safexcel_context` embeds callback pointers used by the core queue and result paths; a missing or wrong callback in an algorithm file can break request processing. The extern algorithm list is broad, so Kconfig/source selection must provide matching definitions. Register offset macros rely on correctly detected EIP97/EIP197 offsets.

## Test Signals
Build all SafeXcel objects together, run sparse/endianness checks, verify descriptor size/offset calculations on different hardware data widths, inspect `/proc/crypto` against hardware `algo_flags`, run ahash export/import tests, and use DMA/debug instrumentation on descriptor rings and context records.
