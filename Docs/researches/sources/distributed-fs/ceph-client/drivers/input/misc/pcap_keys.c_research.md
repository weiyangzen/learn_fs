# sources/distributed-fs/ceph-client/drivers/input/misc/pcap_keys.c

Purpose: reports Motorola PCAP2 PMIC power and headset button events as KEY_POWER and KEY_HP.

Important APIs/types/functions: EZX PCAP MFD helpers, platform IRQ mapping, and input. `struct pcap_keys` stores parent chip and input. Main routines are IRQ handler, probe, and remove.

Control flow: probe allocates state/input, configures EV_KEY bits, registers input, requests ONOFF and MIC IRQs, and returns. Handler maps Linux IRQ to PCAP IRQ, reads `PCAP_REG_PSTAT`, masks the relevant bit, reports inverted status for KEY_POWER or KEY_HP, and syncs. Remove frees IRQs and unregisters input.

State/persistence: no cached button state or durable state.

Dependencies/integration: platform child `pcap-keys`/alias `pcap_keys`, parent `pcap_chip`, BUS_HOST input.

Risks: `ezx_pcap_read` errors are ignored. Status polarity is assumed active-low. No PM/wakeup handling.

Test signals: both IRQ sources, status polarity, IRQ mapping, read failure, second IRQ request failure cleanup, and input reports.
