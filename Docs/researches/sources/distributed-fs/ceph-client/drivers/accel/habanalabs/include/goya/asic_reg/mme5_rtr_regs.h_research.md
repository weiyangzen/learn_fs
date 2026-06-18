# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme5_rtr_regs.h

## Purpose

`mme5_rtr_regs.h` is the generated Goya register map for the `MME5_RTR` router. The block follows the `MME_RTR` prototype and participates in routing high-bandwidth and low-bandwidth traffic around the MME fabric. The header gives symbolic names to the MME5 router MMIO offsets.

## Important APIs, types, and data

The exported surface is the `mmMME5_RTR_*` macro set. It includes HBW and LBW arbitration registers for east/west/north/south/local directions, maximum arbitration counters, credit controls, debug arbiters, split coefficients and split control fields, HBW range hit plus eight split low/high mask/base entries, LBW range hit plus sixteen mask/base entries, register-lane result registers, and scrambler controls.

The address window is `0x140100` through `0x140604`. Relative offsets are the same as the other generated MME router instances, enabling instance-generic code if it computes or tables the base correctly.

## Control flow

There is no internal logic. Consumers write these offsets during fabric setup and read them during diagnostics. Range and scrambler setup should happen while the relevant router traffic is safely quiesced or during early initialization; debug/range-hit reads may occur in fault paths.

## State and persistence behavior

The header has no host-side state. MMIO writes to these registers update volatile device state that persists across workloads until reset/reconfiguration. Arbitration and credit settings shape scheduling; range registers define address recognition; hit/result registers provide hardware observation.

## Dependencies and integration points

The file depends on generated-header inclusion and standard preprocessing. It integrates with Goya-specific initialization, security/range programming, and hardware monitoring paths through common register access helpers. It should be regenerated with the rest of the Goya ASIC register set rather than edited independently.

## Risks and edge cases

The repeated layout invites mechanical loops, but any loop must use the correct base stride and must not assume every MME-adjacent block follows the router layout. Range masks are easy to mispair, especially HBW low/high halves. Bad arbitration or credit values can create performance stalls or fabric starvation rather than immediate compile-time failures.

## Test signals

Useful checks are a clean module build, register-dump comparison against the expected MME5 window, successful MME command execution under load, absence of unexpected range-hit/fabric errors, and regression coverage for any code that applies router range programming across all MME router instances.
