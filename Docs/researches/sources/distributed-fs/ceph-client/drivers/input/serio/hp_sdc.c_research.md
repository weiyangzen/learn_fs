<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc.c

## Purpose
`hp_sdc.c` is the HP System Device Controller driver for PA-RISC and HP300-style systems. It owns the i8042-like SDC hardware registers, services SDC interrupts, provides callback hooks for timer/HIL/cooked events, and exports a queued transaction engine used by higher-level drivers such as `hp_sdc_mlc.c`.

## Important APIs, types, and functions
- Exported transaction APIs are `__hp_sdc_enqueue_transaction()`, `hp_sdc_enqueue_transaction()`, and `hp_sdc_dequeue_transaction()`.
- Exported hook APIs are `hp_sdc_request_timer_irq()`, `hp_sdc_request_hil_irq()`, `hp_sdc_request_cooked_irq()` and matching release functions.
- The single global `hp_i8042_sdc hp_sdc` holds all device state: I/O addresses, IRQs, interrupt mask, tasklet/timer, hook callbacks, read/write queue indices, transaction array, register cache `r7[]`, input-buffer-full tracking, and locks.
- `hp_sdc_status_in8()`, `hp_sdc_data_in8()`, `hp_sdc_status_out8()`, `hp_sdc_data_out8()`, and `hp_sdc_spin_ibf()` are the low-level SDC register access primitives.
- `hp_sdc_isr()` demultiplexes hardware interrupt status into timer, register-transaction, HIL, PUP, and cooked paths.
- `hp_sdc_take()` appends register-read status/data pairs to the current transaction and completes its semaphore or callback when enough data has arrived.
- `hp_sdc_put()` is the transaction scheduler. It serializes output to slow SDC hardware, advances actions, starts reads, updates the interrupt mask, and interleaves queued transactions.
- `hp_sdc_tasklet()` handles read timeouts and invokes `hp_sdc_put()`.

## Control flow
Module init registers the platform-specific discovery path. On PA-RISC the parisc bus probe fills the SDC I/O and IRQ fields, calls `hp_sdc_init()`, and schedules delayed loading of `hp_sdc_mlc`. On HP300 the module probes fixed I/O addresses.

`hp_sdc_init()` initializes locks and queue state, claims I/O/IRQ resources, installs the normal and NMI interrupt handlers, drains the controller, initializes the tasklet, synchronizes the cached output buffer registers through a semaphore-backed transaction, and starts the keepalive timer. `hp_sdc_register()` then reads the keyboard controller config byte, detects old/new SDC style, optionally reads extended config, and writes the self-test register for new-style SDCs.

At runtime clients enqueue `hp_sdc_transaction` objects. The tasklet calls `hp_sdc_put()`, which skips work while IBF is set, finds an eligible transaction, executes action bytes in the transaction sequence, writes precommands/data/data-register updates/postcommands, starts reads by setting `rcurr` and `rqty`, and completes semaphore or callback actions. IRQ context calls `hp_sdc_take()` for register reads and hook callbacks for asynchronous SDC/HIL events.

Exit masks SDC sub-function interrupts, waits for IBF to clear, frees IRQs, deletes the timer, kills the tasklet, cancels delayed module loading, and unregisters the parisc driver where applicable.

## State and persistence
The driver has one global controller instance. Transaction state is in RAM and protected by `hp_sdc.lock` and `hp_sdc.rtq_lock`; callback hooks are protected by `hp_sdc.hook_lock`; IBF tracking is protected by `hp_sdc.ibf_lock`. The cached write-index register and data-register bytes reduce I/O but are not persistent. Hardware configuration changes, interrupt masks, and self-test register writes persist in the SDC until firmware or hardware reset.

## Dependencies and integration points
The file depends on HP SDC protocol definitions from `<linux/hp_sdc.h>`, HIL constants, parisc or m68k I/O accessors, platform-specific discovery, Linux IRQs, tasklets, timers, semaphores, and exported symbols consumed by `hp_sdc_mlc` and other HP SDC clients.

## Risks
- The transaction sequence format is compact and stateful; malformed `seq`, `idx`, `actidx`, or `endidx` values can desynchronize the scheduler or complete the wrong action.
- `hp_sdc_dequeue_transaction()` has a TODO noting it may remove a transaction before completion.
- Timeout handling marks actions dead and may invoke callbacks from tasklet context, which differs from normal IRQ hook context.
- Busy-waiting in `hp_sdc_spin_ibf()` and IBF polling paths is hardware-sensitive and can waste CPU if the SDC wedges.
- The driver assumes a single SDC. Duplicate device discovery is rejected only by the global `hp_sdc.dev` state.
- Error cleanup on some init paths releases fixed regions conditionally; platform-specific resource paths need hardware coverage.

## Test signals
- Build on HPPA/HP300-capable configurations and verify exported symbols match `hp_sdc_mlc`.
- Hardware tests should cover old-style and new-style SDC detection, config-byte read timeout, extended-config read, interrupt-mask updates, delayed `hp_sdc_mlc` autoload, and module unload.
- Transaction tests should cover data-register writes with cached `r7[]`, precommand/dataout/postcommand/datain combinations, queue-full behavior, duplicate transaction rejection, read timeouts, and semaphore/callback completions.
- IRQ tests should inject timer, HIL command/data, PUP, cooked, register, and unknown status classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc.c -->
