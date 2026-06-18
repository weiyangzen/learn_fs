# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c

## Purpose

`dmub_dcn303.c` provides the DCN 3.0.3 DMUB register table. It is a register-metadata-only generation file in this subset.

## Important APIs, Types, And Functions

The exported object is `dmub_srv_dcn303_regs`, initialized as a `struct dmub_srv_common_regs` by expanding the common DMUB register and field macros with DCN 3.0.3 generated headers.

## Control Flow And Data Flow

Runtime flow is indirect through the service layer. The file supplies offsets/masks/shifts so common DMUB functions can access the correct DCN303 registers.

## State And Persistence Behavior

No runtime state is maintained. The register table is immutable.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn303.h`, `sienna_cichlid_ip_offset.h`, and DCN 3.0.3 generated offset/mask headers. It integrates with generation selection code for DCN303 ASICs.

## Risks And Edge Cases

This file uses Sienna Cichlid IP offsets with DCN 3.0.3 register definitions. Wrong pairing would cause register access errors. Since there are no custom functions, runtime tests must catch any generation behavior not handled by common functions.

## Test Signals

Clean build, link success for `dmub_srv_dcn303_regs`, and successful DMUB boot and mailbox command flow on DCN303 hardware are the main signals.
