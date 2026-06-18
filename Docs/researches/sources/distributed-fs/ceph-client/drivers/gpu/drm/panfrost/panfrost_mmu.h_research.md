# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.h

## Purpose
This header declares the Panfrost MMU mapping, context, address-space, reset, IRQ suspend, and lifecycle API.

## Important APIs, Types, and Functions
It forward-declares Panfrost device, GEM mapping, file private, and MMU types. It declares map/unmap, init/fini/reset/suspend IRQ, AS get/put, MMU context get/put/create functions.

## Control Flow
The header has no executable flow. Job submission uses AS get/put, GEM mapping uses map/unmap, file open/close uses context create/get/put, and device reset/PM uses reset and IRQ suspend declarations.

## State and Persistence Behavior
The header stores no state. Implementations mutate page tables, drm_mm VA spaces, AS assignment masks, mapping active bits, and hardware MMU registers.

## Dependencies and Integration Points
It is the boundary between GEM, job manager, device reset/PM, and MMU implementation. Keeping it narrow avoids exposing io-pgtable details to callers.

## Risks
Callers must pair context and AS references correctly. Mapping functions expect a valid `panfrost_gem_mapping` with an allocated VA node and live MMU context.

## Test Signals
Build coverage plus GEM open/close, job submit/completion, MMU fault handling, file close, and reset paths validate the declared contract.
