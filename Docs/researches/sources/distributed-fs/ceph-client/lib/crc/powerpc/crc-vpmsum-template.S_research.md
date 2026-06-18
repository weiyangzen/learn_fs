# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-vpmsum-template.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-vpmsum-template.S` is a parameterized PowerPC VPMSUM assembly template for accelerated CRC algorithms. Including files define constants, reflection mode, and `CRC_FUNCTION_NAME`.

## Important APIs, Types, and Functions

The template emits one function named by `CRC_FUNCTION_NAME`. Key constants/macros include `MAX_SIZE`, `BYTESWAP_DATA`, vector offset registers, `VPERM`, and labels for warm-up, main loop, cool-down, short input, Barrett reduction, and output.

## Control Flow

The function saves nonvolatile GPRs and VMX registers, moves the initial CRC into vector state, conditionally loads byte-swap masks, and chooses a short path for inputs below 256 bytes. The main path processes up to 32 KiB at a time in eight parallel 16-byte lanes to reduce data to 1024 bits, folds the accumulated lanes with constants and optional tails, xors lanes together, then performs reflected or non-reflected Barrett reduction. The short path reduces smaller aligned inputs with `.short_constants`, handles partial lane counts through branch labels, then shares the Barrett/output code.

## State and Persistence Behavior

The template itself owns no concrete constants; includers provide `.constants`, `.short_constants`, and `.barrett_constants`. Runtime state is in VMX/GPR registers, restored before return.

## Dependencies and Integration Points

Dependencies include `asm/ppc_asm.h`, `asm/ppc-opcode.h`, VPMSUM instructions, and includer-defined polynomial constants. It integrates with PPC CRC32C and T10DIF assembly glue.

## Risks and Edge Cases

Because this is a template, macro definitions must match the polynomial orientation and output convention. Register save/restore, endian byte swapping, reflected vs non-reflected Barrett reduction, and tail lane dispatch are all high-risk. The caller must guarantee 16-byte alignment and length multiple requirements documented by the template.

## Test Signals

Signals include includer-specific CRC vectors, short and long inputs, 32 KiB boundary loops, all tail lane counts, big- and little-endian PPC builds, reflected and non-reflected modes, and VMX register preservation checks.

## Read Coverage

Source read size: 746 lines, 14068 bytes.
