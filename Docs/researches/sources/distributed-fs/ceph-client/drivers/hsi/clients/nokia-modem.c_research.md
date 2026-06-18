# sources/distributed-fs/ceph-client/drivers/hsi/clients/nokia-modem.c

## Purpose
`nokia-modem.c` is an HSI composition driver for Nokia modem hardware such as the N900/RX-51 family. It binds to a DT-described `nokia-modem` HSI client, exports modem control GPIOs for userland-based power management, handles modem reset indication interrupts, and instantiates the `ssi-protocol` and `cmt-speech` child HSI clients on the same port.

## Important APIs, Types, and Functions
- Module parameter `pm` controls whether GPIO-based userland power management is enabled; default is 1.
- `struct nokia_modem_gpio` stores one GPIO descriptor and exported name.
- `struct nokia_modem_device` stores the reset tasklet/IRQ, owning device, GPIO array/count, and child `hsi_client` pointers for SSI protocol and CMT speech.
- `nokia_modem_gpio_probe()` reads all unnamed-index GPIOs and `gpio-names` from DT, requests them as output-low, exports them to sysfs, and creates named links under the device kobject.
- `nokia_modem_gpio_unexport()` removes the sysfs links and unexports descriptors.
- `nokia_modem_rst_ind_isr()` schedules `do_nokia_modem_rst_ind_tasklet()`, which calls `ssip_reset_event()` on the SSI protocol child.
- `nokia_modem_probe()` validates DT, maps the reset IRQ, sets wakeup, optionally exports GPIOs, creates and attaches `ssi-protocol` and `cmt-speech` HSI child devices, and unwinds on error.
- `nokia_modem_remove()` removes children, unexports GPIOs, disables wake, and kills the tasklet.

## Control Flow
Probe requires an OF node. It allocates device state with devm, parses the first IRQ with `irq_of_parse_and_map()`, records trigger flags, initializes a tasklet, requests the IRQ, and enables IRQ wake. If `pm` is enabled, it probes and exports GPIOs. It then copies the parent HSI TX/RX config into `struct hsi_board_info` for `ssi-protocol`, creates the child with `hsi_new_client()`, and forces driver binding with `device_attach()`. The same sequence is repeated for `cmt-speech`. On missing child drivers, `device_attach()` returning 0 is converted to `-EPROBE_DEFER`.

The reset indication IRQ handler does minimal work and defers to the tasklet. The tasklet logs the line change and notifies the SSI protocol child so the protocol layer can reset its state.

Remove tears down children in reverse conceptual order, unexports GPIOs, clears drvdata, disables IRQ wake, and kills the tasklet.

## State and Persistence
Runtime state is per modem device and devm-managed except for child HSI clients, sysfs GPIO exports, IRQ wake state, and tasklet lifecycle. GPIO values may be controlled externally through sysfs while the driver is loaded. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on OF device matching, GPIO descriptor APIs, sysfs GPIO export, IRQ APIs, tasklets, HSI child-client creation/removal, and SSI protocol reset notification. Kconfig requires `HSI`, `SSI_PROTOCOL`, and `CMT_SPEECH`, matching the child drivers it instantiates. OF compatibles include `nokia,n900-modem`, `nokia,n950-modem`, and `nokia,n9-modem`.

## Risks and Edge Cases
- If `pm=0`, `remove()` still calls `nokia_modem_gpio_unexport()` unconditionally; with zero/default GPIO state this loop is harmless only if `gpio_amount` remains zero.
- GPIO export is legacy sysfs ABI; failures after partially exporting GPIOs rely on the probe error path calling full unexport.
- `enable_irq_wake()` return value is not checked, so wake capability failures are silent.
- `device_attach()` is forced immediately for children; missing modules produce probe deferral, and attach errors unwind both children.
- The reset tasklet can race with removal unless IRQ disable/devm cleanup and `tasklet_kill()` ordering remain sufficient.

## Test Signals
- DT tests should cover missing OF node, invalid IRQ, mismatched GPIO and `gpio-names` counts, GPIO request/export failures, and valid Nokia compatibles.
- Probe tests should verify creation and binding of `ssi-protocol` and `cmt-speech` children with inherited HSI configs.
- Runtime tests should toggle the reset indication IRQ and verify `ssip_reset_event()` is called without sleeping in IRQ context.
- Remove/error-path tests should confirm child clients are removed, GPIO sysfs links disappear, IRQ wake is disabled, and no tasklet runs after teardown.
