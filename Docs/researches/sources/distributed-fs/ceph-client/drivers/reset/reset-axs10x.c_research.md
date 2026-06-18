# sources/distributed-fs/ceph-client/drivers/reset/reset-axs10x.c

Purpose: Synopsys AXS10x reset driver for a simple write-one reset pulse register.

Important APIs/types/functions: `struct axs10x_rst`, `axs10x_reset_reset()`, `axs10x_reset_probe()`, and `axs10x_reset_ops`.

Control flow: probe maps resource 0, initializes spinlock, registers 32 reset lines. The `.reset` op writes `BIT(id)` to the reset register under lock; no assert/deassert/status are provided.

State and persistence: no cached state and no persistent software state; hardware self-handles the reset pulse.

Dependencies and integration: built-in platform driver bound by `snps,axs10x-reset`, MMIO, reset framework.

Risks and test signals: consumers needing level reset cannot use this provider. Test that reset pulses reach hardware, ID bounds are enforced by `nr_resets`, and clients tolerate lack of status/assert/deassert.
