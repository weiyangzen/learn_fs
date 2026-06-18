# sources/distributed-fs/ceph-client/drivers/input/tablet/pegasus_notetaker.c

## Purpose
`pegasus_notetaker.c` drives the Pegasus Mobile Notetaker EN100 and compatible digital pen receivers. It sets the device into XY pen mode with a vendor control report, reads interrupt packets, reports pen position and buttons, and supports USB autosuspend/resume.

## Important APIs, types, and functions
`struct pegasus` stores the USB/input state, coherent buffer, URB, PM mutex, open flag, names, and deferred initialization work. Key functions are `pegasus_control_msg()`, `pegasus_set_mode()`, `pegasus_parse_packet()`, `pegasus_irq()`, `pegasus_init()`, open/close helpers, probe/disconnect, and suspend/resume/reset-resume callbacks.

## Control flow
Probe binds only interface 0, validates packet size, allocates coherent DMA and an interrupt URB, sets input ABS/KEY properties, and registers the input device. Open gets an autosuspend PM reference, submits the URB, then sends the XY mode command. A special command packet schedules work to resend initialization. XY packets report low battery warnings, touch, pen button, tool, X, and Y; pen-up packets with zero coordinates are ignored. Suspend kills the URB and cancels init work; resume resubmits if open; reset-resume reprograms mode then resubmits.

## State and persistence
`is_open` under `pm_mutex` controls whether resume restarts I/O. The mode command changes device state while open and after reset-resume but is not persisted by the driver. Scheduled work is transient and canceled on close/suspend paths.

## Dependencies and integration points
The driver uses USB interrupt and control transfers, HID request constants, input ABS/KEY properties, workqueues, mutexes, and USB runtime PM. It matches vendor `0x0e20` product `0x0101`.

## Risks
Disconnect unregisters the input device before explicitly canceling `init` work; correctness relies on close/suspend paths or absence of pending work, so work lifetime deserves attention. Pen-up packets do not emit release events, potentially leaving tool/touch state if no later packet clears it. The driver sets both `INPUT_PROP_DIRECT` and `INPUT_PROP_POINTER`, which may be semantically ambiguous for userspace.

## Test signals
Test control-message framing, open failure cleanup after URB submit or mode command failure, special-command reinitialization, low-battery warning once, suspend/resume/reset-resume while open and closed, autosuspend references, and disconnect with pending init work.
