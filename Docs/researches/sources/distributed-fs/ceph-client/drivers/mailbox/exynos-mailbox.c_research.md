<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/exynos-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/exynos-mailbox.c

## Purpose
`exynos-mailbox.c` implements a simple Samsung/Google Exynos mailbox, currently for GS101 ACPM doorbell sends. It exposes virtual mailbox channels and expects the data payload to identify the hardware doorbell channel.

## Important APIs, Types, and Functions
`struct exynos_mbox` holds the MMIO base and controller pointer. `exynos_mbox_send_data()` accepts `struct exynos_mbox_msg`, validates channel ID and type, and writes the interrupt generation bit. `exynos_mbox_of_xlate()` returns the first free virtual channel. Probe enables the peripheral clock and masks supported interrupts.

## Control Flow
Probe allocates state, controller, and 16 channels derived from `EXYNOS_MBOX_INTGR1_MASK`, maps registers, enables `pclk`, initializes mailbox ops/xlate, masks interrupt register 0, and registers the controller. DT phandles carry no args; xlate just reserves an unused mailbox channel. Send validates that `chan_type` is `EXYNOS_MBOX_CHAN_TYPE_DOORBELL` and that `chan_id` is in range, then writes `BIT(chan_id)` to `EXYNOS_MBOX_INTGR1`.

## State and Persistence
There is no receive path and no software queue. Runtime state is the clock-enabled device and mailbox channel client ownership tracked by the mailbox core.

## Dependencies and Integration Points
The driver depends on `linux/mailbox/exynos-message.h`, the clock framework, platform MMIO, OF compatible `google,gs101-mbox`, and mailbox clients that pass `struct exynos_mbox_msg` in `send_data()`.

## Risks and Edge Cases
Because channel ID comes from the payload rather than the mailbox phandle, client misuse can send on a different hardware doorbell than the virtual channel suggests. There is no TX done callback or RX support. Interrupts are masked because only polling/doorbell send is supported for now.

## Test Signals
Compile with Exynos message header, probe with enabled `pclk`, validate invalid channel IDs/types, confirm writes to the expected `INTGR1` bit, and ensure phandle allocation fails when all virtual channels are already bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/exynos-mailbox.c -->
