# sources/distributed-fs/ceph-client/drivers/usb/serial/usb_wwan.c

## Purpose
`usb_wwan.c` implements shared GSM/mobile-broadband USB serial helper callbacks. It improves on simple generic serial behavior by maintaining multiple receive URBs, multiple transmit URBs, runtime PM references, optional CDC modem-control setup, optional zero-length packets, and suspend/resume delayed-write replay.

## Important APIs, Types, and Functions
Exported functions include `usb_wwan_dtr_rts()`, `usb_wwan_tiocmget()`, `usb_wwan_tiocmset()`, `usb_wwan_write()`, `usb_wwan_write_room()`, `usb_wwan_chars_in_buffer()`, `usb_wwan_open()`, `usb_wwan_close()`, `usb_wwan_port_probe()`, `usb_wwan_port_remove()`, and PM helpers. Internal helpers include `usb_wwan_send_setup()`, `usb_wwan_indat_callback()`, `usb_wwan_outdat_callback()`, `usb_wwan_setup_urb()`, `unbusy_queued_urb()`, `stop_urbs()`, and `usb_wwan_submit_delayed_urbs()`.

## Control Flow, State, and Persistence
Consumers allocate `usb_wwan_intf_private` as serial data and use `usb_wwan_port_probe()` to allocate four page-backed IN buffers/URBs and four 4096-byte OUT buffers/URBs per port. Open submits the optional interrupt URB and all IN URBs, enables remote wakeup on first open, and balances the core runtime PM reference. Write slices user data across free OUT URBs, marks busy bits, obtains async runtime PM, queues URBs on the delayed anchor if suspended, or submits immediately and increments `in_flight`. Completion wakes the tty, drops runtime PM, decrements `in_flight`, and clears the matching busy bit. Read completion pushes data to the tty and resubmits unless fatal shutdown errors occur.

Close disables remote wakeup on last close, drains delayed writes while clearing busy bits and PM refs, kills all IN/OUT and interrupt URBs, and gets a no-resume PM reference to rebalance open. Suspend refuses autosuspend if writes are in flight, marks suspended, and kills URBs. Resume resubmits interrupt/read URBs for initialized ports and replays delayed writes before clearing the suspended flag.

State is per interface and per port in the structures declared by `usb-wwan.h`; no state persists outside kernel memory.

## Dependencies and Integration Points
The implementation depends on USB serial core, CDC control-line request definitions, TTY flip buffers, USB anchors, runtime PM, jiffies, and exported symbols for subdriver reuse. Subdrivers control behavior through `use_send_setup` and `use_zlp` flags.

## Risks and Test Signals
Risks include documented insufficient locking around signal and busy state, URB busy bits left set after unusual unlink paths, PM reference imbalance, delayed-anchor replay errors, and writes that make no progress because all URBs are busy or stale for less than ten seconds. Test signals include concurrent multi-URB writes, autosuspend with in-flight writes returning `-EBUSY`, delayed write replay on resume, close while suspended, DTR/RTS setup control transfers, ZLP behavior, and hot unplug during read resubmission.
