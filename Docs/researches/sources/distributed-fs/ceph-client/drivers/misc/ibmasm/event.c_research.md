# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/event.c

## Purpose
`event.c` stores asynchronous IBM ASM service-processor events in a circular buffer and delivers them to registered ibmasmfs event readers.

## Important APIs, Types, and Functions
Public functions are `ibmasm_event_buffer_init()`, `ibmasm_event_buffer_exit()`, `ibmasm_receive_event()`, `ibmasm_event_reader_register()`, `ibmasm_event_reader_unregister()`, `ibmasm_get_next_event()`, and `ibmasm_cancel_next_event()`. Helpers include `wake_up_event_readers()` and `event_available()`.

## Control Flow
Initialization allocates an `event_buffer`, clears serial numbers, and initializes the reader list. Incoming events from interrupt context are truncated to `IBMASM_EVENT_MAX_SIZE`, copied from I/O memory into the next circular slot, assigned a serial number, and all readers are woken. Readers register with the current next serial, block until an event or cancellation, find the first event at or after their expected serial, copy it into reader-private storage, and advance their serial.

## State and Persistence
The service processor owns one circular buffer with ten events, next index, next serial, and a list of readers. Each reader tracks cancellation, next serial, wait queue, and latest copied event. Old events are overwritten if readers fall behind.

## Dependencies and Integration Points
It depends on `sp->lock`, wait queues, list management, and ibmasmfs event file operations. Incoming data is passed by `dot_command.c` from the low-level interrupt path.

## Risks and Edge Cases
Readers that lag by more than the circular buffer depth lose events silently and resume at the oldest still matching serial scan. `wake_up_event_readers()` walks the reader list without taking the service-processor lock, which relies on surrounding usage not racing with unregister. Cancellation returns zero if no event is available.

## Test Signals
Test reader registration/unregistration, blocking read wakeups, cancellation by write, circular overwrite behavior, max-size truncation, concurrent readers, and interrupt-context receive while readers close.
