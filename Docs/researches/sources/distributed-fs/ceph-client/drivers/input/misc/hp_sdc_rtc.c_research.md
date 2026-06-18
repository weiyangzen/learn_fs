<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hp_sdc_rtc.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/hp_sdc_rtc.c

## Purpose
`hp_sdc_rtc.c` is a legacy HP i8042 System Device Controller plus MSM-58321 battery-backed RTC module. It exposes RTC-like diagnostics through `/proc/driver/rtc` and uses HP SDC transactions to read the BBRTC and several i8042 timers.

## Important APIs, Types, and Functions
The code uses `hp_sdc_transaction`, `hp_sdc_enqueue_transaction()`, `hp_sdc_request_timer_irq()`, and `hp_sdc_release_timer_irq()` from the HP SDC subsystem. `hp_sdc_rtc_do_read_bbrtc()` constructs a long command sequence to read BCD RTC fields; `hp_sdc_rtc_read_bbrtc()` reads twice until stable because the MSM-58321 has no read latch. `hp_sdc_rtc_read_i8042timer()` serializes timer register access through semaphore `i8042tregs` and reads real-time, handshake, match, delay, and cycle timers. `hp_sdc_rtc_proc_show()` formats all data for procfs.

## Control Flow
Module init optionally gates on HP300 for m68k, initializes the timer semaphore, requests an SDC timer IRQ with a no-op ISR, creates `/proc/driver/rtc`, and logs module load. Proc reads synchronously issue SDC transactions, sleep on semaphores until results arrive, convert raw timer ticks into `timespec64`, and print failures if reads fail. Module exit removes procfs and releases the timer IRQ.

## State and Persistence Behavior
Global `epoch` defaults to 2000 and `i8042tregs` serializes timer output register use. There is no set-time path or persistent kernel state; hardware RTC/timer state is read-only from this module.

## Dependencies and Integration Points
It depends on HP SDC platform support, procfs/seq_file, semaphores, and RTC formatting constants. Despite living under input misc, it is not an input device.

## Risks and Test Signals
Risks include long synchronous proc reads, fragile hard-coded transaction sequence offsets, interruptible semaphore waits returning generic failures, proc entry collision with other RTC implementations, and limited architecture/platform coverage. Tests should validate stable double-read behavior, nonpresence detection, timer conversion, SDC enqueue failure paths, proc output for partial read failures, and init/exit resource pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hp_sdc_rtc.c -->
