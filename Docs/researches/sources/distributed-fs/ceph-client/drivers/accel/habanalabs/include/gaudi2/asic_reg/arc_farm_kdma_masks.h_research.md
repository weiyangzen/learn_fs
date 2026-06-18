<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_masks.h

## Purpose
`arc_farm_kdma_masks.h` is the generated bitfield companion for the `ARC_FARM_KDMA` `DMA_CORE` register bank. It provides 258 shift/mask macros that describe how to build and decode configuration, traffic-limit, cache, error, status, debug, local-to-host, idle, and APB-control register values.

## Important APIs, types, and functions
The exported API is the macro namespace. Important fields include `CFG_0_EN`, `CFG_1_HALT/FLUSH`, protection value/error bits, clock-gating bits for HBW/LBW/TE paths, `RD_GLBL` force-miss and LB-via-HB controls, HB/LB read outstanding and size fields, HB/LB write outstanding and AWID fields, rate-limit timeout/saturation/enable fields, write-completion limits and AWUSER value, `ERR_CFG` error-message and stop-on-error bits, detailed `ERR_CAUSE` flags, `STS0` request counts and busy bit, `STS1_IS_HALT`, context snapshot selectors, LB ready/valid status bits, power/debug status fields, APB enabler disable, L2H compare/mask values, and `IDLE_IND_MASK`.

## Control flow
There is no code path inside the header. It is used anywhere software composes a DMA core register value or decodes a status/error read. Typical control flow is read-modify-write: mask out a field, shift a new value into place, and write through the matching address macro. Recovery code decodes `ERR_CAUSE`, status bits, and idle indications to decide whether to stop, flush, reset, or report an engine fault.

## State and persistence behavior
The macros describe persistent hardware configuration fields and transient status fields. Configuration writes survive until reset or explicit change; status, request counters, inflight counts, and debug fields evolve with DMA traffic. Because mask names encode semantics, they are part of the implicit ABI between generated register files and driver code even though no data is stored in the header.

## Dependencies and integration points
This header must match the sibling DMA core register-address header and the generated hardware specification for the same ASIC revision. It integrates with initialization code, error interrupt handling, reset flows, and any common helper that abstracts the `DMA_CORE` prototype across KDMA and EDMA instances.

## Risks and edge cases
Mismatched masks can be worse than missing definitions: a write may hit a valid register but set the wrong field. Other risks are unbounded field values being shifted without prior range checks, accidentally clearing adjacent status bits during read-modify-write, and using status masks on write-only or write-one-to-clear registers. Reserved fields should not be used as feature hooks without hardware confirmation.

## Test signals
Good test coverage includes static build coverage of all macro users, register write/readback smoke tests where hardware permits, DMA enable/halt/flush exercises, error injection for every named `ERR_CAUSE` bit, and debug reads showing expected busy/idle and context snapshot fields during active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_masks.h -->
