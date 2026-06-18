# sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec.c

## Purpose
This is the older Amlogic Meson GX AO CEC controller driver. It exposes a single-logical-address CEC adapter over the CEC framework using raw MMIO and an indirect CEC register access window.

## Important APIs, Types, and Functions
`struct meson_ao_cec_device` stores the platform device, mapped base, core clock, spinlock for indirect register access, notifier, adapter, and RX message. Low-level helpers `meson_ao_cec_read`, `meson_ao_cec_write`, and `meson_ao_cec_wait_busy` serialize CEC register access through `CEC_RW_REG`. CEC callbacks are `meson_ao_cec_adap_enable`, `meson_ao_cec_set_log_addr`, and `meson_ao_cec_transmit`.

## Control Flow
Probe obtains the HDMI device from DT, allocates the adapter, maps MMIO, requests a threaded IRQ, gets/enables the `core` clock, sets it to 32768 Hz, resets the device, registers the notifier, and registers the adapter. Enable masks interrupts, asserts reset, enables the gated clock, releases reset, clears RX/TX buffers, programs arbitration timings, and unmasks TX/RX interrupts. Transmit aborts a busy TX, writes message bytes and length, and requests current-message transmission. The IRQ thread handles TX status first, then runs RX processing every interrupt pass.

## State and Persistence
State is volatile: the CEC hardware stores message FIFOs, logical address 0, timing registers, and interrupt status. The driver stores only one in-flight RX message and no persistent logical address configuration. Logical address invalid disables address 0 and clears hardware buffers.

## Dependencies and Integration Points
The driver integrates with `cec_notifier_parse_hdmi_phandle`, `cec_notifier_cec_adap_register`, the CEC core, platform MMIO resources, IRQs, reset, and a `core` clock. DT compatible is `amlogic,meson-gx-ao-cec`.

## Risks and Test Signals
The indirect register access window is protected by a spinlock and 5 ms busy wait; timeout paths are critical. RX processing assumes `CEC_RX_NUM_MSG == 1` and clears/acks buffers after each interrupt. Test with clock-rate setup, reset recovery, busy TX abort, RX/TX interrupt clearing, logical address invalidation, and all signal-free-time modes. Probe failure tests should verify adapter/notifier/clock cleanup.
