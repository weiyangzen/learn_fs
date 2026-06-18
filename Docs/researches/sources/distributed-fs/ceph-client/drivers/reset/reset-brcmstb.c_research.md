# sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb.c

Purpose: Broadcom STB SUN_TOP_CTRL_SW_INIT style reset controller.

Important APIs/types/functions: `struct brcmstb_reset`, `brcmstb_reset_assert()`, `brcmstb_reset_deassert()`, `brcmstb_reset_status()`, and `brcmstb_reset_probe()`.

Control flow: probe maps the resource and derives `nr_resets` from resource size divided by bank size times 32. Assert writes to bank `SW_INIT_SET`; deassert writes to `SW_INIT_CLEAR` then sleeps 100-200 us; status reads `SW_INIT_STATUS`.

State and persistence: hardware banks store reset state; driver only stores base and controller metadata.

Dependencies and integration: platform bus, OF compatible `brcm,brcmstb-reset`, MMIO, reset framework default one-cell xlate.

Risks and test signals: reset count depends on resource size and bank stride, so DT resource errors expose wrong IDs. Test multi-bank IDs, deassert delay, and status bits on supported Broadcom SoCs.
