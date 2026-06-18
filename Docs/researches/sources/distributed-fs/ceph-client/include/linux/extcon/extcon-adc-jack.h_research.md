# sources/distributed-fs/ceph-client/include/linux/extcon/extcon-adc-jack.h

Purpose: platform-data contract for an ADC-based analog jack extcon provider.

Important APIs/types/functions: `struct adc_jack_cond` mapping connector ID to inclusive ADC range, and `struct adc_jack_pdata` carrying extcon name, IIO consumer channel name, supported cable IDs, ADC conditions, IRQ flags, debounce/handling delay, and wakeup-source flag.

Control flow: the ADC jack driver receives platform data, waits for IRQ, optionally delays, samples the ADC channel, selects the first matching condition, and publishes extcon state; no match means no cable attached.

State/persistence: runtime sampled ADC-derived connector state. Hardware accessory connection may persist physically; kernel state is recalculated.

Dependencies/integration: extcon core, module/platform data, IIO ADC consumer channel, IRQ handling, wakeup source integration.

Risks/test signals: risks are overlapping ADC ranges, missing sentinel condition, delay rounding, noisy ADC readings, incorrect cable ID list, and wakeup misconfiguration. Test boundary ADC values, no-match state clearing, IRQ debounce, suspend wakeup, and multiple cable conditions.
