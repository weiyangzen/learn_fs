<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/iguanair.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/iguanair.c

Purpose: USB raw IR receiver/transmitter driver for IguanaWorks USB IR transceivers. It receives compact raw samples, transmits carrier-period encoded waveforms, and exposes rc-core RX/TX callbacks.

Important APIs and functions: `struct iguanair` stores rc device, USB device, firmware version/features, RX/TX URBs and DMA buffers, completion, receiver state, carrier, and TX packet. Key functions are `process_ir_data`, `iguanair_rx`, `iguanair_send`, `iguanair_get_features`, `iguanair_receiver`, TX callbacks `iguanair_set_tx_carrier`, `iguanair_set_tx_mask`, `iguanair_tx`, rc open/close, probe/disconnect, and suspend/resume.

Control flow: probe validates interrupt endpoints, allocates coherent IN/OUT buffers and URBs, submits the IN URB, sends a NOP and feature queries, rejects firmware older than `0x0205`, fills an rc raw device with RX/TX callbacks and timeouts, defaults to 38 kHz and no TX mask, registers rc-core, and stores USB data. Incoming URBs either complete control commands or decode seven-byte IR sample packets into pulse/space events. TX converts microsecond durations to carrier periods, chunks into 7-bit payload entries with pulse/space markers, sends the packet, and reports overflow if firmware returns `CMD_TX_OVERFLOW`. Suspend disables receiver if active and kills URBs; resume resubmits RX and reenables receiver.

State and persistence: state includes firmware version, buffer size, cycle overhead, current carrier, TX channel mask, receiver-on flag, and DMA-backed packet buffers. Settings persist only while the USB device remains bound.

Dependencies and integration points: depends on USB interrupt URBs, coherent DMA buffers, completions, and rc-core raw RX/TX APIs. USB ID is `1781:0938`; default map is RC6 MCE.

Risks: TX packet size is bounded by firmware-reported `bufsize`; long waveforms return `-EINVAL`. Carrier generation relies on firmware CPU-cycle calculations and `cycle_overhead` from feature query. Probe submits the RX URB before feature negotiation, so control responses and raw packets share the same IN path. `iguanair_send` waits for `TIMEOUT` jiffies, not milliseconds, because it passes the raw constant to `wait_for_completion_timeout`.

Test signals: firmware version/feature negotiation, RX sample decoding including `0x80` long space, TX carrier/mask/waveform output, overflow reporting, open/close receiver commands, suspend/resume, and disconnect during active RX/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/iguanair.c -->
