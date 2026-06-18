# sources/distributed-fs/ceph-client/drivers/input/tablet/kbtab.c

## Purpose
`kbtab.c` is a compact USB driver for the KB Gear JamStudio tablet. It converts 8-byte interrupt reports into pen coordinates, right-button state, and either left-click-by-pressure or raw pressure events.

## Important APIs, types, and functions
`struct kbtab` stores the DMA buffer, input device, USB interface, URB, and physical path. `kbtab_irq()` decodes reports. `kbtab_probe()` validates an interrupt-in endpoint, allocates resources, sets input capabilities, and registers the device. `kbtab_open()` submits the URB and `kbtab_close()` kills it. Module parameter `kb_pressure_click` controls pressure threshold or raw pressure reporting when set to `-1`.

## Control flow
Probe matches vendor `0x084e` product `0x1001`, configures `EV_KEY` and `EV_ABS`, sets X/Y/pressure ranges, and fills an 8-byte interrupt URB. Each interrupt reports `BTN_TOOL_PEN`, X/Y from little-endian fields, `BTN_RIGHT`, and either `BTN_LEFT` based on pressure threshold or `ABS_PRESSURE`; then it syncs and resubmits the URB.

## State and persistence
Per-device state is minimal and nonpersistent. The pressure threshold is a module parameter set at load time. The driver always reports the pen tool as present during packets and does not track proximity release state.

## Dependencies and integration points
It uses USB input helpers, coherent DMA, unaligned little-endian access, input event reporting, and module parameter infrastructure.

## Risks
No proximity-out handling means userspace may rely on absence of packets or higher-level heuristics. Threshold mode suppresses pressure events even though ABS_PRESSURE is configured. Only endpoint 0 is considered. The default pressure-to-left-click policy is driver-specific and may not match modern tablet expectations.

## Test signals
Test USB ID binding, invalid endpoint rejection, coordinate decoding, pressure threshold boundaries including `-1`, URB resubmission after transient errors, open/close behavior, and input capability consistency.
