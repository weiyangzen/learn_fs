
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.h

Purpose: PTI/LPP register offset and bit definitions.

Important APIs/types/functions: defines `REG_PTI_CTL` plus PTI enable, free-running clock, mode, clock divider, pattern-generator, LPP-present, destination, active, and busy bits. Also defines LPP destination enum bits for PTI and EXI.

Control flow: no executable logic; `pti.c` composes and decodes `REG_PTI_CTL` with these masks.

State and persistence: describes volatile PTI/LPP register state.

Dependencies and integration: included by `pti.c`.

Risks: header guard is named `__INTEL_TH_STH_H__`, duplicating `sth.h`'s guard name. If both headers are included in one translation unit in the wrong order, PTI definitions can be skipped or STH definitions hidden. Current files avoid that collision, but it is a maintainability risk.

Test signals: compile translation units including PTI and STH headers together to expose guard collision, and hardware tests for mode/destination bit programming.
