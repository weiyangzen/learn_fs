<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/pcap_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/pcap_ts.c

Purpose: platform driver for Motorola PCAP2 PMIC touchscreen ADC on EZX phones. It uses the PCAP MFD ADC async API and a delayed-work state machine to alternate pressure and XY reads, reporting single-touch coordinates and pressure.

Important APIs/types/functions: `struct pcap_ts` holds the PCAP handle, input device, delayed work, latest x/y/pressure, and ADC touchscreen read state. `pcap_ts_event_touch()` starts sampling from standby on PMIC touch IRQ. `pcap_ts_work()` programs touchscreen mode bits and starts ADC conversions. `pcap_ts_read_xy()` is the async ADC callback and drives pressure/XY/release transitions. Open/close are `pcap_ts_open()` and `pcap_ts_close()`, with PM callbacks writing low-power or current mode bits.

Control flow: probe allocates state/input, initializes read state to non-touchscreen, registers input, then requests the PCAP touchscreen IRQ. Open sets standby and schedules work to program mode. Touch IRQ switches to pressure mode and schedules immediate conversion. Pressure callback caches a usable pressure and switches to XY; XY callback either reports release and returns to standby when coordinates are out of range or reports X/Y/pressure and schedules the next pressure read after 20 ms. Close cancels work and programs non-touchscreen mode.

State and persistence: runtime state is the delayed work, last pressure, coordinates, and `read_state`. Hardware mode bits in the PCAP ADC block are modified while active or suspended. No nonvolatile state is written.

Dependencies/integration: depends on `ezx-pcap` MFD APIs (`pcap_set_ts_bits`, `pcap_adc_async`, `pcap_to_irq`), delayed work, platform driver binding `pcap-ts`, and Linux input core.

Risks and test signals: async ADC callbacks can race with close/remove unless work and PMIC callbacks are serialized by the MFD. Test remove while ADC callback is outstanding, pressure reliability filtering, release threshold at coordinate edges, suspend/resume restoring state, IRQ request after input registration failure unwinds, and sampling cadence under repeated touches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/pcap_ts.c -->
