# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_kernel_regs.h

## Purpose

`cc_kernel_regs.h` is a generated register and bitfield map for CryptoCell descriptor queue and AXI monitor registers. It underpins descriptor packing and request completion accounting.

## Important APIs, Types, And Functions

The descriptor block defines completion counter, software reset, queue SRAM size, single-address enable, measure counter, queue word registers 0 through 5, queue watermark, and queue content fields. It also defines every descriptor word field: DIN mode/size/security/constant/not-last, DOUT mode/size/security/last/queue-last, flow/cipher/setup/key/padding fields, and high address bits. The AXI block defines inflight, completion, error, configuration, ACE constant, and cache parameter registers.

## Control Flow

There is no code flow. `cc_hw_queue_defs.h` consumes descriptor field definitions to pack commands, while `cc_request_mgr.c` reads `DSCRPTR_QUEUE_SRAM_SIZE`, writes queue words, reads `DSCRPTR_QUEUE_CONTENT`, and reads AXI completion counters through the driver-selected AXIM monitor offset.

## State And Persistence Behavior

Queue content and completion counters are live hardware state. Descriptor queue words are write-only command ingress from the driver's perspective. AXI monitor counters and error fields reflect transient bus activity and are cleared or consumed by hardware behavior.

## Dependencies And Integration Points

The header is included by `cc_hw_queue_defs.h` and indirectly by most CryptoCell operation builders. Queue size and content fields integrate with software queue admission in `cc_request_mgr.c`; AXI completion fields integrate with IRQ bottom-half completion processing.

## Risks And Edge Cases

Any mismatch between these field definitions and silicon causes global descriptor corruption. The completion counter is central to request dequeue; an incorrect field would desynchronize hardware completions from the software ring. The word-5 high-address fields matter only on 64-bit DMA builds, so they need coverage on systems with addresses above 4 GiB.

## Test Signals

Request manager initialization should read a queue size at or above `MIN_HW_QUEUE_SIZE`. Descriptor submission should reduce queue-content accounting without mismatch warnings. High-throughput crypto stress should not report empty software queue completions, AXI errors, or stalled queue availability.
