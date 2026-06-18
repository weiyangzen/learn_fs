# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_tlv.h

Purpose: provides TLV encapsulation helpers for BNG RoCE command queue messages. It lets common command-preparation code read and write `struct cmdq_base` fields whether the command is sent directly or wrapped behind a RoCE TLV header.

Important APIs and types: `struct roce_tlv` embeds a firmware `struct tlv`, stores `total_size` in 16-byte chunks, and pads to 16-byte alignment. `TLV_SIZE` and `TLV_BYTES` define the aligned header size. `HAS_TLV_HEADER()` tests the command discriminator for `CMD_DISCR_TLV_ENCAP`; `GET_TLV_DATA()` returns the payload following the TLV header. Inline accessors cover opcode, cookie, response address, response size, command size, and flags.

Control flow: every accessor checks whether the passed request appears TLV-encapsulated and whether the buffer is larger than the TLV header. If true, it casts the payload after `TLV_BYTES` to `struct cmdq_base`; otherwise it accesses the base request directly. The command-size getter is special: for TLV messages it returns the outer `roce_tlv.total_size`, while the setter writes the inner base `cmd_size`.

State and persistence: this header stores no state. It performs direct in-place mutation of command buffers supplied by callers, so the lifetime and validity of those buffers are external.

Dependencies and integration points: includes generated HSI definitions from `bng_roce_hsi.h` and depends on little-endian helpers for `cmd_discr`. It integrates with RCFW command builders such as `bng_re_rcfw_cmd_prep()` and `bng_re_fill_cmdqmsg()` that need generic base-field access.

Risks: all helpers assume the supplied `size` accurately describes the backing buffer. Incorrect sizes can cause fields to be written into the outer TLV header or skipped. The pointer arithmetic in `GET_TLV_DATA()` relies on byte-addressing and alignment; malformed TLV commands can still be misinterpreted if their discriminator is set but their payload is shorter than expected.

Test signals: unit-style command-buffer tests for direct and TLV-wrapped commands, verification that opcode/cookie/response fields are set in the right location, malformed short-TLV tests, and command submission tests that confirm firmware accepts both encapsulated and non-encapsulated requests.
