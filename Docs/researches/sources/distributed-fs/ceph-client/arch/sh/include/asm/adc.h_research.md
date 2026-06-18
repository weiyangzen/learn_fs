# sources/distributed-fs/ceph-client/arch/sh/include/asm/adc.h



Source read size: 12 lines, 211 bytes.



Purpose: ADC access facade.

Important APIs/types/functions: `adc_single()` and CPU-specific `<cpu/adc.h>`.

Control flow: callers request one conversion from a CPU-provided ADC implementation.

State and persistence: ADC hardware state is external.

Dependencies and integration points: CPU ADC drivers and board sensor users.

Risks and test signals: channel numbering and CPU header availability. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
