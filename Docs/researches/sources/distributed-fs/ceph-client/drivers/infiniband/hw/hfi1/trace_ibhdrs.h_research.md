# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ibhdrs.h

## Purpose

`trace_ibhdrs.h` declares packet header tracepoints for incoming and outgoing HFI1 packets. It provides symbolic opcode printing, helper prototypes implemented in `trace.c`, and event classes that capture 9B/16B LRH/BTH fields plus dynamic extended headers.

## Important APIs and Events

`show_ib_opcode()` maps RC, UC, UD, CNP, and HFI1 TID RDMA opcodes to names. Helper prototypes cover header-length calculation, 9B/16B parsing, LRH/rest formatting, packet L2/L4 string conversion, and extended header formatting.

`hfi1_input_ibhdr_template` captures receive packet type, LRH/16B fields, BTH fields, QP/PSN, optional management QPNs, and a dynamic copy of extended headers. It instantiates `input_ibhdr`.

`hfi1_output_ibhdr_template` captures the same style of data from outgoing `hfi1_opa_header` values and instantiates `pio_output_ibhdr`, `ack_output_ibhdr`, and `sdma_output_ibhdr`.

## Control Flow and State

The event fast-assign blocks parse fields based on packet type. Bypass packets use 16B parsing; normal packets use 9B parsing. Management packets avoid BTH extended header copying. For other opcodes, the dynamic `ehdrs` array is copied and later formatted through `parse_everbs_hdrs()`.

The header owns no persistent state. It relies on `trace.c` for helper implementations and on the caller to pass packet/header structures with `packet->ohdr` already set correctly.

## Integration, Risks, and Test Signals

This trace surface is central for validating RC and TID RDMA packet construction. It must stay aligned with opcode definitions, `hdr_len_by_opcode`, packet union layouts, and TID RDMA extended headers. Risks include dynamic length mismatches, copying from a NULL `ohdr`, or formatting stale union members for management packets. Tests should enable input/output header tracepoints for 9B, 16B, SDMA, PIO, ACK, and all TID RDMA opcodes and compare decoded fields with packet-builder expectations.
