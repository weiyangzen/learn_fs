# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hdcp.c

## Purpose
Implements HDCP 1.x authentication for the MSM HDMI bridge. It drives the HDMI HDCP cipher, exchanges authentication data with the sink over DDC, validates local and remote KSVs, handles repeaters, and reauthenticates after HDCP link failures.

## Important APIs, types, and functions
- `struct hdmi_hdcp_ctrl` stores HDMI backpointer, retry counters, secure-world write mode, HDCP state, auth/reauth work items, wait events, AKSV/BKSV, repeater topology, and KSV FIFO.
- `msm_hdmi_hdcp_init()`, `msm_hdmi_hdcp_destroy()`, `msm_hdmi_hdcp_on()`, `msm_hdmi_hdcp_off()`, and `msm_hdmi_hdcp_irq()` are the integration surface used by the HDMI driver.
- DDC helpers `msm_hdmi_ddc_read()` and `msm_hdmi_ddc_write()` access HDCP receiver offsets at slave address `0x74`.
- Secure register writes go through `msm_hdmi_hdcp_scm_wr()` when `qcom_scm_hdcp_available()` is true, otherwise normal MMIO writes are used.
- Authentication phases are split across `msm_hdmi_hdcp_auth_prepare()`, part-1 key/R0 helpers, and part-2 repeater KSV/SHA helpers.

## Control flow
`msm_hdmi_hdcp_on()` clears encryption, resets auth events, marks the state authenticating, and queues `hdcp_auth_work`. The worker validates AKSV from QFPROM, switches DDC arbitration to software, writes AKSV/entropy, enables the HDCP block, clears stale DDC failures, waits for keys and An, reads BCAPS, sends An/AKSV, reads BKSV, enables HDCP interrupts, reads R0 prime after the required delay, and waits for the hardware result interrupt. Receiver-only sinks complete after part 1. Repeaters proceed to poll BCAPS READY, read BSTATUS, reject excessive depth/device counts, read the KSV FIFO and V prime hash values, reset the SHA engine, feed KSV bytes to the hardware in 64-byte chunks, and wait for V match.

Interrupt handling acknowledges success/failure bits under `reg_lock`. Auth success wakes the auth worker. Auth failure during an authenticated session queues reauth; failure during authentication wakes the worker to inspect status. Reauth temporarily disables HPD and HDCP interrupts, deauthenticates the link, waits for the DDC engine to settle, disables encryption, reenables HPD, and retries up to `AUTH_RETRIES_TIME`.

## State and persistence
State is held in `hdmi->hdcp_ctrl` and the workqueue while the HDMI device exists. The state machine transitions through no-AKSV, inactive, authenticating, authenticated, and failed. AKSV is cached after QFPROM validation. Hardware state persists in HDMI HDCP, DDC, HPD, SHA, and encryption registers until reset or power loss. Sink-side HDCP registers are written over DDC during each authentication.

## Dependencies and integration points
Depends on `hdmi.h` register helpers, the HDMI I2C/DDC adapter, QFPROM reads, Qualcomm SCM HDCP requests, Linux workqueues/waitqueues, and `hdmi->reg_lock`. It integrates with HDMI IRQ dispatch, bridge enable/disable paths, and the shared HDMI workqueue.

## Risks
Authentication is timing-sensitive and has several long polling loops. The DDC cleanup loop appears easy to misread because it breaks when hardware is not ready, so regressions around DDC recovery are likely. Secure-world register writes must use physical offsets correctly or HDCP programming fails. `ksv_list` size assumes the HDCP 1.x maximum of 127 downstream devices; incorrect BSTATUS handling can overrun protocol expectations. Work cancellation and HPD toggling must remain ordered or reauth/off can race with IRQ wakeups.

## Test signals
Useful signals are `AUTH_SUCCESS_INT`/`AUTH_FAIL_INT` logs, LINK0 status dumps, AKSV/BKSV hweight validation failures, DDC timeout/NACK logs, R0/V match failures, and retry exhaustion. Tests should cover no-QFPROM systems, receiver and repeater sinks, DDC failure recovery, hot-unplug during auth, reauth after link failure, and secure-world versus direct-MMIO paths.
