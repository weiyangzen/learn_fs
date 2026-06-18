# sources/distributed-fs/ceph-client/drivers/memstick/host/rtsx_usb_ms.c Research

## Purpose
`rtsx_usb_ms.c` implements a MemoryStick host for Realtek RTS5129/RTS5139-class USB card readers exposed through the `rtsx_usb` core. It translates memstick core requests into Realtek register-command batches and USB bulk transfers.

## Important APIs, Types, And Functions
`struct rtsx_usb_ms` stores the platform device, Realtek USB core pointer, memstick host, current request, mutex/work items, card polling work, clock/SSC settings, power/interface state, eject flag, and system suspend flag. Important functions include `ms_power_on`, `ms_power_off`, `ms_transfer_data`, `ms_write_bytes`, `ms_read_bytes`, `rtsx_usb_ms_issue_cmd`, `rtsx_usb_ms_handle_req`, `rtsx_usb_ms_request`, `rtsx_usb_ms_set_param`, `rtsx_usb_ms_poll_card`, probe/remove, and PM callbacks.

## Control Flow
Probe obtains the parent `rtsx_ucr`, allocates a memstick host, initializes work and delayed polling, enables runtime PM, and registers the host. Requests schedule a work item. The worker runtime-resumes the device, repeatedly pulls memstick requests, takes the Realtek device mutex, checks exclusive card ownership, issues the command, stores the request error, and lets `memstick_next_req` advance the queue. Long data uses `MS_TRANSFER` plus USB bulk transfer through a ring buffer; short data uses ping-pong buffer register batches. If card INT is required, serial mode explicitly reads `MS_TPC_GET_INT`, while parallel mode derives memstick INT bits from Realtek status.

## State And Persistence
State is volatile: power mode, clock, SSC depth, interface mode, in-flight request, delayed polling, runtime PM references, and error bits in the Realtek core. No card metadata is persisted here.

## Dependencies And Integration Points
The file depends on `rtsx_usb` register helpers, USB bulk pipes, runtime/system PM, memstick host callbacks, workqueues, delayed work, platform-device binding, and Realtek card-sharing arbitration. It advertises `MEMSTICK_CAP_PAR4`.

## Risks
Runtime PM reference balancing is subtle because power-on takes an extra no-resume reference and removal compensates for active state. Card detection is polling-based after power-on, so latency and runtime suspend interactions matter. The host mutex exists but request execution mostly serializes through work and the parent device mutex; removal must safely drain `host->req`. Error decoding differs for read/write byte TPCs and can return timeout for status combinations that are not CRC/INT errors.

## Test Signals
Test probe/remove as platform child of `rtsx_usb`, runtime suspend/resume with no card and with card powered off, system suspend ordering, insertion/removal polling, serial and 4-bit mode, short-byte commands, long bulk read/write paths, exclusive-card conflicts with SD/XD functions, and forced USB transfer errors.
