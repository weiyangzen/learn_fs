<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/adc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/adc.c

Purpose: implements a simple SH ADC single-conversion helper.

Important APIs/types/functions: `adc_single(unsigned int channel)`.

Control flow: selects a channel, starts conversion by programming ADC registers, waits for completion, clears status, and returns the sampled value.

State and persistence: ADC hardware registers hold channel, start, status, and result state.

Dependencies/integration: depends on SH ADC register definitions and callers that serialize/pace conversions.

Risks: busy-wait conversion can hang if hardware clock/reset is wrong; no rich error reporting.

Test signals: test valid channels, timeout behavior if added, and known voltage readings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/adc.c -->
