# sources/distributed-fs/ceph-client/drivers/soc/qcom/qcom_aoss.c

## Purpose

`qcom_aoss.c` implements the Qualcomm Always-On Subsystem QMP mailbox driver. It maps AOSS message RAM, performs the QMP link/channel handshake, exports `qmp_send()` and `qmp_get()/qmp_put()` to other drivers, registers a QDSS clock provider, optional thermal cooling devices, and debugfs write-only controls for AOSS sleep, CX collapse, DDR collapse, and DDR frequency requests.

## Important APIs, Types, and Functions

The central state is `struct qmp`, holding the message RAM mapping, mailbox channel, negotiated mailbox offset/size, waitqueue, TX mutex, clock hw, cooling devices, and debugfs dentries. `qmp_open()` validates `QMP_MAGIC`/`QMP_VERSION`, reads MCORE mailbox location, acknowledges UCORE link state, raises local link/channel state, kicks AOSS, and waits for ACKs. `qmp_send()` serializes formatted string messages into the message RAM and waits until the remote side clears the message length. Exported helpers are `qmp_send()`, `qmp_get()`, and `qmp_put()`. Integration helpers include `qmp_qdss_clk_add/remove()`, `qmp_cooling_devices_register/remove()`, and `qmp_debugfs_create()`.

## Control Flow

Probe allocates `struct qmp`, maps the first platform resource, requests mailbox channel 0 and the AOSS interrupt, opens the QMP link, registers the QDSS clock, registers cooling devices for child nodes with `#cooling-cells`, stores drvdata, and creates debugfs files. Interrupts simply wake the QMP waitqueue; all protocol progress is driven by wait conditions reading message RAM state. Remove tears down debugfs, clock provider, cooling devices, QMP state, and mailbox channel. `qmp_send()` writes the 64-byte payload after the length word, writes the length, readbacks for ordering, kicks AOSS, then waits up to one second for `qmp_message_empty()`.

## State and Persistence Behavior

Driver state is volatile and per platform device. AOSS-visible state is shared in message RAM: link-state words, channel-state words, mailbox offset/size, and the current outbound message. Persistent hardware effects are indirect: QMP messages can change AOSS-managed clock, thermal, and low-power behavior. Debugfs writes and cooling-device state cache the last requested boolean locally, but authoritative effect is in AOSS firmware.

## Dependencies and Integration Points

The driver depends on platform resources, mailbox framework, IRQ wakeups, MMIO accessors, clock provider APIs, thermal cooling devices, debugfs, device tree phandles, and tracepoints. `qcom_stats.c` uses `qmp_get()` and `qmp_send()` to synchronize DDR stats. Other Qualcomm clients can use the exported QMP API if their DT node has `qcom,qmp`.

## Risks and Edge Cases

`qmp_send()` always writes `sizeof(buf)` as the message length, not the formatted length, so the remote protocol must expect fixed 64-byte padded messages. Timeout handling clears the length word locally, which may race with delayed remote consumption. `qmp_cooling_devices_remove()` iterates a fixed two-entry array even when no cooling devices were registered; `qmp->cooling_devs` can be NULL if there were no child cooling nodes. `qmp_cooling_devices_register()` increments `count` without checking more than two eligible child nodes. Debugfs message construction relies on file dentry identity matching the stored dentry array. Link open failures leave link/channel state down but depend on firmware responding to the final kick.

## Test Signals

Useful tests include probe with invalid magic/version/zero mailbox size, mailbox request failure, IRQ timeout during each handshake phase, concurrent `qmp_send()` callers, long debugfs inputs, QDSS prepare/unprepare, cooling-device state changes, `qmp_get()` before and after probe, remove with no cooling devices, and AOSS firmware that delays or drops message acknowledgments.
