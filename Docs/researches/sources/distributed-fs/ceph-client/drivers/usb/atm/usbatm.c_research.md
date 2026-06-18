# sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.c

## Purpose
`usbatm.c` is the shared USB ATM/DSL core used by mini-drivers. It registers an ATM device, manages USB RX/TX URB pools, performs ATM cell extraction and AAL5 reassembly, encodes outbound AAL5 PDUs into ATM cells, handles VCC open/close/send callbacks, runs optional mini-driver heavy initialization, and coordinates disconnect cleanup.

## Important APIs, Types, And Functions
- Module parameters `num_rcv_urbs`, `num_snd_urbs`, `rcv_buf_bytes`, and `snd_buf_bytes` size URB pools and buffers.
- `struct usbatm_vcc_data` tracks VPI/VCI, `atm_vcc`, and SAR reassembly buffer.
- `struct usbatm_control` stores outbound skb ATM metadata, original length, and CRC in `skb->cb`.
- `usbatm_usb_probe()` allocates `struct usbatm_data`, calls mini-driver `bind`, allocates URBs/buffers, starts heavy init or ATM init, and sets USB interface data.
- `usbatm_usb_disconnect()` marks disconnected, stops heavy init, releases VCCs, kills URBs/timers/tasklets, calls mini-driver stop/unbind, frees buffers, deregisters ATM, and drops references.
- `usbatm_extract_one_cell()`/`usbatm_extract_cells()` implement AAL5 receive reassembly and CRC validation.
- `usbatm_write_cells()` and `usbatm_tx_process()` implement outbound cell segmentation.
- `usbatm_atm_open()`, `close()`, `send()`, `ioctl()`, and `proc_read()` implement ATM operations.

## Control Flow
Probe builds one RX and one TX channel, chooses bulk or isochronous RX based on mini-driver flags, allocates URBs, queues TX URBs as spares, and either starts a heavy-init kthread or initializes ATM directly. ATM init registers the ATM device, lets the mini-driver start it, then submits RX URBs. RX completion queues URBs to a tasklet; the tasklet extracts complete cells, handles partial strides, and resubmits URBs. TX send queues skb PDUs; the TX tasklet pops spare URBs and encodes cells until buffers are full or queues drain. Disconnect serializes against open/close, cancels asynchronous activity, releases VCCs, and deregisters ATM.

## State And Persistence Behavior
Per-device state includes kref lifetime, disconnect flag, serialization mutex, heavy-init thread completions, VCC list, cached VPI/VCI lookup, partial RX cell buffer, current TX skb, skb send queue, URB arrays, channel timers/tasklets, and ATM device pointer. No on-disk state exists. ATM counters are maintained through the ATM stack.

## Dependencies And Integration Points
The file depends on USB core, Linux ATM, sk_buffs, CRC32, tasklets, timers, kthreads, completions, and mini-driver hooks declared in `usbatm.h`. Mini-drivers provide endpoints, padding, firmware/control-plane behavior, and optional ATM start/stop callbacks.

## Risks And Edge Cases
URB submit errors are treated as transient and can throttle via timers. RX isochronous frame merging must preserve cell boundaries and resets partial buffers on frame errors. VCC list and cached lookup are protected by disabling RX tasklet during updates. Disconnect ordering is delicate because heavy init, ATM callbacks, tasklets, timers, and URBs can all race. `skb->cb` size is checked at module init. Only AAL5 is supported; OAM F5 is counted as unsupported.

## Test Signals
Run with mini-drivers in bulk and isochronous modes. Open multiple VCCs, verify VPI/VCI demultiplexing and duplicate rejection, send max-size AAL5 PDUs, inject CRC/length errors, and confirm ATM stats. Fault-inject URB submit failures and unplug during heavy init, active RX, active TX, and VCC close. Validate module parameter bounds at init.
