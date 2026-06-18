# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-usb.c

Registers Sunxi USB gate clocks and optional reset controllers for several Allwinner SoCs. It handles register layouts where USB clock enable bits and reset bits share one clock/reset register.

`struct usb_clk_data` defines a `clk_mask`, `reset_mask`, and whether reset operations need the module clock enabled. `sunxi_usb_clk_setup()` maps the register, gets the parent clock name, allocates a sparse onecell clock array sized to the highest clock bit, registers gates for set bits, publishes an OF clock provider, then optionally allocates `usb_reset_data` and registers reset ops. Reset assert/deassert clears/sets reset bit `id` while holding the shared lock and optionally enabling the parent clock.

Gate and reset state persists in the USB clock register. Static spinlocks are used per compatible group. Reset data persists after registration and has no early-boot teardown. The file uses OF early declarations for sun4i/sun5i/sun6i/sun8i/sun9i USB compatibles, CCF gate helpers, and the reset-controller framework. USB PHY, host, and OTG drivers consume these clocks and reset lines.

Several error paths return without unmapping or freeing after partial setup. Reset `nr_resets` is derived from the highest reset bit, so unsupported holes can still be addressed by consumers if DT is wrong. Test signals include USB PHY/host probe, reset deassert sequencing, clock gate register readback, and A80 reset behavior where the reset controller first enables the associated clock.
