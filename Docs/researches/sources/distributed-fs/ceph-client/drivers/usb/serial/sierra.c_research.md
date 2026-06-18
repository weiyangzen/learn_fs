# sources/distributed-fs/ceph-client/drivers/usb/serial/sierra.c

## Purpose
`sierra.c` is a Sierra Wireless modem USB serial subdriver. It handles many legacy AirPrime/Sierra/HP/AT&T device IDs, ignores Direct IP non-serial interfaces, selects alternate settings for some composite devices, manages modem control signaling, and implements high-throughput multi-URB read/write paths with suspend/resume queuing.

## Important APIs, Types, and Functions
`struct sierra_intf_private` tracks suspend state, open-port count, and write URBs in flight. `struct sierra_port_private` tracks per-port anchors, outstanding write URB count, input URBs, modem signal state, and memory profile. Important functions include `sierra_probe()`, `sierra_calc_num_ports()`, `sierra_send_setup()`, `sierra_open()`, `sierra_close()`, `sierra_write()`, `sierra_indat_callback()`, `sierra_instat_callback()`, `sierra_suspend()`, and `sierra_resume()`. Module parameter `nmea` enables a vendor request to start NMEA streaming.

## Control Flow, State, and Persistence
Probe may switch alternate setting 1 on two-altsetting interfaces and rejects interfaces listed in `direct_ip_interface_ignore`. Port count comes from endpoint count except dummy interface `0x99`, which returns zero. Attach allocates interface-private state, sets device power D0, and optionally enables NMEA. Port probe chooses low- or high-memory URB counts based on interface/port lists. Open allocates input URBs, submits read and optional interrupt URBs, enables remote wakeup when the first port opens, and releases the autopm reference acquired by the core. Write allocates a new buffer and URB per request, enforces an outstanding URB limit, anchors active or delayed URBs depending on suspend state, sets `URB_ZERO_PACKET`, and uses async runtime PM references until completion. Close drains delayed writes, stops RX, kills active writes, frees read URBs, and balances runtime PM state.

Runtime state is in anchors, signal booleans, counters, and suspend flags; nothing persists across disconnect. Interrupt-in notifications update CTS/DCD/DSR/RI, and DCD drop triggers a tty hangup.

## Dependencies and Integration Points
The driver integrates with USB serial core callbacks and directly uses USB runtime PM, USB anchors, TTY flip buffers, and generic USB serial module registration. It does not use `usb_wwan.c`; it carries a similar private implementation. Power and NMEA control are Sierra vendor-specific control messages.

## Risks and Test Signals
Risks include URB accounting imbalance across submit failures, delayed URB handling during suspend/resume, overcounted `chars_in_buffer()`, alternate-setting assumptions, and shared global `nmea` behavior. Test signals should cover Direct IP ignore lists, high-memory interfaces, writes during autosuspend, resume delayed-write replay, DCD hangup, multi-port concurrent open/close, and runtime PM reference balance.
