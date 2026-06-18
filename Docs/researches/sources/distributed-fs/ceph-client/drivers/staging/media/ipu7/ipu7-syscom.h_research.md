# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.h

## Purpose
Declares syscom queue configuration and context state plus public token queue APIs for IPU7 firmware communication.

## Important APIs, Types, and Constants
`struct syscom_queue_config` stores token array base, total queue size, token size, and max capacity. `struct ipu7_syscom_context` stores input/output queue counts, queue configs, shared queue indices MMIO pointer, DMA address of queue memory, CPU queue memory pointer, and queue memory size. Public functions are `ipu7_syscom_put_token()`, `ipu7_syscom_get_token()`, and `ipu7_syscom_get_queue_config()`.

## Control Flow and State
The header defines the context consumed by `ipu7-syscom.c`. Queue indices are maintained outside normal kernel heap state and must remain coherent with firmware. Token arrays are addressed by fixed-size offsets derived from queue config.

## Dependencies and Integration Points
Depends on Linux types and firmware syscom config forward declarations. It is used by firmware communication code under the `INTEL_IPU7` namespace and by bus/firmware setup code that allocates queue memory.

## Risks and Test Signals
The API assumes initialized queue counts, capacities, token sizes, and index memory. Bad configuration can produce out-of-bounds token pointers. Test signals include correct queue config parsing from firmware config memory, token pointer alignment, ring wraparound, and balanced get/put behavior across all configured input and output queues.
