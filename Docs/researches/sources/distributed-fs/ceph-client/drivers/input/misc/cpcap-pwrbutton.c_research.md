<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cpcap-pwrbutton.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cpcap-pwrbutton.c

Purpose: Motorola CPCAP PMIC power-button input driver.

Important APIs/types/functions: `struct cpcap_power_button` stores parent regmap, input device, and device pointer. `powerbutton_irq()` calls `cpcap_sense_virq()` to read current button sense, emits KEY_POWER, syncs input, and marks a wakeup event. Probe gets platform IRQ, parent regmap, input device, threaded IRQ, and enables wakeup.

Control flow and state: platform probe wires a single IRQ to a threaded handler. IRQ reads the live PMIC sense value rather than relying on edge polarity and reports it directly.

State and persistence behavior: no driver-side button state is retained. Wakeup capability persists for device lifetime.

Dependencies and integration points: depends on Motorola CPCAP MFD helpers, regmap, OF compatible `motorola,cpcap-pwrbutton`, platform IRQs, Linux input, and PM wakeup.

Risks: `devm_kmalloc()` leaves structure fields uninitialized until assigned, but all fields are set before use. Sense-read failures are logged but still return IRQ_HANDLED. No debounce is performed in this layer.

Test signals: test missing IRQ/regmap, press and release sense values, wakeup event generation, threaded IRQ request failure, and OF matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cpcap-pwrbutton.c -->
