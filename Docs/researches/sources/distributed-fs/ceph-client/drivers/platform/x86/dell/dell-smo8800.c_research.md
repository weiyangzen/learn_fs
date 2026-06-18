# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800.c

Purpose: Dell Latitude ACPI SMO88xx freefall sensor driver exposing events through `/dev/freefall`.

Important APIs/types/functions: `struct smo8800_device`, quick/threaded IRQ handlers, misc read/open/release operations, and platform probe/remove.

Control flow/state/persistence: Probe registers misc device `freefall`, obtains IRQ 0, and requests a threaded rising-edge IRQ. Quick IRQ increments an atomic counter and wakes blocking readers; threaded IRQ logs detection. `read()` waits for an event, returns one byte capped at 255, and clears the counter. Open is exclusive. Remove frees IRQ and deregisters misc device.

Dependencies/integration: ACPI ID table, platform IRQ resources, miscdevice, atomics, waitqueues, threaded IRQs.

Risks/test signals: Blocking single-open semantics and coalesced event count need validation. Test missing IRQ, misc registration failure, interrupted reads, concurrent open `-EBUSY`, actual freefall interrupt delivery, and cleanup with open users.
