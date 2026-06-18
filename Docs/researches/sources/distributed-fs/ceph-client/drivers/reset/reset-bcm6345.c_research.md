# sources/distributed-fs/ceph-client/drivers/reset/reset-bcm6345.c

Purpose: Broadcom BCM6345 reset controller for 32 active-low reset bits.

Important APIs/types/functions: `struct bcm6345_reset`, `bcm6345_reset_update()`, assert/deassert/reset/status ops, and `bcm6345_reset_probe()`.

Control flow: probe maps a single register, initializes lock, and registers 32 resets. Assert clears a bit; deassert sets it. `.reset` asserts, sleeps 10-20 ms, deasserts, then sleeps again so the block is ready. Status returns asserted when the bit is clear.

State and persistence: hardware register stores reset state; spinlock serializes register updates.

Dependencies and integration: built-in platform driver for `brcm,bcm6345-reset` and `brcm,bcm63xx-ephy-ctrl`, MMIO, reset framework.

Risks and test signals: raw read/write and active-low polarity require care. Test reset pulse delays, ePHY compatible binding, status polarity, and concurrent reset operations.
